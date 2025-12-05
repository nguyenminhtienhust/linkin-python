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
import shutil
import json
import requests
import urllib.request
import psycopg2
import pandas as pd
import random
from selenium.common.exceptions import NoSuchElementException
from eld import LanguageDetector
import sys
if sys.version_info.major == 3:
    from urllib.parse import urlencode, urlparse, urlunparse, parse_qs,unquote
else:
    from urllib import urlencode
    from urlparse import urlparse, urlunparse, parse_qs,unquote
# from fake_useragent import UserAgent

from utils_No_Acc import (
    get_lk_credentials,
    enter_ids_on_lk_signin,
    get_job_detail,
    check_lead_existed,
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

def extract_original_referer(url):
    """Extract original_referer parameter from authwall URL"""
    if 'original_referer=' in url:
        # Find the start of the original_referer value
        start = url.index('original_referer=') + len('original_referer=')
        # The value continues to the end of the string
        extracted = url[start:]
        return unquote(extracted)
    return None
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
    home_url = "https://www.linkedin.com/home"

    # jobs_names = [".Net developer","Java developer","iOS developer","Android developer","kotlin developer","Flutter","Dart developer","NodeJS",
    #                "React Native","ReactJS developer","NextJS developer",
    #                "AngularJS developer","VueJS  developer","Django","Golang", "Swift Developer","Python",
    #               "Php developer", "C++","Azure developer"]
    jobs_names = ["iOS developer"]
    #countries = ["Malaysia","Australia and New Zealand","Germany","European Union", "Thailand","Singapore","United States","United Kingdom"]
    countries = ["Malaysia"]
    #
    # jobfile = open("job.txt", "r")
    # jobs_names = jobfile.read().split(",")
    # jobfile.close()
    # countryfile = open("country.txt", "r")
    # countries = countryfile.read().split(",")
    # countryfile.close()
    
    
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
    #chrome_options.add_argument("window-size=1680,8000")
    cService = webdriver.ChromeService(executable_path='D:\FitechCRM\chromedriver-win64\chromedriver.exe')
    
    driver = webdriver.Chrome(service = cService, options=chrome_options)
    # fire_options = webdriver.FirefoxOptions()
    # cService = webdriver.ChromeService(executable_path='C:\Workspace\CRMFitech\WebDriver\geckodriver.exe')
    # driver = webdriver.Firefox(service = cService, options=fire_options)
    
    driver.maximize_window()
    # driver.get("https://www.linkedin.com/login/")
    
    print("Inputting the credentials...")
    lk_credentials = get_lk_credentials(LK_CREDENTIALS_PATH)
    # enter_ids_on_lk_signin(driver, lk_credentials["email"], lk_credentials["password"])

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
    if(lk_credentials["email"] == "tran.habk0605@gmail.com"):
        linkedin_acc = "Ngoc Ha"
    
    print("Starting the scraping...")
    driver.get(home_url)
    time.sleep(5)
    header_content = driver.find_element(By.CLASS_NAME,"top-nav-menu") 
    header_content_li = header_content.find_elements(By.TAG_NAME,"li")
    for content_li in header_content_li:
        content_li_span_text = content_li.find_element(By.TAG_NAME,"span").text
        if(content_li_span_text.lower() == "jobs"):
            content_li.click()
            time.sleep(10)
            break
    dismiss_button = driver.find_element(By.CLASS_NAME,"modal__dismiss")
    dismiss_button.click() 				
    time.sleep(2)
    count_job = 1
    current_job = ""
    current_coutry = ""
    for job_name in jobs_names:   
        if(count_job > 1):
            x = random.randint(300,1000)
            time.sleep(x)
        country_count = 1
        if(count_job == 1):
            time.sleep(5)
        for country in countries:
            if(country_count > 1):
                x = random.randint(100,400)
                time.sleep(x)           
            print("Country: " + country)
            print("Job: " + job_name)
            temp_job_name = job_name
            if (country == "Malaysia"):
                if(job_name == "Android developer"):
                    temp_job_name = "Android"
                else:
                    temp_job_name = job_name
                if(job_name == "kotlin developer"):
                    temp_job_name = "kotlin"
                else:
                    temp_job_name = job_name
            done = False
            while( done == False):
                try:
                    if(current_job != job_name):
                        current_job = job_name
                        #titleInputElement = driver.find_element(By.CLASS_NAME,"jobs-search-box__keyboard-text-input")                     
                        #titleInputElement = driver.find_element(By.CSS_SELECTOR,'[id*="jobs-search-box-keyword-id"]')
                        titleInput = driver.find_element(By.CLASS_NAME,"keywords-typeahead-input")
                        titleInputElement = driver.find_element(By.CSS_SELECTOR,'[id*="job-search-bar-keywords"]')  
                        titleInputElement.clear()
                        time.sleep(2)
                        titleInputElement.send_keys(temp_job_name)
                        time.sleep(4)
                    if(current_coutry != country):
                        current_coutry = country
                        #locationInputElement = driver.find_element(By.CLASS_NAME,"jobs-search-box__keyboard-text-input") 
                        #locationInputElement = driver.find_element(By.CSS_SELECTOR, '[id*="jobs-search-box-location-id"]')
                        localtionInput = driver.find_element(By.CLASS_NAME,"location-typeahead-input")
                        locationInputElement = driver.find_element(By.CSS_SELECTOR, '[id*="job-search-bar-location"]') 
                        locationInputElement.clear()
                        time.sleep(2)
                        locationInputElement.send_keys(country)
                        time.sleep(2)

                    # searchArea = driver.find_element(By.CSS_SELECTOR,'[id*="jobs-search-panel"]')
                    # searchPanel = searchArea.find_element(By.CLASS_NAME,"base-search-bar__form")
                    # time.sleep(3)
                    # searchButton = searchPanel.find_element(By.TAG_NAME,"button")
                    # submitButton = driver.find_elements(By.CLASS_NAME,"base-search-bar__submit-btn")[1]
                    # # print("Button: ", len(submitButtons))
                    # driver.implicitly_wait(10)
                    # submitButton.click()


                    searchButton = driver.find_element(By.CSS_SELECTOR,'[data-tracking-control-name="public_jobs_jobs-search-bar_base-search-bar-search-submit"]')
                    driver.implicitly_wait(5)
                    searchButton.click()
                    current_url = driver.current_url
                    u = urlparse(current_url)
                    query = parse_qs(u.query, keep_blank_values=True)
                    query.pop('geoId', None)
                    u = u._replace(query=urlencode(query, True))
                    driver.get(urlunparse(u))
                    
                    
                    time.sleep(3)
                    filter_list = driver.find_element(By.CLASS_NAME,"filters__list") 
                    filter_li = filter_list.find_elements(By.TAG_NAME,"li")[0]
                    filter_li_btn = filter_li.find_elements(By.TAG_NAME,"button")[0]
                    filter_li_text = filter_li_btn.text
                    filter_li_btn.click()
                    time.sleep(2)
                    past_week = filter_li.find_element(By.CSS_SELECTOR, '[id*="f_TPR-2"]')   
                    print(past_week.get_attribute('value'))                        
                    time.sleep(2)                        
                    past_week.click()
                    time.sleep(1)  
                    done_btn = filter_li.find_elements(By.TAG_NAME,"button")[1]
                    done_btn.click()
                    time.sleep(10)

                    authwall_url = driver.current_url
                    clear_url = extract_original_referer(authwall_url)
                    driver.get(clear_url)                  
                    done = True
                except NoSuchElementException as error:
                    print("search data fill in: ",error)  
                    continue

            jobs_fail = ["IT System Engineer","Market Research Intern","IT Network Engineer","Graduate Trainee","Administrative Assistant","Customer Support Engineer","Customer Support Consultant","Research Internship","Search Quality Rater","Digital Marketing Analyst","Project Administrator","Ford Internship","Management Trainee","Information Security Analyst","Assistant Engineering Executive","R&D Specialist","Veterinary Information Systems Officer","Junior Engineer","Research Assistant","Marketing","Administrative","Database Administration Officer","Administrator","Assistant project manager","Internship","Research Associate","Test Administrator","Document Control Administrator","Administrative Assistant","Practical Trainee","System Administrator","Design & Estimation Engineer","Senior Research Scientist","Project Coordinator","Sales Engineer","Assistant"]
            keys_fail = ["Project Administrator","Project Manager","Research","Intern","Network","Graduate","Administrative","Assistant","Support","Marketing","Internship","Security","R&D","Administrative","Officer","Research","Consultant","Consulting","Sale", "Analyst","Assistant","Trainee","Voluteer"]
            try:
                if(driver.find_element(By.CLASS_NAME,"jobs-search-no-results-banner")):
                    continue
            except:
                pass
            access_token = login_crm()
            result = driver.find_element(By.CLASS_NAME,"jobs-search__results-list")
            jobs = result.find_elements(By.TAG_NAME,"li")
            address = ""
            job_link = ""
            for job in jobs:
                job_state = ""
                match_job = "Yes"
                lead_id = ""
                try:
                    job_title = job.find_element(By.CLASS_NAME,"base-search-card__title").text
                    lower_title = job_title.lower()
                    print(lower_title)
                    detector = LanguageDetector()
                    #if("consultant" in lower_title or  "support" in lower_title or "admin" in lower_title or "manager" in lower_title or "data analyst" in lower_title or "intern" in lower_title or "lecturer" in lower_title or "tutor" in lower_title or "assistant" in lower_title or "graphic" in lower_title or "design" in lower_title or "supervisor" in lower_title or "investors" in lower_title):
                    if("director" in lower_title or "consultant" in lower_title or  "support" in lower_title or "admin" in lower_title or "manager" in lower_title or "analyst" in lower_title or "intern" in lower_title or "lecturer" in lower_title or "tutor" in lower_title or "assistant" in lower_title or "graphic" in lower_title or "design" in lower_title or "supervisor" in lower_title or "investor" in lower_title or "test" in lower_title or "design" in lower_title or "analyst" in lower_title or "specialist" in lower_title or "sales" in lower_title or "student" in lower_title or "purchasing" in lower_title or "infrastructure" in lower_title or "architect" in lower_title or "civil" in lower_title or "site reliability" in lower_title or  detector.detect(lower_title).language != "en"):
                        print("\n title english: ")
                        continue
                    company_name = job.find_element(By.CLASS_NAME,"base-search-card__subtitle").text
                    print("company_name: ",company_name)
                    lead_info = check_lead_existed(job_title,company_name,"")
                    if(lead_info["data"] != ""):
                        print("lead existed")
                        continue
                    # job_footer = job.find_element(By.CLASS_NAME,"job-card-container__footer-wrapper")
                    # if job_footer.find_element(By.CLASS_NAME,"job-card-container__footer-job-state"):
                    #     job_state = job_footer.find_element(By.CLASS_NAME,"job-card-container__footer-job-state").text        
                    # if(job_state == "Viewed"):
                    #     continue
                    job_link = job.find_element(By.CLASS_NAME,"base-card__full-link").get_attribute("href")
                    print(job_link)
                except Exception as errorConnect: #spelling error making this code not work as expected
                    print("\nConnect error :", errorConnect)  
                    pass
                for key_fail in keys_fail:
                    if key_fail in job_title:
                        match_job = "No"
                        break
                    else:
                        for job_fail in jobs_fail:
                            if job_fail == job_title:
                                match_job = "No"
                                break
                print(match_job)
                print(job_link)
                if(match_job == "Yes"):
                    try:
                        # y = random.randint(30,60)
                        # time.sleep(y)
                        get_job_detail(driver,job_link,access_token,country, country,linkedin_acc)
                        job_count = job_count + 1
                        z = random.randint(2,5)
                        time.sleep(z)
                    except NoSuchElementException:
                        pass
            country_count = country_count + 1
            count_job = count_job + 1
            