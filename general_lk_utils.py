import time
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import random
import json
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

SELECT_CONTRACT_BUTTON_SELECTOR = "#main > div > div > div:nth-child(3) > form > div > ul > li:nth-child(1) > div > div.contract-list__item-buttons > button"

def get_job_detail(driver,job_id):
    root_window = driver.window_handles[0]
    driver.execute_script("window.open('');")
    job_detail_window = driver.window_handles[1]
    driver.switch_to.window(job_detail_window)

    time.sleep(2)
    job_detail_url = 'https://www.linkedin.com/jobs/view/' + job_id
    print(job_detail_url)
    time.sleep(3)
    driver.get(job_detail_url)
    time.sleep(3)
    
    infos_list = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__primary-description-without-tagline")
    company_url = infos_list.find_element(By.CSS_SELECTOR,"a").get_attribute("href")
    print("Company URL: " + company_url)
    time.sleep(3)

    job_des = driver.find_element(By.ID,"job-details").text
    print("Job Des: " + job_des)
    time.sleep(3)

    #company screen
    driver.execute_script("window.open('');")
    company_window = driver.window_handles[2]
    driver.switch_to.window(company_window)
    company_about_url = company_url.replace("/life", "/about")
    driver.get(company_about_url)
    time.sleep(3)
        
    text_bodys = driver.find_elements(By.CLASS_NAME,"text-body-medium")
    index = 0
    for text in text_bodys:
        time.sleep(2)
        index += 1
        print(str(index) + ": " +  text.text)
        
    time.sleep(5)
    
    driver.execute_script("window.open('');")
    jobs_company_window = driver.window_handles[3]
    driver.switch_to.window(jobs_company_window)
    jobs_company_url = company_url.replace("/life", "/jobs")
    driver.get(jobs_company_url)
    time.sleep(3)
    show_all_button = driver.find_element(By.CLASS_NAME,"link-without-hover-visited")
    show_all_button.click()
    time.sleep(3)
    
    #get list jobs
    jobs = driver.find_elements(By.CLASS_NAME,"job-card-container__link")
    print("Please Zoom in then press Enter")
    count = len(jobs)
    #input()
    print(count)
    
    for job in jobs:
        time.sleep(3)
        job_title = job.text
        print(job_title)
        
    driver.close()#close  jobs_company_window
    time.sleep(2)
    driver.switch_to.window(company_window)
    time.sleep(2)
    driver.close()#close  company_window
    driver.switch_to.window(job_detail_window)
    time.sleep(2)
    driver.close()#close  job_detail_window
    time.sleep(3)
    driver.switch_to.window(root_window)  

def get_lk_credentials(path="./lk_credentials.json"):
    f = open(path)
    data = json.load(f)
    f.close()
    return data


def enter_ids_on_lk_signin(driver, email, password):
    time.sleep(2)
    usernameInputElement = driver.find_element(By.ID, "username")
    usernameInputElement.send_keys(email)
    passwordInputElement = driver.find_element(By.ID, "password")
    passwordInputElement.send_keys(password)
    submitElement = driver.find_element(
        By.CSS_SELECTOR,
        "#organic-div > form > div.login__form_action_container > button",
    )
    time.sleep(1)
    submitElement.click()
    time.sleep(5)


def get_lk_url_from_sales_lk_url(url):
    parsed = re.search("/lead/(.*?),", url, re.IGNORECASE)
    if parsed:
        return f"https://www.linkedin.com/in/{parsed.group(1)}"
    return None


def select_contract_lk(driver):
    contract_filter = driver.find_element(
        By.CSS_SELECTOR, SELECT_CONTRACT_BUTTON_SELECTOR
    )
    contract_filter.click()
    time.sleep(4)
    return


def remove_url_parameter(url, param):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    if param in query_params:
        del query_params[param]

    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment,
        )
    )

    return new_url
