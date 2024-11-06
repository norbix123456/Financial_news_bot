from abc import ABC, abstractmethod
import time
import math
import re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from .config import COMPANIES


class DataSource(ABC):
    """Abstract base class for defining a data source from which links will be collected."""

    date_format = "%b %d, %Y"

    def __init__(self):
        self.links = COMPANIES

    @staticmethod
    def parse_relative_time(relative_time: str) -> datetime:
        """
        Parses relative time formats like '21 hours ago' or '7 days ago' into a datetime object.

        :param relative_time: A string representing the relative time.
        :return: A datetime object representing the parsed time.
        """
        now = datetime.now()

        if "minute" in relative_time:
            minutes_ago = int(re.search(r'(\d+)', relative_time).group(1))
            return now - timedelta(hours=minutes_ago)
        elif "hour" in relative_time:
            hours_ago = int(re.search(r'(\d+)', relative_time).group(1))
            return now - timedelta(hours=hours_ago)
        elif "day" in relative_time:
            days_ago = int(re.search(r'(\d+)', relative_time).group(1))
            return now - timedelta(days=days_ago)
        else:
            raise ValueError(f"Unknown relative time format: {relative_time}")

    @abstractmethod
    def get_links(self, company: str, time_frame: datetime, chrome_driver_path: str):
        """Abstract method to be implemented in subclasses to fetch links for a given company and time frame."""
        pass


