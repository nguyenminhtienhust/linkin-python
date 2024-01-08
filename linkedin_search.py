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

from general_lk_utils import (
    get_lk_credentials,
    enter_ids_on_lk_signin,
    get_job_detail,
    login_crm,
    connect
)

SCROLL_TO_BOTTOM_COMMAND = (
    "document.getElementById('search-results-container').scrollTop+=100000;"
)
LK_CREDENTIALS_PATH = "./lk_credentials.json"


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
    access_token = login_crm()
    home_url = "https://www.linkedin.com/jobs/search"
    print("Starting the driver...")
    logging.getLogger("selenium").setLevel(logging.CRITICAL)
    # Start the webdriver without any logs
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

    driver.get(home_url)

    print("Starting the scraping...")

    #await driver.wait(until.elementLocated(By.className('link')), 1000);

    #titleInputElement = driver.find_element(By.ID, "jobs-search-box-keyword-id-ember100")
    titleInputElement = driver.find_element(By.CSS_SELECTOR,'[id*="jobs-search-box-keyword-id"]')
    titleInputElement.clear()
    jobs_names = [".net developer","java developer","ios developer","android developer","flutter developer","php developer"]
    
    titleInputElement.send_keys(jobs_names[0])
    
    locationInputElement = driver.find_element(By.CSS_SELECTOR, '[id*="jobs-search-box-location-id"]')
    locationInputElement.clear()
    countries = ["Malaysia","Singapore","Hong Kong SAR","New Zealand","Thailand","Australia"]
    locationInputElement.send_keys(countries[5])

    #jobs-search-box__submit-button
    
    searchButton = driver.find_element(By.CLASS_NAME,"jobs-search-box__submit-button")
    searchButton.click()
    time.sleep(2)
    
    #get list jobs
    # jobs = driver.find_elements(By.CSS_SELECTOR,"#main > div > div:nth-child(1) > div > ul > li > div")
    print("Please Zoom in then press Enter")
    input()
    jobs = driver.find_elements(By.CLASS_NAME,"job-card-container")
    count = len(jobs)
    print("Total jobs:" + str(count))
    
    for job in jobs:
        time.sleep(2)
        job_title = driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__job-title").text
        print(job_title)
        job_id = job.get_attribute("data-job-id")
        print(job_id)
        get_job_detail(driver,job_id,access_token)

