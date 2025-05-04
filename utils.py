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
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select
from eld import LanguageDetector

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
		return json_object
		
def check_lead_existed(title, account_name, contact):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/leads/check"
	jsondata = {"title":title,
				"last_name" : account_name,
				"first_name" : contact
	}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object

def getAccountSentMessageToday():
    headers = {'Content-Type': "application/json", 'Accept': "application/json"}
    check_api = "http://68.183.189.171:9999/getAccountSentMessageToday"
    data = requests.post(check_api,headers=headers)
    if data.status_code != 200:
        print(data.status_code)
        print(data.reason)
    else:
        json_object = data.json()
        return json_object


def add_new_account(access_token,name,phone,website,address, des):
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
	  "billing_address_country" : address,
	  "assigned_user_id": "62b60dd0-9ab9-735e-e291-65d2cd0ab68e",
	  "description" : des
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

def edit_account(access_token,account_id,name,phone,website,address, des):
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
	  "billing_address_country" : address,
	  "assigned_user_id": "62b60dd0-9ab9-735e-e291-65d2cd0ab68e",
	  "description" : des
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
	 
	 
def add_new_lead(access_token,job_id,company_name,company_id,title,address,other_address,phone_company,hirer_phone,hirer_email,website,content,assigned_user_id, lead_status, job_phone, hirer_name, refer, contact_id, status_des):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	assigned_user = ""
	if(len(assigned_user_id)):
		assigned_user = assigned_user_id
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
	   "assigned_user_id" : assigned_user,
	  "refered_by" : "",
	  "contact_id" : contact_id,
	  "status_description": status_des
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
		
def edit_new_lead(access_token,lead_id,job_id,company_name,company_id,title,address,other_address,phone_company,hirer_phone,hirer_email,website,content, lead_status, job_phone, assigned_user_id, hirer_name, refer, contact_id, status_des):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	assigned_user = ""
	if(len(assigned_user_id)):
		assigned_user = assigned_user_id
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
	  "assigned_user_id": assigned_user,
	  "refered_by" : "",
	  "contact_id": contact_id,
	  "status_description": status_des
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


def add_contact(access_token,title, name, email, phone, des, link, account_id):
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
	  "account_id" : account_id,
	  "created_by": "1",
	  "assigned_user_id": "62b60dd0-9ab9-735e-e291-65d2cd0ab68e"
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

