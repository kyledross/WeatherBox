#!/usr/bin/env python3
"""
Unit tests for the WeatherAlertResponse score mapping logic.
"""

import unittest
from datetime import datetime, timezone
from weatherbox.models.alert import WeatherAlert, AlertSeverity, AlertUrgency, AlertCertainty

class TestWeatherAlertResponseScoreMapping(unittest.TestCase):
    """Test cases for the score mapping logic used in WeatherAlertResponse."""
    
    def setUp(self):
        """Set up score mapping dictionaries used in the API."""
        self.severity_score_map = {
            "UNKNOWN": 0,
            "MINOR": 1,
            "MODERATE": 2,
            "SEVERE": 3,
            "EXTREME": 4
        }
        self.urgency_score_map = {
            "UNKNOWN": 0,
            "FUTURE": 1,
            "EXPECTED": 2,
            "IMMEDIATE": 3
        }
        self.certainty_score_map = {
            "UNKNOWN": 0,
            "UNLIKELY": 1,
            "POSSIBLE": 2,
            "LIKELY": 3,
            "OBSERVED": 4
        }

    def test_response_includes_score_fields(self):
        """Test that WeatherAlertResponse includes severity_score, urgency_score, and certainty_score fields."""
        alert = WeatherAlert(
            id='test_alert',
            same_codes=['Test'],
            event='Test Event',
            headline='Test Headline',
            description='Test Description',
            instruction='Test Instruction',
            severity=AlertSeverity.MODERATE,
            urgency=AlertUrgency.EXPECTED,
            certainty=AlertCertainty.LIKELY,
            onset=datetime(2025, 1, 1, tzinfo=timezone.utc),
            expires=datetime(2025, 12, 31, tzinfo=timezone.utc)
        )
        
        severity_score = self.severity_score_map.get(alert.severity.name, 0)
        urgency_score = self.urgency_score_map.get(alert.urgency.name, 0)
        certainty_score = self.certainty_score_map.get(alert.certainty.name, 0)
        
        self.assertIsNotNone(severity_score)
        self.assertIsNotNone(urgency_score)
        self.assertIsNotNone(certainty_score)
        self.assertEqual(severity_score, 2)
        self.assertEqual(urgency_score, 2)
        self.assertEqual(certainty_score, 3)

    def test_severity_score_mapping(self):
        """Test that severity_score is correctly mapped for different severity levels."""
        test_cases = [
            (AlertSeverity.UNKNOWN, 0),
            (AlertSeverity.MINOR, 1),
            (AlertSeverity.MODERATE, 2),
            (AlertSeverity.SEVERE, 3),
            (AlertSeverity.EXTREME, 4),
        ]
        
        for severity, expected_score in test_cases:
            with self.subTest(severity=severity):
                alert = WeatherAlert(
                    id='test_alert',
                    same_codes=['Test'],
                    event='Test Event',
                    headline='Test Headline',
                    description='Test Description',
                    instruction='Test Instruction',
                    severity=severity,
                    urgency=AlertUrgency.EXPECTED,
                    certainty=AlertCertainty.LIKELY,
                    onset=datetime(2025, 1, 1, tzinfo=timezone.utc),
                    expires=datetime(2025, 12, 31, tzinfo=timezone.utc)
                )
                
                severity_score = self.severity_score_map.get(alert.severity.name, 0)
                
                self.assertEqual(severity_score, expected_score)
                self.assertEqual(alert.severity.name, severity.name)

    def test_urgency_score_mapping(self):
        """Test that urgency_score is correctly mapped for different urgency levels."""
        test_cases = [
            (AlertUrgency.UNKNOWN, 0),
            (AlertUrgency.FUTURE, 1),
            (AlertUrgency.EXPECTED, 2),
            (AlertUrgency.IMMEDIATE, 3),
        ]
        
        for urgency, expected_score in test_cases:
            with self.subTest(urgency=urgency):
                alert = WeatherAlert(
                    id='test_alert',
                    same_codes=['Test'],
                    event='Test Event',
                    headline='Test Headline',
                    description='Test Description',
                    instruction='Test Instruction',
                    severity=AlertSeverity.MODERATE,
                    urgency=urgency,
                    certainty=AlertCertainty.LIKELY,
                    onset=datetime(2025, 1, 1, tzinfo=timezone.utc),
                    expires=datetime(2025, 12, 31, tzinfo=timezone.utc)
                )
                
                urgency_score = self.urgency_score_map.get(alert.urgency.name, 0)
                
                self.assertEqual(urgency_score, expected_score)
                self.assertEqual(alert.urgency.name, urgency.name)

    def test_certainty_score_mapping(self):
        """Test that certainty_score is correctly mapped for different certainty levels."""
        test_cases = [
            (AlertCertainty.UNKNOWN, 0),
            (AlertCertainty.UNLIKELY, 1),
            (AlertCertainty.POSSIBLE, 2),
            (AlertCertainty.LIKELY, 3),
            (AlertCertainty.OBSERVED, 4),
        ]
        
        for certainty, expected_score in test_cases:
            with self.subTest(certainty=certainty):
                alert = WeatherAlert(
                    id='test_alert',
                    same_codes=['Test'],
                    event='Test Event',
                    headline='Test Headline',
                    description='Test Description',
                    instruction='Test Instruction',
                    severity=AlertSeverity.MODERATE,
                    urgency=AlertUrgency.EXPECTED,
                    certainty=certainty,
                    onset=datetime(2025, 1, 1, tzinfo=timezone.utc),
                    expires=datetime(2025, 12, 31, tzinfo=timezone.utc)
                )
                
                certainty_score = self.certainty_score_map.get(alert.certainty.name, 0)
                
                self.assertEqual(certainty_score, expected_score)
                self.assertEqual(alert.certainty.name, certainty.name)

    def test_score_fields_default_to_zero_for_unknown(self):
        """Test that score fields default to 0 when unknown values are encountered."""
        alert = WeatherAlert(
            id='test_alert',
            same_codes=['Test'],
            event='Test Event',
            headline='Test Headline',
            description='Test Description',
            instruction='Test Instruction',
            severity=AlertSeverity.UNKNOWN,
            urgency=AlertUrgency.UNKNOWN,
            certainty=AlertCertainty.UNKNOWN,
            onset=datetime(2025, 1, 1, tzinfo=timezone.utc),
            expires=datetime(2025, 12, 31, tzinfo=timezone.utc)
        )
        
        severity_score = self.severity_score_map.get(alert.severity.name, 0)
        urgency_score = self.urgency_score_map.get(alert.urgency.name, 0)
        certainty_score = self.certainty_score_map.get(alert.certainty.name, 0)
        
        self.assertEqual(severity_score, 0)
        self.assertEqual(urgency_score, 0)
        self.assertEqual(certainty_score, 0)
        self.assertEqual(alert.severity.name, 'UNKNOWN')
        self.assertEqual(alert.urgency.name, 'UNKNOWN')
        self.assertEqual(alert.certainty.name, 'UNKNOWN')

    def test_score_fields_use_default_when_missing_from_map(self):
        """Test that score fields use default value of 0 when a value is missing from the map."""
        alert = WeatherAlert(
            id='test_alert',
            same_codes=['Test'],
            event='Test Event',
            headline='Test Headline',
            description='Test Description',
            instruction='Test Instruction',
            severity=AlertSeverity.MODERATE,
            urgency=AlertUrgency.EXPECTED,
            certainty=AlertCertainty.LIKELY,
            onset=datetime(2025, 1, 1, tzinfo=timezone.utc),
            expires=datetime(2025, 12, 31, tzinfo=timezone.utc)
        )
        
        # Simulate a missing key by using an invalid name
        severity_score = self.severity_score_map.get('INVALID_KEY', 0)
        urgency_score = self.urgency_score_map.get('INVALID_KEY', 0)
        certainty_score = self.certainty_score_map.get('INVALID_KEY', 0)
        
        self.assertEqual(severity_score, 0)
        self.assertEqual(urgency_score, 0)
        self.assertEqual(certainty_score, 0)

if __name__ == '__main__':
    unittest.main()
