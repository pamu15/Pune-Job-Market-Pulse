# ============================================================
# STEP 2: CLEAN DATA + STORE IN MYSQL
# ============================================================

import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import re
from collections import Counter

# ---- LOAD RAW DATA ----
df = pd.read_csv("raw_jobs.csv")
print(f"Raw records: {len(df)}")

# ✅ Fill all NaN values immediately
df["title"]      = df["title"].fillna("").astype(str)
df["company"]    = df["company"].fillna("").astype(str)
df["experience"] = df["experience"].fillna("N/A").astype(str)
df["salary"]     = df["salary"].fillna("Not Disclosed").astype(str)
df["location"]   = df["location"].fillna("").astype(str)
df["skills"]     = df["skills"].fillna("").astype(str)
df["posted"]     = df["posted"].fillna("N/A").astype(str)

# ============================================================
# CLEANING
# ============================================================

# 1. Remove duplicates
df.drop_duplicates(subset=["title", "company"], inplace=True)
print(f"After dedup: {len(df)}")

# 2. Clean title
df["title_clean"] = df["title"].str.lower().str.strip()

# 3. Categorize job type
def categorize_job(title):
    if not isinstance(title, str) or title.strip() == "":
        return "Other"
    title = title.lower().strip()
    if any(x in title for x in ["data analyst", "analytics"]):
        return "Data Analyst"
    elif any(x in title for x in ["data scientist", "data science"]):
        return "Data Scientist"
    elif any(x in title for x in ["machine learning", "ml engineer"]):
        return "ML Engineer"
    elif any(x in title for x in ["ai engineer", "ai/ml", "artificial intelligence"]):
        return "AI Engineer"
    elif any(x in title for x in ["intern", "trainee"]):
        return "Intern/Trainee"
    else:
        return "Other"

df["job_category"] = df["title_clean"].apply(categorize_job)

# 4. Extract experience numbers
def extract_exp(exp_str):
    if pd.isna(exp_str) or exp_str == "N/A":
        return None
    nums = re.findall(r'\d+', str(exp_str))
    return int(nums[0]) if nums else None

df["exp_min_years"] = df["experience"].apply(extract_exp)

# 5. Flag fresher-friendly
df["is_fresher_friendly"] = df["exp_min_years"].apply(
    lambda x: True if x is None or x <= 1 else False
)

# 6. Clean salary
def clean_salary(sal):
    if not isinstance(sal, str) or sal.strip() == "":
        return None
    if sal.strip() in ["Not Disclosed", "N/A"]:
        return None
    return sal.strip()

df["salary_clean"] = df["salary"].apply(clean_salary)

# 7. Extract skills from title ✅ ONLY ONE skills_list assignment
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
    if isinstance(row["skills"], str) and row["skills"].strip() not in ["", "nan"]:
        return [s.strip().lower() for s in row["skills"].split(",") if s.strip()]
    
    title = str(row.get("title_clean", "")).lower()
    found = []
    
    for skill in TITLE_SKILL_MAP:
        # ✅ Use word boundary so "r" only matches the word "r" not inside words
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, title):
            found.append(skill)
    
    return found if found else ["general ai/ml"]

df["skills_list"] = df.apply(extract_skills_from_title, axis=1)  # ✅ ONLY THIS ONE

# Save cleaned data
df.to_csv("cleaned_jobs.csv", index=False)
print(f"✅ Cleaned data saved: {len(df)} records")

# ============================================================
# SKILLS FREQUENCY ANALYSIS
# ============================================================
all_skills = []
for skills in df["skills_list"]:
    if isinstance(skills, list):
        all_skills.extend(skills)

all_skills = [s for s in all_skills if s.strip() not in ["", "nan", "none"]]
print(f"Total skill mentions: {len(all_skills)}")

if len(all_skills) == 0:
    print("⚠️ No skills found")
    skill_df = pd.DataFrame(columns=["skill", "count", "percentage"])
else:
    skill_counts = Counter(all_skills)
    skill_df = pd.DataFrame(skill_counts.most_common(50), columns=["skill", "count"])
    skill_df["percentage"] = (skill_df["count"] / len(df) * 100).round(1)
    skill_df.to_csv("skill_frequency.csv", index=False)
    print("\nTop 15 Skills in Pune Job Market:")
    print(skill_df.head(15).to_string(index=False))

# ============================================================
# STORE IN MYSQL
# ============================================================
DB_HOST     = "localhost"
DB_USER     = "root"
DB_PASSWORD = "root"
DB_NAME     = "pune_jobs"

conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
cursor = conn.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
cursor.execute(f"USE {DB_NAME}")
conn.commit()
cursor.close()
conn.close()

engine = create_engine(f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

jobs_to_store = df[[
    "title", "company", "experience", "salary_clean",
    "location", "skills", "posted", "search_query",
    "job_category", "exp_min_years", "is_fresher_friendly", "scraped_at"
]]
jobs_to_store.to_sql("jobs", engine, if_exists="replace", index=False)
print(f"\n✅ {len(jobs_to_store)} jobs stored in MySQL table: jobs")

skill_df.to_sql("skill_frequency", engine, if_exists="replace", index=False)
print(f"✅ {len(skill_df)} skills stored in MySQL table: skill_frequency")