# ============================================================
# STEP 3: NLP ANALYSIS — SKILL CO-OCCURRENCE + INSIGHTS
# ============================================================
# pip install pandas matplotlib seaborn wordcloud nltk

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import itertools
import json
import os
import re

os.makedirs("charts", exist_ok=True)

# ---- LOAD DATA ----
df = pd.read_csv("cleaned_jobs.csv")

df["title"]        = df["title"].fillna("unknown").astype(str)
df["company"]      = df["company"].fillna("unknown").astype(str)
df["skills"]       = df["skills"].fillna("").astype(str)
df["job_category"] = df["job_category"].fillna("Other").astype(str)

# Rebuild skills_list from skills_clean column (saved as string in CSV)
df["skills_list"] = df["skills_clean"].fillna("").apply(
    lambda x: [s.strip().lower() for s in x.split(",") if s.strip()]
)

TITLE_SKILL_MAP = [
    "python", "machine learning", "deep learning", "nlp",
    "computer vision", "tensorflow", "pytorch", "keras",
    "data analysis", "data science", "sql", "excel",
    "power bi", "tableau", "opencv", "scikit-learn",
    "pandas", "numpy", "flask", "django", "fastapi",
    "artificial intelligence", "neural network", "llm",
    "generative ai", "langchain", "huggingface", "aws",
    "azure", "docker", "git", "statistics",
    "big data", "hadoop", "spark", "mongodb", "mysql"
]

def extract_skills_from_title(row):
    if isinstance(row["skills_list"], list) and len(row["skills_list"]) > 0:
        return row["skills_list"]
    title    = str(row.get("title", "")).lower()
    query    = str(row.get("search_query", "")).lower()
    combined = title + " " + query
    found = []
    for skill in TITLE_SKILL_MAP:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, combined):
            found.append(skill)
    if not found:
        category = str(row.get("job_category", "")).lower()
        if "ml engineer" in category or "machine learning" in category:
            return ["machine learning", "python", "deep learning"]
        elif "ai engineer" in category:
            return ["artificial intelligence", "python", "machine learning"]
        elif "data scientist" in category:
            return ["python", "data science", "statistics", "sql"]
        elif "data analyst" in category:
            return ["sql", "excel", "data analysis", "power bi"]
        elif "intern" in category:
            return ["machine learning", "python", "artificial intelligence"]
        else:
            return ["machine learning", "python"]
    return found

df["skills_list"] = df.apply(extract_skills_from_title, axis=1)

skill_df = pd.read_csv("skill_frequency.csv")
if skill_df.empty:
    all_skills_temp = []
    for skills in df["skills_list"]:
        if isinstance(skills, list):
            all_skills_temp.extend(skills)
    skill_counts = Counter(all_skills_temp)
    skill_df = pd.DataFrame(skill_counts.most_common(50), columns=["skill", "count"])
    skill_df["percentage"] = (skill_df["count"] / len(df) * 100).round(1)
    print(" skill_frequency.csv was empty — rebuilt from skills_list")

print(f" Loaded {len(df)} jobs and {len(skill_df)} skills")

# ============================================================
# CHART 1: TOP 15 SKILLS BAR CHART
# ============================================================
top15 = skill_df.head(15)

