from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import requests
import os
import csv
from tqdm import tqdm


class Scraper(ABC):
    """Abstract base class for defining a web scraper for collecting information from articles."""

    headers = {
        "User-Agent": "Java-http-client/"
    }

    @abstractmethod
    def extract_info_from_links(self, company: str, article_links: list, folder_path: str):
        """Abstract method to extract information from the provided article links."""
        pass


class PressReleasesScrape(Scraper):
    """Class responsible for scraping press release information and saving it to a CSV file."""

    def __init__(self):
        super().__init__()

    def extract_info_from_links(self, company: str, article_links: list, folder_path: str):
        """
        Extracts information from the given links and saves it as a CSV file.

        :param company: The name of the company whose articles are being scraped.
        :param article_links: A list of article URLs to scrape.
        :param folder_path: The path to the folder where the CSV file will be saved.
        :return: The path to the created CSV file.
        """
        csv_file_path = os.path.join(folder_path, f'{company}_press_releases.csv')
        print(f"File '{company}_press_releases.csv' created in '{folder_path}'.")

        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Title', 'Published Date', 'Content'])

        for link in tqdm(article_links, desc="Processing articles"):
            response = requests.get(link, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            date_element = soup.find('time', class_='timestamp__date')
            date_text = date_element.text.strip() if date_element else "N/A"

            title_element = soup.find('h1', class_='press-release-header__title')
            title_text = title_element.text.strip() if title_element else "N/A"

            div_content = soup.find('div', class_='body__content')
            text = div_content.get_text(separator="\n") if div_content else "N/A"

            with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([title_text, date_text, text])

        print(f"File '{company}_press_releases.csv' was updated with scraped information.")
        return csv_file_path


class NasdaqNewsScrape(Scraper):
    """Class responsible for scraping NASDAQ news information and saving it to a CSV file."""

    def __init__(self):
        super().__init__()

    def extract_info_from_links(self, company: str, article_links: list, folder_path: str):
        """
        Extracts information from the given links and saves it as a CSV file.

        :param company: The name of the company whose articles are being scraped.
        :param article_links: A list of article URLs to scrape.
        :param folder_path: The path to the folder where the CSV file will be saved.
        :return: The path to the created CSV file.
        """
        csv_file_path = os.path.join(folder_path, f'{company}_nasdaq_news.csv')
        print(f"File '{company}_nasdaq_news.csv' created in '{folder_path}'.")

        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Title', 'Topic', 'Published Date', 'Author', 'Company', 'Content'])

        for link in tqdm(article_links, desc="Processing articles"):
            try:
                response = requests.get(link, headers=self.headers)
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract the topic
                topic_element = soup.find('meta', {'name': 'com.nasdaq.cms.taxonomy.topic'})
                topic_value = topic_element.get('content') if topic_element else "N/A"

                # Extract the author
                author_element = soup.find('span', class_='jupiter22-c-author-byline__author-no-link')
                author_value = author_element.text.strip() if author_element else "N/A"

                # Extract the company
                company_element = soup.find('span', class_='jupiter22-c-text-link__text')
                company_value = company_element.text.strip() if company_element else "N/A"

                # Extract the publication date
                date_element = soup.find('p', class_='jupiter22-c-author-byline__timestamp')
                date_text = date_element.text.strip() if date_element else "N/A"

                # Extract the title
                title_element = soup.find('h1', class_='jupiter22-c-hero-article-title')
                title_text = title_element.text.strip() if title_element else "N/A"

                # Extract the main content
                div_content = soup.find('div', class_='body__content')
                text = div_content.get_text(separator="\n") if div_content else "N/A"

                with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([title_text, topic_value, date_text, author_value, company_value, text])

            except Exception as e:
                print(f"An error occurred while processing {link}: {e}")
                continue

        print(f"File '{company}_nasdaq_news.csv' was updated with scraped information.")
        return csv_file_path
