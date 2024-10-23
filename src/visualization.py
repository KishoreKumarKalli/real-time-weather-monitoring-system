import matplotlib.pyplot as plt
import pandas as pd
import os


def create_visualizations(city_data, output_dir='static/images'):
    """Generate comprehensive weather visualizations"""
    df = pd.DataFrame(city_data)

    # Temperature trends
    plt.figure(figsize=(12, 6))
    plt.plot(df['timestamp'], df['temp'], label='Temperature')
    plt.plot(df['timestamp'], df['feels_like'], label='Feels Like')
    plt.title(f'Temperature Trends')
    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/temp_trends.png')
    plt.close()

    # Weather conditions distribution
    plt.figure(figsize=(8, 6))
    df['main'].value_counts().plot(kind='pie', autopct='%1.1f%%')
    plt.title('Weather Conditions Distribution')
    plt.savefig(f'{output_dir}/weather_dist.png')
    plt.close()

    # Additional parameters
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    ax1.plot(df['timestamp'], df['humidity'], color='blue')
    ax1.set_title('Humidity Trends')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Humidity (%)')
    ax1.tick_params(axis='x', rotation=45)

    ax2.plot(df['timestamp'], df['wind_speed'], color='green')
    ax2.set_title('Wind Speed Trends')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Wind Speed (m/s)')
    ax2.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/additional_params.png')
    plt.close()