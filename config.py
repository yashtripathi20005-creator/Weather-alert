import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for Weather Alert Notifier"""
    
    # Weather API
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    WEATHER_API_URL = os.getenv('WEATHER_API_URL', 'http://api.openweathermap.org/data/2.5/weather')
    
    # Alert Settings
    ALERT_CHECK_INTERVAL = int(os.getenv('ALERT_CHECK_INTERVAL', 300))
    LOCATION = os.getenv('LOCATION', 'London,UK')
    
    # Email Settings
    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    ALERT_RECIPIENT = os.getenv('ALERT_RECIPIENT')
    
    # Push Notification
    PUSHBULLET_API_KEY = os.getenv('PUSHBULLET_API_KEY')
    
    # Console Alerts
    ENABLE_CONSOLE_ALERTS = os.getenv('ENABLE_CONSOLE_ALERTS', 'true').lower() == 'true'
    
    # Weather alert thresholds (in Celsius)
    ALERT_THRESHOLDS = {
        'high_temp': 35,  # degrees Celsius
        'low_temp': 0,    # degrees Celsius
        'high_wind': 50,  # km/h
        'high_rain': 15,  # mm per hour
    }
