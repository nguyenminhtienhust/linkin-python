import time
from bs4 import BeautifulSoup
import bs4
from tqdm import tqdm
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime
from datetime import date
import random
import string
import json
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import requests
from configparser import ConfigParser
import psycopg2
import validators
import phonenumbers
options = Options()
options.add_argument('--headless')
HEADLESS_OPTIONS = {'chrome_options': options}
import logging
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException

logger = logging.getLogger(__name__)

def validate_mobile_number(mobile_number):
	pattern = re.compile(r'^\+((?:9[679]|8[035789]|6[789]|5[90]|42|3[578]|2[1-689])|9[0-58]|8[1246]|6[0-6]|5[1-8]|4[013-9]|3[0-469]|2[70]|7|1)(?:\W*\d){0,13}\d$')
	return bool(pattern.match(mobile_number))

def connect():
	""" Connect to the PostgreSQL database server """
	conn = None
	try:
		# read connection parameters
		params = config(filename='database.ini', section='postgresql')

		# connect to the PostgreSQL server
		print('Connecting to the PostgreSQL database...')
		conn = psycopg2.connect(**params)
		
		# create a cursor
		cur = conn.cursor()
		
	# execute a statement
		print('PostgreSQL database version:')
		cur.execute('SELECT version()')

		# display the PostgreSQL database server version
		db_version = cur.fetchone()
		print(db_version)
	   
	# close the communication with the PostgreSQL
		cur.close()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	finally:
		if conn is not None:
			return conn

			
def config(filename='database.ini', section='postgresql'):
	# create a parser
	parser = ConfigParser()
	# read config file
	parser.read(filename)
	print("Filename:" + filename)
	# get section, default to postgresql
	db = {}
	if parser.has_section(section):
		params = parser.items(section)
		for param in params:
			db[param[0]] = param[1]
	else:
		raise Exception('Section {0} not found in the {1} file'.format(section, filename))

	return db
SELECT_CONTRACT_BUTTON_SELECTOR = "#main > div > div > div:nth-child(3) > form > div > ul > li:nth-child(1) > div > div.contract-list__item-buttons > button"


