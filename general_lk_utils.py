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
from datetime import datetime
from datetime import date
import random
import json
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import requests
from configparser import ConfigParser
import psycopg2
import validators
import phonenumbers

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
    
    
def check_lead_existed(name):
    headers = {'Content-Type': "application/json", 'Accept': "application/json"}
    check_api = "http://68.183.189.171:9999/leads/check"
    jsondata = {"name":name}
    print(jsondata)

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
     "type": "Account",
     "attributes": {
         "account_type": "Customer",
         "name": name,
         "phone_office": phone,
         "phone_alternate": phone,
         "website": website,
         "primary_address_country": address,
         "description": "content"
     }
    }
    }
    
    print(jsondata)
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
        
def add_new_lead(access_token,company_name,title,address,phone,website,content,assigned_user_id):
    headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
    module_api = "https://crm.fitech.com.vn/Api/V8/module"
    jsondata =  {
    "data": {
     "type": "Leads",
     "attributes": {
         "title": title,
         "last_name": company_name,
         "phone_mobile": phone,
         "phone_work": phone,
         "phone_home": phone,
         "phone_other": phone,
         "website": website,
         "account_name": company_name,
         "primary_address_country": address,
         "assigned_user_id": assigned_user_id,
         "description": content
     }
    }
    }
    
    print(jsondata)
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
        
def edit_new_lead(access_token,id,company_name,title,address,phone,website,content):
    headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
    module_api = "https://crm.fitech.com.vn/Api/V8/module"
    jsondata =  {
    "data": {
     "type": "Leads",
     "id": id,
     "attributes": {
         "title": title,
         "last_name": company_name,
         "phone_mobile": phone,
         "phone_work": phone,
         "phone_home": phone,
         "phone_other": phone,
         "website": website,
         "account_name": company_name,
         "primary_address_country": address,
         "description": content
     }
    }
    }
    
    print(jsondata)
    time.sleep(2)
    data = requests.patch(module_api,json=jsondata,headers=headers)
    if data.status_code != 200:
        print('fail')
    else:
        json_object = data.json()
        print(json_object)
    
