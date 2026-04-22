# 📊 Pune Job Market Pulse
### Real-Time Data Analyst Job Demand Tracker — by Pramod Haladkar

> "I didn't use a Kaggle dataset. I scraped live job postings from Naukri to understand 
> what the Pune job market actually needs right now — and built a live dashboard that 
> shows it."

---

## 🎯 What This Project Does

This project scrapes real job postings from Naukri.com for data roles in Pune,
cleans and stores them in MySQL, performs NLP-based skill analysis, and presents
everything in a live Streamlit dashboard.

**Business Question:** *What skills do Pune companies actually demand from data professionals in 2026?*

---

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| Scraping | Python, Selenium, Undetected ChromeDriver |
| Storage | MySQL, Pandas |
| Analysis | Pandas, NLP (NLTK), Matplotlib, Seaborn |
| Dashboard | Streamlit, Plotly |
| Deployment | Streamlit Cloud (free) |

---

## 📁 Project Structure

```
pune_job_pulse/
│
├── step1_scraper.py        # Scrape Naukri job postings
├── step2_clean_store.py    # Clean data + store in MySQL
├── step3_nlp_analysis.py   # NLP analysis + generate charts
├── step4_dashboard.py      # Streamlit live dashboard
├── requirements.txt        # All dependencies
│
├── raw_jobs.csv            # Generated after step 1
├── cleaned_jobs.csv        # Generated after step 2
├── skill_frequency.csv     # Generated after step 2
├── insights.json           # Generated after step 3
│
└── charts/                 # Generated after step 3
    ├── top15_skills.png
    ├── job_category_pie.png
    ├── fresher_vs_experienced.png
    ├── skill_cooccurrence.png
    ├── top_companies.png
    └── skill_wordcloud.png
```

---

## 🚀 STEP-BY-STEP DEPLOYMENT GUIDE

### PHASE 1 — LOCAL SETUP

#### Step 1: Install Python & Chrome
- Download Python 3.10+ from python.org
- Download Google Chrome (latest version)

#### Step 2: Create project folder
```bash
mkdir pune_job_pulse
cd pune_job_pulse
```

#### Step 3: Install all libraries
```bash
pip install -r requirements.txt
```

#### Step 4: Install & Setup MySQL
- Download MySQL Community Server from mysql.com
- During setup, set root password (remember it!)
- Open MySQL Workbench and test connection

---

### PHASE 2 — RUN THE PROJECT

#### Step 5: Run the scraper
```bash
python step1_scraper.py
```
- Chrome will open automatically
- It will scrape Naukri for ~500 jobs
- Output: raw_jobs.csv
- ⚠️ If you see a CAPTCHA, solve it manually once

#### Step 6: Clean data + store in MySQL
- Open step2_clean_store.py
- Change DB_PASSWORD to your MySQL password
```bash
python step2_clean_store.py
```
- Output: cleaned_jobs.csv, skill_frequency.csv
- Data also stored in MySQL database: pune_jobs

#### Step 7: Run NLP analysis
```bash
python step3_nlp_analysis.py
```
- Output: 6 charts in /charts folder + insights.json
- Open charts/ folder to see your visualizations

#### Step 8: Run Streamlit dashboard locally
```bash
streamlit run step4_dashboard.py
```
- Opens at: http://localhost:8501
- You will see the full live dashboard!

---

### PHASE 3 — DEPLOY TO INTERNET (Free!)

#### Step 9: Push to GitHub
```bash
git init
git add .
git commit -m "Pune Job Market Pulse - Data Analyst Project"
git remote add origin https://github.com/pamu15/pune-job-pulse.git
git push -u origin main
```
Note: Do NOT push raw_jobs.csv or cleaned_jobs.csv with real scraped data
to avoid Naukri ToS issues. Push only the code files.

#### Step 10: Deploy on Streamlit Cloud (FREE)
1. Go to share.streamlit.io
2. Sign in with GitHub
3. Click "New App"
4. Select your repo: pamu15/pune-job-pulse
5. Select branch: main
6. Main file: step4_dashboard.py
7. Click Deploy!


This is the link you put on your resume!

---

## 📊 Key Findings (Update after your run)

| Metric | Value |
|--------|-------|
| Total jobs analyzed | ~500+ |
| Fresher-friendly jobs | ~X% |
| Most demanded skill | Python |
| Second most demanded | SQL |
| Power BI demand | ~X% |
| Top hiring company | TCS / Infosys / etc |

---

## 💬 What to Say in Interview

> "Most candidates use Titanic or IPL data from Kaggle. I wanted to do something 
> more relevant. I built a scraper that pulls live job postings from Naukri for 
> data roles in Pune, ran NLP analysis to find which skills actually matter, and 
> deployed it as a live dashboard. The key finding was that Python and SQL appear 
> in over 70% of postings — but Power BI is only in 30%, making it a differentiator 
> not a baseline. You can see the live app here: [your streamlit link]"

---

## 👤 Author

**Pramod Haladkar**  
B.Sc. Data Science — Savitribai Phule Pune University  
GitHub: github.com/pamu15  
Email: pamuhaladkar15@gmail.com
