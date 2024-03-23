import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.firefox.options import Options
from datetime import datetime, timedelta
import json


st.markdown("""
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link href='https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css' rel='stylesheet'>
""", unsafe_allow_html=True)


def scrape_data():
    KosovaJob()
    TelegrafiJob()
    GjirafaJobs()


all_jobs = {}
def KosovaJob():
    try:
        options = Options() 
        options.add_argument("-headless") 
        driver = webdriver.Firefox(options=options)
        driver.get("https://kosovajob.com/")
        driver.maximize_window()
    except Exception as e:
        st.error(f"An error occurred while scraping. Error details: {str(e)}")

    choose_category = driver.find_element(By.XPATH, "//select[@id='jobIndustry']")
    category = Select(choose_category)
    category.select_by_visible_text('Teknologji e Informacionit')
    job_cards = driver.find_elements(
        By.XPATH, "//div[contains(@class,'listCnt')]//div[contains(@class,'jobListCnts') and (contains(@class,'jobListPrm') or contains(@class,'jobListStd'))]"
    )

    for job in job_cards:
        link = job.find_element(By.XPATH, "./a").get_attribute('href')
        title = job.find_element(By.XPATH, ".//div[contains(@class, 'jobListTitle')]").text
        city = job.find_element(By.XPATH, ".//div[contains(@class, 'jobListCity')]").text
        expire_date = job.find_element(By.XPATH, ".//div[contains(@class, 'jobListExpires')]").text


        # Find the element using its XPath or any other locator strategy
        element = job.find_element(By.XPATH, ".//div[@class='jobListImage lozad']")
        data_background_image_value = element.get_attribute("data-background-image")

        all_jobs[title] = {
            'city': city,
            'expire_date': expire_date,
            'image': data_background_image_value,
            'link': link
        }

    driver.quit()

def TelegrafiJob():
    try:
        options = Options() 
        options.add_argument("-headless") 
        driver = webdriver.Firefox(options=options)
        driver.get("https://jobs.telegrafi.com/")
        driver.maximize_window()
    except Exception as e:
        st.error(f"An error occurred while scraping. Error details: {str(e)}")

    choose_city = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//select[@id='vendi']")))
    city = Select(choose_city)
    city.select_by_visible_text('Prishtinë')

    choose_category = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//select[@id='kategoria']")))
    category = Select(choose_category)
    category.select_by_visible_text("Teknologji Informative - IT")

    driver.find_element(By.XPATH, "/html/body/section/div[1]/div[3]/form/div[2]/button").click()

    telegrafi_jobs = driver.find_elements(By.XPATH, "//div[contains(@class,'item-job') or contains(@class, 'job-info')]")

    for telegrafi_job in telegrafi_jobs:
        link = telegrafi_job.find_element(By.XPATH, "./a").get_attribute("href")
        title = telegrafi_job.find_element(By.XPATH, ".//div[contains(@class, 'job-name')]/h3").text
        city = telegrafi_job.find_element(By.XPATH, ".//div[contains(@class, 'job-name')]/span[contains(@class, 'puna-location')]").text
        expire_date = telegrafi_job.find_element(By.XPATH, ".//div[contains(@class,'job-schedule')]/span/strong").text
        
        # Find the img tag using the provided XPath
        img_element = telegrafi_job.find_element(By.XPATH, ".//img")
        data_background_image_value = img_element.get_attribute("src")
        
        all_jobs[title] = {
            'city': city,
            'expire_date': expire_date  + ' ditë',
            'image': data_background_image_value,
            'link': link
        }   

    driver.quit()

    with open('data.json', 'w') as json_file:
        json.dump(all_jobs, json_file, indent=2)



def GjirafaJobs():
    try:
        options = Options() 
        options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)
        driver.get("https://gjirafa.com/Top/Pune?sh=Kosove&r=Prishtine&k=Teknologji%20Informative%20-%20IT")
        driver.maximize_window()
    except Exception as e:
        st.error(f"An error occurred while scraping. Error details: {str(e)}")


    gjirafa_jobs = driver.find_elements(By.XPATH, "//ul[@class='listView fullRelLeft mrrjp']/li")
    
    for job in gjirafa_jobs:
        link = job.find_element(By.XPATH, './a').get_attribute('href')
        title = job.find_element(By.XPATH, ".//h3[@id='titulli']//a").text
        city = job.find_element(By.XPATH, "./div[1]/div[1]/p[2]").text
        
        expire_date = job.find_element(By.XPATH, "./div[1]/div[2]/p[3]").text.split(":")[1].strip()
        today = datetime.today()
        expire_date_object = datetime.strptime(expire_date, "%d/%m/%Y")
        date_difference = expire_date_object - today
        days_difference = date_difference.days

        img_element = job.find_element(By.XPATH, "./a/div[1]/div[1]")
        background_image_style = img_element.get_attribute("style")
        image_url = background_image_style.split("(")[1].split(")")[0].strip("'")

        if days_difference < 1:
            continue

        all_jobs[title] = {
        'city': city,
        'expire_date': f'{days_difference} ditë',
        'image': image_url,
        'link': link
        }
        
    driver.quit()

    with open('data.json', 'w') as json_file:
        json.dump(all_jobs, json_file, indent=2)


col1, col2 = st.columns([3, 1])  
col1.title(":technologist: Jobs")

# Button in the second column
if col2.button("Loading Jobs"):
    scrape_data()


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
                <div class="card m-1">
                    <a href="{job_info['link']}" class="text-decoration-none text-dark d-block">
                        <div class="d-flex flex-row">
                            <div class="p-3" style="flex: 0 0 80px; max-width: 80px;">
                                <div class="bg-image" style="background-image: url({job_info['image']}); height: 80px; background-size: contain; background-position: center; object-fit: contain; background-repeat: no-repeat; width: 100%;"></div>
                            </div>
                            <div class="p-3 flex-grow-1">
                                <div class="font-weight-bold fs-5 mb-3" style="font-size: 15px;">{title}</div>
                                <div class="d-flex justify-content-between">
                                    <div class="d-flex align-items-center" style="font-size: 13px;">
                                        <i class='bx bx-buildings'></i>{job_info['city']}
                                    </div>
                                    <div class="text-muted d-flex align-items-center" style="font-size: 13px;">
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
