import requests
import time
import pandas as pd
import logging

a = 991+990+1+900  # начальный индекс объекта
b = 2950  # конечный индекс объекта

logging.basicConfig(level=logging.INFO, filename=f"API_logs_{a}-{b}.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding="utf-8")
logging.getLogger().addHandler(logging.StreamHandler()) #мы хотим выводить логи в консоль

geoapify_keys = [''] #массив с несколькими API ключами geoapify
api_ninjas = [''] #массив с несколькими API ключами api ninjas
WALKSCORE_API_KEY = ""

REVERSE_GEOCODE_URL = "https://api.geoapify.com/v1/geocode/reverse"
GEOAPIFY_PLACES_URL = "https://api.geoapify.com/v2/places"
WALKSCORE_URL = "https://api.walkscore.com/score"
API_AIR_URL = "https://api.api-ninjas.com/v1/airquality"
GEOAPIFY_ROUTING_URL = "https://api.geoapify.com/v1/routing"

# Координаты центра москвы, потребуется нам позже
center_lat = 55.75405
center_lon = 37.6204


# API для получения адресса в международном формате
def get_adress(lat: float, lon: float):
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "apiKey": GEOAPIFY_API_KEY,
    }
    try:
        data = requests.get(REVERSE_GEOCODE_URL, params)
        results = data.json()['results']
        results = results[0]
        return {
            'housenumber': results['housenumber'],
            'street': results['street'],
            "state": results["state"],
            "country": results["country"],
            "postcode": results["postcode"],
        }
    except Exception as e:
        logging.error(f"Ошибка при запросе адреса: {e}")
        return {
            'housenumber': '',
            'street': '',
            "state": '',
            "country": '',
            "postcode": '',
        }


# API - качество района для пешей ходьбы
def get_walk_score(adress, lat, lon):  # Обязательно нужен сначала адресс

    params = {
        'address': adress,
        'lat': lat,
        'lon': lon,
        'wsapikey': WALKSCORE_API_KEY,
        'format': 'json'
    }
    try:
        response = requests.get(WALKSCORE_URL, params=params)

        data = response.json()
        return {
            'walkscore': data.get('walkscore')
        }
    except Exception as e:
        logging.error(f"Ошибка при запросе walkscore: {e}")
        return {
            'walkscore': None
        }


# API - качество воздуха
def get_air_quality(lat, lon):
    headers = {'X-Api-Key': API_NINJAS_KEY}
    params = {
        'lat': lat,
        'lon': lon
    }
    try:
        response = requests.get(API_AIR_URL, params=params, headers=headers)
        data = response.json()
        if 'overall_aqi' in data:

            return data['overall_aqi']
        else:

            return None
    except Exception as e:
        logging.error(f"Ошибка при запросе качества воздуха: {e}")
        return None


# API - количество мест поблизости
def get_places_nearby(lat, lon):
    categories = [
        "catering.cafe",
        "catering.restaurant",
        "education.school",
        "leisure.park",
        "commercial.supermarket",
        "public_transport",
    ]

    params = {
        "apiKey": GEOAPIFY_API_KEY,
        "categories": ",".join(categories),
        "filter": f"circle:{lon},{lat},1000",
    }
    try:
        response = requests.get(GEOAPIFY_PLACES_URL, params=params, timeout=10)
        data = response.json().get("features", [])

        cafe_count = 0
        restaurant_count = 0
        school_count = 0
        park_count = 0
        supermarket_count = 0
        public_transport_count = 0

        for d in data:
            property = d.get("properties", {})
            category = property.get("categories", []) or []
            category_str = " ".join(category)  # делаём всё в одну строку, чтобы потом посчитать транспорт (подстроки)

            if "catering.cafe" in category:
                cafe_count += 1
            if "catering.restaurant" in category:
                restaurant_count += 1
            if "education.school" in category:
                school_count += 1
            if "leisure.park" in category:
                park_count += 1
            if "commercial.supermarket" in category:
                supermarket_count += 1
            if "public_transport" in category_str:
                public_transport_count += 1

        return {
            "geo_cafe_count_1km": cafe_count,
            "geo_restaurant_count_1km": restaurant_count,
            "geo_school_count_1km": school_count,
            "geo_park_count_1km": park_count,
            "geo_supermarket_count_1km": supermarket_count,
            "geo_public_transport_count_1km": public_transport_count,
        }
    except Exception as e:
        logging.error(f"Ошибка при запросе мест поблизости: {e}")
        return {
            "geo_cafe_count_1km": None,
            "geo_restaurant_count_1km": None,
            "geo_school_count_1km": None,
            "geo_park_count_1km": None,
            "geo_supermarket_count_1km": None,
            "geo_public_transport_count_1km": None,
        }


# API - удаленность от центра в временном выражении
def get_route_to_center(lat, lon, center_lat, center_lon, mode):
    params = {
        'waypoints': f'{lat},{lon}|{center_lat},{center_lon}',
        'mode': mode,
        'apiKey': GEOAPIFY_API_KEY
    }
    try:
        response = requests.get(GEOAPIFY_ROUTING_URL, params=params)
        data = response.json()

        return {
            'geo_time_to_center_min': round(data['features'][0]['properties']['time'] / 60, 2)
        }
    except Exception as e:
        logging.error(f"Ошибка при запросе удаленности от центра: {e}")
        return {
            'geo_time_to_center_min': None
        }


# Берем наш датасет
df = pd.read_csv('kvartiri.csv')

df = df.iloc[a:b + 1]
GEOAPIFY_API_KEY = geoapify_keys[0]
API_NINJAS_KEY = api_ninjas[0]

for i in df.index:
    lat = df.loc[
        i, 'широта']  # берем широту и долготу потому что дальше все запросы по API будут именно с этими параметрами
    lon = df.loc[i, 'долгота']
    if pd.isna(lat) or pd.isna(lon):  # скипаем если у нас
        continue
    adress = ', '.join(get_adress(lat, lon).values())
    df.loc[i, 'адресс'] = adress
    df.loc[i, 'качество воздуха'] = get_air_quality(lat, lon)
    df.loc[i, 'оценка пешей доступности'] = get_walk_score(adress, lat, lon)['walkscore']
    df.loc[i, 'время до центра в минутах'] = get_route_to_center(lat, lon, center_lat, center_lon, mode='drive')[
        'geo_time_to_center_min']
    resp = get_places_nearby(lat, lon)
    df.loc[i, "количество кафе в радиусе 1 км"] = resp["geo_cafe_count_1km"]
    df.loc[i, "количество ресторанов в радиусе 1 км"] = resp["geo_restaurant_count_1km"]
    df.loc[i, "количество школ в радиусе 1 км"] = resp["geo_school_count_1km"]
    df.loc[i, "количество парков в радиусе 1 км"] = resp["geo_park_count_1km"]
    df.loc[i, "количество супермаркетов в радиусе 1 км"] = resp["geo_supermarket_count_1km"]
    df.loc[i, "количество общественного транспорта в радиусе 1 км"] = resp["geo_public_transport_count_1km"]
    logging.info(f"Объект обработан: {df.loc[i, 'ссылка']} | всего объектов сейчас {i+1}")
    time.sleep(0.2)

df.to_csv(f'kvartiri_with_api{a}-{b}.csv')