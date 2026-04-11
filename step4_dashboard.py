# ============================================================
# STEP 4: STREAMLIT DASHBOARD — LIVE WEB APP
# ============================================================
# pip install streamlit pandas plotly
# Run with: streamlit run step4_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import json
import os
import re

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Pune Job Market Pulse",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# TITLE_SKILL_MAP — same as Step 2 & 3
# ============================================================
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

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    # ✅ FIX 1: Check files exist before loading
    if not os.path.exists("cleaned_jobs.csv"):
        st.error("❌ cleaned_jobs.csv not found. Please run Step 2 first.")
        st.stop()
    if not os.path.exists("skill_frequency.csv"):
        st.error("❌ skill_frequency.csv not found. Please run Step 2 first.")
        st.stop()

    df = pd.read_csv("cleaned_jobs.csv")

    # ✅ FIX 2: Fill NaN values immediately
    df["title"]            = df["title"].fillna("unknown").astype(str)
    df["company"]          = df["company"].fillna("unknown").astype(str)
    df["skills"]           = df["skills"].fillna("").astype(str)
    df["job_category"]     = df["job_category"].fillna("Other").astype(str)
    df["experience"]       = df["experience"].fillna("N/A").astype(str)
    df["salary_clean"]     = df["salary_clean"].fillna("Not Disclosed").astype(str)
    df["location"]         = df["location"].fillna("N/A").astype(str)
    df["posted"]           = df["posted"].fillna("N/A").astype(str)
    df["is_fresher_friendly"] = df["is_fresher_friendly"].fillna(False)

    # ✅ FIX 3: Rebuild skills_list using TITLE_SKILL_MAP (not raw skills column)
    df["skills_list"] = df.apply(extract_skills_from_title, axis=1)

    skill_df = pd.read_csv("skill_frequency.csv")

    # ✅ FIX 4: Rebuild skill_df if empty
    if skill_df.empty:
        all_skills_temp = []
        for skills in df["skills_list"]:
            if isinstance(skills, list):
                all_skills_temp.extend(skills)
        skill_counts = Counter(all_skills_temp)
        skill_df = pd.DataFrame(
            skill_counts.most_common(50),
            columns=["skill", "count"]
        )
        skill_df["percentage"] = (skill_df["count"] / len(df) * 100).round(1)

    return df, skill_df

df, skill_df = load_data()

# ---- LOAD INSIGHTS ----
# ✅ FIX 5: Safe insights loading with fallback
if os.path.exists("insights.json"):
    with open("insights.json") as f:
        insights = json.load(f)
else:
    # Build insights on the fly if file missing
    total_jobs   = len(df)
    fresher_jobs = int(df["is_fresher_friendly"].sum())
    valid_cos    = df[~df["company"].str.lower().isin(["unknown", "n/a", "na", ""])]
    insights = {
        "total_jobs_scraped"    : total_jobs,
        "fresher_friendly_jobs" : fresher_jobs,
        "fresher_percentage"    : round(fresher_jobs / total_jobs * 100, 1) if total_jobs > 0 else 0,
        "top_skill"             : skill_df.iloc[0]["skill"] if not skill_df.empty else "N/A",
        "top_skill_percentage"  : float(skill_df.iloc[0]["percentage"]) if not skill_df.empty else 0,
        "top_hiring_company"    : valid_cos["company"].value_counts().index[0] if not valid_cos.empty else "N/A",
        "most_common_role"      : df["job_category"].value_counts().index[0] if not df.empty else "N/A",
        "top_10_skills"         : skill_df.head(10)["skill"].tolist()
    }

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<h1 style='text-align:center; color:#4F46E5;'>📊 Pune Job Market Pulse</h1>
<p style='text-align:center; color:#6B7280; font-size:16px;'>
Real-time analysis of Data Science & Analytics job demand in Pune | Built by Pramod Haladkar
</p>
<hr>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR FILTERS
# ============================================================
st.sidebar.header("🔍 Filter Jobs")

# ✅ FIX 6: Safe unique categories (drop empty/nan)
all_categories = sorted(df["job_category"].dropna().unique().tolist())

selected_category = st.sidebar.multiselect(
    "Job Category",
    options=all_categories,
    default=all_categories
)
fresher_only = st.sidebar.checkbox(
    "Show Fresher-Friendly Jobs Only (0-1 yr)", value=False
)

# Apply filters
# ✅ FIX 7: Handle empty selection gracefully
if not selected_category:
    filtered_df = df.copy()
else:
    filtered_df = df[df["job_category"].isin(selected_category)]

if fresher_only:
    filtered_df = filtered_df[filtered_df["is_fresher_friendly"] == True]

# ✅ FIX 8: Show warning if filters result in empty df
if filtered_df.empty:
    st.warning("⚠️ No jobs match your current filters. Please adjust the filters.")
    st.stop()

# ============================================================
# METRIC CARDS
# ============================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Jobs Analyzed", f"{len(filtered_df):,}")
with col2:
    fresher_count = int(filtered_df["is_fresher_friendly"].sum())
    st.metric("Fresher-Friendly Jobs", f"{fresher_count:,}")
with col3:
    st.metric("Top Demanded Skill", insights.get("top_skill", "N/A").title())
