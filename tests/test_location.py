#!/usr/bin/env python3
"""
Test script to verify the location-based weather alert functionality.
"""

import logging
import sys
from weatherbox.weather_service import WeatherAlertService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    """Test the location-based weather alert functionality."""
    # Use a sample city and state
    city = "Washington"
    state = "DC"

    logger.info(f"Testing weather alerts for location: {city}, {state}")

    # Create weather alert service
    service = WeatherAlertService()

    try:
        # Get coordinates for the location
        try:
            latitude, longitude = service.get_coordinates(city, state)
            logger.info(f"Coordinates for {city}, {state}: {latitude}, {longitude}")
        except ValueError as e:
            logger.error(f"Error getting coordinates: {str(e)}")
            return 1

        # Get alerts for the coordinates
        alerts = service.get_alerts_for_coordinates(latitude, longitude)
        
        if alerts:
            logger.info(f"Successfully fetched {len(alerts)} alerts for coordinates {latitude}, {longitude}")
            for alert in alerts:
                logger.info(f"Alert: {alert.headline}")
                logger.info(f"Event: {alert.event}")
                logger.info(f"Severity: {alert.severity.name}")
                logger.info(f"Expires: {alert.expires.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            logger.info(f"No alerts found for coordinates {latitude}, {longitude}")

        # Get alerts for the location
        alerts = service.get_alerts_for_location(city, state)
        
        if alerts:
            logger.info(f"Successfully fetched {len(alerts)} alerts for location {city}, {state}")
            for alert in alerts:
                logger.info(f"Alert: {alert.headline}")
                logger.info(f"Event: {alert.event}")
                logger.info(f"Severity: {alert.severity.name}")
                logger.info(f"Expires: {alert.expires.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            logger.info(f"No alerts found for location {city}, {state}")

        # Get the most important alert for the location
        alert = service.get_most_important_alerts_for_location(city, state)
        
        if alert:
            logger.info(f"Most important alert for {city}, {state}: {alert.headline}")
            logger.info(f"Event: {alert.event}")
            logger.info(f"Severity: {alert.severity.name}")
            logger.info(f"Urgency: {alert.urgency.name}")
            logger.info(f"Expires: {alert.expires.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            logger.info(f"No important alert found for {city}, {state}")

        logger.info("Test completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"Error testing location-based weather alerts: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())