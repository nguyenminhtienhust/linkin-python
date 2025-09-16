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
import os
import shutil
import json
import requests
import urllib.request
import time
import psycopg2
import pandas as pd
import random
from datetime import datetime
from datetime import date
# from fake_useragent import UserAgent


from utils import (
    get_lk_credentials,
    enter_ids_on_lk_signin,
    get_job_detail,
    login_crm,
    getAccountSentMessageToday,
    get_min_sale
)

LK_CREDENTIALS_PATH = "./credentials.json"

if __name__ == "__main__":
    # mess_count = getAccountSentMessageToday()
    # print("mess_count:",mess_count)

    # print("Starting Clone...")
    
    job_id = "4299274146"   #unavailable company page  4298900261
    logging.getLogger("selenium").setLevel(logging.CRITICAL)
    # ua = UserAgent(browsers='Chrome',os='Windows',platforms='desktop')
    #ua = UserAgent()
    # user_agent = ua.random
    #user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    # chrome_options.add_argument(f'--user-agent={user_agent}')
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])
    # chrome_options.add_argument("window-size=1380,800")
    cService = webdriver.ChromeService(executable_path='C:\Workspace\CRMFitech\ChromeDriver\chromedriver.exe')
    
    driver = webdriver.Chrome(service = cService, options=chrome_options)
    # fire_options = webdriver.FirefoxOptions()
    # cService = webdriver.ChromeService(executable_path='C:\Workspace\CRMFitech\WebDriver\geckodriver.exe')
    # driver = webdriver.Firefox(service = cService, options=fire_options)
    driver.maximize_window()
    driver.get("https://www.linkedin.com/login/")
    
    print("Inputting the credentials...")
    lk_credentials = get_lk_credentials(LK_CREDENTIALS_PATH)
    enter_ids_on_lk_signin(driver, lk_credentials["email"], lk_credentials["password"])

    if "checkpoint/challenge" in driver.current_url:
        print(
            "It looks like you need to complete a double factor authentification. Please do so and press enter when you are done."
        )
        input()


    access_token = login_crm()
    # lead_list = get_num_mess_sent_lead(access_token)
    # print(len(lead_list))
    get_job_detail(driver,job_id,access_token, "Prague, Czechia", "European Union", "Huong Nguyen")
