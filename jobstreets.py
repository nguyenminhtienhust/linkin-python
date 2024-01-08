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
        job_id = job.get_attribute("data-job-id")
        print(job_id)
        time.sleep(2)
    

    