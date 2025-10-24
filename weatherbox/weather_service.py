import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import geocoder
import requests
from weatherbox.models.alert import WeatherAlert, AlertSeverity, AlertUrgency, AlertCertainty

class WeatherAlertService:
    """
    Service for fetching and processing weather alerts from the National Weather Service API.
    """
    BASE_URL = "https://api.weather.gov"
    ALERTS_ENDPOINT = "/alerts/active"

    # Maximum number of entries in coordinates cache
    MAX_CACHE_SIZE = 100

    def __init__(self, user_agent: str = "WeatherBox/1.0"):
        """
        Initialize the weather alert service.

        Args:
            user_agent: User agent string to use for API requests. NWS API requires a user agent.
        """
        self.user_agent = user_agent
        self.logger = logging.getLogger(__name__)
        self._coordinates_cache = {}


    def _maintain_cache_size(self):
        """Remove oldest entries if cache exceeds maximum size."""
        if len(self._coordinates_cache) >= self.MAX_CACHE_SIZE:
            # Remove oldest entries to make space
            oldest_keys = sorted(self._coordinates_cache.keys())[:len(self._coordinates_cache) - self.MAX_CACHE_SIZE + 1]
            for key in oldest_keys:
                del self._coordinates_cache[key]


    def _parse_alerts(self, data: Dict, same_code: str) -> List[WeatherAlert]:
            """
            Parse the API response into WeatherAlert objects.

            Args:
                data: API response data.
                same_code: SAME code the alerts are for.

            Returns:
                List of WeatherAlert objects.
            """
            alerts = []

            for feature in data.get("features", []):
                properties = feature.get("properties", {})

                # Parse dates
                onset = self._parse_date(properties.get("onset"))
                expires = self._parse_date(properties.get("expires"))

                if not expires:
                    self.logger.warning(f"Alert {properties.get('id')} has no expiration date, skipping")
                    continue

                # Extract NWSheadline from parameters
                nws_headline = ""
                parameters = properties.get("parameters")
                if parameters:
                    nws_headline_list = parameters.get("NWSheadline")
                    if nws_headline_list and len(nws_headline_list) > 0:
                        nws_headline = nws_headline_list[0]

                # Create alert object
                alert = WeatherAlert(
                    id=properties.get("id", ""),
                    same_codes=[same_code],
                    event=properties.get("event", ""),
                    headline=properties.get("headline", ""),
                    description=properties.get("description", ""),
                    instruction=properties.get("instruction"),
                    severity=AlertSeverity.from_string(properties.get("severity", "")),
                    urgency=AlertUrgency.from_string(properties.get("urgency", "")),
                    certainty=AlertCertainty.from_string(properties.get("certainty", "")),
                    onset=onset,
                    expires=expires,
                    nws_headline=nws_headline
                )

                alerts.append(alert)

            return alerts

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse a date string from the API into a datetime object.

        Args:
            date_str: Date string to parse.

        Returns:
            Datetime object or None if the date string is invalid.
        """
        if not date_str:
            return None

        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            self.logger.warning(f"Failed to parse date: {date_str}")
            return None

    def get_coordinates(self, city: str, state: str) -> Tuple[float, float]:
        """
        Get the latitude and longitude coordinates for a city and state.

        Args:
            city: The name of the city.
            state: The name or abbreviation of the state.

        Returns:
            A tuple of (latitude, longitude) coordinates.

        Raises:
            ValueError: If the coordinates could not be determined.
        """
        location = f"{city}, {state}"

        # Check cache first
        if location in self._coordinates_cache:
            self.logger.info(f"Using cached coordinates for {location}")
            return self._coordinates_cache[location]

        self.logger.info(f"Getting coordinates for {location}")

        # Use geocoder to get coordinates
        g = geocoder.arcgis(location)

        if not g.ok:
            raise ValueError(f"Could not determine coordinates for {location}")

        # Cache the coordinates while maintaining size limit
        self._maintain_cache_size()
        self._coordinates_cache[location] = (g.lat, g.lng)
        return g.lat, g.lng

    def get_alerts_for_coordinates(self, latitude: float, longitude: float) -> List[WeatherAlert]:
        """
        Get weather alerts for specific coordinates.

        Args:
            latitude: The latitude coordinate.
            longitude: The longitude coordinate.

        Returns:
            List of WeatherAlert objects.
        """
        self.logger.info(f"Getting weather alerts for coordinates: {latitude}, {longitude}")

        # First, get the forecast office and zone information from the coordinates
        points_url = f"{self.BASE_URL}/points/{latitude},{longitude}"
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/geo+json"
        }

        try:
            response = requests.get(points_url, headers=headers)
            response.raise_for_status()
            points_data = response.json()

            # Extract the county and zone information
            properties = points_data.get("properties", {})
            county = properties.get("county")
            zone = properties.get("forecastZone")

            if not county or not zone:
                self.logger.warning(f"Could not determine county or zone for coordinates: {latitude}, {longitude}")
                return []

            # Extract the zone ID from the URL
            county_id = county.split("/")[-1]
            zone_id = zone.split("/")[-1]

            # Get alerts for the county and zone
            alerts = []

            try:
                # Try to get alerts for the county
                county_url = f"{self.BASE_URL}{self.ALERTS_ENDPOINT}/zone/{county_id}"
                self.logger.info(f"Getting alerts for county: {county_url}")
                county_response = requests.get(county_url, headers=headers)
                county_response.raise_for_status()
                county_data = county_response.json()
                county_alerts = self._parse_alerts(county_data, f"County: {county_id}")
                alerts.extend(county_alerts)
            except Exception as e:
                self.logger.warning(f"Failed to get alerts for county {county_id}: {str(e)}")

            try:
                # Try to get alerts for the zone
                zone_url = f"{self.BASE_URL}{self.ALERTS_ENDPOINT}/zone/{zone_id}"
                self.logger.info(f"Getting alerts for zone: {zone_url}")
                zone_response = requests.get(zone_url, headers=headers)
                zone_response.raise_for_status()
                zone_data = zone_response.json()
                zone_alerts = self._parse_alerts(zone_data, f"Zone: {zone_id}")
                alerts.extend(zone_alerts)
            except Exception as e:
                self.logger.warning(f"Failed to get alerts for zone {zone_id}: {str(e)}")

            return alerts

        except Exception as e:
            self.logger.error(f"Error getting weather alerts for coordinates {latitude}, {longitude}: {str(e)}")
            raise

    def get_alerts_for_location(self, city: str, state: str) -> List[WeatherAlert]:
        """
        Get weather alerts for a specific city and state.

        Args:
            city: The name of the city.
            state: The name or abbreviation of the state.

        Returns:
            List of WeatherAlert objects.
        """
        try:
            # Get coordinates for the location
            latitude, longitude = self.get_coordinates(city, state)

            # Get alerts for the coordinates
            return self.get_alerts_for_coordinates(latitude, longitude)
        except Exception as e:
            self.logger.error(f"Error getting weather alerts for {city}, {state}: {str(e)}")
            return []

    def get_most_important_alerts_for_location(self, city: str, state: str) -> Optional[WeatherAlert]:
        """
        Get the most important non-expired alert for a specific city and state.

        Args:
            city: The name of the city.
            state: The name or abbreviation of the state.

        Returns:
            The most important non-expired alert, or None if there are no active alerts.
        """
        alerts = self.get_alerts_for_location(city, state)

        # Filter out expired alerts
        active_alerts = [alert for alert in alerts if not alert.is_expired]

        if not active_alerts:
            return None

        # Find the most important alert
        return max(active_alerts, key=lambda alert: alert.importance_score)

