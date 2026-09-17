"""
skills/weather.py  —  Hava durumu bilgisi (OpenWeatherMap)
"""

import os
import logging
import requests

log = logging.getLogger("Triss.Weather")

# .env veya config.yaml'dan oku; yoksa çevre değişkeni kullan
API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Türkçe hava durumu açıklamaları
WEATHER_TR = {
    "clear sky"           : "açık ve güneşli",
    "few clouds"          : "az bulutlu",
    "scattered clouds"    : "parçalı bulutlu",
    "broken clouds"       : "çok bulutlu",
    "overcast clouds"     : "kapalı",
    "light rain"          : "hafif yağmurlu",
    "moderate rain"       : "orta şiddetli yağmurlu",
    "heavy intensity rain": "şiddetli yağmurlu",
    "thunderstorm"        : "gök gürültülü fırtına",
    "snow"                : "karlı",
    "light snow"          : "hafif karlı",
    "mist"                : "sisli",
    "fog"                 : "yoğun sisli",
    "haze"                : "puslu",
    "drizzle"             : "çiseleyen yağmur",
}


def get_weather(city: str = "İstanbul") -> str:
    """Şehir için hava durumu bilgisini döndür."""

    if not API_KEY:
        return (
            "Hava durumu servisini kullanmak için bir OpenWeatherMap API anahtarı gerekiyor. "
            "Lütfen .env dosyasına OPENWEATHER_API_KEY ekleyin. "
            "api.openweathermap.org adresinden ücretsiz alabilirsiniz."
        )

    try:
        resp = requests.get(
            BASE_URL,
            params={
                "q"     : city,
                "appid" : API_KEY,
                "units" : "metric",
                "lang"  : "tr",
            },
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()

        temp       = round(data["main"]["temp"])
        feels_like = round(data["main"]["feels_like"])
        humidity   = data["main"]["humidity"]
        desc_raw   = data["weather"][0]["description"].lower()
        desc       = WEATHER_TR.get(desc_raw, desc_raw)
        wind       = round(data["wind"]["speed"] * 3.6)  # m/s → km/h

        return (
            f"{city} için hava durumu: {desc}. "
            f"Sıcaklık {temp} derece, hissedilen {feels_like} derece. "
            f"Nem yüzde {humidity}, rüzgar saatte {wind} kilometre."
        )

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"Üzgünüm, {city} şehrini bulamadım."
        return f"Hava durumu alınamadı: {e}"
    except Exception as e:
        log.error(f"Hava durumu hatası: {e}")
        return "Hava durumu bilgisi şu an alınamıyor."
