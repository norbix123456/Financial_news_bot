from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
import re

driver = webdriver.Chrome()

driver.get("https://www.nasdaq.com/market-activity/quotes/press-releases")

WebDriverWait(driver , 5).until(
    EC.presence_of_element_located((By.XPATH, '//button[@id="onetrust-accept-btn-handler"]'))
)

acceptance = driver.find_element(By.XPATH, '//button[@id="onetrust-accept-btn-handler"]')
acceptance.click()

table = driver.find_element(By.ID, 'tablefield-paragraph-8371281-field_table-0')

links = table.find_elements(By.TAG_NAME, 'a')

links_to_click = links[1::2]

for index, link in enumerate(links_to_click):
    link.click()
    try:
        div_element = driver.find_element(By.CLASS_NAME, 'jupiter22-c-nav__title')
    except:
        driver.refresh()
        table = driver.find_element(By.ID, 'tablefield-paragraph-8371281-field_table-0')
        links = table.find_elements(By.TAG_NAME, 'a')
        links_to_click = links[1::2]
        links_to_click[index].click()

    div_element = driver.find_element(By.CLASS_NAME, 'jupiter22-c-nav__title')

    h3_element = div_element.find_element(By.TAG_NAME, 'h3')

    # Pobierz tekst z h3 tagu
    text_content = h3_element.text.strip()

    # Utwórz folder o nazwie "AMD", jeśli jeszcze nie istnieje
    folder_name = text_content
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    os.chdir(folder_name)
    # time.sleep(3)  # Opcjonalne: Czekaj 3 sekundy, aby strona się załadowała
    # driver.refresh()
    # link.click()
    while True:
        ul_element = driver.find_element(By.CSS_SELECTOR,
                                         'ul.jupiter22-c-article-list__list.show-border[data-view-display="related_press_releases_symbol"]')
        articles_to_click = ul_element.find_elements(By.TAG_NAME, 'a')
        for article_index in range(len(articles_to_click)):
            articles_to_click[article_index].click()
            #time.sleep(3)  # Opcjonalne: Czekaj 3 sekundy, aby strona się załadowała

            try:
                h1_element = driver.find_element(By.CLASS_NAME, 'press-release-header__title')
            except:
                driver.refresh()
                ul_element = driver.find_element(By.CSS_SELECTOR,
                                                 'ul.jupiter22-c-article-list__list.show-border[data-view-display="related_press_releases_symbol"]')
                articles_to_click = ul_element.find_elements(By.TAG_NAME, 'a')
                articles_to_click[article_index].click()

            h1_element = driver.find_element(By.CLASS_NAME, 'press-release-header__title')
            file_name = h1_element.text.strip()
            file_name = re.sub(r'[^\w\s]', '', file_name).replace(' ', '_') + '.txt'
            file_path = os.path.join(folder_name, file_name)
            body_content = driver.find_element(By.CLASS_NAME, 'body__content')
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
            # try:
            #     ul_element = driver.find_element(By.CSS_SELECTOR,
            #                                      'ul.jupiter22-c-article-list__list.show-border[data-view-display="related_press_releases_symbol"]')
            # except:
            #     driver.refresh()

            ul_element = driver.find_element(By.CSS_SELECTOR,
                                             'ul.jupiter22-c-article-list__list.show-border[data-view-display="related_press_releases_symbol"]')
            articles_to_click = ul_element.find_elements(By.TAG_NAME, 'a')


        numbers = driver.find_element(By.CLASS_NAME, 'results-info')
        condition = numbers.text
        parts = condition.split()
        if parts[3] == parts[5]:
            break
        next_button = driver.find_element(By.CSS_SELECTOR, 'button.pagination__next[aria-label="click to go to the next page"]')
        next_button.click()


    # < div
    #
    #
    # class ="results-info" tabindex="-1" > Showing 301 - 308 of 308 < /div >

    driver.back()  # Wracaj do poprzedniej strony
    time.sleep(2)  # Opcjonalne: Czekaj 2 sekundy, aby strona się załadowała
    table = driver.find_element(By.ID, 'tablefield-paragraph-8371281-field_table-0')  # Znów znajdź tabelę
    links = table.find_elements(By.TAG_NAME, 'a')  # Znów znajdź linki
    links_to_click = links[1::2]  # Znów wybierz co drugi link

# <h1 class="press-release-header__title">
#
#
# class ="timestamp" ><div class="timestamp__label">Published</div>

#<button class="pagination__next" aria-label="click to go to the next page"></button>