import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
from selenium import webdriver
from bs4 import BeautifulSoup

# --- Page Configuration ---
st.set_page_config(
    page_title="Live Job Market Analyzer",
    page_icon="🚀",
    layout="wide"
)

# --- Sidebar ---
st.sidebar.title("About")
st.sidebar.info(
    "This application scrapes live job data from Naukri.com "
    "to provide real-time analysis on top hiring companies, "
    "locations, and in-demand skills."
)
st.sidebar.markdown("---")
st.sidebar.markdown("Built by a passionate CSE student.")

# --- The Scraper Function ---
@st.cache_data(ttl=3600)
def scrape_naukri_data(job_title):
    formatted_job_title = job_title.replace(' ', '-')
    URL = f"https://www.naukri.com/{formatted_job_title}-jobs"

    # --- SELENIUM SETUP FOR STREAMLIT CLOUD ---
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # On Streamlit Cloud, Selenium Manager or the system's chromedriver will be used
    driver = webdriver.Chrome(options=options)
    
    driver.get(URL)
    time.sleep(10)
    html_after_js = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html_after_js, "html.parser")
    job_listings = soup.find_all('article', class_='jobTuple')

    if not job_listings:
        return pd.DataFrame()

    all_jobs_list = []
    for job in job_listings:
        title = job.find('a', class_='title').text.strip() if job.find('a', class_='title') else "N/A"
        company = job.find('a', class_='subTitle').text.strip() if job.find('a', class_='subTitle') else "N/A"
        skills_container = job.find('ul', class_='tags')
        if skills_container:
            skills_tags = skills_container.find_all('li')
            skills = ', '.join([skill.text.strip() for skill in skills_tags])
        else:
            skills = "N/A"
        
        all_jobs_list.append({'Title': title, 'Company': company, 'Skills': skills})

    return pd.DataFrame(all_jobs_list)


# --- Main App Interface ---
st.title("🚀 Live Job Market Analyzer")
st.markdown("Enter a job title to get instant insights into the current job market.")

job_title_input = st.text_input("Job title:", "Data Analyst", help="e.g., 'Software Engineer', 'Product Manager'")

if st.button("Analyze Job Market"):
    if job_title_input:
        with st.spinner(f"Scraping live data for '{job_title_input}'... Please wait."):
            df = scrape_naukri_data(job_title_input)

        if not df.empty:
            st.success(f"Analysis Complete! Found {len(df)} job listings.")
            # ... (rest of analysis)
            st.markdown("---")
            df['Company'] = df['Company'].astype(str).str.strip()
            company_df = df[(df['Company'].str.lower() != 'nan') & (df['Company'] != 'N/A')]
            st.header(f"Analysis for '{job_title_input}'")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Top 10 Hiring Companies")
                top_companies = company_df['Company'].value_counts().head(10)
                fig1, ax1 = plt.subplots(figsize=(8, 6))
                sns.barplot(x=top_companies.values, y=top_companies.index, ax=ax1, palette='viridis')
                st.pyplot(fig1)
            with col2:
                st.subheader("Top 10 In-Demand Skills")
                skills_series = df[df['Skills'] != 'N/A']['Skills'].str.split(', ').explode()
                top_skills = skills_series.value_counts().head(10)
                fig2, ax2 = plt.subplots(figsize=(8, 6))
                if not top_skills.empty:
                    sns.barplot(x=top_skills.values, y=top_skills.index, ax=ax2, palette='plasma')
                else:
                    ax2.text(0.5, 0.5, 'No skills found', horizontalalignment='center', verticalalignment='center')
                st.pyplot(fig2)
        else:
            st.error(f"Could not find any job listings for '{job_title_input}'. The website may be blocking the scrape.")
    else:
        st.warning("Please enter a job title.")