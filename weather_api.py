import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherAPI:
    """Weather API client for fetching weather data"""
    
    def __init__(self, api_key: str, api_url: str, location: str):
        self.api_key = api_key
        self.api_url = api_url
        self.location = location
        
    def get_current_weather(self) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather data for the configured location.
        
        Returns:
            dict: Weather data or None if request fails
        """
        try:
            params = {
                'q': self.location,
                'appid': self.api_key,
                'units': 'metric'  # Use metric units
            }
            
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Weather data retrieved for {self.location}")
            
            # Parse and structure the weather data
            return self._parse_weather_data(data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch weather data: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse weather data: {e}")
            return None
    
    def _parse_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw weather API response into structured format"""
        weather_info = {
            'location': data.get('name', 'Unknown'),
            'country': data.get('sys', {}).get('country', 'Unknown'),
            'temperature': data.get('main', {}).get('temp', 0.0),
            'feels_like': data.get('main', {}).get('feels_like', 0.0),
            'humidity': data.get('main', {}).get('humidity', 0),
            'pressure': data.get('main', {}).get('pressure', 0),
            'description': data.get('weather', [{}])[0].get('description', 'Unknown'),
            'icon': data.get('weather', [{}])[0].get('icon', ''),
            'wind_speed': data.get('wind', {}).get('speed', 0.0),
            'wind_direction': data.get('wind', {}).get('deg', 0),
            'clouds': data.get('clouds', {}).get('all', 0),
            'rain': data.get('rain', {}).get('1h', 0.0),
            'timestamp': datetime.now().isoformat()
        }
        return weather_info
    
    def check_for_alerts(self, weather_data: Dict[str, Any], thresholds: Dict[str, float]) -> list:
        """
        Check weather data against thresholds to determine alerts.
        
        Args:
            weather_data: Current weather data
            thresholds: Dictionary of threshold values
            
        Returns:
            list: List of alert messages
        """
        alerts = []
        
        temp = weather_data.get('temperature', 0)
        wind = weather_data.get('wind_speed', 0)
        rain = weather_data.get('rain', 0)
        
        # Temperature alerts
        if temp >= thresholds.get('high_temp', 35):
            alerts.append(f"⚠️ High Temperature Alert: {temp}°C (Threshold: {thresholds['high_temp']}°C)")
        elif temp <= thresholds.get('low_temp', 0):
            alerts.append(f"❄️ Low Temperature Alert: {temp}°C (Threshold: {thresholds['low_temp']}°C)")
        
        # Wind alerts
        if wind >= thresholds.get('high_wind', 50):
            alerts.append(f"💨 High Wind Alert: {wind} km/h (Threshold: {thresholds['high_wind']} km/h)")
        
        # Rain alerts
        if rain >= thresholds.get('high_rain', 15):
            alerts.append(f"🌧️ Heavy Rain Alert: {rain} mm/h (Threshold: {thresholds['high_rain']} mm/h)")
        
        return alerts
