#!/usr/bin/env python3
"""
Unit tests for weather alert API response caching.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
import sys
from unittest.mock import MagicMock

sys.modules.setdefault("geocoder", MagicMock())
from weatherbox.weather_service import WeatherAlertService


class MockResponse:
    """Simple mock HTTP response."""

    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class TestAlertResponseCache(unittest.TestCase):
    """Test cases for weather alert response caching behavior."""

    def setUp(self):
        self.service = WeatherAlertService()
        self.points_payload = {
            "properties": {
                "county": "https://api.weather.gov/zones/county/TXC001",
                "forecastZone": "https://api.weather.gov/zones/forecast/TXZ001",
            }
        }
        self.alerts_payload = {"features": []}

    @patch("weatherbox.weather_service.requests.get")
    def test_uses_cached_alert_response_within_60_seconds(self, mock_get):
        """Second identical call within TTL should return cached data and avoid API calls."""
        mock_get.side_effect = [
            MockResponse(self.points_payload),
            MockResponse(self.alerts_payload),
            MockResponse(self.alerts_payload),
        ]

        first = self.service.get_alerts_for_coordinates(30.0, -97.0)
        second = self.service.get_alerts_for_coordinates(30.0, -97.0)

        self.assertEqual(first, [])
        self.assertEqual(second, [])
        self.assertEqual(mock_get.call_count, 3)

    @patch("weatherbox.weather_service.requests.get")
    def test_expired_cache_entry_triggers_refresh(self, mock_get):
        """Cache entries older than 60 seconds should be refreshed from API."""
        mock_get.side_effect = [
            MockResponse(self.points_payload),
            MockResponse(self.alerts_payload),
            MockResponse(self.alerts_payload),
            MockResponse(self.points_payload),
            MockResponse(self.alerts_payload),
            MockResponse(self.alerts_payload),
        ]

        self.service.get_alerts_for_coordinates(31.0, -98.0)

        cache_key = "31.0,-98.0"
        cached_at, cached_alerts = self.service._alerts_cache[cache_key]
        self.service._alerts_cache[cache_key] = (
            cached_at - timedelta(seconds=61),
            cached_alerts,
        )

        self.service.get_alerts_for_coordinates(31.0, -98.0)
        self.assertEqual(mock_get.call_count, 6)

    @patch("weatherbox.weather_service.requests.get")
    def test_alert_cache_is_limited_to_100_unique_calls(self, mock_get):
        """Adding a new unique alert request should evict oldest entry when cache is full."""
        now = datetime.now()
        self.service._alerts_cache["oldest,oldest"] = (now - timedelta(seconds=1000), [])
        for i in range(99):
            key = f"{i}.0,{i}.0"
            self.service._alerts_cache[key] = (now - timedelta(seconds=100 - i), [])

        mock_get.side_effect = [
            MockResponse(self.points_payload),
            MockResponse(self.alerts_payload),
            MockResponse(self.alerts_payload),
        ]

        self.service.get_alerts_for_coordinates(99.9, -99.9)

        self.assertEqual(len(self.service._alerts_cache), 100)
        self.assertNotIn("oldest,oldest", self.service._alerts_cache)
        self.assertIn("99.9,-99.9", self.service._alerts_cache)


if __name__ == "__main__":
    unittest.main()
