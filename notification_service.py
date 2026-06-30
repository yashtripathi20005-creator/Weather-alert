import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending weather alerts through various channels"""
    
    def __init__(self, config):
        self.config = config
        self.console_enabled = config.ENABLE_CONSOLE_ALERTS
        self.email_enabled = all([
            config.SMTP_HOST,
            config.SMTP_USER,
            config.SMTP_PASSWORD,
            config.ALERT_RECIPIENT
        ])
        self.pushbullet_enabled = bool(config.PUSHBULLET_API_KEY)
        
    def send_alerts(self, alerts: List[str], weather_data: dict) -> None:
        """
        Send alerts through all configured channels.
        
        Args:
            alerts: List of alert messages
            weather_data: Current weather data
        """
        if not alerts:
            logger.info("No alerts to send")
            return
        
        logger.info(f"Sending {len(alerts)} alerts")
        
        # Send through each enabled channel
        if self.console_enabled:
            self._send_console_alerts(alerts, weather_data)
        
        if self.email_enabled:
            self._send_email_alerts(alerts, weather_data)
        
        if self.pushbullet_enabled:
            self._send_pushbullet_alerts(alerts, weather_data)
    
    def _send_console_alerts(self, alerts: List[str], weather_data: dict) -> None:
        """Print alerts to console"""
        print("\n" + "="*60)
        print("🔔 WEATHER ALERT NOTIFICATION")
        print("="*60)
        print(f"📍 Location: {weather_data['location']}, {weather_data['country']}")
        print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌡️ Temperature: {weather_data['temperature']}°C")
        print(f"💨 Wind Speed: {weather_data['wind_speed']} km/h")
        print(f"🌧️ Rain: {weather_data['rain']} mm/h")
        print("-"*60)
        print("🚨 ALERTS:")
        for alert in alerts:
            print(f"  • {alert}")
        print("="*60 + "\n")
    
    def _send_email_alerts(self, alerts: List[str], weather_data: dict) -> None:
        """Send alerts via email"""
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.config.SMTP_USER
            msg['To'] = self.config.ALERT_RECIPIENT
            msg['Subject'] = f"Weather Alert - {weather_data['location']}"
            
            # Build email body
            body = self._build_alert_message(alerts, weather_data)
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.config.SMTP_HOST, self.config.SMTP_PORT) as server:
                server.starttls()
                server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
                server.send_message(msg)
                
            logger.info(f"Email alert sent to {self.config.ALERT_RECIPIENT}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _send_pushbullet_alerts(self, alerts: List[str], weather_data: dict) -> None:
        """Send alerts via Pushbullet"""
        try:
            title = f"Weather Alert - {weather_data['location']}"
            body = self._build_alert_message(alerts, weather_data)
            
            headers = {
                'Access-Token': self.config.PUSHBULLET_API_KEY,
                'Content-Type': 'application/json'
            }
            
            data = {
                'type': 'note',
                'title': title,
                'body': body
            }
            
            response = requests.post(
                'https://api.pushbullet.com/v2/pushes',
                json=data,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info("Pushbullet notification sent")
            
        except Exception as e:
            logger.error(f"Failed to send Pushbullet notification: {e}")
    
    def _build_alert_message(self, alerts: List[str], weather_data: dict) -> str:
        """Build formatted alert message"""
        message = f"""
Weather Alert - {weather_data['location']}, {weather_data['country']}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Current Conditions:
• Temperature: {weather_data['temperature']}°C
• Feels Like: {weather_data['feels_like']}°C
• Humidity: {weather_data['humidity']}%
• Wind Speed: {weather_data['wind_speed']} km/h
• Rain: {weather_data['rain']} mm/h
• Condition: {weather_data['description']}

Alerts:
{chr(10).join(f'• {alert}' for alert in alerts)}

Please take necessary precautions.
"""
        return message
