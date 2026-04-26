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
└── charts/                 # Generated after 


``
---


## 👤 Author

**Pramod Haladkar**  
B.Sc. Data Science — Savitribai Phule Pune University  
GitHub: github.com/pamu15  
Email: pamuhaladkar15@gmail.com
