import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import os
import time

import urllib.request
from urllib.parse import quote
from bs4 import BeautifulSoup
import re
import requests

import ssl

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument(
    "user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'")


def scrape_newsbitcoin(load_times, mode):
    url = "https://news.bitcoin.com"
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36')
    req.add_header('Host', 'news.bitcoin.com')
    req.add_header('Cookie', ' __cfduid=dc172749a14b781fa5821f8da67c407a01539049207; _ga=GA1.2.1547810722.1539049209; ac_enable_tracking=1; _omappvp=DF3dpnr8LilMv5Mchn2tUvLDrAKGzHhvvLXuTJVhVpLkq4Y9WYkz38ynl0ha1c9udtcNDtXhtPRdZPta5YoFzUBmqkH1fyYB; _gid=GA1.2.388542892.1539573874; om-in7rat0uxlot0pwxsk3m=1539574334531; om-ead4x65bjbjpfiap4zuo=1539574762692; _gat_UA-59964190-1=1')
    req.add_header('Connection', 'keep-alive')
    LOAD_OUT = 50
    while LOAD_OUT:
        try:
            page_info = urllib.request.urlopen(req, context=context)
            break
        except Exception:
            LOAD_OUT -= 1

    page_info = page_info.read()
    html = page_info.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    titles = []
    update_times = []
    for resultTable in soup.find_all('div',class_='item-details'):
        titles.append(resultTable.find_all('h3')[0].find_all('a')[0].get('title'))
        update_times.append(resultTable.find_all('time')[0].get('datetime'))

    i = 1
    while i < load_times:
        url = "https://news.bitcoin.com/page/" + str(i) + "/"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36')
        req.add_header('Host', 'news.bitcoin.com')
        req.add_header('Cookie', ' __cfduid=dc172749a14b781fa5821f8da67c407a01539049207; _ga=GA1.2.1547810722.1539049209; ac_enable_tracking=1; _omappvp=DF3dpnr8LilMv5Mchn2tUvLDrAKGzHhvvLXuTJVhVpLkq4Y9WYkz38ynl0ha1c9udtcNDtXhtPRdZPta5YoFzUBmqkH1fyYB; _gid=GA1.2.388542892.1539573874; om-in7rat0uxlot0pwxsk3m=1539574334531; om-ead4x65bjbjpfiap4zuo=1539574762692; _gat_UA-59964190-1=1')
        req.add_header('Connection', 'keep-alive')
        while LOAD_OUT:
            try:
                page_info = urllib.request.urlopen(req, context=context)
                break
            except Exception:
                LOAD_OUT -= 1
        page_info = page_info.read()
        html = page_info.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        for resultTable in soup.find_all('div',class_='item-details'):
            titles.append(resultTable.find_all('h3')[0].find_all('a')[0].get('title'))
            update_times.append(resultTable.find_all('time')[0].get('datetime'))
        i += 1
    return (titles, update_times)


def grabber_newsbitcoin(load_times, mode):
    executable_path = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/driver/chromedriver'
    html = "http://news.bitcoin.com"
    cur_time = int(time.time())
    recept_period = 24*60*60
    end_time = cur_time
    browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=executable_path)
    browser.get(html)

    TIME_OUT = 1
    titles = np.array([])
    update_times = np.array([])
    PAGE_OUT = 50

    if mode == 0:
        while load_times and PAGE_OUT:
            try:
                page_titles_element = browser.find_elements_by_xpath("//div[@class='item-details']/h3")
                page_titles = [x.text for x in page_titles_element]
                page_update_time_elememts = browser.find_elements_by_xpath("//div[@class='item-details']/div/span/time")
                page_update_times = []
                for page_update_time in page_update_time_elememts:
                    page_update_times.append(page_update_time.get_attribute("datetime"))
                titles = np.append(titles, page_titles)
                update_times = np.append(update_times, page_update_times)
            except Exception:
                PAGE_OUT -= 1

            try:
                browser.find_element_by_class_name(
                    "td-icon-menu-right").click()
                load_times -= 1
                print("=====load page====", load_times)
                WebDriverWait(browser, TIME_OUT).until(
                    EC.visibility_of_element_located((
                        By.CLASS_NAME, "td-icon-menu-right")))
            except Exception:
                print('load out')
                PAGE_OUT -= 1

    if mode == 1:
        while cur_time - end_time < recept_period and PAGE_OUT:
            try:
                page_titles_element = browser.find_elements_by_xpath("//div[@class='item-details']/h3")
                page_titles = [x.text for x in page_titles_element]
                page_update_time_elememts = browser.find_elements_by_xpath("//div[@class='item-details']/div/span/time")
                page_update_times = []
                for page_update_time in page_update_time_elememts:
                    page_update_times.append(page_update_time.get_attribute("datetime"))
                titles = np.append(titles, page_titles)
                update_times = np.append(update_times, page_update_times)
                end_time = int(datetime.datetime.strptime(update_times[-1], '%Y-%m-%dT%H:%M:%S+00:00').timestamp() + 32400)
            except Exception:
                PAGE_OUT -= 1

            try:
                browser.find_element_by_class_name(
                    "td-icon-menu-right").click()
                WebDriverWait(browser, TIME_OUT).until(
                    EC.visibility_of_element_located((
                        By.CLASS_NAME, "td-icon-menu-right")))
            except Exception:
                print('load out')

    browser.quit()
    return (titles.tolist(), update_times.tolist())


def grabber_ccn(load_times, mode):
    print("=====grab news from ccn======", "====load page===", load_times)
    executable_path = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/driver/chromedriver'
    html = "http://www.ccn.com"
    cur_time = int(time.time())
    recept_period = 12 * 60 * 60
    end_time = cur_time
    browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=executable_path)
    browser.get(html)
    PAGE_OUT = 50

    if mode == 0:
        while load_times and PAGE_OUT:
            try:
                browser.find_element_by_class_name("omaha-CloseButton").click()
            except Exception as e:
                time.sleep(0.1)

            try:
                browser.find_element_by_class_name("load-more-btn").click()
                print("====load page====", load_times)
                load_times -= 1
                time.sleep(0.5)
            except Exception:
                PAGE_OUT -= 1

    if mode == 1:
        while cur_time - end_time < recept_period and PAGE_OUT:
            try:
                browser.find_element_by_class_name("omaha-CloseButton").click()
            except Exception:
                time.sleep(0.1)
            try:
                browser.find_element_by_class_name("load-more-btn").click()
                end_time = int(datetime.datetime.strptime(browser.find_elements_by_class_name("updated")[-1].text, '%Y-%m-%dT%H:%M:%S+00:00').timestamp() + 32400)
                print(end_time)
                time.sleep(0.1)
            except Exception:
                PAGE_OUT -= 1

    titles_element1 = browser.find_elements_by_xpath("//li/div[1]")
    titles_element2 = browser.find_elements_by_xpath("//article/header/h4[1]")
    titles = [x.text for x in titles_element1] + [x.text for x in titles_element2]
    update_time_elememt = browser.find_elements_by_class_name("updated")
    update_time = [x.text for x in update_time_elememt]

    brower.quit()
    return (titles, update_time)
