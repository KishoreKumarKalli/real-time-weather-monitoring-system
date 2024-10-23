import sqlite3
from datetime import datetime, timedelta
import pandas as pd

class WeatherDB:
    def __init__(self, db_path='weather.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Weather data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT,
                    temp REAL,
                    feels_like REAL,
                    humidity REAL,
                    pressure REAL,
                    wind_speed REAL,
                    condition TEXT,
                    timestamp DATETIME
                )
            ''')
            # Daily summaries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT,
                    date DATE,
                    avg_temp REAL,
                    max_temp REAL,
                    min_temp REAL,
                    avg_humidity REAL,
                    avg_wind_speed REAL,
                    dominant_condition TEXT
                )
            ''')
            conn.commit()

    def store_weather_data(self, city, temp, feels_like, humidity, pressure, wind_speed, condition, timestamp):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO weather_data 
                (city, temp, feels_like, humidity, pressure, wind_speed, condition, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (city, temp, feels_like, humidity, pressure, wind_speed, condition, timestamp))
            conn.commit()

    def update_daily_summary(self, city, date):
        with sqlite3.connect(self.db_path) as conn:
            # Get all weather data for the day
            df = pd.read_sql_query('''
                SELECT temp, humidity, wind_speed, condition
                FROM weather_data
                WHERE city = ? AND date(timestamp) = ?
            ''', conn, params=(city, date))

            if not df.empty:
                dominant_condition = df['condition'].mode()[0]
                summary = {
                    'avg_temp': df['temp'].mean(),
                    'max_temp': df['temp'].max(),
                    'min_temp': df['temp'].min(),
                    'avg_humidity': df['humidity'].mean(),
                    'avg_wind_speed': df['wind_speed'].mean(),
                    'dominant_condition': dominant_condition
                }

                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_summaries
                    (city, date, avg_temp, max_temp, min_temp, avg_humidity, 
                     avg_wind_speed, dominant_condition)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (city, date, summary['avg_temp'], summary['max_temp'],
                     summary['min_temp'], summary['avg_humidity'],
                     summary['avg_wind_speed'], summary['dominant_condition']))
                conn.commit()
                return summary
            return None

    def get_daily_summary(self, city, date):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM daily_summaries
                WHERE city = ? AND date = ?
            ''', (city, date))
            return cursor.fetchone()

    def get_historical_data(self, city, days=7):
        with sqlite3.connect(self.db_path) as conn:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            return pd.read_sql_query('''
                SELECT * FROM weather_data
                WHERE city = ? AND date(timestamp) >= ?
                ORDER BY timestamp ASC
            ''', conn, params=(city, start_date))