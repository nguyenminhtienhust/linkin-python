"""
This is meant to be run as a CLI script.
It will scrap the search results of a LinkedIn Sales Navigator search.

Example usage:
python lksn_search_scraper.py --search-url "https://www.linkedin.com/sales/search/people?query=(spellCorrectionEnabled%3Atrue%2Ckeywords%3Ascraping)"
"""
import argparse
import os
import logging
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.firefox.options import Options
#from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
import shutil
import json
import requests
import urllib.request
import psycopg2
import pandas as pd
import random
from selenium.common.exceptions import NoSuchElementException

from utils import (
    get_lk_credentials,
    enter_ids_on_lk_signin,
    get_job_detail,
    login_crm
)

SCROLL_TO_BOTTOM_COMMAND = (
    "document.getElementById('search-results-container').scrollTop+=100000;"
)
LK_CREDENTIALS_PATH = "./credentials.json"


def get_name_info_from_result_el(result_el):
    selector = "div > div > div.flex.justify-space-between.full-width > div.flex.flex-column > div.mb3 > div > div.artdeco-entity-lockup__content.ember-view > div.flex.flex-wrap.align-items-center > div.artdeco-entity-lockup__title.ember-view > a"
    els = result_el.select(selector)
    link_to_profile = ""
    name = ""
    if len(els) > 0:
        link_to_profile = els[0]["href"]
        el_contents = els[0].contents
        if len(el_contents) > 0:
            name = el_contents[0].strip()
    return {"name": name, "link_to_profile": link_to_profile}


def get_connection_level_info_from_result_el(result_el):
    selector = "div > div > div.flex.justify-space-between.full-width > div.flex.flex-column > div.mb3 > div > div.artdeco-entity-lockup__content.ember-view > div.flex.flex-wrap.align-items-center > div.artdeco-entity-lockup__badge.ember-view.ml1 > span.artdeco-entity-lockup__degree"
    els = result_el.select(selector)
    connection_level = ""
    if len(els) > 0:
        link_to_profile = els[0]
        el_contents = els[0].contents
        if len(el_contents) > 0:
            connection_level = el_contents[0].strip().replace("·\xa0", "")
    return {"connection_level": connection_level}


def get_search_url(search_url_base, page=1):
    url = search_url_base + f"&page={page}"
    return url


def get_linkedin_premium_info_from_result_el(result_el):
    selector = "div > div > div.flex.justify-space-between.full-width > div.flex.flex-column > div.mb3 > div > div.artdeco-entity-lockup__content.ember-view > div.inline-flex > div > li-icon"
    els = result_el.select(selector)
    has_linkedin_premium = False
    if len(els) > 0:
        has_linkedin_premium = True
    return {"has_linkedin_premium": has_linkedin_premium}


def get_role_info_from_result_el(result_el):
    selector = "div > div > div.flex.justify-space-between.full-width > div.flex.flex-column > div.mb3 > div > div.artdeco-entity-lockup__content.ember-view > div.artdeco-entity-lockup__subtitle.ember-view.t-14 > span"
    els = result_el.select(selector)
    role_name = ""
    if len(els) > 0:
        el_contents = els[0].contents

        if len(el_contents) > 0:
            role_name = el_contents[0].strip()
    return {"role_name": role_name}


def get_company_info_from_result_el(result_el):
    selector = "div > div > div.flex.justify-space-between.full-width > div.flex.flex-column > div.mb3 > div > div.artdeco-entity-lockup__content.ember-view > div.artdeco-entity-lockup__subtitle.ember-view.t-14 > a"
    els = result_el.select(selector)
    link_to_company = ""
    company_name = ""
    if len(els) > 0:
        link_to_company = els[0]["href"]
        el_contents = els[0].contents
        if len(el_contents) > 0:
            company_name = el_contents[0].strip()
    return {"link_to_company": link_to_company, "company_name": company_name}


def get_time_in_company_info_from_result_el(result_el):
    selector = "div > div > div.flex.justify-space-between.full-width > div.flex.flex-column > div.mb3 > div > div.artdeco-entity-lockup__content.ember-view > div.artdeco-entity-lockup__metadata.ember-view"
    els = result_el.select(selector)
    time_in_company = ""
    if len(els) > 0:
        el_contents = els[0].contents
        if len(el_contents) > 0:
            time_in_company = " | ".join(
                [
                    el_contents[i].strip().replace("\xa0", " ")
                    for i in range(len(el_contents))
                    if "<span" not in str(el_contents[i])
                ]
            )
    return {"time_in_company": time_in_company}


