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

    @staticmethod
    def check_bad_weather(temp,vlazh,wind,rain):
        if temp <= -40 :
            return "на улицу лучше не выходить, там слишком холодно"
        if wind>= 75:
            return "там реальный шторм, если весишь мало, то вероятнее всего летать будешь"
        if wind < 11 and temp > 15 and temp < 25 and rain < 30:
            return "идеальная погода надо на улицу"
        if temp > 40:
            if rain < 30:
                return 'выходи жарить яичницу, только сам не зажарься'
            if rain >= 30 <= 75:
                return 'жарко, но может пойдет дождь и будет кайф'
            if rain > 75:
                return 'убирай яичницу, сейчас лить будет'
        if temp >= 0 and temp <= 15:
            if wind <= 20 :
                if rain > 50:
                    return 'холодновато, оденься потеплее и возьми зонт на всякий'
                else :
                    return 'холодновато, возбми еще кофту, зонт оставь дома'
            else :
                return 'фу, холодно ветренно, я бы дома ботал лучше'
        if temp<0:
            if rain>70:
                return 'let it snow'
            else :
                if wind >= 40:
                    return 'ветер холодно в общем ботай дома'
                else :
                    return 'так-то пойдет, но холодно'
        if temp > 15 and temp<=40:
            if rain > 55:
                if wind <= 20:
                    return 'кайфовый дождик'
                else :
                    return 'ветренный не кайфовый дождик'
            else :
                if wind <=20:
                    return 'кайфовый ветер'
                else :
                    return 'не кайфовый ветер'

        return 'кхм не уверен, что могу дать точные рекомендации на счет этой погоды'


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
            temp=current['Temperature']['Metric']['Value']
            vlazh= current.get('RelativeHumidity', 0)
            wind=current['Wind']['Speed']['Metric']['Value']
            rain= self.get_chance_of_rain(location_key)
            weather = {
                'температура в градусах цельсия': temp,
                'влажность (процентное содержание)': vlazh,
                'скорость ветра': wind,
                'вероятность дождя': rain,
                'погодные условия' : self.check_bad_weather(temp,vlazh,wind,rain)
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
        print(f"оценка погоды: {weather['погодные условия']}")
    except ValueError:
        print("Пожалуйста, введите корректные числовые значения для широты и долготы.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == '__main__':
    main()