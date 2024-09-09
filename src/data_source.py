from abc import ABC, abstractmethod
import time
import math
import os
import csv
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from .config import COMPANIES

class DataSource(ABC):

    def __init__(self):
        self.links = COMPANIES

    headers = {
        "User-Agent": "Java-http-client/"
    }

    @abstractmethod
    def get_links(self, company: str, time_frame: str):
        pass


class PressReleasesLink(DataSource):

    def __init__(self):
        # Wywołanie konstruktora klasy bazowej DataSource
        super().__init__()

    def get_links(self, company: str, time_frame: str):
        """
                Zbiera linki do artykułów na podstawie firmy i zwraca je jako wynik.

        """
        link = self.links[company]['nasdaq_press_releases']
        print(f"Scrapuję dane dla {company} z Nasdaq press releases z linka: {link} na okres {time_frame}")
        data_links = []
        driver = webdriver.Chrome()
        driver.get(link)
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='results-info']"))
            )
            time.sleep(3)
            results_info = driver.find_element(By.XPATH, "//div[@class='results-info']")
        except TimeoutException:
            print(f'Element {link} not seen, refreshing...')
            driver.refresh()
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='results-info']"))
            )
            time.sleep(3)
            results_info = driver.find_element(By.XPATH, "//div[@class='results-info']")
        max_number = results_info.text.split()[5]
        page_number = math.ceil((int(max_number) / 10))
        i = 1
        while i <= page_number:
            current_page = f'{link}?page={i}&rows_per_page=10'
            driver.get(current_page)
            driver.implicitly_wait(30)
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper'))
                )
                time.sleep(2)
                article_links = driver.find_elements(By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper')
            except TimeoutException:
                print(f'Element not seen, refreshing...')
                driver.refresh()
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper'))
                )
                time.sleep(2)
                article_links = driver.find_elements(By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper')
            try_again = False
            for linkin in article_links:
                try:
                    href = linkin.get_attribute('href')
                    if href is None:
                        try_again = True
                        break
                    data_links.append(href)
                except StaleElementReferenceException:
                    print(f'Stale element encountered on page {i}, refreshing...')
                    driver.refresh()
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper'))
                    )
                    article_links = driver.find_elements(By.CSS_SELECTOR,
                                                         'a.jupiter22-c-article-list__item_title_wrapper')
                    for linkin in article_links:
                        try:
                            href = linkin.get_attribute('href')
                            data_links.append(href)
                        except StaleElementReferenceException:
                            continue

            if try_again:
                print(f"Retrying page {i} due to missing or stale element...")
                continue
            i += 1

        driver.quit()

        return data_links

class NasdaqNewsLink(DataSource):

    def __init__(self):
        # Wywołanie konstruktora klasy bazowej DataSource
        super().__init__()

    def get_links(self, company: str, time_frame: str):
        link = self.links[company]['nasdaq_news']
        print(f"Scrapuję dane dla {company} z Nasdaq News z linka: {link} na okres {time_frame}")
        data_links = []
        driver = webdriver.Chrome()
        driver.get(link)
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='results-info']"))
            )
            time.sleep(3)
            results_info = driver.find_element(By.XPATH, "//div[@class='results-info']")
        except TimeoutException:
            print(f'Element {link} not seen, refreshing...')
            driver.refresh()
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='results-info']"))
            )
            time.sleep(3)
            results_info = driver.find_element(By.XPATH, "//div[@class='results-info']")
        max_number = results_info.text.split()[5]
        page_number = math.ceil((int(max_number) / 10))
        i = 1
        while i <= page_number:
            current_page = f'{link}?page={i}&rows_per_page=10'
            driver.get(current_page)
            driver.implicitly_wait(30)
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper'))
                )
                time.sleep(2)
                article_links = driver.find_elements(By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper')
            except TimeoutException:
                print(f'Element not seen, refreshing...')
                driver.refresh()
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper'))
                )
                time.sleep(2)
                article_links = driver.find_elements(By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper')
            try_again = False
            for linkin in article_links:
                try:
                    href = linkin.get_attribute('href')
                    if href is None:
                        try_again = True
                        break
                    data_links.append(href)
                except StaleElementReferenceException:
                    print(f'Stale element encountered on page {i}, refreshing...')
                    driver.refresh()
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper'))
                    )
                    article_links = driver.find_elements(By.CSS_SELECTOR,
                                                         'a.jupiter22-c-article-list__item_title_wrapper')
                    for linkin in article_links:
                        try:
                            href = linkin.get_attribute('href')
                            data_links.append(href)
                        except StaleElementReferenceException:
                            continue

            if try_again:
                print(f"Retrying page {i} due to missing or stale element...")
                continue
            i += 1

        driver.quit()

        return data_links


class YahooFinanceLink(DataSource):
    def __init__(self):
        # Wywołanie konstruktora klasy bazowej DataSource
        super().__init__()

    def get_links(self, company: str, time_frame: str):
        # Implementacja scrapowania danych dla Yahoo Finance
        pass

class XdFinanseLink(DataSource):
    def __init__(self):
        # Wywołanie konstruktora klasy bazowej DataSource
        super().__init__()

    def get_links(self, company: str, time_frame: str):
        # Implementacja scrapowania danych dla Xd Finanse
        pass

class CnbcLink(DataSource):
    def __init__(self):
        # Wywołanie konstruktora klasy bazowej DataSource
        super().__init__()

    def get_links(self, company: str, time_frame: str):
        # Implementacja scrapowania danych dla CNBC
        pass