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

def check_lead_existed(name):
    headers = {'Content-Type': "application/json", 'Accept': "application/json"}
    check_api = "http://68.183.189.171:8080/leads/check"
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

def add_new_lead(access_token,company_name,title,address,phone,website,content):
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
         "primary_address_country": address,
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
        
def get_job_detail(driver,job_id,access_token):
    root_window = driver.window_handles[0]
    driver.execute_script("window.open('');")
    job_detail_window = driver.window_handles[1]
    driver.switch_to.window(job_detail_window)

    job_detail_url = 'https://www.linkedin.com/jobs/view/' + job_id
    print(job_detail_url)
    driver.get(job_detail_url)
    time.sleep(5)
    
    current_job_title = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__job-title").text    
    infos_list = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__primary-description-without-tagline")
    company_url = infos_list.find_element(By.CSS_SELECTOR,"a").get_attribute("href")
    company_name = infos_list.find_element(By.CSS_SELECTOR,"a").text
    if(check_lead_existed(company_name)):
        print("Leads đã tồn tại. Bỏ qua....")
        driver.close()#close  job_detail_window
        driver.switch_to.window(root_window)
        return

    job_des = driver.find_element(By.ID,"job-details").text

    #company screen
    driver.execute_script("window.open('');")
    company_window = driver.window_handles[2]
    driver.switch_to.window(company_window)
    time.sleep(5)
    full_content = ""

    company_about_url = company_url.replace("/life", "/about")
    full_content = '\n'.join([full_content, company_about_url])
    full_content = '\n'.join([full_content, "\nJob đang tuyển dụng: " + current_job_title])
    full_content = '\n'.join([full_content, job_detail_url + "\n"])

    driver.get(company_about_url)
    time.sleep(5)
        
    text_bodys = driver.find_elements(By.CLASS_NAME,"text-body-medium")
    address = driver.find_elements(By.CLASS_NAME,"org-top-card-summary-info-list__info-item")[1].text
    print("Address:" + address)
    
    index = 0
    website_company = ""
    phone_company = ""
    
    for text in text_bodys:
        print(text.text)
        sub_content = text.text
        full_content = '\n'.join([full_content, sub_content[:350]])
        if(("http" in text.text) or (".com" in text.text) or ("www" in text.text)):
            website_company = text.text
        if("Phone number is" in text.text):
            phone_company = text.text.split("Phone number is")[0]
        index = index + 1
                
    add_new_lead(access_token=access_token,company_name=company_name,title= current_job_title,address=address,phone=phone_company,website=website_company,content=full_content)

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