def get_additional_info_from_result_el(result_el):
    selector = "div > div > div.flex.justify-space-between.full-width > div.flex.flex-column > div.ml8.pl1 > dl > div > dd > div > span"
    els = result_el.select(selector)
    additional_info = ""
    if len(els) > 1:
        el_contents = els[1].contents
        if len(el_contents) > 0:
            additional_info = " | ".join(
                [
                    el_contents[i].strip().replace("\xa0", " ")
                    for i in range(len(el_contents))
                    if "<span" not in str(el_contents[i])
                    and "<button" not in str(el_contents[i])
                ]
            )
    return {"additional_info": additional_info}


def get_info_from_result_el(result_el):
    r = []
    r.append(get_name_info_from_result_el(result_el))
    r.append(get_connection_level_info_from_result_el(result_el))
    r.append(get_linkedin_premium_info_from_result_el(result_el))
    r.append(get_role_info_from_result_el(result_el))
    r.append(get_company_info_from_result_el(result_el))
    r.append(get_time_in_company_info_from_result_el(result_el))
    r.append(get_additional_info_from_result_el(result_el))

    info = {}

    for obj in r:
        for k in obj.keys():
            info[k] = obj[k]

    info["time_scraped"] = int(time.time() * 1000)
    return info


def get_result_els(page_source):
    soup = BeautifulSoup(page_source, "html.parser")
    full_results_selector = "#search-results-container > div > ol > li"
    all_results_el = soup.select(full_results_selector)
    return all_results_el


def get_all_info_from_page_source(page_source):
    print("Getting all result elements...")
    result_els = get_result_els(page_source)
    n = len(result_els)
    print(f"Found {n} elements.")

    print("Getting the info for all elements...")
    infos = []
    for i in tqdm(range(n)):
        new_info = get_info_from_result_el(result_els[i])
        infos.append(new_info)
    return infos


def get_all_info_from_search_url(
    driver, url, wait_after_page_loaded=3, wait_after_scroll_down=2
):
    driver.get(url)
    print(f"Waiting for {wait_after_page_loaded}s...")
    time.sleep(wait_after_page_loaded)

    # Chrome must be unzoomed so that the whole page fits in the screen in 2 times
    try:
        driver.execute_script(SCROLL_TO_BOTTOM_COMMAND)
    except:
        print("There was an error scrolling down")
    print(f"Waiting for {wait_after_scroll_down}s...")
    time.sleep(wait_after_scroll_down)
    page_source = driver.page_source
    page_parsed_info = get_all_info_from_page_source(page_source)
    return page_parsed_info


def scrap_lksn_pages(
    driver,
    page_list,
    get_search_url,
    wait_time_between_pages=3,
    wait_after_page_loaded=3,
    wait_after_scroll_down=2,
):
    total_info = []
    for p in page_list:
        print(f"Waiting for {wait_time_between_pages}s...")
        time.sleep(wait_time_between_pages)

        print(f"Getting new page: {p}.")
        info = get_all_info_from_search_url(
            driver,
            get_search_url(p),
            wait_after_page_loaded=wait_after_page_loaded,
            wait_after_scroll_down=wait_after_scroll_down,
        )
        total_info += info
    return total_info
            
