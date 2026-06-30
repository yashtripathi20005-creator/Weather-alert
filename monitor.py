import time
import logging
from typing import Dict, Any, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherMonitor:
    """Monitors weather conditions and triggers alerts when thresholds are exceeded"""
    
    def __init__(self, weather_api, notification_service, config):
        self.weather_api = weather_api
        self.notification_service = notification_service
        self.config = config
        self.last_alert_time = {}
        self.alert_cooldown = 600  # 10 minutes cooldown for repeated alerts
        
    def run_check(self) -> None:
        """Perform a single weather check and send alerts if necessary"""
        logger.info("Checking weather conditions...")
        
        # Fetch current weather
        weather_data = self.weather_api.get_current_weather()
        
        if not weather_data:
            logger.error("Failed to fetch weather data, skipping check")
            return
        
        # Check for alerts
        alerts = self.weather_api.check_for_alerts(
            weather_data,
            self.config.ALERT_THRESHOLDS
        )
        
        if alerts:
            # Apply cooldown to prevent alert spam
            alerts_to_send = self._apply_cooldown(alerts)
            
            if alerts_to_send:
                self.notification_service.send_alerts(alerts_to_send, weather_data)
                self._update_cooldown(alerts_to_send)
            else:
                logger.info("Alerts detected but in cooldown period")
        else:
            logger.info("No alerts detected")
            
        return weather_data
    
    def _apply_cooldown(self, alerts: List[str]) -> List[str]:
        """
        Apply cooldown to prevent sending the same alert repeatedly.
        
        Args:
            alerts: List of alert messages
            
        Returns:
            List of alerts that can be sent
        """
        current_time = time.time()
        alerts_to_send = []
        
        for alert in alerts:
            alert_key = alert.split('(')[0].strip()  # Use alert type as key
            
            if alert_key not in self.last_alert_time:
                alerts_to_send.append(alert)
            elif current_time - self.last_alert_time[alert_key] > self.alert_cooldown:
                alerts_to_send.append(alert)
                
        return alerts_to_send
    
    def _update_cooldown(self, alerts: List[str]) -> None:
        """Update the cooldown timestamps for sent alerts"""
        current_time = time.time()
        
        for alert in alerts:
            alert_key = alert.split('(')[0].strip()
            self.last_alert_time[alert_key] = current_time
    
    def run_continuous(self) -> None:
        """Run the monitor continuously with the configured interval"""
        logger.info(f"Starting continuous monitoring (interval: {self.config.ALERT_CHECK_INTERVAL}s)")
        
        while True:
            try:
                self.run_check()
                time.sleep(self.config.ALERT_CHECK_INTERVAL)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait a minute before retrying on error
