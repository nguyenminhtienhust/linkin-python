import argparse
import os
import logging
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import pandas as pd

from general_lk_utils import (
    get_lk_credentials,
    enter_ids_on_lk_signin,
    get_job_detail,
    login_crm,
    connect,
    hasClass
)

if __name__ == "__main__":
    job_url = "https://www.jobstreet.com.my/ios-developer-jobs/in-Malaysia"
    list_webs = ["https://www.jobstreet.com.my","https://www.jobstreet.com.sg","https://www.jobstreet.co.id"]
    jobs_names = [".net developer","java developer","ios developer","android developer","flutter developer"]

    driver = webdriver.Chrome(options=Options())
    driver.maximize_window()
    driver.get(list_webs[0])
    time.sleep(3)
    
    titleInputElement = driver.find_element(By.ID,"keywords-input")
    titleInputElement.send_keys(jobs_names[0])
    
    seekButton = driver.find_element(By.ID,"searchButton")
    
    seekButton.click()
    time.sleep(5)
    
    jobs = driver.find_elements(By.TAG_NAME,"article")
    for job in jobs:
        print(job.text)
        job_id = job.get_attribute("data-job-id")
        job_title = job.get_attribute("aria-label")
        print(job_id)
        print(job_title)
        
        job_detail_url = "https://www.jobstreet.com.my/job/" + job_id
        print(job_detail_url)
        root_window = driver.window_handles[0]
        driver.execute_script("window.open('');")
        job_detail_window = driver.window_handles[1]
        driver.switch_to.window(job_detail_window)
        driver.get(job_detail_url)
        time.sleep(5)
        #_126xumx1
        company_info = driver.find_elements(By.CLASS_NAME,"_1d0g9qk4")
        for (index,info) in enumerate(company_info):
            print(str(index) + ": " + info.text)
        
        company_name = company_info[29].text
        print("Company Name:" + company_name)

        #_126xumx1
        all_a = driver.find_elements(By.TAG_NAME,"a")
        for a in all_a:
            if hasClass(a,"_126xumx1"):
                company_url = driver.find_element(By.CLASS_NAME,"_126xumx1").get_attribute("href")
                print("Company URL: " + company_url)
            else:
                continue

        time.sleep(2)
        driver.close()#close  company_window
        driver.switch_to.window(root_window)
    

    