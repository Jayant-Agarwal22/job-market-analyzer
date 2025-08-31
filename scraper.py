from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import pandas as pd

# --- Selenium Setup ---
DRIVER_PATH = 'D:/job-market-analyzer/chromedriver.exe'
service = Service(executable_path=DRIVER_PATH)
driver = webdriver.Chrome(service=service)

URL = "https://www.naukri.com/data-analyst-jobs"
driver.get(URL)

print("Scraping page, please wait...")
time.sleep(10) # Wait for JavaScript to load

html_after_js = driver.page_source
driver.quit() # Close the browser

# --- BeautifulSoup Parsing ---
soup = BeautifulSoup(html_after_js, "html.parser")
job_listings = soup.find_all('div', class_='srp-jobtuple-wrapper')

all_jobs_list = []

for job in job_listings:
    title = job.find('a', class_='title').text.strip() if job.find('a', class_='title') else "N/A"
    
    # The final, correct selector for company name
    company = job.find('a', class_='comp-name').text.strip() if job.find('a', class_='comp-name') else "N/A"
    
    experience_tag = job.find('span', class_='exp-wrap')
    experience = experience_tag.find('span').text.strip() if experience_tag and experience_tag.find('span') else "N/A"

    location_tag = job.find('span', class_='loc-wrap')
    location = location_tag.find('span').text.strip() if location_tag and location_tag.find('span') else "N/A"

    job_data = {
        'Title': title,
        'Company': company,
        'Experience': experience,
        'Location': location
    }
    all_jobs_list.append(job_data)

df = pd.DataFrame(all_jobs_list)
df.to_csv('naukri_jobs.csv', index=False)

print("----------------------------------------")
print(f"Success! Scraped {len(df)} jobs and saved them to 'naukri_jobs.csv'")