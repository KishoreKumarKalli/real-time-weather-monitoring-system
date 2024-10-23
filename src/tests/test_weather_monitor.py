import pytest
from src.weather_monitor import process_weather_data
from src.database import WeatherDB
from src.alerts import AlertSystem
import os
import json

@pytest.fixture
def sample_weather_data():
    return {
        'weather': [{'main': 'Clear'}],
        'main': {
            'temp': 308.15,  # 35°C
            'feels_like': 310.15,  # 37°C
        },
        'dt': 1600000000
    }

@pytest.fixture
def test_db():
    db = WeatherDB('test_weather.db')
    yield db
    os.remove('test_weather.db')

def test_process_weather_data(sample_weather_data):
    processed = process_weather_data(sample_weather_data)
    assert processed['main'] == 'Clear'
    assert abs(processed['temp'] - 35.0) < 0.1
    assert abs(processed['feels_like'] - 37.0) < 0.1

def test_database_operations(test_db):
    test_db.store_weather_data('Delhi', 35.0, 37.0, 'Clear', '2024-10-22 14:30:00')
    summary = test_db.get_daily_summary('Delhi', '2024-10-22')
    assert summary is not None

def test_alert_system():
    alert_system = AlertSystem()
    # Test consecutive high temperatures
    assert alert_system.check_temperature_alert('Delhi', 36.0, '2024-10-22 14:30:00') == False
    assert alert_system.check_temperature_alert('Delhi', 36.0, '2024-10-22 14:35:00') == True
