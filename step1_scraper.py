# ============================================================
# JOB SCRAPER — Naukri + Internshala
# ============================================================

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import random
from datetime import datetime

# ---------------- CONFIG ----------------
NAUKRI_QUERIES = [
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "Junior Data Scientist",
]

INTERNSHALA_QUERIES = [
    "data-science",
    "machine-learning",
    "data-analyst",
    "artificial-intelligence",
    "python",
]

LOCATION    = "Pune"
MAX_PAGES   = 3
OUTPUT_FILE = "raw_jobs.csv"


# ============================================================
# DRIVER
# ============================================================
def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--headless=new")
    driver = uc.Chrome(options=options, use_subprocess=True)
    driver.set_page_load_timeout(30)
    return driver


# ============================================================
# NAUKRI SCRAPER
# ============================================================
def scrape_naukri(driver, query, location, max_pages=3):
    jobs = []

    for page in range(max_pages):
        url = (
            f"https://www.naukri.com/{query.lower().replace(' ', '-')}-jobs"
            f"-in-{location.lower()}?pageNo={page + 1}"
        )
        print(f"  [Naukri] Page {page + 1}: {url}")

        try:
            driver.get(url)
            time.sleep(random.uniform(5, 9))

            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "div.srp-jobtuple-wrapper")
                    )
                )
            except Exception:
                print(f"    ⚠ No cards found on page {page + 1}")
                continue

            cards = driver.find_elements(By.CSS_SELECTOR, "div.srp-jobtuple-wrapper")
            print(f"    Found {len(cards)} cards")

            for card in cards:
                def get(selector, attr=None):
                    try:
                        el = card.find_element(By.CSS_SELECTOR, selector)
                        return el.get_attribute(attr) if attr else el.text.strip()
                    except Exception:
                        return "N/A"

                title      = get("a.title")
                company    = get("a.comp-name")
                experience = get("span.expwdth")
                salary     = get("span.sal")
                loc        = get("span.locWdth")
                posted     = get("span.job-post-day")

                # JavaScript executor reliably gets href even with lazy loading
                try:
                    anchor = card.find_element(By.CSS_SELECTOR, "a.title")
                    job_link = driver.execute_script("return arguments[0].href;", anchor)
                    if not job_link:
                        job_link = "N/A"
                except Exception:
                    job_link = "N/A"

                try:
                    skill_els = card.find_elements(By.CSS_SELECTOR, "ul.tags-gt li")
                    skills = ", ".join(s.text.strip() for s in skill_els if s.text.strip())
                except Exception:
                    skills = "N/A"

                jobs.append({
                    "source":       "Naukri",
                    "title":        title,
                    "company":      company,
                    "experience":   experience,
                    "salary":       salary,
                    "location":     loc,
                    "skills":       skills,
                    "posted":       posted,
                    "job_link":     job_link,
                    "search_query": query,
                    "scraped_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })

        except Exception as e:
            print(f"    ✗ Error: {e}")

    return jobs


# ============================================================
# INTERNSHALA SCRAPER
# ============================================================
INTERNSHALA_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://internshala.com/",
}

def scrape_internshala(query, location, max_pages=3):
    jobs    = []
    session = requests.Session()
    session.headers.update(INTERNSHALA_HEADERS)

    city = location.lower()

    for page in range(1, max_pages + 1):
        url = (
            f"https://internshala.com/internships/keywords-{query}"
            f"/location-{city}/page-{page}/"
        )
        print(f"  [Internshala] Page {page}: {url}")

        try:
            resp = session.get(url, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")

            cards = soup.select("div.internship_meta")
            if not cards:
                cards = soup.select("div.individual_internship")

            print(f"    Found {len(cards)} cards")

            for card in cards:
                def txt(selector, default="N/A"):
                    el = card.select_one(selector)
                    return el.get_text(strip=True) if el else default

                title    = txt("h3.job-internship-name") or txt("div.profile")
                company  = txt("h4.company-name") or txt("a.link_display_like_text")
                loc      = txt("div.location_link") or txt("a.location_link")
                stipend  = txt("span.stipend") or txt("div.stipend")
                duration = txt("div.item_body.duration") or txt("span.duration")
                posted   = txt("div.posted_by_container time") or txt("div.status-li")

                # Fix: correct Internshala link selectors
                try:
                    a_tag = card.select_one("a.job-title-href") \
                         or card.select_one("div.profile a") \
                         or card.select_one("h3 a") \
                         or card.select_one("a[href*='/internship/detail']")
                    if a_tag and a_tag.has_attr("href"):
                        raw = a_tag["href"]
                        job_link = ("https://internshala.com" + raw) if raw.startswith("/") else raw
                    else:
                        job_link = "N/A"
                except Exception:
                    job_link = "N/A"

                jobs.append({
                    "source":       "Internshala",
                    "title":        title,
                    "company":      company,
                    "experience":   "Fresher/Intern",
                    "salary":       stipend,
                    "location":     loc,
                    "skills":       duration,
                    "posted":       posted,
                    "job_link":     job_link,
                    "search_query": query,
                    "scraped_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })

            time.sleep(random.uniform(2, 5))

        except Exception as e:
            print(f"    ✗ Error: {e}")

    return jobs


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":

    all_jobs = []

    # ── NAUKRI (Selenium) ────────────────────────────────────────────────
    print("\n========== NAUKRI ==========")
    driver = init_driver()
    try:
        for query in NAUKRI_QUERIES:
            print(f"\n→ Query: {query}")
            jobs = scrape_naukri(driver, query, LOCATION, MAX_PAGES)
            all_jobs.extend(jobs)
            print(f"  +{len(jobs)} jobs  |  Total: {len(all_jobs)}")
            time.sleep(random.uniform(4, 8))
    finally:
        driver.quit()

    # ── INTERNSHALA (requests, no login needed) ──────────────────────────
    print("\n========== INTERNSHALA ==========")
    for query in INTERNSHALA_QUERIES:
        print(f"\n→ Query: {query}")
        jobs = scrape_internshala(query, LOCATION, MAX_PAGES)
        all_jobs.extend(jobs)
        print(f"  +{len(jobs)} jobs  |  Total: {len(all_jobs)}")
        time.sleep(random.uniform(3, 6))

    # ── SAVE CSV ─────────────────────────────────────────────────────────
    print(f"\n========== SAVING ==========")
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        before = len(df)
        df.drop_duplicates(subset=["title", "company", "location"], inplace=True)
        after = len(df)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"✅ Saved {after} unique jobs to '{OUTPUT_FILE}'  ({before - after} duplicates removed)")
        print("\nSample rows:")
        print(df[["source", "title", "company", "location", "job_link"]].head(10).to_string(index=False))
    else:
        print("❌ No jobs collected — check your internet connection.")