def get_job_detail(driver,job_id,access_token,country):
    root_window = driver.window_handles[0]
    
    #job detail windo
    driver.execute_script("window.open('');")
    job_detail_window = driver.window_handles[1]
    driver.switch_to.window(job_detail_window)

    job_detail_url = 'https://www.linkedin.com/jobs/view/' + job_id
    print(job_detail_url)
    driver.get(job_detail_url)
    time.sleep(5)
    
    current_job_title = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__job-title").text    
    infos_element = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__primary-description-without-tagline")
    address_element = infos_element.find_elements(By.TAG_NAME,"span")[0]
    address = address_element.text
    print(address)

    company_element = infos_element.find_element(By.TAG_NAME,"a")
    
    if not company_element:
        print("company_url is empty")
    else:
        company_url = infos_element.find_element(By.CSS_SELECTOR,"a").get_attribute("href")
        company_name = company_element.text
    #job_des = driver.find_element(By.ID,"job-details").text

    #company screen
    driver.execute_script("window.open('');")
    company_window = driver.window_handles[2]
    driver.switch_to.window(company_window)
    time.sleep(5)

    company_about_url = company_url.replace("/life", "/about")
    driver.get(company_about_url)
    time.sleep(5)
    full_content = ""
    full_content = '\n Link giới thiệu:'.join([full_content, company_about_url])

    wrap_section = driver.find_element(By.CLASS_NAME,"org-grid__content-height-enforcer")
    dds = wrap_section.find_elements(By.TAG_NAME,"dd")
    
    index = 0
    website_company = ""
    phone_company = ""
    
    for dd in dds:
        print(dd.text)
        if(("http" in dd.text) or (".com" in dd.text) or ("www" in dd.text)):
            website_company = dd.text
        if("Phone number is" in dd.text):
            phone_company = dd.text.split("Phone number is")[0]
        index = index + 1
    input()
    
    
    # text_bodys = driver.find_elements(By.CLASS_NAME,"text-body-medium")
    # if len(text_bodys) > 1:
    #     address_element = driver.find_elements(By.CLASS_NAME,"org-top-card-summary-info-list__info-item")
    #     if (len(address_element) > 0 ):
    #         address = address_element[1].text
    #     else:
    #         address = country
    # print("Address:" + address)
    
    
    
    # for text in text_bodys:
    #     print(text.text)
    #     #sub_content = text.text
    #     #full_content = '\n'.join([full_content, sub_content[:350]])
    #     if(("http" in text.text) or (".com" in text.text) or ("www" in text.text)):
    #         website_company = text.text
    #     if("Phone number is" in text.text):
    #         phone_company = text.text.split("Phone number is")[0]
    #     index = index + 1
        
    #Get List Job:
    #https://www.linkedin.com/company/mindvalley/jobs/            
    #Jobs Company Screen
    driver.execute_script("window.open('');")
    jobs_window = driver.window_handles[3]
    driver.switch_to.window(jobs_window)
    
    jobs_list_company_url = company_url.replace("/life", "/jobs")

    driver.get(jobs_list_company_url)
    full_content = '\n Link danh sách công việc: '.join([full_content, jobs_list_company_url])
    time.sleep(5)
    #org-jobs-recently-posted-jobs-module__show-all-jobs-btn
    button_show_all_jobs = driver.find_element(By.CLASS_NAME,"org-jobs-recently-posted-jobs-module__show-all-jobs-btn")
    link_all_jobs = button_show_all_jobs.find_element(By.TAG_NAME,"a").get_attribute("href")
    print(link_all_jobs) 
    
    #Clone All Jobs
    driver.execute_script("window.open('');")
    list_jobs_detail_window = driver.window_handles[4]
    driver.switch_to.window(list_jobs_detail_window)
    driver.get(link_all_jobs)
    time.sleep(5)
    job_containers = driver.find_elements(By.CLASS_NAME,"jobs-search-results__list-item")
    count = len(job_containers)
    print("Total jobs:" + str(count))
    should_change_status = False
    last_time = datetime(2023, 1 , 1)
    for job_item in job_containers:
        full_content = '\n'.join([full_content, "#####"])
        sub_content = ""
        
        time_string = job_item.find_element(By.TAG_NAME,"time").get_attribute("datetime")
        datetime_object = datetime.strptime(time_string, '%Y-%m-%d') #2024-01-08
        if datetime_object > last_time:
            last_time = datetime_object
        sub_content = ''.join([sub_content, time_string.replace("\n","")])
        
        job_title = job_item.find_element(By.CLASS_NAME,"job-card-list__title").text
        sub_content = '\n'.join([sub_content, job_title])
        
        specific_address = job_item.find_element(By.CLASS_NAME,"job-card-container__metadata-item ").text
        sub_content = '\n'.join([sub_content, specific_address])

        job_url = job_item.find_element(By.CLASS_NAME,"job-card-container__link").get_attribute("href")
        sub_content = '\n'.join([sub_content, job_url])

        full_content = '\n'.join([full_content, sub_content])
    last_time_string = last_time.strftime("%Y-%m-%d")
    full_content = '\n'.join([full_content, "#####"])
    full_content = '\n'.join([full_content, last_time_string])
            
    lead_id = check_lead_existed(company_name)
    print("\nLead id:" + lead_id + "\n")
    if (lead_id == ""):
        print("\n\nStarting add new:......\n\n")
        assigned_user_id = get_min_sale()
        print("Assigned User Id:" + assigned_user_id)
        time.sleep(2)
        add_new_lead(access_token=access_token,company_name=company_name,title=current_job_title,address=address,phone=phone_company,website=website_company,content=full_content,assigned_user_id=assigned_user_id)
    else:
        print("\n\nStarting edit:......\n\n")
        edit_new_lead(access_token=access_token,id=lead_id,company_name=company_name,title= current_job_title,address=address,phone=phone_company,website=website_company,content=full_content)
    driver.close()#close  list_jobs_detail_window
    driver.switch_to.window(jobs_window)
    driver.close()#close  company_window
    driver.switch_to.window(job_detail_window)
    driver.close()#close  job_detail_window
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