import requests
import json
from datetime import datetime
import pandas as pd

API_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

with open('config/config.json') as config_file:
    config = json.load(config_file)
API_KEY = config['api_key']


def get_weather_data(city):
    params = {'q': city, 'appid': API_KEY, 'units': 'metric'}
    response = requests.get(API_URL, params=params)
    return response.json()


def get_forecast_data(city):
    params = {'q': city, 'appid': API_KEY, 'units': 'metric', 'cnt': 5}
    response = requests.get(FORECAST_URL, params=params)
    return response.json()


def process_weather_data(weather_data):
    """Enhanced weather data processing with additional parameters"""
    main = weather_data['weather'][0]['main']
    temp = weather_data['main']['temp']
    feels_like = weather_data['main']['feels_like']
    humidity = weather_data['main'].get('humidity', 0)
    pressure = weather_data['main'].get('pressure', 0)
    wind_speed = weather_data.get('wind', {}).get('speed', 0)
    timestamp = datetime.fromtimestamp(weather_data['dt']).strftime('%Y-%m-%d %H:%M:%S')

    return {
        'main': main,
        'temp': temp,
        'feels_like': feels_like,
        'humidity': humidity,
        'pressure': pressure,
        'wind_speed': wind_speed,
        'timestamp': timestamp
    }


def aggregate_daily_data(data):
    df = pd.DataFrame(data)
    return {
        'avg_temp': df['temp'].mean(),
        'max_temp': df['temp'].max(),
        'min_temp': df['temp'].min(),
        'avg_humidity': df['humidity'].mean(),
        'avg_wind_speed': df['wind_speed'].mean(),
        'dominant_condition': df['main'].mode()[0]
    }