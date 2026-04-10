from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import time



all_links = set()  # список для ссылок
all_links2 = []
rows = []  # список для итоговой таблицы

start_page = 1  # первая страница
end_page = 700  # последняя страница

for i in range (1, 11):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-features=Translate,BackForwardCache,AcceptCHFrame")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--window-size=1280,720")
    options.add_argument("--hide-scrollbars")
    driver = webdriver.Chrome(options=options)

    url = f"https://realty.yandex.ru/moskva/kupit/kvartira/?floorMax={i}&floorMin={i}"
    driver.get(url)
    time.sleep(3)
    for page_num in range(1, 25):  # цикл по страницам
        print("Уникальных:", len(all_links), "| Всего:", len(all_links2), "| Страница:", page_num, "| Этаж:", i)
        cards = driver.find_elements(By.CSS_SELECTOR, 'li[data-seo="snippet"]')  # ищем карточки
        for card in cards:  # идем по карточкам на странице
            try:
                link = card.find_element(By.CSS_SELECTOR, 'a[href*="/offer/"]').get_attribute("href")  # берем ссылку
                if link:
                    all_links.add(link)
                    all_links2.append(link)
            except:
                continue

        pager_links = driver.find_elements(By.CSS_SELECTOR, 'a.Pager__radio-link')
        next_button = None

        for link_btn in pager_links:
            if "Следующая" in link_btn.text:
                next_button = link_btn
                break

        if next_button is None:
            print("Кнопка 'Следующая' не найдена")
            break
        time.sleep(3)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
        next_button.click()
        time.sleep(3)
    driver.quit()

# all_links = list(dict.fromkeys(all_links))
print("Кол-во ссылок в массиве:", len(all_links))
print("Кол-во ссылок в массиве:", len(all_links2))

all_links = list(all_links)
df = pd.DataFrame({"ссылка": all_links})
df.to_excel("links.xlsx", index=False)
df.to_csv("links.csv", index=False)

df = pd.DataFrame({"ссылка": all_links2})
df.to_excel("links2.xlsx", index=False)
df.to_csv("links2.csv", index=False)