if __name__ == "__main__":
    home_url = "https://www.linkedin.com/jobs/search"
    print("Starting Clone...")
    
    # jobs_names = ["Android","ios","Objective C","kotlin developer","Flutter","Dart developer",
    #               "React Native","Mobile Application",".Net","Java","C language",
    #               "Python","C++","Php","ReactJS","NextJS",
    #               "AngularJS","VueJS  developer","Django","Golang", "Swift Developer","Fullstack Engineer",
    #               "Remote developer","Software Architect","AWS developer","Azure developer","DevOps","NodeJS",
    #               "Database","Oracle Database"]
    jobs_names = ["Android","ios","Objective C","kotlin developer","Flutter","Dart developer",
                  "React Native","Mobile Application",".Net","Java developer","C language",
                  "Python","C++","Php","ReactJS","NextJS",
                  "AngularJS","VueJS  developer","Django","Golang", "Swift Developer", "Azure developer","NodeJS",
                  "Database","Oracle Database"]
    #job_name = jobs_names[6]
    job_name = "React Native"
    print("Job: " + job_name)
    
    #countries = ["Singapore","New Zealand","Thailand","Australia","Malaysia"]
    countries = ["Australia","New Zealand","Germany","European Union","United Kingdom","United States","Malaysia","Thailand", "Singapore"]
    #country = countries[2]
    #print("Country: " + country)
    
    logging.getLogger("selenium").setLevel(logging.CRITICAL)
    driver = webdriver.Chrome(options=Options())
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])
    cService = webdriver.ChromeService(executable_path='C:\Workspace\CRMFitech\WebDriver\chromedriver.exe')
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
    job_count = 0
    
    linkedin_acc = ""
    if(lk_credentials["email"] == "nguyenminhtiendeveloper@gmail.com"):
        linkedin_acc = "Minh Tien"
    if(lk_credentials["email"] == "huongnd@fitech.com.vn"):
        linkedin_acc = "Huong Nguyen"
    if(lk_credentials["email"] == "thuydtabc123@gmail.com"):
        linkedin_acc = "Thu Thuy"
    country_count = 1

    for country in countries:
        if(country_count > 1):
            x = random.randint(60,200)
            time.sleep(x)
        if(country_count == 1):
            driver.get(home_url)
            time.sleep(5)
        print("Starting the scraping...")
        print("Country: " + country)
        done = False
        while( done == False):
            try:
                titleInputElement = driver.find_element(By.CSS_SELECTOR,'[id*="jobs-search-box-keyword-id"]')
                titleInputElement.clear()
                time.sleep(2)
                titleInputElement.send_keys(job_name)
    
                locationInputElement = driver.find_element(By.CSS_SELECTOR, '[id*="jobs-search-box-location-id"]')
                locationInputElement.clear()
                time.sleep(2)
                locationInputElement.send_keys(country)
                
    
                searchButton = driver.find_element(By.CLASS_NAME,"jobs-search-box__submit-button")
                searchButton.click()
                searchButton.accessible_name
                time.sleep(5)

                page_indicators = driver.find_elements(By.CLASS_NAME,"artdeco-pagination__indicator--number")
                done = True
            except NoSuchElementException:
                continue
        #print("Please Zoom in then press Enter")
        #input()

        # SCROLL_PAUSE_TIME = 0.5

        # # Get scroll height
        # last_height = driver.execute_script("return document.body.scrollHeight")

        # while True:
        #     # Scroll down to bottom
        #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        #     # Wait to load page
        #     time.sleep(SCROLL_PAUSE_TIME)

        #     # Calculate new scroll height and compare with last scroll height
        #     new_height = driver.execute_script("return document.body.scrollHeight")
        #     if new_height == last_height:
        #         break
        #     last_height = new_height
        # driver.execute_script("window.scrollTo(0, - document.body.scrollHeight);")

        driver.execute_script('window.scrollBy(0, 1000)') 

        jobs_fail = ["IT System Engineer","Market Research Intern","IT Network Engineer","Graduate Trainee","Administrative Assistant","Customer Support Engineer","Customer Support Consultant","Research Internship","Search Quality Rater","Digital Marketing Analyst","Project Administrator","Ford Internship","Management Trainee","Information Security Analyst","Assistant Engineering Executive","R&D Specialist","Veterinary Information Systems Officer","Junior Engineer","Research Assistant","Marketing Assistant","Administrative Assistant","Database Administration Officer","Administrator","Assistant project manager","Internship","Research Associate","Test Administrator","Document Control Administrator","Administrative Assistant","Practical Trainee","System Administrator","Design & Estimation Engineer","Senior Research Scientist","Project Coordinator","Sales Engineer"]
        keys_fail = ["Project Administrator","Project Manager","Research","Intern","Network","Graduate","Administrative","Assistant","Support","Marketing","Internship","Security","R&D","Junior","Administrative","Officer","Research","Consultant","Consulting","Sale", "Analyst","Assistant","Trainee","Voluteer"]
    
        access_token = login_crm()
    
        jobs = driver.find_elements(By.CLASS_NAME,"jobs-search-results__list-item")
        count = len(jobs)
        address = ""
        for job in jobs:
            job_state = ""
            match_job = "Yes"
            lead_id = ""
            try:
                job_title = job.find_element(By.CLASS_NAME,"job-card-list__title").text
                lower_title = job_title.lower()
                if("consultant" in lower_title or  "support" in lower_title or "admin" in lower_title or "manager" in lower_title or "data analyst" in lower_title or "intern" in lower_title or "lecturer" in lower_title or "tutor" in lower_title):
                    continue
                company_name = job.find_element(By.CLASS_NAME,"job-card-container__primary-description").text
                address = job.find_element(By.CLASS_NAME,"job-card-container__metadata-item").text
                # lead_id = check_lead_existed(job_title,company_name )
                # if(lead_id != ""):
                #     continue
                job_footer = job.find_element(By.CLASS_NAME,"job-card-list__footer-wrapper")
                if job_footer.find_element(By.CLASS_NAME,"job-card-container__footer-job-state"):
                    job_state = job_footer.find_element(By.CLASS_NAME,"job-card-container__footer-job-state").text           
                if(job_state == "Viewed"):
                    continue
            except NoSuchElementException:  #spelling error making this code not work as expected
                pass
            if(job_state == "Viewed"):
            #if(lead_id != ""):
                continue
            for key_fail in keys_fail:
                if key_fail in job_title:
                    match_job = "No"
                    break
                else:
                    for job_fail in jobs_fail:
                        if job_fail == job_title:
                            match_job = "No"
                            break
            if(match_job == "Yes"):
                # if((job_count // 10) == 1):
                #     z = random.randint(90,180)
                #     time.sleep(z)
                try:
                    # y = random.randint(30,60)
                    # time.sleep(y)
                    job_id = job.get_attribute("data-occludable-job-id")
                    get_job_detail(driver,job_id,access_token,country, country,linkedin_acc)
                    job_count = job_count + 1
                except NoSuchElementException:
                    pass
        country_count = country_count + 1
        #Go to next page
        page_index = 0
        for page_indicator in page_indicators:
            if page_index == 0:
                continue
            else:
                button = page_indicator.find_element(By.TAG_NAME,"button")
                button.click()
                time.sleep(5)
                jobs = driver.find_elements(By.CLASS_NAME,"job-card-container")
                count = len(jobs)
                for job in jobs:
                    job_state = ""
                    match_job = "Yes"
                    lead_id = ""
                    try:
                        job_title = job.find_element(By.CLASS_NAME,"job-card-list__title").text
                        lower_title = job_title.lower()
                        if("consultant" in lower_title or  "support" in lower_title or "admin" in lower_title or "manager" in lower_title or "data analyst" in lower_title or "intern" in lower_title or "lecturer" in lower_title or "tutor" in lower_title):
                            continue
                        company_name = job.find_element(By.CLASS_NAME,"job-card-container__primary-description").text
                        address = job.find_element(By.CLASS_NAME,"job-card-container__metadata-item").text
                        # lead_id = check_lead_existed(job_title,company_name )
                        # if(lead_id != ""):
                        #     continue
                        job_footer = job.find_element(By.CLASS_NAME,"job-card-list__footer-wrapper")
                        if job_footer.find_element(By.CLASS_NAME,"job-card-container__footer-job-state"):
                            job_state = job_footer.find_element(By.CLASS_NAME,"job-card-container__footer-job-state").text           
                        if(job_state == "Viewed"):
                            continue
                    except NoSuchElementException:  #spelling error making this code not work as expected
                        pass
                    if(job_state == "Viewed"):
                    #if(lead_id != ""):
                        continue
                    for key_fail in keys_fail:
                        if key_fail in job_title:
                            match_job = "No"
                            break
                        else:
                            for job_fail in jobs_fail:
                                if job_fail == job_title:
                                    match_job = "No"
                                    break
                    if(match_job == "Yes"):
                        try:
                            job_id = job.get_attribute("data-occludable-job-id")
                            get_job_detail(driver,job_id,access_token,country, country,linkedin_acc)
                            job_count = job_count + 1
                        except NoSuchElementException:
                            pass
