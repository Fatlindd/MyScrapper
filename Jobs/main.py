import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.firefox.options import Options
import json


class JobScraper:
    def __init__(self):
        self.all_jobs = {}
        self.initialize_webdriver()

    def initialize_webdriver(self):
        options = Options()
        options.add_argument("-headless")
        self.driver = webdriver.Firefox(options=options)
        self.driver.maximize_window()

    def scrape_kosova_job(self):
        self.driver.get("https://kosovajob.com/")
        choose_category = self.driver.find_element(By.XPATH, "//select[@id='jobIndustry']")
        category = Select(choose_category)
        category.select_by_visible_text('Teknologji e Informacionit')
        job_cards = self.driver.find_elements(
            By.XPATH, "//div[contains(@class,'listCnt')]//div[contains(@class,'jobListCnts') and (contains(@class,'jobListPrm') or contains(@class,'jobListStd'))]"
        )

        for job in job_cards:
            self.extract_job_data(job)

    def scrape_telegrafi_job(self):
        self.driver.get("https://jobs.telegrafi.com/")
        choose_city = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//select[@id='vendi']"))
        )
        city = Select(choose_city)
        city.select_by_visible_text('Prishtinë')

        choose_category = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//select[@id='kategoria']"))
        )
        category = Select(choose_category)
        category.select_by_visible_text("Teknologji Informative - IT")

        self.driver.find_element(By.XPATH, "/html/body/section/div[1]/div[3]/form/div[2]/button").click()
        telegrafi_jobs = self.driver.find_elements(By.XPATH, "//div[contains(@class,'item-job') or contains(@class, 'job-info')]")

        for telegrafi_job in telegrafi_jobs:
            self.extract_job_data(telegrafi_job, is_telegrafi=True)

    def extract_job_data(self, job, is_telegrafi=False):
        link = job.find_element(By.XPATH, "./a").get_attribute('href')
        title_xpath = ".//div[contains(@class, 'jobListTitle')]" if not is_telegrafi else ".//div[contains(@class, 'job-name')]/h3"
        title = job.find_element(By.XPATH, title_xpath).text
        city_xpath = ".//div[contains(@class, 'jobListCity')]/span" if not is_telegrafi else ".//div[contains(@class, 'job-name')]/span[contains(@class, 'puna-location')]"
        city = job.find_element(By.XPATH, city_xpath).text
        expire_date_xpath = ".//div[contains(@class, 'jobListExpires')]" if not is_telegrafi else ".//div[contains(@class,'job-schedule')]/span/strong"
        expire_date = job.find_element(By.XPATH, expire_date_xpath).text

        img_xpath = ".//div[@class='jobListImage lozad']//img" if not is_telegrafi else ".//img"
        img_element = job.find_element(By.XPATH, img_xpath)
        data_background_image_value = img_element.get_attribute("src")

        self.all_jobs[title] = {
            'city': city,
            'expire_date': expire_date,
            'image': data_background_image_value,
            'link': link
        }

    def save_to_json(self):
        with open('data.json', 'w') as json_file:
            json.dump(self.all_jobs, json_file, indent=2)

    def close_driver(self):
        self.driver.quit()


def main():
    st.markdown("""
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <link href='https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css' rel='stylesheet'>
    """, unsafe_allow_html=True)

    job_scraper = JobScraper()

    st.title(":technologist: Jobs For You")

    # Create a button to trigger scraping
    if st.button("Loading Jobs"):
        st.text("Fetching data. Please wait...")
        job_scraper.scrape_kosova_job()
        job_scraper.scrape_telegrafi_job()
        job_scraper.save_to_json()
        st.success("Data fetched successfully!")

    # Read data from the JSON file
    with open('data.json', 'r') as json_file:
        all_jobs = json.load(json_file)

    # Display cards in rows with three cards per row
    cards_per_row = 2
    num_jobs = len(all_jobs)

    for i in range(0, num_jobs, cards_per_row):
        row_jobs = list(all_jobs.items())[i:i + cards_per_row]

        # Create a row of cards
        card_columns = st.columns(cards_per_row)
        for card_column, (title, job_info) in zip(card_columns, row_jobs):
            with card_column:
                st.markdown(
                    f"""
                    <div class="card m-2">
                        <a href="{job_info['link']}" class="text-decoration-none text-dark">
                            <div class="d-flex flex-row">
                                <div class="p-3" style="width: 80px;">
                                    <div class="bg-image" style="background-image: url({job_info['image']}); height: 80px; background-size: contain; background-position: center; object-fit: contain; background-repeat: no-repeat;"></div>
                                </div>
                                <div class="p-3">
                                    <div class="font-weight-bold fs-5" style="font-size: 15px;">{title}</div>
                                    <div class="d-flex justify-content-between my-3">
                                        <div class="mt-2 d-flex align-items-center" style="font-size: 13px;">
                                            <i class='bx bx-buildings'></i>{job_info['city']}
                                        </div>
                                        <div class="text-muted mt-2 d-flex align-items-center" style="font-size: 13px;">
                                            <i class='bx bx-time-five px-1'></i>{job_info['expire_date']}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    job_scraper.close_driver()


if __name__ == "__main__":
    main()
