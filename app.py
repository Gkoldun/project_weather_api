import requests
from flask import Flask, jsonify, request


class AccuWeatherClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://dataservice.accuweather.com"

    def get_location_key(self, lat, long):
        url = f"{self.base_url}/locations/v1/cities/geoposition/search"
        params = {
            'apikey': self.api_key,
            'q': f"{lat},{long}"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            location_key = data.get('Key')
            if not location_key:
                raise Exception("Не удалось получить ключ местоположения.")
            return location_key
        else:
            raise Exception(f"Ошибка при получении ключа местоположения: {response.status_code} - {response.text}")

    def get_current_weather(self, latitude, longitude):
        location_key = self.get_location_key(latitude, longitude)
        url = f"{self.base_url}/currentconditions/v1/{location_key}"
        params = {
            'apikey': self.api_key,
            'details': 'true'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if not data:
                raise Exception("Нет данных о текущей погоде.")
            current = data[0]
            weather = {
                'температура в градусах цельсия': current['Temperature']['Metric']['Value'],
                'влажность (процентное содержание)': current.get('RelativeHumidity', 0),
                'скорость ветра': current['Wind']['Speed']['Metric']['Value'],
                'вероятность дождя': self.get_chance_of_rain(location_key)
            }
            return weather
        else:
            raise Exception(f"Ошибка при получении данных о погоде: {response.status_code} - {response.text}")

    def get_chance_of_rain(self, location_key):
        url = f"{self.base_url}/forecasts/v1/daily/1day/{location_key}"
        params = {
            'apikey': self.api_key,
            'metric': 'true'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            daily_forecasts = data.get('DailyForecasts')
            if not daily_forecasts:
                raise Exception('Нет данных о прогнозе погоды')
            precipitation = daily_forecasts[0].get('Day', {}).get('PrecipitationProbability', 0)
            return precipitation
        else:
            raise Exception(f"Ошибка при получении вероятности дождя: {response.status_code} - {response.text}")


def main():
    API_KEY = 'To9kdnWqK8aLNc9upCNUVHIlmMnlZPdd'
    weather_client = AccuWeatherClient(API_KEY)

    try:
        latitude = float(input("Введите широту: ").strip())
        longitude = float(input("Введите долготу: ").strip())

        weather = weather_client.get_current_weather(latitude, longitude)

        print("\nТекущая погода:")
        print(f"Температура: {weather['температура в градусах цельсия']}°C")
        print(f"Влажность: {weather['влажность (процентное содержание)']}%")
        print(f"Скорость ветра: {weather['скорость ветра']} км/ч")
        print(f"Вероятность дождя: {weather['вероятность дождя']}%")

    except ValueError:
        print("Пожалуйста, введите корректные числовые значения для широты и долготы.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == '__main__':
    main()