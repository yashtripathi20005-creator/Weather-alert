#!/usr/bin/env python3
"""
Weather Alert Notifier - Main Entry Point

This application monitors weather conditions and sends notifications
when severe weather alerts are triggered.
"""

import sys
import logging
from config import Config
from weather_api import WeatherAPI
from notification_service import NotificationService
from monitor import WeatherMonitor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_config(config: Config) -> bool:
    """Validate that required configuration is present"""
    if not config.WEATHER_API_KEY:
        logger.error("Missing WEATHER_API_KEY in configuration")
        return False
    
    if not config.LOCATION:
        logger.error("Missing LOCATION in configuration")
        return False
    
    # Check if at least one notification channel is enabled
    channels_enabled = False
    
    if config.ENABLE_CONSOLE_ALERTS:
        channels_enabled = True
        logger.info("Console alerts enabled")
    
    if all([config.SMTP_HOST, config.SMTP_USER, config.SMTP_PASSWORD, config.ALERT_RECIPIENT]):
        channels_enabled = True
        logger.info("Email alerts enabled")
    
    if config.PUSHBULLET_API_KEY:
        channels_enabled = True
        logger.info("Pushbullet alerts enabled")
    
    if not channels_enabled:
        logger.error("No notification channels enabled! Enable at least one channel.")
        return False
    
    return True


def main():
    """Main entry point for the Weather Alert Notifier"""
    logger.info("Weather Alert Notifier Starting...")
    logger.info("="*50)
    
    # Load configuration
    config = Config()
    
    # Validate configuration
    if not validate_config(config):
        logger.error("Configuration validation failed. Exiting.")
        sys.exit(1)
    
    # Initialize components
    weather_api = WeatherAPI(
        api_key=config.WEATHER_API_KEY,
        api_url=config.WEATHER_API_URL,
        location=config.LOCATION
    )
    
    notification_service = NotificationService(config)
    
    monitor = WeatherMonitor(weather_api, notification_service, config)
    
    # Run initial check
    logger.info("Performing initial weather check...")
    try:
        weather_data = monitor.run_check()
        
        if weather_data:
            logger.info("Initial check completed successfully")
            logger.info(f"Location: {weather_data['location']}, {weather_data['country']}")
            logger.info(f"Temperature: {weather_data['temperature']}°C")
            logger.info(f"Conditions: {weather_data['description']}")
        else:
            logger.warning("Initial weather check failed")
    except Exception as e:
        logger.error(f"Error during initial check: {e}")
    
    # Start continuous monitoring
    logger.info("Starting continuous monitoring...")
    logger.info(f"Check interval: {config.ALERT_CHECK_INTERVAL} seconds")
    logger.info("Press Ctrl+C to stop")
    logger.info("="*50)
    
    try:
        monitor.run_continuous()
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
