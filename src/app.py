from flask import Flask, render_template, jsonify, request
from weather_monitor import get_weather_data, process_weather_data, aggregate_daily_data
from datetime import datetime, timedelta
from database import WeatherDB
import requests
import json
import pandas as pd

# Load config
with open('config/config.json') as config_file:
    config = json.load(config_file)

app = Flask(__name__)
db = WeatherDB()

CITIES = config.get('cities', ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad'])
API_KEY = config['api_key']


def get_city_weather(city):
    try:
        # Get current weather
        current_data = get_weather_data(city)
        processed_data = process_weather_data(current_data)

        # Store in database
        db.store_weather_data(
            city=city,
            temp=processed_data['temp'],
            feels_like=processed_data['feels_like'],
            humidity=processed_data['humidity'],
            pressure=processed_data['pressure'],
            wind_speed=processed_data['wind_speed'],
            condition=processed_data['main'],
            timestamp=processed_data['timestamp']
        )

        # Calculate trend using historical data
        historical_data = db.get_historical_data(city, days=1)
        if not historical_data.empty:
            prev_temp = historical_data.iloc[-2]['temp'] if len(historical_data) > 1 else historical_data.iloc[0]['temp']
            trend = {
                'direction': '↑' if processed_data['temp'] > prev_temp else '↓',
                'value': abs(processed_data['temp'] - prev_temp)
            }
        else:
            trend = {
                'direction': '-',
                'value': 0
            }

        # Get daily summary from database
        current_date = datetime.now().date()
        daily_summary = db.update_daily_summary(city, current_date)

        if not daily_summary:
            daily_summary = {
                'max_temp': processed_data['temp'],
                'min_temp': processed_data['temp'],
                'avg_temp': processed_data['temp'],
                'avg_humidity': processed_data['humidity'],
                'avg_wind_speed': processed_data['wind_speed'],
                'dominant_condition': processed_data['main']
            }

        # Check for alerts
        alerts = []
        temp_threshold = config.get('temp_threshold', 35)
        if processed_data['temp'] > temp_threshold:
            alerts.append(f"⚠️ Temperature exceeded {temp_threshold}°C at {processed_data['timestamp']}")

        # Add humidity alert
        if processed_data['humidity'] > 80:
            alerts.append(f"⚠️ High humidity ({processed_data['humidity']}%) at {processed_data['timestamp']}")

        return {
            'current': processed_data,
            'trend': trend,
            'daily_summary': daily_summary,
            'alerts': alerts
        }
    except Exception as e:
        print(f"Error fetching data for {city}: {str(e)}")
        return None


@app.route('/')
def dashboard():
    return render_template('dashboard.html', cities=CITIES)


@app.route('/api/weather/<city>')
def get_weather_for_city(city):
    if city not in CITIES:
        return jsonify({'error': 'City not found'}), 404

    weather_data = get_city_weather(city)
    if weather_data is None:
        return jsonify({'error': 'Failed to fetch weather data'}), 500

    return jsonify(weather_data)


@app.route('/api/historical/<city>')
def get_historical_data(city):
    if city not in CITIES:
        return jsonify({'error': 'City not found'}), 404

    db = WeatherDB()
    historical_data = db.get_historical_data(city)

    if historical_data.empty:
        return jsonify({'error': 'No historical data found'}), 404

    return jsonify(historical_data.to_dict(orient='records'))


@app.route('/api/forecast/<city>')
def get_forecast(city):
    if city not in CITIES:
        return jsonify({'error': 'City not found'}), 404

    try:
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric',
            'cnt': 5  # 5-day forecast
        }
        response = requests.get(
            'http://api.openweathermap.org/data/2.5/forecast',
            params=params
        )
        forecast_data = response.json()

        processed_forecast = []
        for item in forecast_data['list']:
            processed_forecast.append({
                'timestamp': datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d %H:%M:%S'),
                'temp': item['main']['temp'],
                'condition': item['weather'][0]['main'],
                'humidity': item['main']['humidity'],
                'wind_speed': item['wind']['speed']
            })

        return jsonify(processed_forecast)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/summary/<city>')
def get_city_summary(city):
    if city not in CITIES:
        return jsonify({'error': 'City not found'}), 404

    try:
        # Get current date
        current_date = datetime.now().date()

        # Get daily summary from database
        summary = db.get_daily_summary(city, current_date)

        if summary is None:
            return jsonify({'error': 'No summary data available'}), 404

        return jsonify({
            'date': current_date.strftime('%Y-%m-%d'),
            'avg_temp': summary[3],  # Adjust index based on your database schema
            'max_temp': summary[4],
            'min_temp': summary[5],
            'avg_humidity': summary[6],
            'avg_wind_speed': summary[7],
            'dominant_condition': summary[8]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
