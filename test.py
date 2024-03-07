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


from utilsTest import (
    get_lk_credentials,
    enter_ids_on_lk_signin,
    get_job_detail,
    login_crm,
    test
)

LK_CREDENTIALS_PATH = "./credentials.json"

if __name__ == "__main__":

    print("Starting Clone...")
    
    job_id = "3783887454"   #3817294045 : job_id with strong style foe email
    logging.getLogger("selenium").setLevel(logging.CRITICAL)
    driver = webdriver.Chrome(options=Options())
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


    print("Starting the scraping...")

    #await driver.wait(until.elementLocated(By.className('link')), 1000);

    access_token = login_crm()
    test(driver,job_id,access_token,"Malaysia")
