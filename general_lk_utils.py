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
        print('fail')
        print(data.status_code)
        print(data.reason)
    else:
        print('done')
        json_object = data.json()
        return json_object["access_token"]

def check_lead_existed(access_token,name):
    headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
    check_api = "https://crm.fitech.com.vn/Api/V8/module/Leads?fields=name&page[size]=100000&page[number]=1"
    data = requests.get(check_api,headers=headers)
    if data.status_code != 200:
        print('fail')
        print(data.status_code)
        print(data.reason)
    else:
        print('done')
        json_object = data.json()
        print(json_object)

def add_new_lead(access_token,company_name,title,address,content):
    headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
    module_api = "https://crm.fitech.com.vn/Api/V8/module"
    jsondata =  {
    "data": {
     "type": "Leads",
     "attributes": {
         "title": title,
         "last_name": company_name,
         "description": content
     }
    }
    }
    
    print(jsondata)
    time.sleep(10)
    data = requests.post(module_api,json=jsondata,headers=headers)
    if data.status_code != 200:
        print('fail')
        print(data.status_code)
        print(data.reason)
    else:
        print('done')
        json_object = data.json()
        print(json_object)
    

def add_new_task(access_token,company_name,content):
    #POST {{suitecrm.url}}/Api/V8/module
    headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
    module_api = "https://crm.fitech.com.vn/Api/V8/module"
    
    jsondata =  {
    "data": {
     "type": "Tasks",
     "attributes": {
         "name": company_name,
         "description": content
     }
    }
    }
    
    print(jsondata)
    time.sleep(10)
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

    time.sleep(3)
    job_detail_url = 'https://www.linkedin.com/jobs/view/' + job_id
    print(job_detail_url)
    driver.get(job_detail_url)
    time.sleep(3)
    
    current_job_title = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__job-title").text
    print(current_job_title)
    
    infos_list = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__primary-description-without-tagline")
    company_url = infos_list.find_element(By.CSS_SELECTOR,"a").get_attribute("href")
    company_name = infos_list.find_element(By.CSS_SELECTOR,"a").text
    real_company_url =  "org-top-card-primary-actions__action"
    
    print("Company URL: " + company_url)
    time.sleep(3)

    job_des = driver.find_element(By.ID,"job-details").text
    print("Job Des: " + job_des)
    time.sleep(3)

    #company screen
    driver.execute_script("window.open('');")
    company_window = driver.window_handles[2]
    driver.switch_to.window(company_window)
    
    full_content = ""

    company_about_url = company_url.replace("/life", "/about")
    full_content = '\n'.join([full_content, company_about_url])
    full_content = '\n'.join([full_content, "Job đang tuyển dụng: " + current_job_title])

    driver.get(company_about_url)
    time.sleep(3)
        
    text_bodys = driver.find_elements(By.CLASS_NAME,"text-body-medium")
    address = driver.find_elements(By.CLASS_NAME,"org-top-card-summary-info-list__info-item")
    index = 0
    
    for text in text_bodys:
        time.sleep(2)
        sub_content = str(index) + ": " +  text.text 
        full_content = '\n'.join([full_content, sub_content])
        index = index + 1
            
    
    
    full_content = '\n'.join([full_content, job_des])

    time.sleep(5)
    
    # driver.execute_script("window.open('');")
    # jobs_company_window = driver.window_handles[3]
    # driver.switch_to.window(jobs_company_window)
    # jobs_company_url = company_url.replace("/life", "/jobs")
    # driver.get(jobs_company_url)
    # time.sleep(3)
    # show_all_button = driver.find_element(By.CLASS_NAME,"link-without-hover-visited")
    # show_all_button.click()
    # time.sleep(3)
    
    #add task
    #check_lead_existed(access_token=access_token,name="tiktok")
    time.sleep(20)
    add_new_lead(access_token=access_token,company_name=company_name,title= current_job_title,address=address,content=full_content)

    #get list jobs
    # jobs = driver.find_elements(By.CLASS_NAME,"job-card-container__link")
    # print("Please Zoom in then press Enter")
    # count = len(jobs)
    # #input()
    # print(count)
    
    # for job in jobs:
    #     time.sleep(3)
    #     try:
    #         job_title = job.text
    #         print(job_title)
    #     except Exception:
    #         print(Exception)
        
    # driver.close()#close  jobs_company_window
    # time.sleep(2)
    #driver.switch_to.window(company_window)
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
