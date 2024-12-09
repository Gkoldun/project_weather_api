import requests
from flask import Flask, render_template, request, redirect, url_for, flash
ъ
app = Flask(__name__)
class AccuWeatherClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://dataservice.accuweather.com"

    def get_location_key(self, city_name):
        url = f"{self.base_url}/locations/v1/cities/search"
        params = {
            'apikey': self.api_key,
            'q': city_name,
            'language': 'ru-ru',
            'details': 'false',
            'offset': '0'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                location_key = data[0]['Key']
                return location_key
            else:
                raise Exception(f"Город '{city_name}' не найден.")
        else:
            raise Exception(f"Ошибка при поиске города '{city_name}': {response.status_code} - {response.text}")


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
            if rain >= 30 and rain<= 75:
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


    def get_current_weather(self, city_name):
        location_key = self.get_location_key(city_name)
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
            rain=current.get('PrecipitationProbability', 0)
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


API_KEY = '7pAa2btQjQ2JzkZ84kNLTytTBOZJLpcb'
weather_client = AccuWeatherClient(API_KEY)


@app.route('/', methods=['GET'])
def home():
    return render_template('form.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    start_city = request.form.get('start_city')
    end_city = request.form.get('end_city')

    try:
        if not start_city or not end_city:
            raise Exception("Необходимо указать названия начальной и конечной точек маршрута.")
        start_weather = weather_client.get_current_weather(start_city)
        end_weather = weather_client.get_current_weather(end_city)
        return render_template('result.html',
                               start_city=start_city,
                               end_city=end_city,
                               start_weather=start_weather,
                               end_weather=end_weather,)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        flash(str(e), 'error')
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)