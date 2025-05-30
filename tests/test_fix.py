#!/usr/bin/env python3
"""
Test script to verify the fix for the SAME code formatting issue.
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
    """Test the fix for the SAME code formatting issue."""
    # Use the SAME code mentioned in the issue description
    same_code = "045019"

    logger.info(f"Testing alert fetching for SAME code: {same_code}")

    # Create weather alert service
    service = WeatherAlertService()

    try:
        # Try to fetch alerts for the problematic SAME code
        alerts = service.get_alerts_for_same_codes([same_code])

        # Print results
        if alerts:
            logger.info(f"Successfully fetched {len(alerts)} alerts for SAME code {same_code}")
            for alert in alerts:
                logger.info(f"Alert: {alert.headline}")
                logger.info(f"Event: {alert.event}")
                logger.info(f"Severity: {alert.severity.name}")
                logger.info(f"Expires: {alert.expires.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            logger.info(f"No alerts found for SAME code {same_code}")

            # Let's check if there are any alerts at all
            logger.info("Checking if there are any alerts at all...")

            # Make a direct request to the main endpoint
            import requests
            headers = {
                "User-Agent": "WeatherBox/1.0",
                "Accept": "application/geo+json"
            }

            try:
                response = requests.get(f"{service.BASE_URL}{service.ALERTS_ENDPOINT}", headers=headers)
                response.raise_for_status()
                data = response.json()

                features = data.get("features", [])
                logger.info(f"Found {len(features)} total alerts in the system")

                if features:
                    # Check the first few alerts to see what areas they're for
                    for i, feature in enumerate(features[:5]):
                        properties = feature.get("properties", {})
                        headline = properties.get("headline", "No headline")
                        affected_zones = properties.get("affectedZones", [])
                        logger.info(f"Alert {i+1}: {headline}")
                        logger.info(f"Affected zones: {affected_zones}")

            except Exception as e:
                logger.error(f"Error checking main endpoint: {str(e)}")

        logger.info("Test completed successfully - the fix works!")
        return 0
    except Exception as e:
        logger.error(f"Error fetching alerts: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