with col4:
    st.metric("Top Hiring Company", insights.get("top_hiring_company", "N/A"))

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# ROW 2: TOP SKILLS + JOB CATEGORY PIE
# ============================================================
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🔥 Top 15 In-Demand Skills in Pune")

    # ✅ FIX 9: Check skill_df has data before plotting
    if not skill_df.empty:
        top15 = skill_df.head(15).copy()
        fig_skills = px.bar(
            top15.iloc[::-1].reset_index(drop=True),
            x="percentage", y="skill",
            orientation="h",
            text="percentage",
            color="percentage",
            color_continuous_scale="Purples",
            labels={"percentage": "% of Job Postings", "skill": "Skill"}
        )
        fig_skills.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_skills.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            height=500,
            margin=dict(l=10, r=60, t=20, b=10)
        )
        st.plotly_chart(fig_skills, use_container_width=True)
    else:
        st.warning("⚠️ No skill data available")

with col_right:
    st.subheader("📁 Jobs by Category")
    cat_counts = filtered_df["job_category"].value_counts().reset_index()
    cat_counts.columns = ["category", "count"]

    if not cat_counts.empty:
        fig_pie = px.pie(
            cat_counts, names="category", values="count",
            color_discrete_sequence=px.colors.sequential.Purples_r,
            hole=0.4
        )
        fig_pie.update_layout(height=500, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("⚠️ No category data available")

# ============================================================
# ROW 3: FRESHER VS EXPERIENCED + TOP COMPANIES
# ============================================================
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("👩‍💻 Fresher vs Experienced Openings")
    fresher_val    = int(filtered_df["is_fresher_friendly"].sum())
    experienced_val = int((~filtered_df["is_fresher_friendly"]).sum())

    exp_data = pd.DataFrame({
        "type" : ["Fresher Friendly (0-1 yr)", "Experienced (2+ yrs)"],
        "count": [fresher_val, experienced_val]
    })
    fig_exp = px.bar(
        exp_data, x="type", y="count",
        color="type",
        color_discrete_map={
            "Fresher Friendly (0-1 yr)": "#10B981",
            "Experienced (2+ yrs)"     : "#EF4444"
        },
        text="count"
    )
    fig_exp.update_traces(textposition="outside")
    fig_exp.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig_exp, use_container_width=True)

with col_b:
    st.subheader("🏢 Top 10 Hiring Companies")

    # ✅ FIX 10: Filter unknown/N/A companies before plotting
    valid_cos = filtered_df[
        ~filtered_df["company"].str.lower().isin(["unknown", "n/a", "na", ""])
    ]

    if not valid_cos.empty:
        top_cos = valid_cos["company"].value_counts().head(10).reset_index()
        top_cos.columns = ["company", "openings"]
        fig_cos = px.bar(
            top_cos.iloc[::-1].reset_index(drop=True),
            x="openings", y="company",
            orientation="h",
            color="openings",
            color_continuous_scale="Blues",
            text="openings"
        )
        fig_cos.update_traces(textposition="outside")
        fig_cos.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            height=350,
            margin=dict(l=10, r=40, t=20, b=10)
        )
        st.plotly_chart(fig_cos, use_container_width=True)
    else:
        st.warning("⚠️ No valid company data found")

# ============================================================
# ROW 4: KEY INSIGHT CALLOUT
# ============================================================
st.markdown("---")
st.subheader("💡 Key Insight")

# ✅ FIX 11: Safe skill percentage lookup
def get_skill_pct(skill_name):
    match = skill_df[skill_df["skill"].str.contains(skill_name, case=False, na=False)]
    return round(float(match.iloc[0]["percentage"]), 1) if not match.empty else 0

python_pct  = get_skill_pct("python")
sql_pct     = get_skill_pct("sql")
powerbi_pct = get_skill_pct("power bi")

st.info(f"""
**Python** appears in **{python_pct}%** of Pune data job postings.  
**SQL** appears in **{sql_pct}%** of postings.  
But **Power BI** appears in only **{powerbi_pct}%** — meaning it's a **differentiator**, not a baseline requirement.

👉 If you have Python + SQL + Power BI, you stand out from **most** fresher candidates in Pune.
""")

# ============================================================
# ROW 5: RAW DATA TABLE
# ============================================================
st.markdown("---")
st.subheader("📋 Raw Job Listings")

# ✅ FIX 12: Only show columns that actually exist in the dataframe
desired_cols = ["title", "company", "experience", "salary_clean",
                "location", "skills", "posted", "job_category", "is_fresher_friendly"]
show_cols = [c for c in desired_cols if c in filtered_df.columns]

rename_map = {
    "title"             : "Job Title",
    "company"           : "Company",
    "experience"        : "Experience",
    "salary_clean"      : "Salary",
    "location"          : "Location",
    "skills"            : "Skills",
    "posted"            : "Posted",
    "job_category"      : "Category",
    "is_fresher_friendly": "Fresher?"
}

st.dataframe(
    filtered_df[show_cols].rename(columns=rename_map),
    use_container_width=True,
    height=400
)

# Download button
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Filtered Data as CSV",
    data=csv,
    file_name="pune_jobs_filtered.csv",
    mime="text/csv"
)

# ---- FOOTER ----
st.markdown("---")
st.markdown("""
<p style='text-align:center; color:#9CA3AF; font-size:13px;'>
Built by <strong>Pramod Haladkar</strong> | Data scraped from Naukri.com |
<a href='https://github.com/pamu15' target='_blank'>GitHub: pamu15</a>
</p>
""", unsafe_allow_html=True)