if not top15.empty:
    plt.figure(figsize=(12, 6))
    bars = plt.barh(top15["skill"][::-1], top15["percentage"][::-1], color="#4F46E5")
    plt.xlabel("% of Job Postings Requiring This Skill", fontsize=12)
    plt.title("Top 15 In-Demand Skills in Pune Data Jobs (2026)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    for bar, pct in zip(bars, top15["percentage"][::-1]):
        plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                 f"{pct}%", va="center", fontsize=10)
    plt.savefig("charts/top15_skills.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(" Chart 1 saved: top15_skills.png")
else:
    print(" Chart 1 skipped: no skill data")

# ============================================================
# CHART 2: JOBS BY CATEGORY PIE CHART
# ============================================================
cat_counts = df["job_category"].value_counts()

if not cat_counts.empty:
    plt.figure(figsize=(8, 8))
    colors = ["#4F46E5", "#7C3AED", "#EC4899", "#F59E0B", "#10B981",
              "#3B82F6", "#EF4444"]
    plt.pie(cat_counts.values, labels=cat_counts.index, autopct="%1.1f%%",
            colors=colors[:len(cat_counts)], startangle=140,
            textprops={"fontsize": 12})
    plt.title("Job Distribution by Category — Pune 2026", fontsize=14, fontweight="bold")
    plt.savefig("charts/job_category_pie.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(" Chart 2 saved: job_category_pie.png")
else:
    print(" Chart 2 skipped: no category data")

# ============================================================
# CHART 3: FRESHER FRIENDLY vs EXPERIENCED
# ============================================================
fresher_counts  = df["is_fresher_friendly"].value_counts()
fresher_val     = int(fresher_counts.get(True, 0))
experienced_val = int(fresher_counts.get(False, 0))
labels = ["Fresher Friendly\n(0-1 yr)", "Experienced\n(2+ yrs)"]
values = [fresher_val, experienced_val]

if sum(values) > 0:
    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color=["#10B981", "#EF4444"], width=0.5)
    plt.title("Fresher vs Experienced Job Openings in Pune",
              fontsize=14, fontweight="bold")
    plt.ylabel("Number of Jobs")
    for bar in bars:
        plt.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.5,
                 str(int(bar.get_height())),
                 ha="center", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig("charts/fresher_vs_experienced.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(" Chart 3 saved: fresher_vs_experienced.png")
else:
    print(" Chart 3 skipped: no fresher data")

# ============================================================
# CHART 4: SKILL CO-OCCURRENCE HEATMAP
# ============================================================
top10_skills = skill_df.head(10)["skill"].tolist()

if len(top10_skills) >= 2:
    co_matrix = pd.DataFrame(0, index=top10_skills, columns=top10_skills)

    for skills in df["skills_list"]:
        relevant = [s for s in skills if s in top10_skills]
        for s1, s2 in itertools.combinations(relevant, 2):
            co_matrix.loc[s1, s2] += 1
            co_matrix.loc[s2, s1] += 1

    plt.figure(figsize=(10, 8))
    sns.heatmap(co_matrix, annot=True, fmt="d", cmap="Blues",
                linewidths=0.5, square=True)
    plt.title("Skill Co-occurrence in Pune Job Postings\n(How often skills appear together)",
              fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig("charts/skill_cooccurrence.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(" Chart 4 saved: skill_cooccurrence.png")
else:
    print(" Chart 4 skipped: not enough skills for heatmap")

# ============================================================
# CHART 5: TOP HIRING COMPANIES
# ============================================================
company_counts = df[
    ~df["company"].str.lower().isin(["unknown", "n/a", "na", ""])
]["company"].value_counts().head(10)

if not company_counts.empty:
    plt.figure(figsize=(10, 5))
    company_counts[::-1].plot(kind="barh", color="#7C3AED")
    plt.xlabel("Number of Job Postings")
    plt.title("Top 10 Hiring Companies for Data Roles in Pune",
              fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig("charts/top_companies.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(" Chart 5 saved: top_companies.png")
else:
    print(" Chart 5 skipped: no valid company data found")

# ============================================================
# CHART 6: WORD CLOUD OF ALL SKILLS
# ============================================================
all_skills_text = " ".join([
    s.replace(" ", "_")
    for skills in df["skills_list"]
    if isinstance(skills, list)
    for s in skills
])

if all_skills_text.strip():
    wordcloud = WordCloud(
        width=1200, height=600,
        background_color="white",
        colormap="cool",
        max_words=100
    ).generate(all_skills_text)

    plt.figure(figsize=(14, 7))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("Skill Cloud — Pune Data Jobs 2026", fontsize=16, fontweight="bold")
    plt.savefig("charts/skill_wordcloud.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(" Chart 6 saved: skill_wordcloud.png")
else:
    print(" Chart 6 skipped: no skills text available")

# ============================================================
# GENERATE KEY INSIGHTS
# ============================================================
total_jobs   = len(df)
fresher_jobs = int(df["is_fresher_friendly"].sum())

top_skill     = skill_df.iloc[0]["skill"]      if not skill_df.empty else "N/A"
top_skill_pct = skill_df.iloc[0]["percentage"] if not skill_df.empty else 0

valid_companies = df[~df["company"].str.lower().isin(["unknown", "n/a", "na", ""])]
top_company = valid_companies["company"].value_counts().index[0] \
              if not valid_companies.empty else "N/A"

most_common_category = df["job_category"].value_counts().index[0] \
                       if not df["job_category"].empty else "N/A"

insights = {
    "total_jobs_scraped"    : int(total_jobs),
    "fresher_friendly_jobs" : fresher_jobs,
    "fresher_percentage"    : round(fresher_jobs / total_jobs * 100, 1) if total_jobs > 0 else 0,
    "top_skill"             : top_skill,
    "top_skill_percentage"  : float(top_skill_pct),
    "top_hiring_company"    : top_company,
    "most_common_role"      : most_common_category,
    "top_10_skills"         : skill_df.head(10)["skill"].tolist() if not skill_df.empty else []
}

with open("insights.json", "w") as f:
    json.dump(insights, f, indent=2)

print("\n" + "="*50)
print("KEY INSIGHTS FOR YOUR INTERVIEW:")
print("="*50)
print(f"Total jobs analyzed     : {total_jobs}")
print(f"Fresher-friendly jobs   : {fresher_jobs} ({insights['fresher_percentage']}%)")
print(f"Most demanded skill     : {top_skill} ({top_skill_pct}% of postings)")
print(f"Top hiring company      : {top_company}")
print(f"Most common role        : {most_common_category}")
print(f"Top 10 skills           : {', '.join(insights['top_10_skills'])}")
print("\n All charts saved in /charts folder")
print(" insights.json saved")