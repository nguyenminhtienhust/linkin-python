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

from utils import (
    get_lk_credentials,
    enter_ids_on_lk_signin,
    get_job_detail,
    login_crm,
    connect,
    hasClass,
    check_lead_existed,
    edit_new_lead,
    add_new_lead
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
    titleInputElement.send_keys(jobs_names[2])
    
    seekButton = driver.find_element(By.ID,"searchButton")
    
    seekButton.click()
    time.sleep(5)
    jobs_fail = ["IT System Engineer","Market Research Intern","IT Network Engineer","Graduate Trainee","Administrative Assistant","Customer Support Engineer","Customer Support Consultant","Research Internship","Search Quality Rater","Digital Marketing Analyst","Project Administrator","Ford Internship","Management Trainee","Information Security Analyst","Assistant Engineering Executive","R&D Specialist","Veterinary Information Systems Officer","Junior Engineer","Research Assistant","Marketing Assistant","Administrative Assistant","Database Administration Officer","Administrator","Assistant project manager","Internship","Research Associate","Test Administrator","Document Control Administrator","Administrative Assistant","Practical Trainee","System Administrator","Design & Estimation Engineer","Senior Research Scientist","Project Coordinator"]
    keys_fail = ["Project Administrator","Project Manager","Research","Intern","Network","Graduate","Administrative","Assistant","Support","Marketing","Internship","Security","R&D","Junior","Administrative","Officer","Research"]
    access_token = login_crm()

    jobs = driver.find_elements(By.TAG_NAME,"article")
    for job in jobs:
        job_id = job.get_attribute("data-job-id")
        job_title = job.get_attribute("aria-label")
        print(job_id)
        print(job_title)
        
        job_detail_url = "https://www.jobstreet.com.my/job/" + job_id
        print(job_detail_url)
        root_window = driver.window_handles[0]
        #1 job window 
        driver.execute_script("window.open('');")
        job_detail_window = driver.window_handles[1]
        driver.switch_to.window(job_detail_window)
        driver.get(job_detail_url)
        
        time.sleep(5)
        #_126xumx1
        company_info = driver.find_elements(By.CLASS_NAME,"_1d0g9qk4")
        # for (index,info) in enumerate(company_info):
        #     print(str(index) + ": " + info.text)
        
        job_title = company_info[28].text
        print("Job Title:" + job_title)

        company_name = company_info[29].text
        print("Company Name:" + company_name)
        
        #szurmz6
        other_info = driver.find_elements(By.CLASS_NAME,"szurmz6")[1]
        address_element = other_info.find_elements(By.CLASS_NAME,"a1msqir")[1]
        address = address_element.text
        
        print("Address: " + address)
        
        company_detail_url = ""
        website_company = ""
        all_a = driver.find_elements(By.TAG_NAME,"a")
        for a in all_a:
            if hasClass(a,"_126xumx1"):
                print("Containt")
                company_detail_url = driver.find_element(By.CLASS_NAME,"_126xumx1").get_attribute("href")
                print("Company URL: " + company_detail_url)
            else:
                continue
        #2 company detail window 
        print(company_detail_url)
        if (company_detail_url != ""):
            driver.execute_script("window.open('');")
            company_detail_window = driver.window_handles[2]
            driver.switch_to.window(company_detail_window)
            driver.get(company_detail_url)
            time.sleep(5)
             #_116mc3b7 #2
            website_company = driver.find_elements(By.CLASS_NAME,"_116mc3b7")[1].get_attribute("href")

        full_content = ""
        full_content = '\n'.join([full_content, job_detail_url])
        full_content = '\n'.join([full_content, "#####"])
        sub_content = ""
        for key_fail in keys_fail:
            if key_fail in job_title:
                continue
        for job_fail in jobs_fail:
            if job_fail == job_title:
                continue
            
        sub_content = '\n'.join([sub_content, job_title])
        sub_content = '\n'.join([sub_content, job_detail_url])
        full_content = '\n'.join([full_content, sub_content])
        full_content = '\n'.join([full_content, "#####"])
    
        lead_id = check_lead_existed(company_name)
        print("\nLead id:" + lead_id + "\n")
        if (lead_id == ""):
            print("\n\nStarting add new:......\n\n")
            #assigned_user_id = get_min_sale()
            #print("Assigned User Id:" + assigned_user_id)
            time.sleep(2)
            add_new_lead(access_token=access_token,company_name=company_name,title=job_title,address=address,other_address="",phone="",website=website_company,content=full_content,assigned_user_id="assigned_user_id")
            if (website_company != ""):
                driver.close()#2 close company detail
                driver.switch_to.window(job_detail_window)
            driver.close()#1 close job detail
            driver.switch_to.window(root_window)
        else:
            print("\n\nStarting edit:......\n\n")
            time.sleep(2)
            #edit_new_lead(access_token=access_token,id=lead_id,company_name=company_name,title= job_title,address=address,other_address="",phone="",website=website_company,content=full_content)
            if (website_company != ""):
                driver.close()#2 close company detail
                driver.switch_to.window(job_detail_window)
            driver.close()#1 close job detail
            driver.switch_to.window(root_window)