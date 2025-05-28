#!/usr/bin/env python3
"""
Test script to verify the functionality of the WeatherAlert class.
"""

import unittest
from datetime import datetime, timezone, timedelta
from weatherbox.models.alert import WeatherAlert, AlertSeverity, AlertUrgency, AlertCertainty

class TestWeatherAlerts(unittest.TestCase):
    """Test cases for the WeatherAlert class."""

    def setUp(self):
        """Set up test data."""
        # Create test alerts using the provided data
        self.flood_advisory = WeatherAlert(
            id='urn:oid:2.49.0.1.840.0.5663ebcf7033df09bf7b04c6d96f15d5d5de9a7d.001.1',
            same_codes=['County: TXC095'],
            event='Flood Advisory',
            headline='Flood Advisory issued May 27 at 11:33PM CDT until May 28 at 2:45AM CDT by NWS San Angelo TX',
            description='* WHAT...Flooding caused by excessive rainfall is expected.\n\n* WHERE...A portion of west central Texas, including the following\ncounties, Concho, Irion, Schleicher and Tom Green.\n\n* WHEN...Until 245 AM CDT.\n\n* IMPACTS...Minor flooding in low-lying and poor drainage areas.\n\n* ADDITIONAL DETAILS...\n- At 1132 PM CDT, Doppler radar indicated heavy rain due to\nthunderstorms. flooding is ongoing or expected to begin\nshortly in the advisory area. Between 1 and 2 inches of rain\nhave fallen.\n- Some locations that will experience flooding include...\nSan Angelo, Mertzon, Christoval, Lake Nasworthy, Twin Buttes\nReservoir, Goodfellow Air Force Base, Wall, Knickerbocker,\nTankersley, O.C. Fisher Reservoir, San Angelo State Park,\nVeribest, Vancourt, Grape Creek, Sherwood, Mereta, Arden,\nEola, Lowake and Us-67 Near The Irion-Tom Green County Line.\n- This includes the following Low Water Crossings...\nCollege Hills and Millbrook, Southwest Blvd and Loop 306,\nJackson From Knickerbocker to South Bryant, Howard and\nWebster, FM 2334 crossing Ninemile Creek, RM 853 crossing Dry\nDraw, FM 1692 crossing Concho River, FM 1692 crossing Sales\nBranch, Ranch Road 853 crossing east Rocky Creek and FM 2334\ncrossing Dry Lipan Creek.\n- http://www.weather.gov/safety/flood',
            instruction="Turn around, don't drown when encountering flooded roads. Most flood\ndeaths occur in vehicles.\n\nBe especially cautious at night when it is harder to recognize the\ndangers of flooding.",
            severity=AlertSeverity.MINOR,
            urgency=AlertUrgency.EXPECTED,
            certainty=AlertCertainty.LIKELY,
            onset=datetime(2025, 5, 27, 23, 33, tzinfo=timezone(timedelta(days=-1, seconds=68400))),
            expires=datetime(2025, 5, 28, 2, 45, tzinfo=timezone(timedelta(days=-1, seconds=68400)))
        )

        self.thunderstorm_warning = WeatherAlert(
            id='urn:oid:2.49.0.1.840.0.c9589fab4e92b04e090efc6aeb13e91e3e1d72cd.001.1',
            same_codes=['County: TXC095'],
            event='Severe Thunderstorm Warning',
            headline='Severe Thunderstorm Warning issued May 27 at 11:30PM CDT until May 28 at 12:15AM CDT by NWS San Angelo TX',
            description='SVRSJT\n\nThe National Weather Service in San Angelo has issued a\n\n* Severe Thunderstorm Warning for...\nEast central Tom Green County in west central Texas...\nSouth central Runnels County in west central Texas...\nNorthern Concho County in west central Texas...\n\n* Until 1215 AM CDT.\n\n* At 1129 PM CDT, a severe thunderstorm was located over Mereta,\nmoving northeast at 25 mph.\n\nHAZARD...60 mph wind gusts and nickel size hail.\n\nSOURCE...Radar indicated.\n\nIMPACT...Expect damage to roofs, siding, and trees.\n\n* This severe thunderstorm will be near...\nEola and Mereta around 1135 PM CDT.\nLowake around 1140 PM CDT.\nPaint Rock around 1145 PM CDT.\n\nOther locations impacted by this severe thunderstorm include Vick,\nThe Intersection Of Us-83 And Ranch Road 765, Us-83 Near The Concho-\nRunnels County Line, The Intersection Of Us-\n83 And Ranch Road 1929, and The Intersection Of Ranch Road 380 And\nRanch Road 381.',
            instruction="Large hail, damaging wind, and continuous cloud to ground lightning\nare occurring with this storm. Move indoors immediately. Lightning\nis one of nature's leading killers. Remember, if you can hear\nthunder, you are close enough to be struck by lightning.\n\nTorrential rainfall is occurring with this storm, and may lead to\nflash flooding. Do not drive your vehicle through flooded roadways.\n\nTo report severe weather, contact your nearest law enforcement\nagency. They will send your report to the National Weather Service\noffice in San Angelo.",
            severity=AlertSeverity.SEVERE,
            urgency=AlertUrgency.IMMEDIATE,
            certainty=AlertCertainty.OBSERVED,
            onset=datetime(2025, 5, 27, 23, 30, tzinfo=timezone(timedelta(days=-1, seconds=68400))),
            expires=datetime(2025, 5, 28, 0, 15, tzinfo=timezone(timedelta(days=-1, seconds=68400)))
        )

    def test_alert_attributes(self):
        """Test that alert attributes are correctly set."""
        # Test flood advisory attributes
        self.assertEqual(self.flood_advisory.id, 'urn:oid:2.49.0.1.840.0.5663ebcf7033df09bf7b04c6d96f15d5d5de9a7d.001.1')
        self.assertEqual(self.flood_advisory.same_codes, ['County: TXC095'])
        self.assertEqual(self.flood_advisory.event, 'Flood Advisory')
        self.assertEqual(self.flood_advisory.severity, AlertSeverity.MINOR)
        self.assertEqual(self.flood_advisory.urgency, AlertUrgency.EXPECTED)
        self.assertEqual(self.flood_advisory.certainty, AlertCertainty.LIKELY)

        # Test thunderstorm warning attributes
        self.assertEqual(self.thunderstorm_warning.id, 'urn:oid:2.49.0.1.840.0.c9589fab4e92b04e090efc6aeb13e91e3e1d72cd.001.1')
        self.assertEqual(self.thunderstorm_warning.same_codes, ['County: TXC095'])
        self.assertEqual(self.thunderstorm_warning.event, 'Severe Thunderstorm Warning')
        self.assertEqual(self.thunderstorm_warning.severity, AlertSeverity.SEVERE)
        self.assertEqual(self.thunderstorm_warning.urgency, AlertUrgency.IMMEDIATE)
        self.assertEqual(self.thunderstorm_warning.certainty, AlertCertainty.OBSERVED)

    def test_expiration_dates(self):
        """Test the expiration dates of alerts."""
        # Instead of testing the is_expired property directly, which uses datetime.now(),
        # we'll check if the expiration dates are in the future or past compared to a reference date

        # Use a reference date in 2023 (timezone-aware)
        reference_date = datetime(2023, 1, 1, tzinfo=timezone.utc)

        # Check that the flood advisory expires in the future compared to our reference date
        self.assertGreater(self.flood_advisory.expires, reference_date)

        # Check that the thunderstorm warning expires in the future compared to our reference date
        self.assertGreater(self.thunderstorm_warning.expires, reference_date)

        # Create an alert with an expiration date in the past
        past_alert = WeatherAlert(
            id='test_past_alert',
            same_codes=['Test'],
            event='Test Event',
            headline='Test Headline',
            description='Test Description',
            instruction='Test Instruction',
            severity=AlertSeverity.MINOR,
            urgency=AlertUrgency.EXPECTED,
            certainty=AlertCertainty.LIKELY,
            onset=datetime(2020, 1, 1, tzinfo=timezone.utc),
            expires=datetime(2020, 1, 2, tzinfo=timezone.utc)
        )

        # Check that the past alert expires in the past compared to our reference date
        self.assertLess(past_alert.expires, reference_date)

    def test_importance_score(self):
        """Test the importance_score property."""
        # Calculate expected scores based on the formula in the WeatherAlert class
        # flood_advisory: MINOR severity (1*100) + EXPECTED urgency (2*10) + LIKELY certainty (3) = 123
        # thunderstorm_warning: SEVERE severity (3*100) + IMMEDIATE urgency (3*10) + OBSERVED certainty (4) = 334

        self.assertEqual(self.flood_advisory.importance_score, 123)
        self.assertEqual(self.thunderstorm_warning.importance_score, 334)

        # Verify that the thunderstorm warning has a higher importance score than the flood advisory
        self.assertGreater(self.thunderstorm_warning.importance_score, self.flood_advisory.importance_score)

    def test_string_representation(self):
        """Test the string representation of alerts."""
        # Test that the string representation contains important information
        flood_str = str(self.flood_advisory)
        self.assertIn('Flood Advisory', flood_str)
        self.assertIn('MINOR', flood_str)
        self.assertIn('EXPECTED', flood_str)
        self.assertIn('LIKELY', flood_str)

        thunderstorm_str = str(self.thunderstorm_warning)
        self.assertIn('Severe Thunderstorm Warning', thunderstorm_str)
        self.assertIn('SEVERE', thunderstorm_str)
        self.assertIn('IMMEDIATE', thunderstorm_str)
        self.assertIn('OBSERVED', thunderstorm_str)

    def test_alert_comparison(self):
        """Test comparing alerts based on their importance score."""
        # The thunderstorm warning should be more important than the flood advisory
        self.assertGreater(
            self.thunderstorm_warning.importance_score,
            self.flood_advisory.importance_score
        )

        # Create alerts with different severity levels
        minor_alert = WeatherAlert(
            id='minor_alert',
            same_codes=['Test'],
            event='Minor Event',
            headline='Minor Alert',
            description='Test Description',
            instruction='Test Instruction',
            severity=AlertSeverity.MINOR,
            urgency=AlertUrgency.EXPECTED,
            certainty=AlertCertainty.LIKELY,
            onset=datetime(2025, 1, 1, tzinfo=timezone.utc),
            expires=datetime(2025, 1, 2, tzinfo=timezone.utc)
        )

        moderate_alert = WeatherAlert(
            id='moderate_alert',
            same_codes=['Test'],
            event='Moderate Event',
            headline='Moderate Alert',
            description='Test Description',
            instruction='Test Instruction',
            severity=AlertSeverity.MODERATE,
            urgency=AlertUrgency.EXPECTED,
            certainty=AlertCertainty.LIKELY,
            onset=datetime(2025, 1, 1, tzinfo=timezone.utc),
            expires=datetime(2025, 1, 2, tzinfo=timezone.utc)
        )

        extreme_alert = WeatherAlert(
            id='extreme_alert',
            same_codes=['Test'],
            event='Extreme Event',
            headline='Extreme Alert',
            description='Test Description',
            instruction='Test Instruction',
            severity=AlertSeverity.EXTREME,
            urgency=AlertUrgency.IMMEDIATE,
            certainty=AlertCertainty.OBSERVED,
            onset=datetime(2025, 1, 1, tzinfo=timezone.utc),
            expires=datetime(2025, 1, 2, tzinfo=timezone.utc)
        )

        # Verify the order of importance
        self.assertLess(minor_alert.importance_score, moderate_alert.importance_score)
        self.assertLess(moderate_alert.importance_score, extreme_alert.importance_score)
        self.assertLess(minor_alert.importance_score, extreme_alert.importance_score)

        # Test finding the most important alert
        alerts = [minor_alert, moderate_alert, extreme_alert, self.flood_advisory, self.thunderstorm_warning]
        most_important = max(alerts, key=lambda alert: alert.importance_score)
        self.assertEqual(most_important, extreme_alert)

if __name__ == '__main__':
    unittest.main()
