import schedule
import time
from datetime import datetime
from weather_monitor import get_weather_data, process_weather_data
from database import WeatherDB
from alerts import AlertSystem
import json


class WeatherScheduler:
    def __init__(self):
        with open('../config/config.json') as f:
            self.config = json.load(f)

        self.db = WeatherDB()
        self.alert_system = AlertSystem()
        self.cities = self.config['cities']

    def fetch_and_process_city(self, city):
        try:
            # Fetch weather data
            data = get_weather_data(city)
            processed_data = process_weather_data(data)

            # Store in database
            self.db.store_weather_data(
                city=city,
                temp=processed_data['temp'],
                feels_like=processed_data['feels_like'],
                condition=processed_data['main'],
                timestamp=processed_data['timestamp']
            )

            # Update daily summary
            current_date = datetime.now().date()
            self.db.update_daily_summary(city, current_date)

            # Check for alerts
            self.alert_system.check_temperature_alert(
                city,
                processed_data['temp'],
                processed_data['timestamp']
            )

        except Exception as e:
            print(f"Error processing data for {city}: {str(e)}")

    def run(self):
        # Schedule jobs for each city
        interval = self.config.get('update_interval', 300)  # default 5 minutes

        for city in self.cities:
            schedule.every(interval).seconds.do(self.fetch_and_process_city, city)

        print(f"Started weather monitoring for cities: {', '.join(self.cities)}")
        print(f"Update interval: {interval} seconds")

        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    scheduler = WeatherScheduler()
    scheduler.run()