def login_crm():
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	jsondata = {}
	login_api = "https://crm.fitech.com.vn/Api/access_token"
	
	jsondata["grant_type"] = "client_credentials"
	jsondata["client_id"] = "ccfd00e1-307e-e56f-1e06-6592d6c95397"
	jsondata["client_secret"] = "apiuser@Fitech#vn"
	print(type(jsondata))
	data = requests.post(login_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object["access_token"]

def get_min_sale():
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/leads/find-minimum-sale"
	data = requests.get(check_api,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)
		return json_object["data"]
	
	
def check_company_existed(name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/accounts/check"
	jsondata = {"name":name}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)
		return json_object["data"]
		
def check_lead_existed(title, account_name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/leads/check"
	jsondata = {"title":title,
				"last_name" : account_name
	}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)
		return json_object["data"]
	
def add_new_account(access_token,name,phone,website,address):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	jsondata =  {
  "data": {
	"type": "Accounts",
	"attributes": {
	  "name": name,
	  "account_type": "Customer",
   	  "phone_office": phone,
	  "phone_alternate": phone,
	  "website": website,
	  "billing_address_country" : address
	}
  }
}
	time.sleep(2)
	data = requests.post(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)

def edit_account(access_token,account_id,name,phone,website,address):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	jsondata =  {
  "data": {
	"type": "Accounts",
 	"id": account_id,
	"attributes": {
	  "name": name,
	  "account_type": "Customer",
   	  "phone_office": phone,
	  "phone_alternate": phone,
	  "website": website,
	  "billing_address_country" : address
	}
  }
}
	time.sleep(2)
	data = requests.patch(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)
	 
	 
def add_new_lead(access_token,job_id,company_name,company_id,title,address,other_address,phone_company,hirer_phone,hirer_email,website,content,assigned_user_id, lead_status, job_phone, hirer_name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	jsondata =  {
  "data": {
	"type": "Leads",
	"attributes": {
	  "first_name": hirer_name,
	  "last_name": company_name,
	  "phone_work": phone_company,
	  "phone_mobile": hirer_phone,
	  "phone_other": job_phone,
	  "phone_home": hirer_phone,
	  "website": website,
	  "account_name": company_name,
	  "account_id" : company_id,
	  "status" : lead_status,
	  "primary_address_country": address,
	  "alt_address_street": other_address,
	  "description": content,
	  "title": title,
	  "email1": hirer_email,
	  "assigned_user_id" : assigned_user_id
	}
  }
}
	# Ha cmt
	#print(jsondata)
	time.sleep(2)
	data = requests.post(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print('fail')
		print(data.status_code)
		print(data.reason)
	else:
		print('done')
		json_object = data.json()
		print(json_object)
		
def edit_new_lead(access_token,lead_id,job_id,company_name,company_id,title,address,other_address,phone_company,hirer_phone,hirer_email,website,content, lead_status, job_phone, assigned_user_id, hirer_name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	print(hirer_email)
	jsondata =  {
  "data": {
	"type": "Leads",
	"id" : lead_id,
	"attributes": {
	  "first_name": hirer_name,
	  "last_name": company_name,
	  "phone_work": phone_company,
	  "phone_mobile": hirer_phone,
	  "phone_other": job_phone,
	  "phone_home": hirer_phone,
	  "website": website,
	  "account_name": company_name,
	  "account_id" : company_id,
	  "status" : lead_status,
	  "primary_address_country": address,
	  "alt_address_street": other_address,
	  "title": title,
	  "description": content,
	  "email1" : hirer_email,
	  "assigned_user_id": assigned_user_id
	}
  }
}
	# Ha cmt
	#print(jsondata)
	time.sleep(2)
	data = requests.patch(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print('fail')
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)

def check_email_existed(name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/emails/check"
	jsondata = {"name":name}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)
		return json_object["data"]  

def check_email_lead(lead_id):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/email_lead/check"
	jsondata = {"name":lead_id}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)
		return json_object["data"] 
def add_email_lead(access_token, email_id, lead_id, bean_type):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	jsondata =  {
  "data": {
	"type": "email_addr_bean_rel",
	"attributes": {
		 "email_address_id": email_id,
		 "bean_id": lead_id,
		 "bean_module" : bean_type
	}
	}
	}
	time.sleep(2)
	data = requests.post(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)
		
def edit_email_lead(access_token,email_lead_id,email_id):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	jsondata =  {
  "data": {
	"type": "email_addr_bean_rel",
	"id": email_lead_id,
	"attributes": {
		 "email_address_id": email_id
	}
	}
	}
	time.sleep(2)
	data = requests.patch(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)

def check_contact(name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/contact/check"
	jsondata = {"name":name}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print("\ncheck_contact" + data.reason)
	else:
		json_object = data.json()
		return json_object

def add_contact(access_token,title, name, email, phone, des, link, account_name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	jsondata =  {
  "data": {
	"type": "Contacts",
	"attributes": {
	  "last_name": name,
	  "title": title,
	  "description" : des,
	  "email" : email,
	  "phone_work" : phone,
	  "created_by_link" : link,
	  "account_name" : account_name,
	  "deleted" : True,
	  "created_by": "1"
	}
  }
}
	time.sleep(2)
	data = requests.post(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print('fail')
		print(data.status_code)
		print(data.reason)
	else:
		print('done')
		json_object = data.json()
		print(json_object)

def edit_contact(access_token, id , title, name, email, phone, des, link, account_name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	jsondata =  {
  "data": {
	"type": "contacts",
	"id" : id,
	"attributes": {
	  "last_name": name,
	  "title": title,
	  "description" : des,
	  "email" : email,
	  "phone_work" : phone,
	  "created_by_link" : link,
	  "account_name" : account_name
	}
  }
}
	# Ha cmt
	#print(jsondata)
	time.sleep(2)
	data = requests.post(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print('fail')
		print(data.status_code)
		print(data.reason)
	else:
		print('done')
		json_object = data.json()
		print(json_object)


def get_contact_assigned_user(name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/lead/getassigneduserbycontact"
	jsondata = {"name":name}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print("\ncontact_assigned" + data.reason)
	else:
		json_object = data.json()
		print(json_object)
		return json_object["data"]

def get_account_assigned_user(name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/lead/getassigneduserbyaccount"
	print("\n search assigned by company" + name)
	jsondata = {"name":name}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print("\naccount_assigned" + data.reason)
	else:
		json_object = data.json()
		print(json_object)
		return json_object["data"]


def test(driver,job_id,access_token,address):
	root_window = driver.window_handles[0]
	#1 job detail window 
	driver.execute_script("window.open('');")
	job_detail_window = driver.window_handles[1]
	driver.switch_to.window(job_detail_window)
	time.sleep(2)

	job_detail_url = 'https://www.linkedin.com/jobs/view/' + job_id
	print(job_detail_url)
	driver.get(job_detail_url)
	time.sleep(10)
	company_url = ""
	# try :
		# infos_element = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__primary-description-without-tagline")
		# company_element = infos_element.find_element(By.TAG_NAME,"a")
	
		# if not company_element:
		# 	print("company_url is empty")
		# else:
		# 	company_url = infos_element.find_element(By.CSS_SELECTOR,"a").get_attribute("href")
		# 	company_name = company_element.text
		# driver.execute_script("window.open('');")
		# company_window = driver.window_handles[2]
		# driver.switch_to.window(company_window)
		# time.sleep(2)

	
		# company_about_url = company_url.replace("/life", "/about")
		# driver.get(company_about_url)
		# driver.implicitly_wait(10)
		# account_actions = driver.find_element(By.CLASS_NAME,"org-top-card-primary-actions__inner")
		# message_button = account_actions.find_element(By.CLASS_NAME,"artdeco-button--secondary")
		# text_message_button = hirer_detail_button.find_element(By.CLASS_NAME,"artdeco-button__text").text
		# if(text_message_button.lower() == "message"):
		# 	message_button.click()
		# 	driver.implicitly_wait(5)
		# 	select_actions = driver.find_element(By.ID,"org-message-page-modal-conversation-topic")
		# 	select_list = Select(select_actions)
		# 	select_list.select_by_visible_text('Careers')
		# 	mess_text_area = driver.find_element(By.ID,"org-message-page-modal-message")
		# 	mess_text_area.clear()
		# 	mess_text_area.send_keys("Heard you're on the lookout for tech talent, and Fitech's team is all in! Our crew excels in various program languages. They work remotely, delivering top-notch results managed seamlessly from our Vietnam office. Looking forward to the possibility of working together!")
		# 	send_button = driver.find_element(By.CLASS_NAME,"artdeco-button--primary")
		# 	if(send_button.is_enabled()):
		# 		send_button.click()   

		# current_job_title = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__job-title").text    
		# infos_element = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__primary-description-without-tagline")
		# address_element = infos_element.find_elements(By.TAG_NAME,"span")[0]
		# other_address = address_element.text
		# company_element = infos_element.find_element(By.TAG_NAME,"a")
		# company_name = ""
		# if not company_element:
		# 	print("company_url is empty")
		# else:
		# 	company_url = infos_element.find_element(By.CSS_SELECTOR,"a").get_attribute("href")
		# 	company_name = company_element.text
		# job_detail = driver.find_element(By.CLASS_NAME,"jobs-description-content__text").text
		# print(job_detail)
		# job_emails = re.findall(r"[a-z0-9A-Z\.\-+_]+@[a-z0-9A-Z\.\-+_]+\.[a-zA-Z]+", job_detail)
		# job_detail = "it is +84914979558"
		# job_phones = re.findall(r'\+?[1-9][0-9 .\-\(\)]{8,}[0-9]', job_detail)
		# print(job_phones)
		# hirer_name = driver.find_element(By.CLASS_NAME,"jobs-poster__name ").text
		# print(hirer_name)
		# print("\n get assigned by contact")
		# assigned_user_id = get_contact_assigned_user(hirer_name)
		# print(assigned_user_id)
		# print("\n get assigned by company_name")
		# assigned_user_id_account = get_account_assigned_user(company_name)	
		# print(assigned_user_id)
	# except NoSuchElementException:
	# 	print("not found job title")
	# 	pass

	hirer_name = ""
	hirer_profile = ""
	hirer_website = ""
	hirer_phone = ""
	hirer_address = ""
	hirer_email = ""
	hirer_other = ""	
	request_note_str = ""
	#Get Hirer Link
	try:
		hirer_name = driver.find_element(By.CLASS_NAME,"jobs-poster__name ").text
		print(hirer_name)
		contact_info = {"data": "", "des" : ""}
		if(hirer_name != ""):
			contact_info = check_contact(hirer_name)			
			if(contact_info["data"] == ""):
				try:
					print("Not exist")
					entry_point = driver.find_element(By.CLASS_NAME,"entry-point")
					message_button = entry_point.find_element(By.TAG_NAME,"button")
					message_button.click()
					time.sleep(2)

					message_box = driver.find_element(By.CLASS_NAME,"artdeco-text-input--container")
					message_title_input = message_box.find_element(By.TAG_NAME,"input")
					message_title_input.send_keys("Elevate Your Team with Fitech's Offshore Talent")
					time.sleep(2)

					message_content_input = driver.find_element(By.CLASS_NAME,"msg-form__contenteditable")
					message_content_input.clear()
					message_content_input.send_keys(" Hey ," + hirer_name + ", \n Hope your day's fantastic! Heard you're on the lookout for tech talent, and Fitech's team is all in! \n Our crew excels in various program languages. They work remotely, delivering top-notch results managed seamlessly from our Vietnam office. \n Let's make it happen: \n Remote excellence \n Tailored solutions \n Cost-effective partnership \n Interested? Let's chat! Schedule a quick meeting or connect via email or WhatsApp \n Looking forward to the possibility of working together! \n Best, \n Fitech - Minh Tien ")
					time.sleep(2)  
		
					send_button = driver.find_element(By.CLASS_NAME,"msg-form__send-button")
					if(send_button.is_enabled()):
						isMessaged = "Yes"
						request_note_str = "Message sent"
					send_button.submit()   
				except NoSuchElementException:
					print("\n No message box")       
					pass

			# get contact info
				hirer = driver.find_element(By.CLASS_NAME,"hirer-card__hirer-information")
				hirer_link = hirer.find_element(By.TAG_NAME,"a").get_attribute("href")
				driver.get(hirer_link)
				time.sleep(5)
				hirer_detail = driver.find_element(By.CLASS_NAME,"pv-top-card-v2-ctas")
				hirer_detail_button = hirer_detail.find_element(By.CLASS_NAME,"pvs-profile-actions__action")
				text_hirer_button = hirer_detail_button.find_element(By.CLASS_NAME,"artdeco-button__text").text
				if (text_hirer_button == "Connect"):
					hirer_detail_button.click()	
					driver.implicitly_wait(10)		
					hirer_connect_modal = driver.find_element(By.CLASS_NAME,"send-invite")
					hirer_connect_request_buttons = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-modal__actionbar")
					if(hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")):
						hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")
						hirer_connect_request_button.click()
						driver.implicitly_wait(10)
						connect_mess_modal = driver.find_element(By.CLASS_NAME,"send-invite")
						connect_mess_area = connect_mess_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
						connect_mess_area.send_keys("Heard you're on the lookout for tech talent, and Fitech's team is all in! Our crew excels in various program languages. They work remotely, delivering top-notch results managed seamlessly from our Vietnam office. Looking forward to the possibility of working together!")
						time.sleep(2)
						connect_button = connect_mess_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
						connect_button.click() 
						time.sleep(2)				
					else:
						hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--primary")
						hirer_connect_request_button.click()
					print("connect request sent")
					request_note_str = request_note_str + "\nConnect request sent"		
				print("Get contact")	
				contact_info_link = driver.find_element(By.ID,"top-card-text-details-contact-info").get_attribute("href")
				driver.get(contact_info_link)
				time.sleep(5)
				contact_info_list = driver.find_elements(By.CLASS_NAME,"pv-contact-info__contact-type")
				for contact_info_detail in contact_info_list:
					contact_info_header = contact_info_detail.find_element(By.CLASS_NAME,"pv-contact-info__header")
					contact_info_content = contact_info_detail.find_element(By.CLASS_NAME,"pv-contact-info__ci-container")
					if "email" in contact_info_header.text.lower():
						hirer_email = contact_info_content.text
					elif "profile" in contact_info_header.text.lower():
						hirer_profile = contact_info_content.text
					elif "website" in contact_info_header.text.lower():
				   		hirer_website = contact_info_content.text
					elif "address" in contact_info_header.text.lower():
				   		hirer_address = contact_info_content.text
					elif "phone" in contact_info_header.text.lower():
				   		hirer_phone = contact_info_content.text
					else:
						hirer_other = contact_info_content.text
				add_contact(access_token = access_token,title = "" , name = hirer_name, email = hirer_email, phone = hirer_phone, des = request_note_str, link = contact_info_link, account_name= hirer_name)
			else:
				driver.get(job_detail_url)
				print(contact_info["des"])
				if(contact_info["des"] is None or "message" not in contact_info["des"].lower()):
					try:
						entry_point = driver.find_element(By.CLASS_NAME,"entry-point")
						message_button = entry_point.find_element(By.TAG_NAME,"button")
						message_button.click()
						time.sleep(2)

						message_box = driver.find_element(By.CLASS_NAME,"artdeco-text-input--container")
						message_title_input = message_box.find_element(By.TAG_NAME,"input")
						message_title_input.send_keys("Elevate Your Team with Fitech's Offshore Talent")
						time.sleep(2)

						message_content_input = driver.find_element(By.CLASS_NAME,"msg-form__contenteditable")
						message_content_input.clear()
						message_content_input.send_keys(" Hey ," + hirer_name + ", \n Hope your day's fantastic! Heard you're on the lookout for tech talent, and Fitech's team is all in! \n Our crew excels in various program languages. They work remotely, delivering top-notch results managed seamlessly from our Vietnam office. \n Let's make it happen: \n Remote excellence \n Tailored solutions \n Cost-effective partnership \n Interested? Let's chat! Schedule a quick meeting or connect via email or WhatsApp \n Looking forward to the possibility of working together! \n Best, \n Fitech - Minh Tien ")
						time.sleep(2)  
		
						send_button = driver.find_element(By.CLASS_NAME,"msg-form__send-button")
						if(send_button.is_enabled()):
							isMessaged = "Yes"
							request_note_str = "Message sent"
						send_button.submit() 
					except NoSuchElementException:
						print("\n No message box")       
						pass
				if(contact_info["des"] is None or "connect" not in contact_info["des"].lower()):
					try:
						print("\nTry to connect")
						hirer = driver.find_element(By.CLASS_NAME,"hirer-card__hirer-information")
						hirer_link = hirer.find_element(By.TAG_NAME,"a").get_attribute("href")
						driver.get(hirer_link)
						time.sleep(5)
						hirer_detail = driver.find_element(By.CLASS_NAME,"pv-top-card-v2-ctas")
						hirer_detail_button = hirer_detail.find_element(By.CLASS_NAME,"pvs-profile-actions__action")
						text_hirer_button = hirer_detail_button.find_element(By.CLASS_NAME,"artdeco-button__text").text
						if (text_hirer_button == "Connect"):
							hirer_detail_button.click()	
							driver.implicitly_wait(10)		
							hirer_connect_modal = driver.find_element(By.CLASS_NAME,"send-invite")
							hirer_connect_request_buttons = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-modal__actionbar")
							if(hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")):
								hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")
								hirer_connect_request_button.click()
								driver.implicitly_wait(10)
								connect_mess_modal = driver.find_element(By.CLASS_NAME,"send-invite")
								connect_mess_area = connect_mess_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
								connect_mess_area.send_keys("Heard you're on the lookout for tech talent, and Fitech's team is all in! Our crew excels in various program languages. They work remotely, delivering top-notch results managed seamlessly from our Vietnam office. Looking forward to the possibility of working together!")
								time.sleep(2)
								connect_button = connect_mess_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
								connect_button.click() 
								time.sleep(2)				
							else:
								hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--primary")
								hirer_connect_request_button.click()
							print("connect request sent")
							request_note_str = request_note_str + "\nConnect request sent"
					except NoSuchElementException:
						print("\n No message box")       
						pass
				hirer = driver.find_element(By.CLASS_NAME,"hirer-card__hirer-information")
				hirer_link = hirer.find_element(By.TAG_NAME,"a").get_attribute("href")
				driver.get(hirer_link)
				time.sleep(5)
				contact_info_link = driver.find_element(By.ID,"top-card-text-details-contact-info").get_attribute("href")
				driver.get(contact_info_link)
				time.sleep(5)
				contact_info_list = driver.find_elements(By.CLASS_NAME,"pv-contact-info__contact-type")
				for contact_info_detail in contact_info_list:
					contact_info_header = contact_info_detail.find_element(By.CLASS_NAME,"pv-contact-info__header")
					contact_info_content = contact_info_detail.find_element(By.CLASS_NAME,"pv-contact-info__ci-container")
					if "email" in contact_info_header.text.lower():
						hirer_email = contact_info_content.text
					elif "profile" in contact_info_header.text.lower():
						hirer_profile = contact_info_content.text
					elif "website" in contact_info_header.text.lower():
				   		hirer_website = contact_info_content.text
					elif "address" in contact_info_header.text.lower():
				   		hirer_address = contact_info_content.text
					elif "phone" in contact_info_header.text.lower():
				   		hirer_phone = contact_info_content.text
					else:
						hirer_other = contact_info_content.text

	except NoSuchElementException:
		print("\nCan't found")       
		pass

def get_job_detail(driver,job_id,access_token,address, country):	 
	root_window = driver.window_handles[0]
	
	#1 job detail window 
	driver.execute_script("window.open('');")
	job_detail_window = driver.window_handles[1]
	driver.switch_to.window(job_detail_window)
	time.sleep(2)

	job_detail_url = 'https://www.linkedin.com/jobs/view/' + job_id
	print(job_detail_url)
	driver.get(job_detail_url)
	time.sleep(10)
	company_url = ""
	company_name = ""
	job_emails = []
	job_phones = []
	job_phone = ""
	try :
		current_job_title = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__job-title").text    
		infos_element = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__primary-description-without-tagline")
		address_element = infos_element.find_elements(By.TAG_NAME,"span")[0]
		other_address = address_element.text
		company_element = infos_element.find_element(By.TAG_NAME,"a")
	
		if not company_element:
			print("company_url is empty")
		else:
			company_url = infos_element.find_element(By.CSS_SELECTOR,"a").get_attribute("href")
			company_name = company_element.text
		job_detail = driver.find_element(By.CLASS_NAME,"jobs-description-content__text").text
		job_emails = re.findall(r"[a-z0-9A-Z\.\-+_]+@[a-z0-9A-Z\.\-+_]+\.[a-zA-Z]+", job_detail)
		if(country == "Australia"):
			job_phones =re.findall(r'^(?=.*)((?:\+61) ?(?:\((?=.*\)))?([2-47-8])\)?|(?:\((?=.*\)))?([0-1][2-47-8])\)?) ?-?(?=.*)((\d{1} ?-?\d{3}$)|(00 ?-?\d{4} ?-?\d{4}$)|( ?-?\d{4} ?-?\d{4}$)|(\d{2} ?-?\d{3} ?-?\d{3}$))', job_detail) 
		elif (country == "Malaysia"):
			job_phones =re.findall(r'^(?:(?:\+60|0060)(?:[1]|[0]?[1])[ -]?|[0])[0-9]{2}[ -]?[0-9]{3,4}[ -]?[0-9]{3,4}$', job_detail) 
		elif (country == "Thailand"):
			job_phones = re.findall(r'^(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}$', job_detail)
		else:
			print("Not interested country")
	except NoSuchElementException:
		print("not found job title")
		pass

	#####Message entry-point
	contact_info = {"data": "", "des" : ""}
	hirer_name = ""
	hirer_title = ""
	hirer_link = ""
	hirer_profile = ""
	hirer_website = ""
	hirer_phone = ""
	hirer_address = ""
	hirer_email = ""
	hirer_other = ""	
	contact_id = ""
	request_note_str = ""
	#Get Hirer Link
	try:
		hirer_name = driver.find_element(By.CLASS_NAME,"jobs-poster__name ").text
		hirer_title = driver.find_element(By.CLASS_NAME,"hirer-card__hirer-job-title").text
		if(hirer_name != ""):
			contact_info = check_contact(hirer_name)			
			if(contact_info["data"] == ""):
				try:
					print("Not exist")
					entry_point = driver.find_element(By.CLASS_NAME,"entry-point")
					message_button = entry_point.find_element(By.TAG_NAME,"button")
					message_button.click()
					time.sleep(2)

					message_box = driver.find_element(By.CLASS_NAME,"artdeco-text-input--container")
					message_title_input = message_box.find_element(By.TAG_NAME,"input")
					message_title_input.send_keys("Elevate Your Team with Fitech's Offshore Talent")
					time.sleep(2)

					message_content_input = driver.find_element(By.CLASS_NAME,"msg-form__contenteditable")
					message_content_input.clear()
					message_content_input.send_keys(" Hey ," + hirer_name + ", \n Hope your day's fantastic! Heard you're on the lookout for tech talent, and Fitech's team is all in! \n Our crew excels in various program languages. They work remotely, delivering top-notch results managed seamlessly from our Vietnam office. \n Let's make it happen: \n Remote excellence \n Tailored solutions \n Cost-effective partnership \n Interested? Let's chat! Schedule a quick meeting or connect via email or WhatsApp \n Looking forward to the possibility of working together! \n Best, \n Fitech - Minh Tien ")
					time.sleep(2)  
		
					send_button = driver.find_element(By.CLASS_NAME,"msg-form__send-button")
					if(send_button.is_enabled()):
						request_note_str = "Message sent"
					send_button.submit()   
				except NoSuchElementException:
					print("\n No message box")       
					pass

			# get contact info
				hirer = driver.find_element(By.CLASS_NAME,"hirer-card__hirer-information")
				hirer_link = hirer.find_element(By.TAG_NAME,"a").get_attribute("href")
				driver.get(hirer_link)
				time.sleep(5)
				hirer_detail = driver.find_element(By.CLASS_NAME,"pv-top-card-v2-ctas")
				hirer_detail_button = hirer_detail.find_element(By.CLASS_NAME,"pvs-profile-actions__action")
				text_hirer_button = hirer_detail_button.find_element(By.CLASS_NAME,"artdeco-button__text").text
				if (text_hirer_button == "Connect"):
					hirer_detail_button.click()	
					driver.implicitly_wait(10)		
					hirer_connect_modal = driver.find_element(By.CLASS_NAME,"send-invite")
					hirer_connect_request_buttons = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-modal__actionbar")
					if(hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")):
						hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")
						hirer_connect_request_button.click()
						driver.implicitly_wait(10)
						connect_mess_modal = driver.find_element(By.CLASS_NAME,"send-invite")
						connect_mess_area = connect_mess_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
						connect_mess_area.send_keys("Heard you're on the lookout for tech talent, and Fitech's team is all in! Our crew excels in various program languages. They work remotely, delivering top-notch results managed seamlessly from our Vietnam office. Looking forward to the possibility of working together!")
						time.sleep(2)
						connect_button = connect_mess_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
						connect_button.click() 
						time.sleep(2)				
					else:
						hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--primary")
						hirer_connect_request_button.click()
					print("connect request sent")
					request_note_str = request_note_str + "\nConnect request sent"		
				print("Get contact")	
				contact_info_link = driver.find_element(By.ID,"top-card-text-details-contact-info").get_attribute("href")
				driver.get(contact_info_link)
				time.sleep(5)
				contact_info_list = driver.find_elements(By.CLASS_NAME,"pv-contact-info__contact-type")
				for contact_info_detail in contact_info_list:
					contact_info_header = contact_info_detail.find_element(By.CLASS_NAME,"pv-contact-info__header")
					contact_info_content = contact_info_detail.find_element(By.CLASS_NAME,"pv-contact-info__ci-container")
					if "email" in contact_info_header.text.lower():
						hirer_email = contact_info_content.text
					elif "profile" in contact_info_header.text.lower():
						hirer_profile = contact_info_content.text
					elif "website" in contact_info_header.text.lower():
				   		hirer_website = contact_info_content.text
					elif "address" in contact_info_header.text.lower():
				   		hirer_address = contact_info_content.text
					elif "phone" in contact_info_header.text.lower():
				   		hirer_phone = contact_info_content.text
					else:
						hirer_other = contact_info_content.text
				add_contact(access_token = access_token,title = hirer_title , name = hirer_name, email = hirer_email, phone = hirer_phone, des = request_note_str, link = contact_info_link, account_name= company_name)
				contact_info = check_contact(hirer_name)
				contact_id = contact_info["data"]
			else:
				contact_id = contact_info["data"]
				print(contact_info["des"])
				if("message" not in contact_info["des"].lower()):
					entry_point = driver.find_element(By.CLASS_NAME,"entry-point")
					message_button = entry_point.find_element(By.TAG_NAME,"button")
					message_button.click()
					time.sleep(2)

					message_box = driver.find_element(By.CLASS_NAME,"artdeco-text-input--container")
					message_title_input = message_box.find_element(By.TAG_NAME,"input")
					message_title_input.send_keys("Elevate Your Team with Fitech's Offshore Talent")
					time.sleep(2)

					message_content_input = driver.find_element(By.CLASS_NAME,"msg-form__contenteditable")
					message_content_input.clear()
					message_content_input.send_keys(" Hey ," + hirer_name + ", \n Hope your day's fantastic! Heard you're on the lookout for tech talent, and Fitech's team is all in! \n Our crew excels in various program languages. They work remotely, delivering top-notch results managed seamlessly from our Vietnam office. \n Let's make it happen: \n Remote excellence \n Tailored solutions \n Cost-effective partnership \n Interested? Let's chat! Schedule a quick meeting or connect via email or WhatsApp \n Looking forward to the possibility of working together! \n Best, \n Fitech - Minh Tien ")
					time.sleep(2)  
		
					send_button = driver.find_element(By.CLASS_NAME,"msg-form__send-button")
					if(send_button.is_enabled()):
						isMessaged = "Yes"
						request_note_str = contact_info["des"] + "\nMessage sent"
					send_button.submit() 
				if("connect" not in contact_info["des"].lower()):
					hirer = driver.find_element(By.CLASS_NAME,"hirer-card__hirer-information")
					hirer_link = hirer.find_element(By.TAG_NAME,"a").get_attribute("href")
					driver.get(hirer_link)
					time.sleep(5)
					hirer_detail = driver.find_element(By.CLASS_NAME,"pv-top-card-v2-ctas")
					hirer_detail_button = hirer_detail.find_element(By.CLASS_NAME,"pvs-profile-actions__action")
					text_hirer_button = hirer_detail_button.find_element(By.CLASS_NAME,"artdeco-button__text").text
					if (text_hirer_button == "Connect"):
						hirer_detail_button.click()	
						driver.implicitly_wait(3)		
						hirer_connect_modal = driver.find_element(By.CLASS_NAME,"send-invite")
						hirer_connect_request_buttons = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-modal__actionbar")
						if(hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")):
							hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")
							hirer_connect_request_button.click()
							driver.implicitly_wait(3)
							connect_mess_modal = driver.find_element(By.CLASS_NAME,"send-invite")
							connect_mess_area = connect_mess_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
							connect_mess_area.send_keys("Heard you're on the lookout for tech talent, and Fitech's team is all in! Our crew excels in various program languages. They work remotely, delivering top-notch results managed seamlessly from our Vietnam office. Looking forward to the possibility of working together!")
							time.sleep(2)
							connect_button = connect_mess_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
							connect_button.click() 
							time.sleep(2)				
						else:
							hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--primary")
							hirer_connect_request_button.click()
						print("connect request sent")
						request_note_str = contact_info["des"] + "\nConnect request sent"
				hirer = driver.find_element(By.CLASS_NAME,"hirer-card__hirer-information")
				hirer_link = hirer.find_element(By.TAG_NAME,"a").get_attribute("href")
				driver.get(hirer_link)
				time.sleep(3)
				contact_info_link = driver.find_element(By.ID,"top-card-text-details-contact-info").get_attribute("href")
				driver.get(contact_info_link)
				time.sleep(3)
				contact_info_list = driver.find_elements(By.CLASS_NAME,"pv-contact-info__contact-type")
				for contact_info_detail in contact_info_list:
					contact_info_header = contact_info_detail.find_element(By.CLASS_NAME,"pv-contact-info__header")
					contact_info_content = contact_info_detail.find_element(By.CLASS_NAME,"pv-contact-info__ci-container")
					if "email" in contact_info_header.text.lower():
						hirer_email = contact_info_content.text
					elif "profile" in contact_info_header.text.lower():
						hirer_profile = contact_info_content.text
					elif "website" in contact_info_header.text.lower():
				   		hirer_website = contact_info_content.text
					elif "address" in contact_info_header.text.lower():
				   		hirer_address = contact_info_content.text
					elif "phone" in contact_info_header.text.lower():
				   		hirer_phone = contact_info_content.text
					else:
						hirer_other = contact_info_content.text
				edit_contact(access_token = access_token, contact_id = contact_info["data"] , title = hirer_title, name = hirer_name, email = hirer_email, phone= hirer_phone, des = request_note_str, link = contact_info_link, account_name = company_name)

	except NoSuchElementException:
		print("\nCan't found")       
		pass

	if(country == "Australia"):
		if (hirer_phone.startswith('0') or hirer_phone.startswith("(0")):			
			hirer_phone = hirer_phone.replace('0','+61',1)
		else:
			if(hirer_phone.startswith('2') or hirer_phone.startswith('3') or hirer_phone.startswith('7') or hirer_phone.startswith('8') or hirer_phone.startswith('4') or hirer_phone.startswith('5')):
				hirer_phone = "+61" + hirer_phone
	elif (country == "Malaysia"):
		if (hirer_phone.startswith('0') or hirer_phone.startswith("(0")):			
			hirer_phone = hirer_phone.replace('0','+60',1)
		if(hirer_phone.startswith(("1","2","3","4","5","6","7","8","9")) ):
			hirer_phone = "+60" + hirer_phone
	elif (country == "Thailand"): 
		if (hirer_phone.startswith('0') or hirer_phone.startswith("(0")):			
			hirer_phone = hirer_phone.replace('0','+66',1)
		if(hirer_phone.startswith(("1","2","3","4","5","6","7","8","9")) ):
			hirer_phone = "+66" + hirer_phone
	else:
		print("Not interested country")
	hirer_phone.replace("-","")
	email_info = ""
	full_content = ""
	if(hirer_email != ""):
		email_info = hirer_email
		full_content = '\n Email được lấy từ trang cá nhân nhà tuyển dụng.'
	else:
		if (job_emails and len(job_emails) > 0):
			email_info = job_emails[0]
			full_content = '\n Email được lấy từ job description.'
	maylaysia_phone_valid = "123456789"
	if (job_phones and len(job_phones) > 0):
		job_phone = job_phones[0]
		if(country == "Australia"):
			if (job_phone.startswith('0') or job_phone.startswith("(0")):			
				job_phone = job_phone.replace('0','+61',1)
			else:
				if(job_phone.startswith('2') or job_phone.startswith('3') or job_phone.startswith('7') or job_phone.startswith('8') or job_phone.startswith('4') or job_phone.startswith('5')):
					job_phone = "+61" + job_phone
		elif (country == "Malaysia"):
			if (job_phone.startswith('0') or job_phone.startswith("(0")):			
				job_phone = job_phone.replace('0','+60',1)
			if(job_phone.startswith(("1","2","3","4","5","6","7","8","9")) ):
				job_phone = "+60" + job_phone
		elif (country == "Thailand"): 
			if (job_phone.startswith('0') or job_phone.startswith("(0")):			
				job_phone = job_phone.replace('0','+66',1)
			if(job_phone.startswith(("1","2","3","4","5","6","7","8","9")) ):
				job_phone = "+66" + job_phone
		else:
			print("Not interested country")
		job_phone.replace("-","")
	#2 company screen
	try:
		driver.execute_script("window.open('');")
		company_window = driver.window_handles[2]
		driver.switch_to.window(company_window)
		time.sleep(2)

	
		company_about_url = company_url.replace("/life", "/about")
		driver.get(company_about_url)
		driver.implicitly_wait(10)	
	
		full_content = '\n Link giới thiệu:'.join([full_content, company_about_url])

		wrap_section = driver.find_element(By.CLASS_NAME,"org-grid__content-height-enforcer")
		dds = wrap_section.find_elements(By.TAG_NAME,"dd")
	
		index = 0
		website_company = ""
		phone_company = ""
	
		for dd in dds:
	# Ha cmt
		#print(dd.text)
			if(("http" in dd.text) or (".com" in dd.text) or ("www" in dd.text)):
				website_company = dd.text
			if("Phone number is" in dd.text):
				phone_company = dd.text.split("Phone number is")[0]
			index = index + 1
		if(country == "Australia"):
			if (phone_company.startswith('0') or phone_company.startswith("(0")):			
				phone_company = phone_company.replace('0','+61',1)
			else:
				if(phone_company.startswith('2') or phone_company.startswith('3') or phone_company.startswith('7') or phone_company.startswith('8') or phone_company.startswith('4') or phone_company.startswith('5')):
					phone_company = "+61" + phone_company
		elif (country == "Malaysia"): 
			if (phone_company.startswith('0') or phone_company.startswith("(0")):			
				phone_company = phone_company.replace('0','+60',1)
			if(phone_company.startswith(("1","2","3","4","5","6","7","8","9")) ):
				phone_company = "+60" + phone_company
		elif (country == "Thailand"): 
			if (phone_company.startswith('0') or phone_company.startswith("(0")):			
				phone_company = phone_company.replace('0','+66',1)
			if(phone_company.startswith(("1","2","3","4","5","6","7","8","9")) ):
				phone_company = "+66" + phone_company
		else:
			print("Not interested country")
		phone_company.replace("-","")
		full_content = '\n Link tuyển dụng: '.join([full_content, job_detail_url])
		if("message" in request_note_str.lower() or "message" in contact_info["des"].lower()):
			full_content = '\n Đã gửi tin nhắn đến: '.join([full_content, hirer_link])
		if("connect" in request_note_str.lower() or "connect" in contact_info["des"].lower()):
			full_content = '\n Đã gửi connect request đến: '.join([full_content, hirer_link])
		if(hirer_link != ""):
			full_content = '\n Trang cá nhân nhà tuyển dụng: '.join([full_content, hirer_link])
	#Get List Job:
	#https://www.linkedin.com/company/mindvalley/jobs/            
	#3 Jobs Company Screen
	#driver.execute_script("window.open('');")
	#jobs_window = driver.window_handles[3]
	#driver.switch_to.window(jobs_window)
	#time.sleep(2)

	#jobs_list_company_url = company_url.replace("/life", "/jobs")
	#driver.get(jobs_list_company_url)

	#full_content = '\n Link danh sách công việc: '.join([full_content, jobs_list_company_url])
	#time.sleep(10)
	
	#button_show_all_jobs = driver.find_element(By.CLASS_NAME,"org-jobs-recently-posted-jobs-module__show-all-jobs-btn")
	#link_all_jobs = button_show_all_jobs.find_element(By.TAG_NAME,"a").get_attribute("href")
	#print(link_all_jobs) 
	
	#4 Clone All Jobs
	#driver.execute_script("window.open('');")
	#list_jobs_detail_window = driver.window_handles[3]
	#driver.switch_to.window(list_jobs_detail_window)
		time.sleep(2)
	
	#driver.get(link_all_jobs)
	#time.sleep(10)
		job_containers = driver.find_elements(By.CLASS_NAME,"jobs-search-results__list-item")
		count = len(job_containers)
		should_change_status = False
		last_time = datetime(2023, 1 , 1)
		jobs_fail = ["IT System Engineer","Market Research Intern","IT Network Engineer","Graduate Trainee","Administrative Assistant","Customer Support Engineer","Customer Support Consultant","Research Internship","Search Quality Rater","Digital Marketing Analyst","Project Administrator","Ford Internship","Management Trainee","Information Security Analyst","Assistant Engineering Executive","R&D Specialist","Veterinary Information Systems Officer","Junior Engineer","Research Assistant","Marketing Assistant","Administrative Assistant","Database Administration Officer","Administrator","Assistant project manager","Internship","Research Associate","Test Administrator","Document Control Administrator","Administrative Assistant","Practical Trainee","System Administrator","Design & Estimation Engineer","Senior Research Scientist","Project Coordinator"]
		keys_fail = ["Project Administrator","Project Manager","Research","Intern","Network","Graduate","Administrative","Assistant","Support","Marketing","Internship","Security","R&D","Junior","Administrative","Officer","Research"]
		lead_status = "New"
		if(hirer_profile == "" and email_info == "" and hirer_website == "" and phone_company == "" and hirer_name == "" and hirer_phone == "" and job_phone == ""):
			lead_status = "Recycled"
		company_id = check_company_existed(company_name)
		website = website_company
		if(hirer_website != ""):
			website = hirer_website
		# bỏ thêm mới account
		#if(company_id == ""):
			#print("\n\nStarting add new account:......\n\n")
			#add_new_account(access_token = access_token, name = company_name, phone = phone_company, website = website_company, address = address)
		#else:
			#print("\n\nStarting editing account:......\n\n")
			#edit_account(access_token = access_token, account_id = company_id ,name = company_name, phone = phone_company, website = website_company, address = address)
		#company_id = check_company_existed(company_name)
		
		lower_title = current_job_title.lower()
		if("consultant" in lower_title or  "support" in lower_title or "admin" in lower_title or "manager" in lower_title or "data analyst" in lower_title):
			print("Job not suitable")
		else:
			assigned_user_id = ""
			if(hirer_name != ""):
				assigned_user_id = get_contact_assigned_user(hirer_name)
			else:
				assigned_user_id = get_account_assigned_user(company_name)
			if(lead_status == "Recycled"):
				assigned_user_id = ""
			lead_id = check_lead_existed(current_job_title, company_name)
			if (lead_id == ""):
				print("\n\nStarting add new:......\n\n")
				time.sleep(2)
				add_new_lead(access_token=access_token,job_id = job_id, company_name=company_name, company_id = company_id,title=current_job_title,address=address,other_address=other_address,phone_company=phone_company,hirer_phone = hirer_phone,hirer_email = email_info,website=website,content=full_content,assigned_user_id=assigned_user_id, lead_status = lead_status, job_phone = job_phone, hirer_name = hirer_name, refer= "", contact_id = contact_id)
			else:
				print("\n\nStarting edit:......\n\n")
				edit_new_lead(access_token=access_token,lead_id =lead_id,job_id=job_id,company_name=company_name,company_id = company_id,title= current_job_title,address=address,other_address=other_address,phone_company=phone_company,hirer_phone = hirer_phone, hirer_email = email_info,website=website,content=full_content, lead_status = lead_status, job_phone = job_phone, assigned_user_id = assigned_user_id, hirer_name = hirer_name, refer= "", contact_id = contact_id)
		driver.switch_to.window(company_window)
		driver.close()#2 close  company_window
		time.sleep(1)

		driver.switch_to.window(job_detail_window)
		driver.close()#1 close  job_detail_window
		time.sleep(1)

		driver.switch_to.window(root_window)
	except NoSuchElementException:
		pass

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
	time.sleep(2)
	submitElement.click()
	time.sleep(2)


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
	time.sleep(2)
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

def hasClass(element,class_search: str):
	classes = element.get_attribute("class");
	list = classes.split(" ")
	for item in list:
		if item == class_search:
			return True
		else:
			continue
	return False

def _find_element(driver, by):
	"""Looks up an element using a Locator"""
	return driver.find_element(*by)


def flatten_list(l):
	return [item for sublist in l for item in sublist]


def split_lists(lst, num):
	k, m = divmod(len(lst), num)
	return [lst[i * k + min(i, m): (i+1) * k + min(i + 1, m)] for i in range(num)]


class TextChanged(object):
	def __init__(self, locator, text):
		self.locator = locator
		self.text = text

	def __call__(self, driver):
		actual_text = _find_element(driver, self.locator).text
		return actual_text != self.text


class AnyEC(object):
	def __init__(self, *args):
		self.ecs = args

	def __call__(self, driver):
		for fn in self.ecs:
			try:
				if fn(driver):
					return True
			except:
				pass
		return False
#Optional[bs4.Tag]
def one_or_default(element: any, selector: str, default=None) -> any:
	"""Return the first found element with a given css selector

	Params:
		- element {beautifulsoup element}: element to be searched
		- selector {str}: css selector to search for
		- default {any}: default return value

	Returns:
		beautifulsoup element if match is found, otherwise return the default
	"""
	try:
		el = element.select_one(selector)
		if not el:
			return default
		return element.select_one(selector)
	except Exception as e:
		return default


def text_or_default(element, selector, default=None):
	"""Same as one_or_default, except it returns stripped text contents of the found element
	"""
	try:
		return element.select_one(selector).get_text().strip()
	except Exception as e:
		return default


def all_or_default(element, selector, default=[]):
	"""Get all matching elements for a css selector within an element

	Params:
		- element: beautifulsoup element to search
		- selector: str css selector to search for
		- default: default value if there is an error or no elements found

	Returns:
		{list}: list of all matching elements if any are found, otherwise return
		the default value
	"""
	try:
		elements = element.select(selector)
		if len(elements) == 0:
			return default
		return element.select(selector)
	except Exception as e:
		return default


def get_info(element, mapping, default=None):
	"""Turn beautifulsoup element and key->selector dict into a key->value dict

	Args:
		- element: A beautifulsoup element
		- mapping: a dictionary mapping key(str)->css selector(str)
		- default: The defauly value to be given for any key that has a css
		selector that matches no elements

	Returns:
		A dict mapping key to the text content of the first element that matched
		the css selector in the element.  If no matching element is found, the
		key's value will be the default param.
	"""
	return {key: text_or_default(element, mapping[key], default=default) for key in mapping}

#Optional[bs4.Tag]
#List[dict]
def get_job_info(job: any) -> any:
	"""
	Returns:
		list of dicts, each element containing the details of a job for some company:
		   - job title
		   - company
		   - date_range
		   - location
		   - description
		   - company link
	"""
	def _get_company_url(job_element):
		company_link = one_or_default(
			job_element, 'a[data-control-name="background_details_company"]')

		if not company_link:
			logger.info("Could not find link to company.")
			return ''

		pattern = re.compile('^/company/.*?/$')
		if not hasattr(company_link, 'href') or not pattern.match(company_link['href']):
			logger.warning(
				"Found company link el: %s, but either the href format was unexpected, or the href didn't exist.", company_link)
			return ''
		else:
			return 'https://www.linkedin.com' + company_link['href']

	position_elements = all_or_default(
		job, '.pv-entity__role-details-container')

	company_url = _get_company_url(job)

	all_positions = []

	# Handle UI case where user has muttiple consec roles at same company
	if (position_elements):
		company = text_or_default(job,
								  '.pv-entity__company-summary-info > h3 > span:nth-of-type(2)')
		positions = list(map(lambda pos: get_info(pos, {
			'title': '.pv-entity__summary-info-v2 > h3 > span:nth-of-type(2)',
			'date_range': '.pv-entity__date-range span:nth-of-type(2)',
			'location': '.pv-entity__location > span:nth-of-type(2)',
			'description': '.pv-entity__description'
		}), position_elements))
		for pos in positions:
			pos['company'] = company
			pos['li_company_url'] = company_url
			if pos['description'] is not None:
				pos['description'] = pos['description'].replace(
					'See less\n', '').replace('... See more', '').strip()

			all_positions.append(pos)

	else:
		job_info = get_info(job, {
			'title': '.pv-entity__summary-info h3:nth-of-type(1)',
			'company': '.pv-entity__secondary-title',
			'date_range': '.pv-entity__date-range span:nth-of-type(2)',
			'location': '.pv-entity__location span:nth-of-type(2)',
			'description': '.pv-entity__description',
		})
		if job_info['description'] is not None:
			job_info['description'] = job_info['description'].replace(
				'See less\n', '').replace('... See more', '').strip()

		job_info['li_company_url'] = company_url
		all_positions.append(job_info)

	if all_positions:
		company = all_positions[0].get('company', "Unknown")
		job_title = all_positions[0].get('title', "Unknown")
		logger.debug(
			"Attempting to determine company URL from position: {company: %s, job_title: %s}", company, job_title)
		url = _get_company_url(job)
		for pos in all_positions:
			pos['li_company_url'] = url

	return all_positions


def get_school_info(school):
	"""
	Returns:
		dict of school name, degree, grades, field_of_study, date_range, &
		extra-curricular activities
	"""
	return get_info(school, {
		'name': '.pv-entity__school-name',
		'degree': '.pv-entity__degree-name span:nth-of-type(2)',
		'grades': '.pv-entity__grade span:nth-of-type(2)',
		'field_of_study': '.pv-entity__fos span:nth-of-type(2)',
		'date_range': '.pv-entity__dates span:nth-of-type(2)',
		'activities': '.activities-societies'
	})


def get_volunteer_info(exp):
	"""
	Returns:
		dict of title, company, date_range, location, cause, & description
	"""
	return get_info(exp, {
		'title': '.pv-entity__summary-info h3:nth-of-type(1)',
		'company': '.pv-entity__secondary-title',
		'date_range': '.pv-entity__date-range span:nth-of-type(2)',
		'location': '.pv-entity__location span:nth-of-type(2)',
		'cause': '.pv-entity__cause span:nth-of-type(2)',
		'description': '.pv-entity__description'
	})


def get_skill_info(skill):
	"""
	Returns:
		dict of skill name and # of endorsements
	"""
	return get_info(skill, {
		'name': '.pv-skill-category-entity__name',
		'endorsements': '.pv-skill-category-entity__endorsement-count'
	}, default=0)


# Takes a recommendation element and return a dict of relevant information.
def get_recommendation_details(rec):
	li_id_expr = re.compile(
		r'((?<=in\/).+(?=\/)|(?<=in\/).+)')  # re to get li id
	# re to get date of recommendation
	date_expr = re.compile(r'\w+ \d{1,2}, \d{4}, ')
	rec_dict = {
		'text': None,
		'date': None,
		'connection': {
			'relationship': None,
			'name': None,
			'li_id': None
		}
	}

	# remove See more and See less
	for text_link in all_or_default(rec, 'a[role="button"]'):
		text_link.decompose()
	for ellipsis in all_or_default(rec, '.lt-line-clamp__ellipsis'):
		ellipsis.decompose()

	text = text_or_default(rec, '.pv-recommendation-entity__highlights')
	rec_dict['text'] = text.replace('\n', '').replace('  ', '')

	recommender = one_or_default(rec, '.pv-recommendation-entity__member')
	if recommender:
		try:
			rec_dict['connection']['li_id'] = li_id_expr.search(
				recommender.attrs['href']).group()
		except AttributeError as e:
			pass

		recommender_detail = one_or_default(
			recommender, '.pv-recommendation-entity__detail')
		if recommender_detail:
			name = text_or_default(recommender, 'h3')
			rec_dict['connection']['name'] = name

			recommender_ps = recommender_detail.find_all('p', recursive=False)

			if len(recommender_ps) == 2:
				try:
					recommender_meta = recommender_ps[-1]
					recommender_meta = recommender_meta.get_text().strip()
					match = date_expr.search(recommender_meta).group()
					dt = datetime.strptime(match, '%B %d, %Y, ')
					rec_dict['date'] = dt.strftime('%Y-%m-%d')
					relationship = recommender_meta.split(match)[-1]
					rec_dict['connection']['relationship'] = relationship
				except (ValueError, AttributeError) as e:
					pass

	return rec_dict
