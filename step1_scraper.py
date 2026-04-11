# ============================================================
# STEP 1: SCRAPE JOB POSTINGS FROM NAUKRI & INDEED
# ============================================================

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random
from datetime import datetime
import os


# ---------------- CONFIG ----------------
SEARCH_QUERIES = [
"Data Analyst",
"Data Scientist",
"Machine Learning Engineer",
"Junior Data Scientist",
 "AI & ML intern",
 "machine learning intern",
 "Data Science intern",
 "Data Analyst intern",
 "Ai intern"]

LOCATION = "Pune"
MAX_PAGES = 3


# ---------------- DRIVER ----------------
def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options, use_subprocess=True)
    return driver

# ---------------- SCRAPER ----------------
def scrape_naukri(driver,query, location, max_pages=3):

    driver = init_driver()
    jobs = []

    try:
        for page in range(max_pages):

            url = f"https://www.naukri.com/{query.replace(' ', '-')}-jobs-in-{location.lower()}?pageNo={page+1}"
            print("Scraping:", url)

            driver.get(url)
            time.sleep(random.uniform(5, 10))

            try:
                
                WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.jobTuple"))
            
                
)
                
            except:
                print(f"No jobs found on page {page+1}")
                continue

            job_cards = driver.find_elements(By.CSS_SELECTOR, "article.jobTuple")
            print("Found:", len(job_cards))

            for card in job_cards:

                try:
                    title = card.find_element(By.CSS_SELECTOR, "a.title").text.strip()
                except:
                    title = "N/A"

                try:
                    company = card.find_element(By.CSS_SELECTOR, "a.subTitle").text.strip()
                except:
                    company = "N/A"

                try:
                    experience = card.find_element(By.CSS_SELECTOR, "li.experience span").text.strip()
                except:
                    experience = "N/A"

                try:
                    salary = card.find_element(By.CSS_SELECTOR, "li.salary span").text.strip()
                except:
                    salary = "Not Disclosed"

                try:
                    location_text = card.find_element(By.CSS_SELECTOR, "li.location span").text.strip()
                except:
                    location_text = "N/A"

                try:
                    skills_elements = card.find_elements(By.CSS_SELECTOR, "li.tag-li")
                    skills = [s.text.strip() for s in skills_elements if s.text.strip()]
                except:
                    skills = []

                try:
                    posted = card.find_element(By.CSS_SELECTOR, "span.type").text.strip()
                except:
                    posted = "N/A"

                try:
                    job_link = card.find_element(By.CSS_SELECTOR, "a.title").get_attribute("href")
                except:
                    job_link = "N/A"

                jobs.append({
                    "title": title,
                    "company": company,
                    "experience": experience,
                    "salary": salary,
                    "location": location_text,
                    "skills": ", ".join(skills),
                    "posted": posted,
                    "job_link": job_link,
                    "search_query": query,
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
    
    finally:
        try:
            driver.quit()
        except:
            pass
        
    return jobs

def scrape_indeed(driver,query, location, max_pages=3):

    driver = init_driver()
    jobs = []

    try:
        for page in range(max_pages):

            url = f"https://in.indeed.com/jobs?q={query.replace(' ', '+')}&l={location}&start={page*10}"
            print("Scraping:", url)

            driver.get(url)
            time.sleep(random.uniform(2, 6))

            try:
                WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.job_seen_beacon")))
                
            except:
                print(f"No jobs found on page {page+1}")
                continue

            job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon")
            print("Found:", len(job_cards))

            for card in job_cards:

                try:
                    title = card.find_element(By.CSS_SELECTOR, "h2.jobTitle span").text
                except:
                    title = "N/A"

                try:
                    company = card.find_element(By.CSS_SELECTOR, "span.companyName").text
                except:
                    company = "N/A"

                try:
                    experience = card.find_element(By.CSS_SELECTOR, "div.metadata span").text.strip()

                except:
                    experience = "N/A"

                try:
                    salary = card.find_element(By.CSS_SELECTOR, "li.salary span").text.strip()
                except:
                    salary = "Not Disclosed"

                try:
                    location_text = card.find_element(By.CSS_SELECTOR, "div.companyLocation").text
                except:
                    location_text = "N/A"

                try:
                    skills_elements = card.find_elements(By.CSS_SELECTOR, "li.tag-li")
                    skills = [s.text.strip() for s in skills_elements if s.text.strip()]
                except:
                    skills = []

                try:
                    posted = card.find_element(By.CSS_SELECTOR, "span.type").text.strip()
                except:
                    posted = "N/A"

                try:
                    job_link = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a").get_attribute("href")
                except:
                    job_link = "N/A"

                jobs.append({
                    "title": title,
                    "company": company,
                    "experience": experience,
                    "salary": salary,
                    "location": location_text,
                    "skills": ", ".join(skills),
                    "posted": posted,
                    "job_link": job_link,
                    "search_query": query,
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
    
    finally:
        try:
            driver.quit()
        except:
            pass
        
    return jobs

# ---------------- MAIN ----------------
if __name__ == "__main__":
   
    
    all_jobs = []

    driver = init_driver()                

    for query in SEARCH_QUERIES:
        print("\nSearching:", query)

        naukri_jobs = scrape_naukri(driver, query, LOCATION, MAX_PAGES)   
        indeed_jobs = scrape_indeed(driver, query, LOCATION, MAX_PAGES)   

        all_jobs.extend(naukri_jobs)
        all_jobs.extend(indeed_jobs)

        print("Total jobs so far:", len(all_jobs))
        time.sleep(random.uniform(5, 10))

    driver.quit()                         
    
    if len(all_jobs) > 0:
        df = pd.DataFrame(all_jobs)
        df.drop_duplicates(subset=["title", "company", "location"], inplace=True)  # ✅ dedup
        df.to_csv("raw_jobs.csv", index=False)
        print("✅ File saved successfully")
    else:
        print("❌ No jobs collected")
    
  

   
