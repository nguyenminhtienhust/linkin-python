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
	add_new_lead,
	check_company_existed,
	add_new_account,
	edit_account
)

if __name__ == "__main__":
	job_url = "https://www.jobstreet.com.my/ios-developer-jobs/in-Malaysia"
	list_webs = ["https://www.jobstreet.com.my","https://www.jobstreet.com.sg","https://www.jobstreet.co.id"]
	jobs_names = [".net developer","java developer","ios developer","android developer","flutter developer"]
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--disable-blink-features=AutomationControlled')    
	chrome_options.add_experimental_option("useAutomationExtension", False)
	chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])
	cService = webdriver.ChromeService(executable_path='C:\Workspace\CRMFitech\ChromeDriver\chromedriver.exe')
	driver = webdriver.Chrome(service = cService, options=chrome_options)
    #chrome_options.add_argument("window-size=1680,8000")

	# driver = webdriver.Chrome(options=Options())
	driver.maximize_window()
	driver.get(list_webs[0])
	# time.sleep(3)
	
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
		# job_title = job.get_attribute("aria-label")
		print(job_id)
		hirer_link = job.find_element(By.TAG_NAME,"a").get_attribute("href")
		print(hirer_link)
  
		
		# job_detail_url = "https://www.jobstreet.com.my/job/" + job_id
		# print(job_detail_url)
		root_window = driver.window_handles[0]
		#1 job window 
		driver.execute_script("window.open('');")
		job_detail_window = driver.window_handles[1]
		driver.switch_to.window(job_detail_window)
		driver.get(hirer_link)
		
		time.sleep(5)
		driver.close()
		driver.switch_to.window(root_window)
		# #_126xumx1
		# title = driver.find_element(By.CLASS_NAME,"_94v4wp")
		# # for (index,info) in enumerate(company_info):
		# #     print(str(index) + ": " + info.text)
		# job_title = title.text
		# print("Job Title:" + job_title)
		# job_info = driver.find_elements(By.CLASS_NAME,"_94v4wd")
		# company_name = job_info[0].text
		# print("Company Name:" + company_name)
		
		# #szurmz6
		# other_info = driver.find_elements(By.CLASS_NAME,"_1akoxc56")[1]
		# address_element = other_info.find_elements(By.CLASS_NAME,"_94v4wa")[0]
		# address = address_element.text
		
		# print("Address: " + address)
		
		# company_detail_url = ""
		# website_company = ""
		# all_a = driver.find_elements(By.TAG_NAME,"a")
		# for a in all_a:
		# 	if hasClass(a,"_126xumx1"):
		# 		print("Containt")
		# 		company_detail_url = driver.find_element(By.CLASS_NAME,"_126xumx1").get_attribute("href")  # Ha ok
		# 		print("Company URL: " + company_detail_url)
		# 	else:
		# 		continue
		# #2 company detail window 
		# if (company_detail_url != ""):
		# 	driver.execute_script("window.open('');")
		# 	company_detail_window = driver.window_handles[2]
		# 	driver.switch_to.window(company_detail_window)
		# 	driver.get(company_detail_url)
		# 	time.sleep(5)
		# 	 #_116mc3b7 #2
		# 	website_company = driver.find_elements(By.CLASS_NAME,"_116mc3b7")[1].get_attribute("href")

		# full_content = ""
		# full_content = '\n'.join([full_content, job_detail_url])
		# full_content = '\n'.join([full_content, "#####"])
		# sub_content = ""
		# for key_fail in keys_fail:
		# 	if key_fail in job_title:
		# 		continue
		# for job_fail in jobs_fail:
		# 	if job_fail == job_title:
		# 		continue
			
		# sub_content = '\n'.join([sub_content, job_title])
		# sub_content = '\n'.join([sub_content, job_detail_url])
		# full_content = '\n'.join([full_content, sub_content])
		# full_content = '\n'.join([full_content, "#####"])
		# company_id = check_company_existed(company_name)
		# if(company_id == ""):
		# 	print("\n\nStarting add new account:......\n\n")
		# 	add_new_account(access_token = access_token, name = company_name, phone = "", website = website_company, address = address)
		# else:
		# 	print("\n\nStarting editing account:......\n\n")
		# 	edit_account(access_token = access_token, account_id = company_id ,name = company_name, phone = "", website = website_company, address = address)
		# company_id = check_company_existed(company_name)       
		# lower_title = job_title.lower()
		# if("consultant" in lower_title or  "support" in lower_title or "admin" in lower_title or "manager" in lower_title or "data analyst" in lower_title):
		# 	print("Job not suitable")
		# else:
		# 	lead_id = check_lead_existed(company_name)
		# 	if (lead_id == ""):
		# 		print("\n\nStarting add new:......\n\n")
		# 		time.sleep(2)
		# 		add_new_lead(access_token=access_token,job_id = job_id, company_name=company_name, company_id = company_id,title=job_title,address=address,other_address=address,phone_company="",hirer_phone = "",hirer_email = "",website=website_company,content=full_content,assigned_user_id="", lead_status = "New")
		# 		if (website_company != ""):
		# 			driver.close()#2 close company detail
		# 			driver.switch_to.window(job_detail_window)
		# 		driver.close()#1 close job detail
		# 		driver.switch_to.window(root_window)
		# 	else:
		# 		print("\n\nStarting edit:......\n\n")
		# 		edit_new_lead(access_token=access_token,lead_id =lead_id,job_id=job_id,company_name=company_name,company_id = company_id,title= job_title,address=address,other_address=address,phone_company="",hirer_phone = "", hirer_email = "",website=website_company,content=full_content, lead_status = "New")
		# 		if (website_company != ""):
		# 			driver.close()#2 close company detail
		# 			driver.switch_to.window(job_detail_window)
		# 		driver.close()#1 close job detail
		# 		driver.switch_to.window(root_window)