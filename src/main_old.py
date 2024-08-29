from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import os
import re


def reklama(element):
    print("ez")


driver = webdriver.Chrome()

actions = ActionChains(driver)

driver.get("https://www.nasdaq.com/market-activity/quotes/press-releases")

# Kliknij w zgodę
WebDriverWait(driver , 5).until(
    EC.presence_of_element_located((By.XPATH, '//button[@id="onetrust-accept-btn-handler"]'))
)
acceptance = driver.find_element(By.XPATH, '//button[@id="onetrust-accept-btn-handler"]')
acceptance.click()

# znajdź tabele z firmami
WebDriverWait(driver , 5).until(
    EC.presence_of_element_located((By.ID, 'tablefield-paragraph-8371281-field_table-0'))
)
table = driver.find_element(By.ID, 'tablefield-paragraph-8371281-field_table-0')

# znajdź wszystkie linki w tabeli
WebDriverWait(table , 5).until(
    EC.presence_of_element_located((By.TAG_NAME, 'a'))
)
links = table.find_elements(By.TAG_NAME, 'a')

links_to_click = links[1::2]

for index, link in enumerate(links_to_click):
    link.click()
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'jupiter22-c-nav__title'))
        )
        div_element = driver.find_element(By.CLASS_NAME, 'jupiter22-c-nav__title')
    except:
        driver.refresh()

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, 'tablefield-paragraph-8371281-field_table-0'))
        )
        table = driver.find_element(By.ID, 'tablefield-paragraph-8371281-field_table-0')

        WebDriverWait(table, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, 'a'))
        )
        links = table.find_elements(By.TAG_NAME, 'a')
        links_to_click = links[1::2]
        link = links_to_click[index]
        link.click()

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'jupiter22-c-nav__title'))
    )
    div_element = driver.find_element(By.CLASS_NAME, 'jupiter22-c-nav__title')

    WebDriverWait(div_element, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, 'h3'))
    )
    h3_element = div_element.find_element(By.TAG_NAME, 'h3')

    # Pobierz tekst z h3 tagu
    text_content = h3_element.text.strip()

    # Utwórz folder o nazwie "AMD", jeśli jeszcze nie istnieje
    folder_name = text_content
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    os.chdir(folder_name)

    while True:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'jupiter22-c-article-list'))
        )
        ul_element = driver.find_element(By.CLASS_NAME, 'jupiter22-c-article-list')

        WebDriverWait(ul_element, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, 'a'))
        )
        articles_to_click = ul_element.find_elements(By.TAG_NAME, 'a')
        for article_index in range(len(articles_to_click)):

            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'jupiter22-c-article-list'))
            )
            ul_element = driver.find_element(By.CLASS_NAME, 'jupiter22-c-article-list')

            WebDriverWait(ul_element, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, 'a'))
            )
            articles_to_click = ul_element.find_elements(By.TAG_NAME, 'a')

            try:
                print(len(articles_to_click))
                driver.execute_script("arguments[0].scrollIntoView(true);", articles_to_click[article_index])
                driver.execute_script("arguments[0].click();", articles_to_click[article_index])
            except:
                actions.send_keys(Keys.PAGE_UP).perform()
                time.sleep(3)
                actions.send_keys(Keys.ARROW_UP).perform()
                time.sleep(2)
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'jupiter22-c-article-list'))
                )
                ul_element = driver.find_element(By.CLASS_NAME, 'jupiter22-c-article-list')

                WebDriverWait(ul_element, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'a'))
                )
                articles_to_click = ul_element.find_elements(By.TAG_NAME, 'a')
                driver.execute_script("arguments[0].scrollIntoView(true);", articles_to_click[article_index])
                driver.execute_script("arguments[0].click();", articles_to_click[article_index])

            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'press-release-header__title'))
                )
                h1_element = driver.find_element(By.CLASS_NAME, 'press-release-header__title')
            except:
                actions.send_keys(Keys.PAGE_UP).perform()
                time.sleep(2)

                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'jupiter22-c-article-list'))
                )
                ul_element = driver.find_element(By.CLASS_NAME, 'jupiter22-c-article-list')

                WebDriverWait(ul_element, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'a'))
                )
                articles_to_click = ul_element.find_elements(By.TAG_NAME, 'a')
                driver.execute_script("arguments[0].scrollIntoView(true);", articles_to_click[article_index])
                driver.execute_script("arguments[0].click();", articles_to_click[article_index])


            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'press-release-header__title'))
            )
            h1_element = driver.find_element(By.CLASS_NAME, 'press-release-header__title')
            file_name = h1_element.text.strip()
            file_name = re.sub(r'[^\w\s]', '', file_name).replace(' ', '_') + '.txt'
            file_path = os.path.join(folder_name, file_name)

            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'body__content'))
            )
            body_content = driver.find_element(By.CLASS_NAME, 'body__content')

            WebDriverWait(body_content, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, 'p'))
            )
            paragraphs = body_content.find_elements(By.TAG_NAME, 'p')
            accumulated_text = ''
            for paragraph in paragraphs:
                paragraph_text = paragraph.text
                accumulated_text += paragraph_text + '\n'

            if not os.path.exists(file_name):
                # Jeśli plik nie istnieje, utwórz go i zapisz w nim treść
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(accumulated_text)
                    print(f"Plik {file_name} został utworzony i zapisano w folderze {folder_name}.")
            else:
                print(f"Plik {file_name} już istnieje w folderze {folder_name}.")

            driver.back()


        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'results-info'))
        )
        numbers = driver.find_element(By.CLASS_NAME, 'results-info')
        condition = numbers.text
        if condition == '':
            actions.send_keys(Keys.PAGE_UP).perform()
            time.sleep(2)
            actions.send_keys(Keys.ARROW_UP).perform()
            time.sleep(2)
            actions.send_keys(Keys.PAGE_UP).perform()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'results-info'))
            )
            numbers = driver.find_element(By.CLASS_NAME, 'results-info')
            condition = numbers.text
            parts = condition.split()
            if parts[3] == parts[5]:
                break
        else:
            parts = condition.split()
            if parts[3] == parts[5]:
                break

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button.pagination__next[aria-label="click to go to the next page"]'))
        )
        next_button = driver.find_element(By.CSS_SELECTOR, 'button.pagination__next[aria-label="click to go to the next page"]')
        next_button.click()

    driver.back()  # Wracaj do poprzedniej strony
    time.sleep(2)  # Opcjonalne: Czekaj 2 sekundy, aby strona się załadowała

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, 'tablefield-paragraph-8371281-field_table-0'))
    )
    table = driver.find_element(By.ID, 'tablefield-paragraph-8371281-field_table-0')  # Znów znajdź tabelę

    WebDriverWait(table, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, 'a'))
    )
    links = table.find_elements(By.TAG_NAME, 'a')  # Znów znajdź linki
    links_to_click = links[1::2]  # Znów wybierz co drugi link