def edit_contact(access_token, contact_id , title, name, email, phone, des, link, account_id):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	jsondata =  {
  "data": {
	"type": "Contacts",
	"id" : contact_id,
	"attributes": {
	  "last_name": name,
	  "title": title,
	  "description" : des,
	  "email" : email,
	  "phone_work" : phone,
	  "created_by_link" : link,
	  "account_id" : account_id
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
		print('done')
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
		return json_object
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
		return json_object["data"]

def get_account_assigned_user(name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/lead/getassigneduserbyaccount"
	jsondata = {"name":name}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print("\naccount_assigned" + data.reason)
	else:
		json_object = data.json()
		return json_object["data"]

def get_account_email_assigned_user(name,email):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/lead/getassigneduserbyaccountandemail"
	jsondata = {"param_1":name,
			 "param_2":email}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print("\naccount_assigned" + data.reason)
	else:
		json_object = data.json()
		return json_object["data"]

def get_num_mess_sent_lead(access_token):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module/Leads?filter[mess_sent_c][eq]=1"
	time.sleep(2)
	data = requests.get(module_api,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object["data"]

def check_email_expired(email):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/getactivelead"
	jsondata = {"name":email}
	data = requests.get(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object["email_expired"]
	

def check_lead_status_with_email(email):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/get_lead_status_with_email"
	jsondata = {"name":email}
	data = requests.get(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object["status_count"]


def get_job_detail(driver,job_id,access_token,address, country, linkedin_acc):	 
	root_window = driver.window_handles[0]
	print("\n job_id",job_id)
	#1 job detail window 
	driver.execute_script("window.open('');")
	job_detail_window = driver.window_handles[1]
	driver.switch_to.window(job_detail_window)

	job_detail_url = 'https://www.linkedin.com/jobs/view/' + job_id
	driver.get(job_detail_url)
	# try:
	# 	see_more_button_click = random.randint(0,1)
	# 	see_more_button = driver.find_element(By.CLASS_NAME,"jobs-description__footer-button")
	# 	see_more_button_text = see_more_button.find_element(By.TAG_NAME,"span").text
	# 	if(see_more_button_click == 1 and see_more_button_text.lower() == "see more"):
	# 		start_scroll = time.time()
	# 		see_more_button.click()	
	# 		last_height = driver.execute_script("return document.body.scrollHeight")
	# 		page_offset = driver.execute_script("return window.pageYOffset;")
	# 		threshold = random.randint(1500, 1800)
	# 		while True:
	# 			driver.execute_script("window.scrollTo(0, " + str(page_offset) + ");")
	# 			new_page_offset = driver.execute_script("return window.pageYOffset;")
	# 			z = random.uniform(0, 2)
	# 			time.sleep(z)
	# 			end_scroll = time.time()
	# 			page_offset = page_offset + 100
	# 			if new_page_offset > last_height - threshold or end_scroll - start_scroll > 10 :
	# 				break
	# 	# driver.execute_script('window.scrollBy(0, 0)') 
	# except Exception as error:
	# 	print("there is no show more button:", error)
	# 	pass
	y = random.randint(10,20)
	time.sleep(y)
	company_url = ""
	company_name = ""
	job_emails = []
	job_phones = []
	job_phone = ""
	expired = "No"
	contact_new_tab = 0
	company_about_url = ""
	current_job_title = ""
	other_address = ""
	try:		
		current_job_title = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__job-title").text    
		job_detail = driver.find_element(By.CLASS_NAME,"jobs-description-content__text--stretch").text
		detector = LanguageDetector()
		title_lan = detector.detect(current_job_title).language
		detail_lan = detector.detect(job_detail).language
		if(title_lan != "en" or detail_lan != "en"):
			driver.switch_to.window(job_detail_window)
			z = random.randint(3,7)
			time.sleep(z)
			driver.close()#1 close  job_detail_window
			time.sleep(1)

			driver.switch_to.window(root_window)
			return 
		expired = driver.find_element(By.CLASS_NAME,"jobs-details-top-card__apply-error").text 
		if("no longer" in expired.lower() ):
			driver.switch_to.window(job_detail_window)
			z = random.randint(2,5)
			time.sleep(z)
			driver.close()#1 close  job_detail_window
			time.sleep(1)

			driver.switch_to.window(root_window)
			return 
	except Exception as error:
		print("First ex: ",error)
		pass
	try :
		current_job_title = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__job-title").text    
		job_detail_text = driver.find_element(By.CLASS_NAME,"jobs-description-content__text--stretch").text	
		#job_detail = driver.find_element(By.CLASS_NAME,"jobs-description-content__text")
		#job_detail_text = job_detail.text
		# job_detail_spans = job_detail.find_elements(By.TAG_NAME,"span")
		# for job_detail_span in job_detail_spans:
		# 	job_detail_text = job_detail_text + job_detail_span.text
		# 	job_detail_ps = job_detail_span.find_elements(By.TAG_NAME,"p")
		# 	for job_detail_p in job_detail_ps:
		# 		job_detail_text = job_detail_text + job_detail_p.text
		job_emails = re.findall(r"[a-z0-9A-Z\.\-+_]+@[a-z0-9A-Z\.\-+_]+\.[a-zA-Z]+", job_detail_text)
		if(country == "Australia"):
			job_phones =re.findall(r'^(?=.*)((?:\+61) ?(?:\((?=.*\)))?([2-47-8])\)?|(?:\((?=.*\)))?([0-1][2-47-8])\)?) ?-?(?=.*)((\d{1} ?-?\d{3}$)|(00 ?-?\d{4} ?-?\d{4}$)|( ?-?\d{4} ?-?\d{4}$)|(\d{2} ?-?\d{3} ?-?\d{3}$))', job_detail_text) 
		elif (country == "Malaysia"):
			job_phones =re.findall(r'^(?:(?:\+60|0060)(?:[1]|[0]?[1])[ -]?|[0])[0-9]{2}[ -]?[0-9]{3,4}[ -]?[0-9]{3,4}$', job_detail_text) 
		elif (country == "Thailand"):
			job_phones = re.findall(r'^(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}$', job_detail_text)
		elif (country == "New Zealand"):
			job_phones = re.findall(r'^(0|(\+64(\s|-)?)){1}(21|22|27){1}(\s|-)?\d{3}(\s|-)?\d{4}$', job_detail_text)
		else:
			print("Not interested country")
		infos_element = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__primary-description-container")
		address_element = infos_element.find_elements(By.TAG_NAME,"span")[0]
		other_address = address_element.text	
		# address_from_web = other_address.split(',')
		# address = address_from_web[address_from_web.len() -1]
		company_element = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__company-name")
		company_name = company_element.text
		company_name_lower = company_name.lower()
		skiped_company_list = ["centre for strategic infocomm technologies","govtech","minnesota housing","police","authority","national","bureau","notary","airway","airline","lufthansa","booking.com","united nations","grab","federal","canva","tesla","netflix","walmart","government","tripadvisor","general motors","barclays","formula 1","gitlab","bank","boeing","easyjet","bp","ikea","oracle","amazon","google","microsoft","siemens","visa","university","airlines","shopee","millennium","aribus","mastercard","meta","volvo","airbnb","bloomberg","openai","mcdonald's","lego","facebook","bbc","department","dhl","ministry","workforce australia for individuals","american express","cnn","philips","ibm","cisco","agoda","spotify","nokia","paypal", "audi", "disney", "dhl", "bosch", "council","lgbtq+","standard chartered","expressvpn","jollibee","liberty","shopify","universal","lenovo","college","hitachi","electrolux","the guardian","skyscanner","new york times","mercedes","formula one","institute"]
		# for skiped_company in skiped_company_list:
		# 	if(skiped_company in company_name_lower):
		# 		driver.switch_to.window(job_detail_window)
		# 		z = random.randint(3,7)
		# 		time.sleep(z)
		# 		driver.close()#1 close  job_detail_window
		# 		time.sleep(1)
		# 		driver.switch_to.window(root_window)
		# 		return 
		if not company_element.find_element(By.TAG_NAME,"a"):
			print("company_url is empty")
		else:
			company_element_url = company_element.find_element(By.TAG_NAME,"a")
			company_url = company_element.find_element(By.CSS_SELECTOR,"a").get_attribute("href")
			company_name = company_element_url.text
		company_name_lower = company_name.lower() 
		for skiped_company in skiped_company_list:
			if(skiped_company in company_name_lower):
				driver.switch_to.window(job_detail_window)
				z = random.randint(3,7)
				time.sleep(z)
				driver.close()#1 close  job_detail_window
				time.sleep(1)
				driver.switch_to.window(root_window)
				return 
	except Exception as error:
		print("not found job title", error)
		pass
	
	company_info = {"data": "", "des" : ""}
	company_info = check_company_existed(company_name)
	company_id = company_info["data"]
	company_desc = company_info["des"]
	contact_info = {"data": "", "des" : ""}
	lead_info = {"data": "", "status" : ""}
	hirer_name = ""
	hirer_name_first_name = ""
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
	mess_sent = ""
	company_people = ""
	contact_people = 0
	#Get Hirer Link
	try:
		hirer_name_element = driver.find_element(By.CLASS_NAME,"jobs-poster__name")
		hirer_name = hirer_name_element.find_element(By.TAG_NAME,"strong").text
		hirer_name_split = hirer_name.split()
		ii = 0
		while(hirer_name_split[ii].isalpha() == False):
			ii = ii + 1
		hirer_name_first_name = hirer_name.split()[ii]
		#hirer_name = hirer_name_element.text
	except NoSuchElementException as error:
		print("Second ex: " , error)
		pass
	try:
		lead_info = check_lead_existed(current_job_title, company_name, hirer_name)
		z = random.randint(5,10)
		time.sleep(z)
		if(hirer_name != ""):			
			contact_info = check_contact(hirer_name)		
			if(contact_info["data"] == ""):
			# get contact info and send request
				hirer = driver.find_element(By.CLASS_NAME,"hirer-card__hirer-information")
				hirer_title = hirer.find_element(By.CLASS_NAME,"linked-area").text
				hirer_link = hirer.find_element(By.TAG_NAME,"a").get_attribute("href")
				contact_new_tab = random.randint(0,1)
				contact_new_tab = 1
				if(contact_new_tab == 0):				
					driver.get(hirer_link)
					z = random.randint(15,20)
					time.sleep(z)
				else:
					driver.execute_script("window.open('');")
					contact_window = driver.window_handles[2]
					driver.switch_to.window(contact_window)
					driver.get(hirer_link)
					z = random.randint(3,5)
					time.sleep(z)	
				contact_info_link = driver.find_element(By.ID,"top-card-text-details-contact-info").get_attribute("href")
				driver.get(contact_info_link)
				time.sleep(3)
				contact_info_list = driver.find_elements(By.CLASS_NAME,"pv-contact-info__contact-type")
				for contact_info_detail in contact_info_list:
					contact_info_header = contact_info_detail.find_element(By.CLASS_NAME,"pv-contact-info__header")
					contact_info_content = contact_info_detail.find_element(By.CLASS_NAME,"t-14")
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
				dismiss_button = driver.find_element(By.CLASS_NAME,"artdeco-modal__dismiss")
				dismiss_button.click() 				
				time.sleep(2)
				if("gov" in hirer_email.lower() or "edu" in hirer_email.lower()):
					if(contact_new_tab == 1):
						driver.switch_to.window(contact_window)
						driver.close()#2 close  company_window
						time.sleep(2)	
					driver.switch_to.window(job_detail_window)
					time.sleep(6)
					driver.close()#1 close  job_detail_window
					time.sleep(2)
					driver.switch_to.window(root_window)
					return	
				if(lead_info["status"] is None or lead_info["status"] == "" or (lead_info["status"] is not None and lead_info["status"] != "Converted" and lead_info["status"] != "Assigned" and lead_info["status"] != "In Process" and lead_info["status"] != "Dead") ):
					hirer_detail = driver.find_element(By.CLASS_NAME,"AbrjnZkFZdsBACByvMYEeLvfAMdGxUSUtjY")
					#hirer_detail_button = hirer_detail.find_element(By.CLASS_NAME,"pvs-profile-actions__action")
					hirer_detail_button = hirer_detail.find_element(By.CLASS_NAME,"artdeco-button--primary")					
					text_hirer_button = hirer_detail_button.find_element(By.CLASS_NAME,"artdeco-button__text").text
					driver.implicitly_wait(3)
					if (text_hirer_button == "Connect"):
						hirer_detail_button.click()	
						z = random.randint(4,7)
						time.sleep(z)	
						#driver.implicitly_wait(10)		
						hirer_connect_modal = driver.find_element(By.CLASS_NAME,"send-invite")
						hirer_connect_request_buttons = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-modal__actionbar")
						if(hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")):
							hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")
							hirer_connect_request_button.click()
							driver.implicitly_wait(10)
							connect_mess_modal = driver.find_element(By.CLASS_NAME,"send-invite")
							connect_mess_area = connect_mess_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
							connect_mess_area.clear()
							driver.implicitly_wait(5)
							#connect_mess_area.send_keys("We are Fitech founded in 2007. If you are looking for tech partners to develop your solutions in various domains including fintech, stock market, banking and payment gateway, our good team would help.")
							connect_mess_area.send_keys("Dear " + hirer_name_first_name +", we are Fitech founded since 2007. If you are looking for tech partners who can collaborate to develop your solutions in various domains and knowledges about fintech, stock market, banking, payment gateway and e-commerce we believe that our good teams would help.")
							z = random.randint(2,7)
							time.sleep(z)
							#time.sleep(2)
							connect_button = connect_mess_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
							if(connect_button.is_enabled()):
								z = random.randint(2,4)
								time.sleep(z)
								connect_button.click() 
								request_note_str = request_note_str + "\nconnect by " + linkedin_acc
								mess_sent = "message sent by AdminAccount"
								time.sleep(2)	
											
						else:
							hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--primary")
							if(hirer_connect_request_button.is_enabled()):
								z = random.randint(2,4)
								time.sleep(z)
								hirer_connect_request_button.click()	
								request_note_str = request_note_str + "\nconnect by " + linkedin_acc
								mess_sent = "message sent by AdminAccount"
								time.sleep(2)
						# connect_mess_area = hirer_connect_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
						# connect_mess_area.clear()
						# driver.implicitly_wait(5)
						# connect_mess_area.send_keys("We are Fitech founded in 2007. If you are looking for tech partners to develop your solutions in various domains including fintech, stock market, banking and payment gateway, our good team would help.")
						# z = random.randint(2,7)
						# time.sleep(z)
						# connect_button = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
						# if(connect_button.is_enabled()):
						# 	z = random.randint(2,4)
						# 	time.sleep(z)
						# 	connect_button.click() 
						# 	request_note_str = request_note_str + "\nconnect by " + linkedin_acc
						# 	mess_sent = "message sent by AdminAccount"
						# 	time.sleep(2)
					else:
						try:
							z = random.randint(30,35)
							time.sleep(z)
							if(text_hirer_button != "Pending"):
								hirer_more_dropdown = hirer_detail.find_element(By.CLASS_NAME,"artdeco-dropdown")
								#hirer_more_button = hirer_more_dropdown.find_element(By.CLASS_NAME, "pvs-profile-actions__action")
								hirer_more_button = hirer_more_dropdown.find_element(By.CLASS_NAME, "artdeco-button")
								
								driver.implicitly_wait(5)
					#hirer_more_button = driver.find_element(By.XPATH, '//button[text()="More"]')
								hirer_more_button.click()
								driver.implicitly_wait(5)
								hirer_more_option = hirer_more_dropdown.find_element(By.CLASS_NAME,"artdeco-dropdown__content-inner")
								hirer_more_option_ul = hirer_more_option.find_element(By.TAG_NAME,"ul")
								hirer_more_option_li = hirer_more_option_ul.find_elements(By.TAG_NAME,"li")
								for option_li in hirer_more_option_li:
									try:
										option_li_div = option_li.find_element(By.CLASS_NAME,"artdeco-dropdown__item")
										driver.implicitly_wait(3)
										option_li_text = option_li_div.find_element(By.TAG_NAME,"span").text
										if(option_li_text == "Connect"):
											option_li.click()
											z = random.randint(3,5)
											time.sleep(z)	
											#driver.implicitly_wait(5)
											hirer_connect_modal = driver.find_element(By.CLASS_NAME,"send-invite")
											hirer_connect_request_buttons = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-modal__actionbar")
											if(hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")):
												hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")
												hirer_connect_request_button.click()
												driver.implicitly_wait(10)
												connect_mess_modal = driver.find_element(By.CLASS_NAME,"send-invite")
												connect_mess_area = connect_mess_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
												connect_mess_area.clear()
												driver.implicitly_wait(5)
												#connect_mess_area.send_keys("We are Fitech founded in 2007. If you are looking for tech partners to develop your solutions in various domains including fintech, stock market, banking and payment gateway, our good team would help.")
												connect_mess_area.send_keys("Dear " + hirer_name_first_name +", we are Fitech founded since 2007. If you are looking for tech partners who can collaborate to develop your solutions in various domains and knowledges about fintech, stock market, banking, payment gateway and e-commerce we believe that our good teams would help.")
												z = random.randint(3,9)
												time.sleep(z)
												connect_button = connect_mess_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
												if(connect_button.is_enabled()):
													z = random.randint(2,4)
													time.sleep(z)
													connect_button.click() 
													request_note_str = request_note_str + "\nconnect by" + linkedin_acc
													mess_sent = "message sent by AdminAccount"
													time.sleep(2)				
											else:
												hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--primary")
												if(hirer_connect_request_button.is_enabled()):
													z = random.randint(2,4)
													time.sleep(z)
													hirer_connect_request_button.click()
													request_note_str = request_note_str + "\nconnect by " + linkedin_acc
													mess_sent = "message sent by AdminAccount"
													time.sleep(2)

											# connect_mess_area = hirer_connect_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
											# connect_mess_area.clear()
											# driver.implicitly_wait(5)
											# connect_mess_area.send_keys("We are Fitech founded in 2007. If you are looking for tech partners to develop your solutions in various domains including fintech, stock market, banking and payment gateway, our good team would help.")
											# z = random.randint(2,7)
											# time.sleep(z)
											# connect_button = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
											# if(connect_button.is_enabled()):
											# 	z = random.randint(2,4)
											# 	time.sleep(z)
											# 	connect_button.click() 
											# 	request_note_str = request_note_str + "\nconnect by " + linkedin_acc
											# 	mess_sent = "message sent by AdminAccount"
											# 	time.sleep(2)
									except Exception as error:
										print("\n Connect sent to new contact: ", error)
										continue
						except Exception as error:
							print("thrid ex:", error)		
							pass
					try:
						if(request_note_str == "" and text_hirer_button != "Pending"):
							entry_point = hirer_detail.find_element(By.CLASS_NAME,"entry-point")
							message_button = entry_point.find_element(By.TAG_NAME,"button")
							if(message_button.is_enabled()):
								message_button.click()
								time.sleep(2)

							message_box = driver.find_element(By.CLASS_NAME,"artdeco-text-input--container")
							message_title_input = message_box.find_element(By.TAG_NAME,"input")
							message_title_input.send_keys("Elevate Your Team with Fitech's Offshore Talent")
							time.sleep(5)

							message_content_input = driver.find_element(By.CLASS_NAME,"msg-form__contenteditable")
							message_content_input.clear()
							input_mess = "Dear " + hirer_name_first_name + ", we are from Fitech founded since 2007, where we have some software solutions in various domains and knowledges about fintech, stock market, banking, payment gateway and e-commerce. If you are looking for partners who can collaborate with your company to develop such a solution we believe that our good teams would help. If you are interested we can setup a meeting call to introduce more about capabilities and opportunities working together. Thank you! \n \n" + linkedin_acc
							print(input_mess)
							message_content_input.send_keys(input_mess)
							z = random.randint(2,5)
							time.sleep(z)
							# send_button = driver.find_element(By.CLASS_NAME,"msg-form__send-button")
							# if(send_button.is_enabled()):
							# 	request_note_str = contact_info["des"] + "\nmessage by " + linkedin_acc
							# 	z = random.randint(2,4)
							# 	time.sleep(z)
							# 	send_button.submit() 
							# 	mess_sent = "message sent by AdminAccount"
							# 	time.sleep(3)
					except Exception as error:
						print("forth ex: ", error)
						pass
				print("\n add contact")
				add_contact(access_token = access_token,title = hirer_title , name = hirer_name, email = hirer_email, phone = hirer_phone, des = request_note_str, link = contact_info_link, account_id= company_id)
				contact_info = check_contact(hirer_name)
				contact_id = contact_info["data"]
				z = random.randint(2,5)
				time.sleep(z)
			else:
				contact_id = contact_info["data"]
				request_note_str = contact_info["des"]
				hirer = driver.find_element(By.CLASS_NAME,"hirer-card__hirer-information")
				hirer_link = hirer.find_element(By.TAG_NAME,"a").get_attribute("href")
				contact_new_tab = random.randint(0,1)
				if(contact_new_tab == 0):
					driver.get(hirer_link)
					time.sleep(2)
				else:
					driver.execute_script("window.open('');")
					contact_window = driver.window_handles[2]
					driver.switch_to.window(contact_window)
					driver.get(hirer_link)
					time.sleep(3)	
				contact_info_link = driver.find_element(By.ID,"top-card-text-details-contact-info").get_attribute("href")
				driver.get(contact_info_link)
				time.sleep(3)
				contact_info_list = driver.find_elements(By.CLASS_NAME,"pv-contact-info__contact-type")
				for contact_info_detail in contact_info_list:
					contact_info_header = contact_info_detail.find_element(By.CLASS_NAME,"pv-contact-info__header")
					contact_info_content = contact_info_detail.find_element(By.CLASS_NAME,"t-14")
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
				dismiss_button = driver.find_element(By.CLASS_NAME,"artdeco-modal__dismiss")
				dismiss_button.click() 				
				time.sleep(2)
				if("gov" in hirer_email.lower() or "edu" in hirer_email.lower()):
					if(contact_new_tab == 1):
						driver.switch_to.window(contact_window)
						driver.close()#2 close  company_window
						time.sleep(1)	
					driver.switch_to.window(job_detail_window)
					driver.close()#1 close  job_detail_window
					time.sleep(1)
					driver.switch_to.window(root_window)
					return
				if(lead_info["status"] is None or lead_info["status"] == "" or (lead_info["status"] is not None and lead_info["status"] != "Converted" and lead_info["status"] != "Assigned" and lead_info["status"] != "In Process" and lead_info["status"] != "Dead")):
					if(contact_info["des"] is None or ("connect" not in contact_info["des"].lower() and "message" not in contact_info["des"].lower())):
						try:
							hirer_detail = driver.find_element(By.CLASS_NAME,"AbrjnZkFZdsBACByvMYEeLvfAMdGxUSUtjY")
							#hirer_detail_button = hirer_detail.find_element(By.CLASS_NAME,"pvs-profile-actions__action")
							hirer_detail_button = hirer_detail.find_element(By.CLASS_NAME,"artdeco-button--primary")
							
							text_hirer_button = hirer_detail_button.find_element(By.CLASS_NAME,"artdeco-button__text").text
							driver.implicitly_wait(3)
							if (text_hirer_button == "Connect"):
								hirer_detail_button.click()	
								#driver.implicitly_wait(20)	
								time.sleep(5)	
								hirer_connect_modal = driver.find_element(By.CLASS_NAME,"send-invite")
								hirer_connect_request_buttons = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-modal__actionbar")
								if(hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")):
									hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")
									hirer_connect_request_button.click()
									driver.implicitly_wait(10)
									connect_mess_modal = driver.find_element(By.CLASS_NAME,"send-invite")
									connect_mess_area = connect_mess_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
									connect_mess_area.clear()
									driver.implicitly_wait(5)
									#connect_mess_area.send_keys("We are Fitech founded in 2007. If you are looking for tech partners to develop your solutions in various domains including fintech, stock market, banking and payment gateway, our good team would help.")
									connect_mess_area.send_keys("Dear " + hirer_name_first_name +", we are Fitech founded since 2007. If you are looking for tech partners who can collaborate to develop your solutions in various domains and knowledges about fintech, stock market, banking, payment gateway and e-commerce we believe that our good teams would help.")
									driver.implicitly_wait(10)
									time.sleep(5)
									connect_button = connect_mess_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
									if(connect_button.is_enabled()):
										z = random.randint(2,6)
										time.sleep(z)
										connect_button.click() 
										request_note_str = contact_info["des"] + "\nconnect by " + linkedin_acc
										mess_sent = "message sent by AdminAccount"
										time.sleep(2)				
								else:
									hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--primary")
									if(hirer_connect_request_button.is_enabled()):
										hirer_connect_request_button.click()
										request_note_str = contact_info["des"] + "\nconnect by " + linkedin_acc
										mess_sent = "message sent by AdminAccount"
										time.sleep(2)	

								# connect_mess_area = hirer_connect_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
								# connect_mess_area.clear()
								# driver.implicitly_wait(5)
								# connect_mess_area.send_keys("We are Fitech founded in 2007. If you are looking for tech partners to develop your solutions in various domains including fintech, stock market, banking and payment gateway, our good team would help.")
								# z = random.randint(2,7)
								# time.sleep(z)
								# connect_button = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
								# if(connect_button.is_enabled()):
								# 	z = random.randint(2,4)
								# 	time.sleep(z)
								# 	connect_button.click() 
								# 	request_note_str = request_note_str + "\nconnect by " + linkedin_acc
								# 	mess_sent = "message sent by AdminAccount"
								# 	time.sleep(2)
							
							else:
								try:
									z = random.randint(10,15)
									time.sleep(z)
									hirer_more_dropdown = hirer_detail.find_element(By.CLASS_NAME,"artdeco-dropdown")
									#hirer_more_button = hirer_more_dropdown.find_element(By.CLASS_NAME, "pvs-profile-actions__action")
									hirer_more_button = hirer_more_dropdown.find_element(By.CLASS_NAME, "artdeco-button")
									driver.implicitly_wait(3)
							#hirer_more_button = driver.find_element(By.XPATH, '//button[text()="More"]')
									hirer_more_button.click()
									driver.implicitly_wait(5)
									hirer_more_option = hirer_more_dropdown.find_element(By.CLASS_NAME,"artdeco-dropdown__content-inner")
									hirer_more_option_ul = hirer_more_option.find_element(By.TAG_NAME,"ul")
									hirer_more_option_li = hirer_more_option_ul.find_elements(By.TAG_NAME,"li")
									for option_li in hirer_more_option_li:
										try:
											option_li_div = option_li.find_element(By.CLASS_NAME,"artdeco-dropdown__item")
											driver.implicitly_wait(3)
											option_li_text = option_li_div.find_element(By.TAG_NAME,"span").text
											if(option_li_text == "Connect"):
												option_li.click()
												z = random.randint(4,6)
												time.sleep(z)	
												#driver.implicitly_wait(5)
												hirer_connect_modal = driver.find_element(By.CLASS_NAME,"send-invite")
												hirer_connect_request_buttons = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-modal__actionbar")
												if(hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")):
													hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")
													hirer_connect_request_button.click()
													driver.implicitly_wait(10)
													connect_mess_modal = driver.find_element(By.CLASS_NAME,"send-invite")
													connect_mess_area = connect_mess_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
													connect_mess_area.clear()
													driver.implicitly_wait(5)
													#connect_mess_area.send_keys("We are Fitech founded in 2007. If you are looking for tech partners to develop your solutions in various domains including fintech, stock market, banking and payment gateway, our good team would help.")
													connect_mess_area.send_keys("Dear " + hirer_name_first_name +", we are Fitech founded since 2007. If you are looking for tech partners who can collaborate to develop your solutions in various domains and knowledges about fintech, stock market, banking, payment gateway and e-commerce we believe that our good teams would help.")
													y = random.randint(1,7)
													time.sleep(y)
												#time.sleep(2)
													connect_button = connect_mess_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
													if(connect_button.is_enabled()):
														y = random.randint(2,5)
														time.sleep(y)
														connect_button.click() 
														request_note_str = request_note_str + "\nconnect by " + linkedin_acc
														mess_sent = "message sent by AdminAccount"
														time.sleep(2)				
												else:
													hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--primary")
													if(hirer_connect_request_button.is_enabled()):
														hirer_connect_request_button.click()
														request_note_str = request_note_str + "\nconnect by " + linkedin_acc
														mess_sent = "message sent by AdminAccount"
														time.sleep(2)

												# connect_mess_area = hirer_connect_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
												# connect_mess_area.clear()
												# driver.implicitly_wait(5)
												# connect_mess_area.send_keys("We are Fitech founded in 2007. If you are looking for tech partners to develop your solutions in various domains including fintech, stock market, banking and payment gateway, our good team would help.")
												# z = random.randint(2,7)
												# time.sleep(z)
												# connect_button = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
												# if(connect_button.is_enabled()):
												# 	z = random.randint(2,4)
												# 	time.sleep(z)
												# 	connect_button.click() 
												# 	request_note_str = request_note_str + "\nconnect by " + linkedin_acc
												# 	mess_sent = "message sent by AdminAccount"
												# 	time.sleep(2)	
										except Exception as error:
											print("\nConnect error loop to existing contact :", error)	
											time.sleep(1)
											continue								
								except Exception as errorConnect:
									print("\nConnect error :", errorConnect)   
									pass
						except Exception as error: 
							print("Fifth ex: ", error)
							pass	
					if(contact_info["des"] is None or ("message" not in contact_info["des"].lower() and "connect" not in contact_info["des"].lower() and (request_note_str is None or request_note_str == ""))):	
						try:
							hirer_detail = driver.find_element(By.CLASS_NAME,"AbrjnZkFZdsBACByvMYEeLvfAMdGxUSUtjY")
							entry_point = hirer_detail.find_element(By.CLASS_NAME,"entry-point")
							message_button = entry_point.find_element(By.TAG_NAME,"button")
							if(message_button.is_enabled()):
								message_button.click()
								time.sleep(2)

							message_box = driver.find_element(By.CLASS_NAME,"artdeco-text-input--container")
							message_title_input = message_box.find_element(By.TAG_NAME,"input")
							message_title_input.clear()
							message_title_input.send_keys("Elevate Your Team with Fitech's Offshore Talent")
							time.sleep(2)

							message_content_input = driver.find_element(By.CLASS_NAME,"msg-form__contenteditable")
							message_content_input.clear()
							input_mess = "Dear " + hirer_name_first_name + ", we are from Fitech founded since 2007, where we have some software solutions in various domains and knowledges about fintech, stock market, banking, payment gateway and e-commerce. If you are looking for partners who can collaborate with your company to develop such a solution we believe that our good teams would help. If you are interested we can setup a meeting call to introduce more about capabilities and opportunities working together. Thank you!" + linkedin_acc
							message_content_input.send_keys(input_mess)
							z = random.randint(3,7)
							time.sleep(z) 
		
							send_button = driver.find_element(By.CLASS_NAME,"msg-form__send-button")
							if(send_button.is_enabled()):
								request_note_str = contact_info["des"] + "\nmessage by " + linkedin_acc
								z = random.randint(2,4)
								time.sleep(z)
								send_button.submit() 
								mess_sent = "message sent by AdminAccount"
								time.sleep(2)
						except Exception as error:
							print("Sixth ex: ", error)
							pass
				print("\n edit contact")
				edit_contact(access_token = access_token, contact_id = contact_info["data"] , title = hirer_title, name = hirer_name, email = hirer_email, phone= hirer_phone, des = request_note_str, link = contact_info_link, account_id= company_id)
		else:
			company_people_url = "/people".join(company_url.rsplit("/life", 1))
			driver.execute_script("window.open('');")
			if(contact_new_tab == 0):
				company_people_window = driver.window_handles[2]
			else:				
				company_people_window = driver.window_handles[3]
			driver.switch_to.window(company_people_window)
			driver.get(company_people_url)
			time.sleep(8)
			people_div = driver.find_element(By.CLASS_NAME,"org-people-profile-card__card-spacing")
			people_div_content = people_div.find_element(By.CLASS_NAME,"scaffold-finite-scroll__content")
			people_div_content_ul = people_div_content.find_element(By.TAG_NAME,"ul")
			people_div_content_li = people_div_content_ul.find_elements(By.TAG_NAME,"li")
			breaker = False
			for option_li in people_div_content_li:
				if (breaker == False):
					try:
						option_li_title_div = option_li.find_element(By.CLASS_NAME,"artdeco-entity-lockup__subtitle")
						option_title_div = option_li_title_div.find_element(By.CLASS_NAME,"lt-line-clamp--multi-line")
						people_title = option_title_div.text
						title_list =["cto","chief technology officer","ceo","founder","head of technical","project manager","consultant","talent acquisition"]
						for each_title in title_list:
							if each_title in people_title.lower():
								profile_click_div = option_li.find_element(By.CLASS_NAME,"artdeco-entity-lockup__image")
								people_link = profile_click_div.find_element(By.TAG_NAME,"a").get_attribute("href")
								people_name_div = option_li.find_element(By.CLASS_NAME,"artdeco-entity-lockup__title")
								people_name_line = people_name_div.find_element(By.CLASS_NAME,"lt-line-clamp--single-line")
								people_name = people_name_line.text
								people_name_split = people_name.split()
								jj = 0
								while(people_name_split[jj].isalpha() == False):
									jj = jj + 1
								people_name_first_name = hirer_name.split()[jj]
								people_info = check_contact(people_name)
								if(people_info["data"] == ""):
									driver.get(people_link)
									time.sleep(4)
									if(lead_info["data"] == ""):
										hirer_detail = driver.find_element(By.CLASS_NAME,"AbrjnZkFZdsBACByvMYEeLvfAMdGxUSUtjY")
										hirer_detail_button = hirer_detail.find_element(By.CLASS_NAME,"artdeco-button--primary")
										text_hirer_button = hirer_detail_button.find_element(By.CLASS_NAME,"artdeco-button__text").text
										driver.implicitly_wait(3)
										if (text_hirer_button == "Connect"):
											hirer_detail_button.click()
											z = random.randint(4,7)
											time.sleep(z)
											hirer_connect_modal = driver.find_element(By.CLASS_NAME,"send-invite")
											hirer_connect_request_buttons = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-modal__actionbar")
											if(hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")):
												hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")
												hirer_connect_request_button.click()
												driver.implicitly_wait(10)
												connect_mess_modal = driver.find_element(By.CLASS_NAME,"send-invite")
												connect_mess_area = connect_mess_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
												connect_mess_area.clear()
												driver.implicitly_wait(5)
												connect_mess_area.send_keys("Dear " + people_name_first_name +", we are Fitech founded since 2007. If you are looking for tech partners who can collaborate to develop your solutions in various domains and knowledges about fintech, stock market, banking, payment gateway and e-commerce we believe that our good teams would help.")
												z = random.randint(2,7)
												time.sleep(z)
												connect_button = connect_mess_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
												if(connect_button.is_enabled()):
													z = random.randint(2,4)
													time.sleep(z)
													connect_button.click() 
													request_note_str = request_note_str + "\nconnect request sent by " + linkedin_acc
													mess_sent = "message sent by AdminAccount"
													time.sleep(2)
											else:
												hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--primary")
												if(hirer_connect_request_button.is_enabled()):
													z = random.randint(2,4)
													time.sleep(z)
													hirer_connect_request_button.click()	
													request_note_str = request_note_str + "\nconnect request sent by " + linkedin_acc
													mess_sent = "message sent by AdminAccount"
													time.sleep(2)
										else:
											try:
												if(text_hirer_button != "Pending"):
													hirer_more_dropdown = hirer_detail.find_element(By.CLASS_NAME,"artdeco-dropdown")
													hirer_more_button = hirer_more_dropdown.find_element(By.CLASS_NAME, "artdeco-button")
													driver.implicitly_wait(5)
													hirer_more_button.click()
													driver.implicitly_wait(5)
													hirer_more_option = hirer_more_dropdown.find_element(By.CLASS_NAME,"artdeco-dropdown__content-inner")
													hirer_more_option_ul = hirer_more_option.find_element(By.TAG_NAME,"ul")
													hirer_more_option_li = hirer_more_option_ul.find_elements(By.TAG_NAME,"li")
													for option_li in hirer_more_option_li:
														try:
															option_li_div = option_li.find_element(By.CLASS_NAME,"artdeco-dropdown__item")
															driver.implicitly_wait(3)
															option_li_text = option_li_div.find_element(By.TAG_NAME,"span").text
															if(option_li_text == "Connect"):
																option_li.click()
																z = random.randint(3,5)
																time.sleep(z)	
																hirer_connect_modal = driver.find_element(By.CLASS_NAME,"send-invite")
																hirer_connect_request_buttons = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-modal__actionbar")
																if(hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")):
																	hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")
																	hirer_connect_request_button.click()
																	driver.implicitly_wait(10)
																	connect_mess_modal = driver.find_element(By.CLASS_NAME,"send-invite")
																	connect_mess_area = connect_mess_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
																	connect_mess_area.clear()
																	driver.implicitly_wait(5)
																	#connect_mess_area.send_keys("We are Fitech founded in 2007. If you are looking for tech partners to develop your solutions in various domains including fintech, stock market, banking and payment gateway, our good team would help.")
																	connect_mess_area.send_keys("Dear " + people_name_first_name +", we are Fitech founded since 2007. If you are looking for tech partners who can collaborate to develop your solutions in various domains and knowledges about fintech, stock market, banking, payment gateway and e-commerce we believe that our good teams would help.")
																	z = random.randint(3,9)
																	time.sleep(z)
																	connect_button = connect_mess_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
																	if(connect_button.is_enabled()):
																		z = random.randint(2,4)
																		time.sleep(z)
																		connect_button.click() 
																		request_note_str = request_note_str + "\nconnect request sent by" + linkedin_acc
																		mess_sent = "message sent by AdminAccount"
																		time.sleep(2)	
																else:
																	hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--primary")
																	if(hirer_connect_request_button.is_enabled()):
																		z = random.randint(2,4)
																		time.sleep(z)
																		hirer_connect_request_button.click()
																		request_note_str = request_note_str + "\nconnect request sent by " + linkedin_acc
																		mess_sent = "message sent by AdminAccount"
																		time.sleep(2)
														except Exception as error:
															print("\n Connect sent to people 1: ", error)
															continue
											except Exception as error:
												print("Connect sent to people 2:", error)
												continue
									add_contact(access_token = access_token,title = hirer_title , name = people_name, email = "", phone = "", des = request_note_str, link = people_link, account_id= company_id)
									people_info = check_contact(people_name)
									contact_id = people_info["data"]
									breaker = True
									break
								else:
									if people_info["des"] is not None and ("message" in people_info["des"].lower() or "connect" in people_info["des"].lower()):
										continue
									else:
										driver.get(people_link)
										time.sleep(6)
										contact_id = people_info["data"]
										if(lead_info["data"] == ""):
											hirer_detail = driver.find_element(By.CLASS_NAME,"AbrjnZkFZdsBACByvMYEeLvfAMdGxUSUtjY")
											hirer_detail_button = hirer_detail.find_element(By.CLASS_NAME,"artdeco-button--primary")
											text_hirer_button = hirer_detail_button.find_element(By.CLASS_NAME,"artdeco-button__text").text
											driver.implicitly_wait(3)
											if (text_hirer_button == "Connect"):
												hirer_detail_button.click()
												z = random.randint(4,7)
												time.sleep(z)
												hirer_connect_modal = driver.find_element(By.CLASS_NAME,"send-invite")
												hirer_connect_request_buttons = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-modal__actionbar")
												if(hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")):
													hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")
													hirer_connect_request_button.click()
													driver.implicitly_wait(10)
													connect_mess_modal = driver.find_element(By.CLASS_NAME,"send-invite")
													connect_mess_area = connect_mess_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
													connect_mess_area.clear()
													driver.implicitly_wait(5)
													connect_mess_area.send_keys("Dear " + people_name_first_name +", we are Fitech founded since 2007. If you are looking for tech partners who can collaborate to develop your solutions in various domains and knowledges about fintech, stock market, banking, payment gateway and e-commerce we believe that our good teams would help.")
													z = random.randint(2,7)
													time.sleep(z)
													connect_button = connect_mess_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
													if(connect_button.is_enabled()):
														z = random.randint(2,4)
														time.sleep(z)
														connect_button.click() 
														request_note_str = request_note_str + "\nconnect request sent by " + linkedin_acc
														mess_sent = "message sent by AdminAccount"
														time.sleep(2)
												else:
													hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--primary")
													if(hirer_connect_request_button.is_enabled()):
														z = random.randint(2,4)
														time.sleep(z)
														hirer_connect_request_button.click()	
														request_note_str = request_note_str + "\nconnect request sent by " + linkedin_acc
														mess_sent = "message sent by AdminAccount"
														time.sleep(2)
											else:
												try:
													if(text_hirer_button != "Pending"):
														hirer_more_dropdown = hirer_detail.find_element(By.CLASS_NAME,"artdeco-dropdown")
														hirer_more_button = hirer_more_dropdown.find_element(By.CLASS_NAME, "artdeco-button")
														driver.implicitly_wait(5)
														hirer_more_button.click()
														driver.implicitly_wait(5)
														hirer_more_option = hirer_more_dropdown.find_element(By.CLASS_NAME,"artdeco-dropdown__content-inner")
														hirer_more_option_ul = hirer_more_option.find_element(By.TAG_NAME,"ul")
														hirer_more_option_li = hirer_more_option_ul.find_elements(By.TAG_NAME,"li")
														for option_li in hirer_more_option_li:
															try:
																option_li_div = option_li.find_element(By.CLASS_NAME,"artdeco-dropdown__item")
																driver.implicitly_wait(3)
																option_li_text = option_li_div.find_element(By.TAG_NAME,"span").text
																if(option_li_text == "Connect"):
																	option_li.click()
																	z = random.randint(3,5)
																	time.sleep(z)	
																	hirer_connect_modal = driver.find_element(By.CLASS_NAME,"send-invite")
																	hirer_connect_request_buttons = hirer_connect_modal.find_element(By.CLASS_NAME,"artdeco-modal__actionbar")
																	if(hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")):
																		hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--secondary")
																		hirer_connect_request_button.click()
																		driver.implicitly_wait(10)
																		connect_mess_modal = driver.find_element(By.CLASS_NAME,"send-invite")
																		connect_mess_area = connect_mess_modal.find_element(By.CLASS_NAME,"connect-button-send-invite__custom-message")
																		connect_mess_area.clear()
																		driver.implicitly_wait(5)
																		#connect_mess_area.send_keys("We are Fitech founded in 2007. If you are looking for tech partners to develop your solutions in various domains including fintech, stock market, banking and payment gateway, our good team would help.")
																		connect_mess_area.send_keys("Dear " + people_name_first_name +", we are Fitech founded since 2007. If you are looking for tech partners who can collaborate to develop your solutions in various domains and knowledges about fintech, stock market, banking, payment gateway and e-commerce we believe that our good teams would help.")
																		z = random.randint(3,9)
																		time.sleep(z)
																		connect_button = connect_mess_modal.find_element(By.CLASS_NAME,"artdeco-button--primary")
																		if(connect_button.is_enabled()):
																			z = random.randint(2,4)
																			time.sleep(z)
																			connect_button.click() 
																			request_note_str = request_note_str + "\nconnect request sent by" + linkedin_acc
																			mess_sent = "message sent by AdminAccount"
																			time.sleep(2)
																	else:
																		hirer_connect_request_button = hirer_connect_request_buttons.find_element(By.CLASS_NAME,"artdeco-button--primary")
																		if(hirer_connect_request_button.is_enabled()):
																			z = random.randint(2,4)
																			time.sleep(z)
																			hirer_connect_request_button.click()
																			request_note_str = request_note_str + "\nconnect request sent by " + linkedin_acc
																			mess_sent = "message sent by AdminAccount"
																			time.sleep(2)
															except Exception as error:
																print("\n Connect sent to people 3: ", error)
																continue
												except Exception as error:
													print("\n Connect sent to people 4: ", error)
													continue
										breaker = True
										edit_contact(access_token = access_token, contact_id = people_info["data"] , title = hirer_title, name = hirer_name, email = hirer_email, phone= hirer_phone, des = request_note_str, link = contact_info_link, account_id= company_id)
										break
					except Exception as error:
						print("Seventh ex: ", error)
						continue
				else:
					break
	except Exception as error:
		print("\nCan't found ", error)       
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
	elif (country == "New Zealand"):
		if (hirer_phone.startswith('0') or hirer_phone.startswith("(0")):			
			hirer_phone = hirer_phone.replace('0','+64',1)
		if(hirer_phone.startswith(("1","2","3","4","5","6","7","8","9")) ):
			hirer_phone = "+64" + hirer_phone
	else:
		print("Not interested country")
	hirer_phone.replace("-","")
	email_info = ""
	full_content = ""
	if(hirer_email != ""):
		email_info = hirer_email
		full_content = '\n Email được lấy từ trang cá nhân nhà tuyển dụng.'
	else:
		if (job_emails and len(job_emails) > 0 and "accommodation" not in job_emails[0].lower()):
			email_info = job_emails[0]
			full_content = '\n Email được lấy từ job description.'
	if("gov" in email_info.lower() or "edu" in email_info.lower()):
		if(hirer_name != "" and contact_new_tab == 1):
			driver.switch_to.window(contact_window)
			driver.close()#2 close  company_window
			time.sleep(1)	
		driver.switch_to.window(job_detail_window)
		driver.close()#1 close  job_detail_window
		time.sleep(1)
		driver.switch_to.window(root_window)
		return
	email_expired = check_email_expired(email_info)
	lead_status_with_email = check_lead_status_with_email(email_info)
	maylaysia_phone_valid = "123456789"
	if (job_phones and len(job_phones) > 0):
		job_phone = job_phones[0]
		if(country == "Australia"):
			if (job_phone.startswith('0') or job_phone.startswith("0")):			
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
		elif (country == "New Zealand"):
			if (job_phone.startswith('0') or job_phone.startswith("(0")):			
				job_phone = job_phone.replace('0','+64',1)
			if(job_phone.startswith(("1","2","3","4","5","6","7","8","9")) ):
				job_phone = "+64" + job_phone
		else:
			print("Not interested country")
		job_phone.replace("-","")
	#2 company screen
	try:
		website_company = ""
		phone_company = ""
		message_company_sent = ""
		message_sent_to_company = 0
		if(hirer_name == ""):
			driver.switch_to.window(company_people_window)
			z = random.randint(5,7)
			time.sleep(z) 
			if(driver.find_element(By.CLASS_NAME,"org-page-navigation__items")):
				page_navigation_items = driver.find_element(By.CLASS_NAME,"org-page-navigation__items")
				page_navigation_option_li = page_navigation_items.find_elements(By.CLASS_NAME,"org-page-navigation__item")
				for option_li in page_navigation_option_li:
					button_content = option_li.find_element(By.TAG_NAME,"a")
					if(button_content.text == "About"):
						option_li.click() 
						time.sleep(6)
						break
		else:
			driver.switch_to.window(job_detail_window)
			z = random.randint(5,7)
			time.sleep(z)
			if(company_url != "" and "unavailable" not in company_url):
				driver.execute_script("window.open('');")
				if(contact_new_tab == 0): 
					company_window = driver.window_handles[2]
				else:
					company_window = driver.window_handles[3]
			driver.switch_to.window(company_window)
			time.sleep(2)
			company_about_url = "/about".join(company_url.rsplit("/life", 1))
			driver.get(company_about_url)
			driver.implicitly_wait(10)
		
		full_content =full_content + "\n Link giới thiệu:" + company_about_url

		wrap_section = driver.find_element(By.CLASS_NAME,"org-grid__content-height-enforcer")
		dds = wrap_section.find_elements(By.TAG_NAME,"dd")
	
		index = 0
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
		elif (country == "New Zealand"):
			if (phone_company.startswith('0') or phone_company.startswith("(0")):			
				phone_company = phone_company.replace('0','+64',1)
			if(phone_company.startswith(("1","2","3","4","5","6","7","8","9")) ):
				phone_company = "+64" + phone_company
		else:
			print("Not interested country")
		phone_company.replace("-","")
		if(company_info["des"] is not None and "message" in company_info["des"].lower()):
			message_company_sent = company_info["des"]
			message_sent_to_company = 1
		if(hirer_email == "" and (request_note_str is None or "message" not in request_note_str.lower()) and (contact_info["des"] is None or "message" not in contact_info["des"].lower()) and (request_note_str is None or "connect" not in request_note_str.lower()) and (contact_info["des"] is None or "connect" not in contact_info["des"].lower()) and "message" not in message_company_sent):
			try:
				driver.get(company_about_url)
				driver.implicitly_wait(10)
				account_actions = driver.find_element(By.CLASS_NAME,"org-top-card-primary-actions__inner")
				message_button = account_actions.find_element(By.CLASS_NAME,"artdeco-button--secondary")
				text_message_button = message_button.find_element(By.CLASS_NAME,"artdeco-button__text").text
				message_to_page_count = getAccountSentMessageToday()
				# if(message_to_page_count <= 40 and text_message_button.lower() == "message"):
				# 	message_button.click()
				# 	driver.implicitly_wait(10)
				# 	select_actions = driver.find_element(By.ID,"msg-shared-modals-msg-page-modal-presenter-conversation-topic")
				# 	select_list = Select(select_actions)
				# 	select_list.select_by_visible_text('Careers')
				# 	mess_text_area = driver.find_element(By.ID,"org-message-page-modal-message")
				# 	mess_text_area.clear()
				# 	z = random.randint(3,7)
				# 	time.sleep(z)
				# 	mess_text_area.send_keys("Dear Sir/Madam, we are from Fitech founded since 2007, where we have some software solutions in various domains and knowledges about fintech, stock market, banking, payment gateway and e-commerce. If you are looking for partners who can collaborate with your company to develop such a solution we believe that our good teams would help. If you are interested we can setup a meeting call to introduce more about capabilities and opportunities working together. Thank you! \n \n" + linkedin_acc)
				# 	send_button = driver.find_element(By.CLASS_NAME,"artdeco-button--primary")
				# 	if(send_button.is_enabled()):
				# 		z = random.randint(2,4)
				# 		time.sleep(z)
				# 		send_button.click()  
				# 		message_company_sent = "message by " + linkedin_acc
				# 		mess_sent = "message sent by AdminAccount"
				# 		time.sleep(1)
			except :
				print("not found message area for company")
				pass
		full_content = '\n Link tuyển dụng: '.join([full_content, job_detail_url])
		if((request_note_str is not None and "message" in request_note_str.lower()) or (contact_info["des"] is not None and "message" in contact_info["des"].lower())):
			full_content = '\n Đã gửi tin nhắn đến: '.join([full_content, hirer_link])
		if((request_note_str is not None and "connect" in request_note_str.lower()) or (contact_info["des"] is not None and "connect" in contact_info["des"].lower())):
			full_content = '\n Đã gửi connect request đến: '.join([full_content, hirer_link])
   
		if(hirer_link != ""):
			full_content = '\n Trang cá nhân nhà tuyển dụng: '.join([full_content, hirer_link])
		time.sleep(2)	
		last_time = datetime(2023, 1 , 1)
		lead_status = "New"
		if(request_note_str is not None and request_note_str != "" and hirer_name != ""):
			lead_status = "Recycled"
			mess_sent = "message sent by AdminAccount"
		# if(hirer_profile == "" and email_info == "" and hirer_website == "" and phone_company == "" and hirer_name == "" and hirer_phone == "" and job_phone == "" and request_note_str != ""):
		# 	lead_status = "Recycled"		
		website = website_company
		if(hirer_website != ""):
			website = hirer_website

		if(company_id == ""):
			print("\n\nStarting add new account:......\n\n")
			add_new_account(access_token = access_token, name = company_name, phone = phone_company, website = website_company + "\n" + company_about_url, address = address, des = message_company_sent)
			company_info = check_company_existed(company_name)
			company_id = company_info["data"]
		else:
			print("\n\nStarting editing account:......\n\n")
			edit_account(access_token = access_token, account_id = company_id ,name = company_name, phone = phone_company, website = website_company + "\n" + company_about_url, address = address, des = message_company_sent)
		# if(message_company_sent != "" and message_sent_to_company == 1 ):
		# 	lead_status = "Recycled"
		lower_title = current_job_title.lower()
		if("consultant" in lower_title or  "support" in lower_title or "admin" in lower_title or "manager" in lower_title or "analyst" in lower_title or "intern" in lower_title or "lecturer" in lower_title or "tutor" in lower_title or "assistant" in lower_title or "graphic" in lower_title or "design" in lower_title or "supervisor" in lower_title or "investors" in lower_title or "test" in lower_title or "design" in lower_title or "analyst" in lower_title or "specialist" in lower_title or "sales" in lower_title or "student" in lower_title or "purchasing" in lower_title):
			print("Job not suitable")
		else:
			assigned_user_id = ""
			if(hirer_name != ""):
				assigned_user_id = get_contact_assigned_user(hirer_name)
			else:
				#assigned_user_id = get_account_assigned_user(company_name)
				assigned_user_id = get_account_email_assigned_user(company_name,email_info)
			if((message_company_sent != "" or (hirer_name == "" and request_note_str != "")) and assigned_user_id == ""):
				assigned_user_id = "62b60dd0-9ab9-735e-e291-65d2cd0ab68e"
			lead_id = lead_info["data"]
			if (lead_id == ""):
				print("\n\nStarting add new:......\n\n")
				time.sleep(2)
				# if(lead_status == "Recycled" or assigned_user_id == "d6ea87ac-8c7e-a4ed-ba81-65f500a98e58"):
				# 	assigned_user_id = ""
				if(email_expired > 0):
					assigned_user_id = "d6ea87ac-8c7e-a4ed-ba81-65f500a98e58"
					lead_status = "Recycled"
				if(lead_status_with_email > 0):
					lead_status = "Recycled"
					if(assigned_user_id != "62b60dd0-9ab9-735e-e291-65d2cd0ab68e"):
						assigned_user_id = ""
				if(request_note_str != ""):
					assigned_user_id = "1"
				if(lead_status == "New" and assigned_user_id == "1"):
					assigned_user_id = ""
				if(assigned_user_id == "d6ea87ac-8c7e-a4ed-ba81-65f500a98e58"):
					lead_status = "Recycled"
				if(assigned_user_id == "9d80c69a-3bcf-4005-245b-659379197a46"):
					assigned_user_id = ""
				add_new_lead(access_token=access_token,job_id = job_id, company_name=company_name, company_id = company_id,title=current_job_title,address=address,other_address=other_address,phone_company=phone_company,hirer_phone = hirer_phone,hirer_email = email_info,website=website,content=full_content,assigned_user_id=assigned_user_id, lead_status = lead_status, job_phone = job_phone, hirer_name = hirer_name, refer= "", contact_id = contact_id, status_des = mess_sent)
			else:					
				if(lead_info["status"] == "Recycled" and lead_status == "Recycled"):
					lead_status = "Recycled"	
				isEdit = 1
				isMailInclude = 0
				lead_email_list = check_email_lead(lead_id)
				for lead_email in lead_email_list["email_list"]:
					if(email_info == lead_email):
						isMailInclude = 1
						break
				if(email_info == ""):
					isMailInclude = 1
				if(lead_info["phone_work"] == phone_company and lead_info["phone_mobile"] == hirer_phone and lead_info["phone_other"] == job_phone and isMailInclude == 1):
					isEdit = 0
				if(lead_info["status"] != "Assigned" and lead_info["status"] != "Converted" and lead_info["status"] != "In Process" and lead_info["status"] != "Dead" and lead_info["status"] != "Response" and isEdit == 1):
					print("\n\nStarting edit:......\n\n")	
					if(lead_status == "New" and assigned_user_id == "1"):
						assigned_user_id = ""
					if(lead_info["assigned_user"] != ""):
						assigned_user_id = lead_info["assigned_user"]
					if(email_expired > 0):
						assigned_user_id = "d6ea87ac-8c7e-a4ed-ba81-65f500a98e58"
						lead_status = "Recycled"
					if(assigned_user_id == "d6ea87ac-8c7e-a4ed-ba81-65f500a98e58"  or "sent" in lead_info["desc"]):
						lead_status = "Recycled"
					if(assigned_user_id == "9d80c69a-3bcf-4005-245b-659379197a46"):
						assigned_user_id = ""
					edit_new_lead(access_token=access_token,lead_id =lead_id,job_id=job_id,company_name=company_name,company_id = company_id,title= current_job_title,address=address,other_address=other_address,phone_company=phone_company,hirer_phone = hirer_phone, hirer_email = email_info,website=website,content=full_content, lead_status = lead_status, job_phone = job_phone, assigned_user_id = assigned_user_id, hirer_name = hirer_name, refer= "", contact_id = contact_id, status_des= mess_sent)
		if(hirer_name == ""):
			driver.switch_to.window(company_people_window)
			driver.close()
			time.sleep(1)
		else:			
			driver.switch_to.window(company_window)
			driver.close()#2 close  company_window
			time.sleep(1)
			if(contact_new_tab == 1):
				driver.switch_to.window(contact_window)
				driver.close()#2 close  company_window
				time.sleep(1)
		driver.switch_to.window(job_detail_window)
		driver.close()#1 close  job_detail_window
		time.sleep(1)

		driver.switch_to.window(root_window)
		z = random.randint(2,7)
		time.sleep(z)
	except Exception as error:
		print("An exception occurred:", error)
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

# -*- coding: utf-8 -*-
def isEnglish(s):
	try:
		s.encode(encoding='utf-8').encode('ascii')
	except UnicodeEncodeError:
		return False
	else:
		return True