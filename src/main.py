from bs4 import BeautifulSoup
import requests
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import math
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import os
import pandas as pd
from datetime import timedelta
from dateutil import parser
import yfinance as yf



headers = {
        "User-Agent": "Java-http-client/"
    }
base_url = 'https://www.nasdaq.com'

def get_links(link):
    data_links = []
    driver = webdriver.Chrome()
    driver.get(link)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='results-info']"))
    )
    results_info = driver.find_element(By.XPATH, "//div[@class='results-info']")
    max_number = results_info.text.split()[5]
    page_number = math.ceil((int(max_number) / 10))
    i = 1
    while i <= page_number:
        current_page = f'{link}?page={i}&rows_per_page=10'
        driver.get(current_page)
        driver.implicitly_wait(30)
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
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper'))
                )
                article_links = driver.find_elements(By.CSS_SELECTOR, 'a.jupiter22-c-article-list__item_title_wrapper')
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

def scrape_news(data, folder_name):

    if not os.path.exists(folder_name):
        os.makedirs(folder_name, exist_ok=True)
        print(f"Folder '{folder_name}' został utworzony.")
    for firma, urls in data.items():
        csv_file_path = os.path.join(folder_name, f'{firma}.csv')
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Title', 'Published Date', 'Content'])
        for i in urls:
            response = requests.get(i, headers=headers)
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


def main():

    category_url = f'{base_url}/market-activity/quotes/press-releases'
    response = requests.get(category_url, headers=headers)
    data_links = []
    short_names = []
    data = {}

    if response.status_code == 200:

        # parse HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', id='tablefield-paragraph-8371281-field_table-0')

        for row in table.find_all('tr'):
            short_names.append(row.text.strip().split('\n')[0])


        # Wyciągnięcie wszystkich linków (elementów <a>) z tej tabeli
        links = table.find_all('a')

        # Wyświetlenie adresów URL
        for i, link in enumerate(links):
            if i % 2:
                href = link.get('href')
                data_links.append(base_url + href)

        for key, value in enumerate(data_links):
            arts = get_links(value)
            print(len(arts))
            data[short_names[key+1]] = arts


    else:
        print(f'An error has occurred with status {response.status_code}')

    folder_name = 'nasdaq_press_releases'
    scrape_news(data, folder_name)
    download_news(folder_name)


def download_news(folder_name):
    dataframes = []
    for filename in os.listdir(folder_name):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_name, filename)
            # Wczytywanie pliku CSV do DataFrame
            df = pd.read_csv(file_path, encoding='utf-8')
            file_name_without_ext = os.path.splitext(filename)[0]
            df['source_file'] = file_name_without_ext
            # Dodawanie DataFrame do listy
            dataframes.append(df)

    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

def check_stock_sentiment(df):

    df['Parsed Date'] = df['Published Date'].apply(parse_date)
    opinion_fin = []
    for index, row in df.iterrows():

        date_start = row['Parsed Date']
        #date_start = pd.Timestamp('2024-05-27 06:00:00')
        end_price = 'Close'
        # Change weekends date
        date_end = date_start + pd.Timedelta(days=1)
        if date_start.time() < pd.Timestamp('09:30').time():
            start_price = 'Close'
        elif pd.Timestamp('09:30').time() <= date_start.time() < pd.Timestamp('16:00').time():
            start_price = 'Open'
        else:
            start_price = 'Close'

        if date_start.weekday() == 4:
            if pd.Timestamp('09:30').time() < date_start.time():
                date_end = date_start + timedelta(days=3)
        elif date_start.weekday() == 5:
            if pd.Timestamp('09:30').time() > date_start.time():
                date_end = date_start + pd.Timedelta(days=3)
            else:
                date_end = date_start + pd.Timedelta(days=2)
                date_start = date_start - pd.Timedelta(days=1)
                start_price = 'Close'
        elif date_start.weekday() == 6:
            if pd.Timestamp('09:30').time() > date_start.time():
                date_end = date_start + pd.Timedelta(days=2)
            else:
                date_end = date_start + pd.Timedelta(days=1)
                date_start = date_start - pd.Timedelta(days=2)
                start_price = 'Close'
        elif date_start.weekday() == 0:
            if pd.Timestamp('09:30').time() > date_start.time():
                date_start = date_start - pd.Timedelta(days=3)

        company = yf.Ticker(row['source_file'])
        data = company.history(start= date_start, end = date_end)
        if data.shape[0] == 1:
            if data.index[0].day == date_start.day and data.index[0].month == date_start.month and data.index[0].year == date_start.year:
                date_end = date_end + timedelta(days=1)
                if date_end.weekday() == 5:
                    date_end = date_end + pd.Timedelta(days=2)
                elif date_end.weekday() == 6:
                    date_end = date_end + pd.Timedelta(days=2)
            elif data.index[0].day == date_end.day and data.index[0].month == date_end.month and data.index[0].year == date_end.year:
                date_start = date_start - pd.Timedelta(days=1)
                if date_start.weekday() == 6:
                    if pd.Timestamp('09:30').time() < date_start.time():
                        date_start = date_start - pd.Timedelta(days=2)
                        start_price = 'Close'
                elif date_start.weekday() == 0:
                    if pd.Timestamp('09:30').time() > date_start.time():
                        date_start = date_start - pd.Timedelta(days=3)
            data = company.history(start=date_start, end=date_end)
        print(index, row)
        open_price = data.iloc[0][start_price]
        close_price = data.iloc[-1][end_price]
        difference = open_price - close_price
        if -1 < difference < 1:
            sentiment = 'neutral'
        elif difference >= 1:
            sentiment = 'negative'
        else:
            sentiment = 'positive'
        opinion_fin.append(sentiment)
    df['Financial Sentiment'] = opinion_fin
    #NIE INTERWAL TYLKO DNIOWY
def parse_date(date_str):
    # Usuń strefę czasową z daty
    date_str_without_tz = date_str.rsplit(' ', 1)[0]
    date_obj = parser.parse(date_str_without_tz)
    return date_obj


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    df = download_news('nasdaq_press_releases')
    df = check_stock_sentiment(df)

    #main()
