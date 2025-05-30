#!/usr/bin/env python3
"""
Sample program to demonstrate the WeatherBox weather alert functionality.
"""

import argparse
import logging
import sys
from typing import Tuple

from weatherbox.weather_service import WeatherAlertService

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )

def parse_arguments() -> Tuple[str, str]:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Get weather alerts for a location.")
    parser.add_argument(
        "city",
        help="The name of the city to get weather alerts for."
    )
    parser.add_argument(
        "state",
        help="The name or abbreviation of the state the city is in."
    )

    args = parser.parse_args()
    return args.city, args.state


def main():
    """Main entry point for the sample program."""
    setup_logging()
    logger = logging.getLogger(__name__)

    # Parse command line arguments
    city, state = parse_arguments()
    logger.info(f"Getting weather alerts for location: {city}, {state}")

    # Create weather alert service
    service = WeatherAlertService()

    # Get coordinates for the location
    try:
        latitude, longitude = service.get_coordinates(city, state)
        logger.info(f"Coordinates for {city}, {state}: {latitude}, {longitude}")
    except ValueError as e:
        logger.error(f"Error getting coordinates: {str(e)}")
        sys.exit(1)

    # Get most important alert for the location
    alert = service.get_most_important_alerts_for_location(city, state)

    # Print results
    print("\n=== Weather Alerts ===\n")

    print(f"Location: {city}, {state}")
    print(f"Coordinates: {latitude}, {longitude}")

    if alert:
        print(f"Alert: {alert.headline}")
        print(f"Event: {alert.event}")
        print(f"Severity: {alert.severity.name}")
        print(f"Urgency: {alert.urgency.name}")
        print(f"Expires: {alert.expires.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Description: {alert.description[:200]}..." if len(alert.description) > 200 else f"Description: {alert.description}")

        if alert.instruction:
            print(f"Instructions: {alert.instruction[:200]}..." if len(alert.instruction) > 200 else f"Instructions: {alert.instruction}")
    else:
        print("No active alerts for this area.")

    print("\n" + "-" * 50 + "\n")




if __name__ == "__main__":
    main()
