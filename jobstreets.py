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
        print(job)
        continue
        job_id = job.get_attribute("data-job-id")
        job_detail_url = "https://www.jobstreet.com.my/job/" + job_id
        print(job_detail_url)
        root_window = driver.window_handles[0]
        driver.execute_script("window.open('');")
        job_detail_window = driver.window_handles[1]
        driver.switch_to.window(job_detail_window)
        driver.get(job_detail_url)
        time.sleep(5)
        #_126xumx1
        company_info = driver.find_element(By.CLASS_NAME,"_1wkzzauf")
        print(company_info)
        
        company_url = company_info.get_attribute("href")
        print("Company URL: " + company_url)
        company_name = company_info.text
        print("Company Name:" + company_name)
        time.sleep(2)
    

    