class PressReleasesLink(DataSource):
    """Class responsible for collecting press release links from NASDAQ for a given company."""
    def __init__(self):
        super().__init__()

    def get_links(self, company: str, time_frame: datetime, chrome_driver_path: str):
        """
        Collects press release links for a specific company within a specified time frame.

        :param company: The company's name for which to collect press releases.
        :param time_frame: The starting point of time to collect press releases.
        :param chrome_driver_path: The path to the Chrome WebDriver executable.
        :return: A list of URLs to press releases.
        """
        link = self.links[company]['nasdaq_press_releases']
        print(f"Scraping data for {company} from Nasdaq press releases using link: {link} until {time_frame.date()}")
        data_links = []
        service = Service(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=service)
        driver.get(link)
        try:
            WebDriverWait(driver, 30).until(
                ec.presence_of_element_located((By.XPATH, "//div[@class='results-info']"))
            )
            time.sleep(3)
            results_info = driver.find_element(By.XPATH, "//div[@class='results-info']")
        except TimeoutException:
            print(f'Element {link} not seen, refreshing...')
            driver.refresh()
            WebDriverWait(driver, 30).until(
                ec.presence_of_element_located((By.XPATH, "//div[@class='results-info']"))
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
                    ec.presence_of_element_located((By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper'))
                )
                time.sleep(2)
                article_links = driver.find_elements(By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper')
                date_elements = driver.find_elements(By.CLASS_NAME, 'jupiter22-c-article-list__item_timeline')

            except TimeoutException:
                print(f'Element not seen, refreshing...')
                driver.refresh()
                WebDriverWait(driver, 30).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper'))
                )
                time.sleep(2)
                article_links = driver.find_elements(By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper')
                date_elements = driver.find_elements(By.CLASS_NAME, 'jupiter22-c-article-list__item_timeline')

            try_again = False
            for linkin, date in zip(article_links, date_elements):
                try:
                    date_text = date.text
                    if "ago" in date_text:
                        article_date = self.parse_relative_time(date_text)
                    else:
                        article_date = datetime.strptime(date_text, self.date_format)
                    if article_date < time_frame:
                        driver.quit()
                        return data_links
                    href = linkin.get_attribute('href')
                    if href is None:
                        try_again = True
                        break
                    data_links.append(href)
                except StaleElementReferenceException:
                    print(f'Stale element encountered on page {i}, refreshing...')
                    driver.refresh()
                    WebDriverWait(driver, 20).until(
                        ec.presence_of_element_located(
                            (By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper'))
                    )
                    article_links = driver.find_elements(By.CSS_SELECTOR,
                                                         'a.jupiter22-c-article-list__item_title_wrapper')
                    date_elements = driver.find_elements(By.CLASS_NAME, 'jupiter22-c-article-list__item_timeline')
                    for link_e, date_e in zip(article_links, date_elements):
                        try:
                            date_text = date_e.text
                            if "ago" in date_text:
                                article_date = self.parse_relative_time(date_text)
                            else:
                                article_date = datetime.strptime(date_text, self.date_format)
                            if article_date < time_frame:
                                driver.quit()
                                return data_links
                            href = link_e.get_attribute('href')
                            data_links.append(href)
                        except StaleElementReferenceException:
                            print(f'Stale element encountered on page {i}, refreshing...')
                            driver.refresh()
                            continue

            if try_again:
                print(f"Retrying page {i} due to missing or stale element...")
                continue
            i += 1

        driver.quit()

        return data_links


class NasdaqNewsLink(DataSource):
    """Class responsible for collecting news links from NASDAQ for a given company."""
    def __init__(self):
        super().__init__()

    def get_links(self, company: str, time_frame: datetime, chrome_driver_path: str):
        """
        Collects news links for a specific company within a specified time frame.

        :param company: The company's name for which to collect news.
        :param time_frame: The starting point of time to collect news.
        :param chrome_driver_path: The path to the Chrome WebDriver executable.
        :return: A list of URLs to news articles.
        """
        link = self.links[company]['nasdaq_news']
        print(f"Scraping data for {company} from Nasdaq News using link: {link} until {time_frame.date()}")
        data_links = []
        service = Service(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=service)
        driver.get(link)
        try:
            WebDriverWait(driver, 30).until(
                ec.presence_of_element_located((By.XPATH, "//div[@class='results-info']"))
            )
            time.sleep(3)
            results_info = driver.find_element(By.XPATH, "//div[@class='results-info']")
        except TimeoutException:
            print(f'Element {link} not seen, refreshing...')
            driver.refresh()
            WebDriverWait(driver, 30).until(
                ec.presence_of_element_located((By.XPATH, "//div[@class='results-info']"))
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
                    ec.presence_of_element_located((By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper'))
                )
                time.sleep(2)
                article_links = driver.find_elements(By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper')
                date_elements = driver.find_elements(By.CLASS_NAME, 'jupiter22-c-article-list__item_timeline')
            except TimeoutException:
                print(f'Element not seen, refreshing...')
                driver.refresh()
                WebDriverWait(driver, 30).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper'))
                )
                time.sleep(2)
                article_links = driver.find_elements(By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper')
                date_elements = driver.find_elements(By.CLASS_NAME, 'jupiter22-c-article-list__item_timeline')
            try_again = False
            for linkin, date in zip(article_links, date_elements):
                try:
                    date_text = date.text
                    if "ago" in date_text:
                        article_date = self.parse_relative_time(date_text)
                    else:
                        article_date = datetime.strptime(date_text, self.date_format)
                    if article_date < time_frame:
                        driver.quit()
                        return data_links
                    href = linkin.get_attribute('href')
                    if href is None:
                        try_again = True
                        break
                    data_links.append(href)
                except StaleElementReferenceException:
                    print(f'Stale element encountered on page {i}, refreshing...')
                    driver.refresh()
                    WebDriverWait(driver, 20).until(
                        ec.presence_of_element_located(
                            (By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper'))
                    )
                    article_links = driver.find_elements(By.CSS_SELECTOR,
                                                         'a.jupiter22-c-article-list__item_title_wrapper')
                    date_elements = driver.find_elements(By.CLASS_NAME, 'jupiter22-c-article-list__item_timeline')
                    for link_e, date_e in zip(article_links, date_elements):
                        try:
                            date_text = date_e.text
                            if "ago" in date_text:
                                article_date = self.parse_relative_time(date_text)
                            else:
                                article_date = datetime.strptime(date_text, self.date_format)
                            if article_date < time_frame:
                                driver.quit()
                                return data_links
                            href = link_e.get_attribute('href')
                            data_links.append(href)
                        except StaleElementReferenceException:
                            print(f'Stale element encountered on page {i}, refreshing...')
                            driver.refresh()
                            continue

            if try_again:
                print(f"Retrying page {i} due to missing or stale element...")
                continue
            i += 1

        driver.quit()

        return data_links
