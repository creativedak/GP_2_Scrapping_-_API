from selenium import webdriver  # импортируем Selenium
from selenium.webdriver.chrome.options import Options  # импортируем настройки Chrome
from selenium.webdriver.common.by import By  # импортируем способ поиска элементов
import pandas as pd  # импортируем pandas для таблицы
import time  # импортируем time для ожидания загрузки
import re  # импортируем re для поиска координат
import logging

logging.basicConfig(level=logging.INFO, filename="parser.log", filemode="w", format="%(asctime)s %(levelname)s %(message)s", encoding="utf-8")

options = Options()  # создаем настройки браузера
# options.add_argument("--headless=new")  # запускаем без открытия окна
options.add_argument("--no-sandbox")  # служебная настройка
options.add_argument("--disable-dev-shm-usage")  # служебная настройка
options.add_argument("--window-size=1000,600")  # задаем размер окна
options.add_argument("--blink-settings=imagesEnabled=false") #вырубили картинки
options.add_argument("--disable-renderer-backgrounding")
prefs = {
    "profile.managed_default_content_settings.images": 2,
    "profile.default_content_setting_values.notifications": 2
}

options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=options)  # создаем браузер

all_links = pd.read_csv("final_urls.csv")["ссылка"].tolist()
rows = []  # список для итоговой таблицы
ok = 1

for link in all_links:
    latitude = None
    longitude = None
    price = None
    metro = None
    total_area = None
    pot = None
    floor_apart = None
    floor_house = None
    year = None
    description = None
    year_author = None

    driver.get(link)
    time.sleep(1)

    page_source = driver.page_source
    coord = re.search(r'll=([\d.]+),([\d.]+)', page_source)
    if coord:
        longitude = coord.group(1)
        latitude = coord.group(2)

    price = driver.find_elements(By.XPATH, '//h1/following::div[contains(text(),"₽")][1]')
    if len(price) > 0:
        price = int(driver.find_element(By.XPATH, '//h1/following::div[contains(text(),"₽")][1]').text.split("₽")[0].replace("\xa0", " ").replace(" ", ""))

    metro = driver.find_elements(By.CSS_SELECTOR, 'span[class*="MetroStation__title"]')
    if len(metro) > 0:
        metro = metro[0].text

    total_area = driver.find_elements(By.XPATH, '//div[text()="общая"]')
    if len(total_area) > 0:
        total_area = float(driver.find_element(By.XPATH, '//div[text()="общая"]').find_element(By.XPATH,'./preceding-sibling::div[1]').text.replace("м²", "").replace(",", "."))

    pot = driver.find_elements(By.XPATH, '//div[contains(text(), "потолки")]')
    if len(pot) > 0:
        pot = float(driver.find_element(By.XPATH, '//div[contains(text(), "потолки")]').find_element(By.XPATH, './preceding-sibling::div[1]').text.replace(",", ".").replace("м", "").strip())

    floor = driver.find_elements(By.XPATH, '//span[contains(text(),"этаж")]')
    if len(floor) > 0:
        try:
            floor = driver.find_element(By.XPATH, '//span[contains(text(),"этаж")]').text.split(",")[-1].replace("этаж", "").strip().split("/")
            floor_house = int(floor[-1])
            floor_apart = int(floor[0])
        except:
            floor_house = None
            floor_apart = None

    year = driver.find_elements(By.CSS_SELECTOR, 'div[class*="OfferCardHighlight__value"]')
    if len(year) > 0:
        year = driver.find_elements(By.CSS_SELECTOR, 'div[class*="OfferCardHighlight__value"]')[-1].text.split(" ")[0]

    description = driver.find_elements(By.CSS_SELECTOR, 'p[class*="OfferCardTextDescription__text"]')
    if len(description) > 0:
        description = description[0].get_attribute("textContent")

    author_name = driver.find_elements(By.CSS_SELECTOR, 'h2[class*="OfferCardAuthorStats__authorName"]')
    if len(author_name) > 0:
        author_name = author_name[0].text

    rows.append({"ссылка": link, "широта": latitude, "долгота": longitude, "цена": price, "метро": metro, "общая площадь": total_area, "этаж квартиры": floor_apart, "этажность дома": floor_house, "потолки": pot, "год": year, "описание": description, "имя застройщика": author_name})
    logging.info({"ссылка": link, "широта": latitude, "долгота": longitude, "цена": price, "метро": metro, "общая площадь": total_area, "этаж квартиры": floor_apart, "этажность дома": floor_house, "потолки": pot, "год": year, "имя застройщика": author_name})
    print(ok, "Добавлено:", link, latitude, longitude, price, metro, total_area, floor_apart, floor_house, pot, year, author_name)
    ok+=1

df = pd.DataFrame(rows)
df.to_csv("KVARTIRI.csv", index=False)

driver.quit()