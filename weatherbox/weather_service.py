import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
import geocoder

from weatherbox.models.alert import WeatherAlert, AlertSeverity, AlertUrgency, AlertCertainty


class WeatherAlertService:
    """
    Service for fetching and processing weather alerts from the National Weather Service API.
    """

    BASE_URL = "https://api.weather.gov"
    ALERTS_ENDPOINT = "/alerts/active"

    def __init__(self, user_agent: str = "WeatherBox/1.0"):
        """
        Initialize the weather alert service.

        Args:
            user_agent: User agent string to use for API requests. NWS API requires a user agent.
        """
        self.user_agent = user_agent
        self.logger = logging.getLogger(__name__)

    def get_alerts_for_same_codes(self, same_codes: List[str]) -> List[WeatherAlert]:
        """
        Get weather alerts for a list of SAME codes.

        Args:
            same_codes: List of SAME (Specific Area Message Encoding) codes to get alerts for.

        Returns:
            List of WeatherAlert objects.
        """
        all_alerts = []

        for same_code in same_codes:
            try:
                alerts = self._fetch_alerts_for_same_code(same_code)
                all_alerts.extend(alerts)
            except Exception as e:
                self.logger.error(f"Error fetching alerts for SAME code {same_code}: {str(e)}")

        return all_alerts

    def _fetch_alerts_for_same_code(self, same_code: str) -> List[WeatherAlert]:
        """
        Fetch weather alerts for a specific SAME code.

        Args:
            same_code: SAME code to get alerts for.

        Returns:
            List of WeatherAlert objects.
        """
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/geo+json"
        }

        # Try different endpoints and formats for the SAME code
        # This increases the chances of finding the correct endpoint
        endpoints_to_try = [
            # Try the main alerts endpoint first (no specific area/zone)
            f"{self.BASE_URL}{self.ALERTS_ENDPOINT}",

            # Try the area endpoint with the raw SAME code
            f"{self.BASE_URL}{self.ALERTS_ENDPOINT}/area/{same_code}",

            # Try the zone endpoint with the raw SAME code
            f"{self.BASE_URL}{self.ALERTS_ENDPOINT}/zone/{same_code}",

            # Try the county endpoint with the raw SAME code
            f"{self.BASE_URL}{self.ALERTS_ENDPOINT}/county/{same_code}"
        ]

        # If the SAME code is 6 digits, try some formatted versions too
        if len(same_code) == 6:
            state_code = same_code[:2]
            zone_code = same_code[2:]

            # Try with state + Z + zone (removing leading zeros from zone)
            formatted_zone = f"{state_code}Z{zone_code.lstrip('0')}"
            endpoints_to_try.append(f"{self.BASE_URL}{self.ALERTS_ENDPOINT}/zone/{formatted_zone}")

            # Try with state + C + county (removing leading zeros from county)
            formatted_county = f"{state_code}C{zone_code.lstrip('0')}"
            endpoints_to_try.append(f"{self.BASE_URL}{self.ALERTS_ENDPOINT}/county/{formatted_county}")

        # Try each endpoint until one works
        last_error = None
        for url in endpoints_to_try:
            try:
                self.logger.info(f"Trying endpoint: {url}")
                response = requests.get(url, headers=headers)
                response.raise_for_status()

                data = response.json()

                # For the main endpoint, we need to filter the results by the SAME code
                if url == f"{self.BASE_URL}{self.ALERTS_ENDPOINT}":
                    # Filter alerts by the SAME code
                    # This is a simplified approach - in reality, you might need more logic
                    # to match alerts to the specific SAME code
                    self.logger.info("Using main endpoint - filtering results by SAME code")
                    return self._parse_alerts_from_main_endpoint(data, same_code)
                else:
                    return self._parse_alerts(data, same_code)

            except Exception as e:
                self.logger.warning(f"Failed to fetch alerts from {url}: {str(e)}")
                last_error = e

        # If we get here, none of the endpoints worked
        self.logger.error(f"All endpoints failed for SAME code {same_code}")
        if last_error:
            raise last_error

        # Return an empty list if no endpoint worked but no error was raised
        return []

    def _parse_alerts_from_main_endpoint(self, data: Dict, same_code: str) -> List[WeatherAlert]:
        """
        Parse alerts from the main endpoint, filtering by SAME code.

        Args:
            data: API response data.
            same_code: SAME code to filter alerts by.

        Returns:
            List of WeatherAlert objects.
        """
        alerts = []

        for feature in data.get("features", []):
            properties = feature.get("properties", {})

            # Check if this alert is relevant for the SAME code
            # We need to check different formats of the SAME code against the affected zones
            affected_zones = properties.get("affectedZones", [])

            # Extract the zone identifiers from the URLs
            zone_ids = []
            for zone in affected_zones:
                # Extract the last part of the URL (e.g., "GMZ633" from "https://api.weather.gov/zones/forecast/GMZ633")
                parts = zone.split("/")
                if parts:
                    zone_ids.append(parts[-1])

            # Try different formats of the SAME code
            same_code_formats = [
                same_code,  # Raw SAME code
                same_code.upper(),  # Uppercase
                same_code.lower(),  # Lowercase
            ]

            # If the SAME code is 6 digits, try some formatted versions too
            if len(same_code) == 6:
                state_code = same_code[:2]
                zone_code = same_code[2:]

                # Try with state + Z + zone (removing leading zeros from zone)
                same_code_formats.append(f"{state_code}Z{zone_code.lstrip('0')}")

                # Try with state + C + county (removing leading zeros from county)
                same_code_formats.append(f"{state_code}C{zone_code.lstrip('0')}")

                # Try with just the state code
                same_code_formats.append(state_code)

                # Try with just the zone code
                same_code_formats.append(zone_code)
                same_code_formats.append(zone_code.lstrip('0'))

            # Check if any of the SAME code formats match any of the zone IDs
            if not any(format in zone_id for format in same_code_formats for zone_id in zone_ids):
                # Also check if any of the zone IDs contain the SAME code
                if not any(zone_id in format for format in same_code_formats for zone_id in zone_ids):
                    continue

            # Parse dates
            onset = self._parse_date(properties.get("onset"))
            expires = self._parse_date(properties.get("expires"))

            if not expires:
                self.logger.warning(f"Alert {properties.get('id')} has no expiration date, skipping")
                continue

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
                expires=expires
            )

            alerts.append(alert)

        return alerts

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
                expires=expires
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
        self.logger.info(f"Getting coordinates for {location}")

        # Use geocoder to get coordinates
        g = geocoder.arcgis(location)

        if not g.ok:
            raise ValueError(f"Could not determine coordinates for {location}")

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
            response.raise_for_status() # todo what does this doq
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

    def get_most_important_alerts(self, same_codes: List[str]) -> Dict[str, Optional[WeatherAlert]]:
        """
        Get the most important non-expired alert for each SAME code.

        Args:
            same_codes: List of SAME codes to get alerts for.

        Returns:
            Dictionary mapping SAME codes to their most important non-expired alert,
            or None if there are no active alerts for that code.
        """
        all_alerts = self.get_alerts_for_same_codes(same_codes)
        result = {code: None for code in same_codes}

        # Group alerts by SAME code
        for alert in all_alerts:
            if alert.is_expired:
                continue

            for code in alert.same_codes:
                if code in same_codes:
                    current_alert = result[code]

                    # Replace if this alert is more important
                    if current_alert is None or alert.importance_score > current_alert.importance_score:
                        result[code] = alert

        return result
