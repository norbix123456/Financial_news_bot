from abc import ABC, abstractmethod
from .config import COMPANIES
from bs4 import BeautifulSoup
import requests
import os
import csv
from tqdm import tqdm

class Scraper(ABC):

    def __init__(self):
        self.links = COMPANIES

    headers = {
        "User-Agent": "Java-http-client/"
    }

    @abstractmethod
    def extract_info_from_links(self, company: str, article_links: list, folder_path: str):
        pass

class PressReleasesScrape(Scraper):

    def __init__(self):
        # Wywołanie konstruktora klasy bazowej DataSource
        super().__init__()

    def extract_info_from_links(self, company: str, article_links: list, folder_path: str):
        """
        Ekstraktuje informacje z podanych linków i zapisuje jako CSV.
        """
        csv_file_path = os.path.join(folder_path, f'{company}_press_releases.csv')
        print(f"File f'{company}_press_releases.csv was made in '{folder_path}'.")
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Title', 'Published Date', 'Content'])
        for i in tqdm(article_links, desc="Processing articles"):
            response = requests.get(i, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            date_element = soup.find('time', class_='timestamp__date')
            date_text = date_element.text.strip()
            title_element = soup.find('h1', class_='press-release-header__title')
            title_text = title_element.text.strip()
            div_content = soup.find('div', class_='body__content')
            text = div_content.get_text(separator="\n")

            with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([title_text, date_text, text])

        print(f"File f'{company}_press_releases.csv was updated with scraped information.")

class NasdaqNewsScrape(Scraper):

    def __init__(self):
        # Wywołanie konstruktora klasy bazowej DataSource
        super().__init__()

    def extract_info_from_links(self, company: str, article_links: list, folder_path: str):
        """
        Ekstraktuje informacje z podanych linków i zapisuje jako CSV.
        """
        csv_file_path = os.path.join(folder_path, f'{company}_nasdaq_news.csv')
        print(f"File f'{company}_press_releases.csv was made in '{folder_path}'.")
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Title', 'Topic', 'Published Date', 'Author', 'Company', 'Content'])
        for i in tqdm(article_links, desc="Processing articles"):
            response = requests.get(i, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            topic_element = soup.find('meta', {'name': 'com.nasdaq.cms.taxonomy.topic'})
            topic_value = topic_element.get('content')
            author_element = soup.find('span', class_='jupiter22-c-author-byline__author-no-link')
            if author_element is not None:
                author_value = author_element.text.strip()
            else:
                author_value = "Nasdaq"
            company_element = soup.find('span', class_='jupiter22-c-text-link__text')
            company_value = company_element.text.strip()
            date_element = soup.find('p', class_='jupiter22-c-author-byline__timestamp')
            date_text = date_element.text.strip()
            title_element = soup.find('h1', class_='jupiter22-c-hero-article-title')
            title_text = title_element.text.strip()
            div_content = soup.find('div', class_='body__content')
            text = div_content.get_text(separator="\n")

            with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([title_text, topic_value, date_text, author_value, company_value, text])

        print(f"File f'{company}_nasdaq_news was updated with scraped information.")