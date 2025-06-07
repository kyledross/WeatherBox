from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum, auto
from typing import List, Optional


class AlertSeverity(Enum):
    """Enum representing the severity of a weather alert."""
    UNKNOWN = auto()
    MINOR = auto()
    MODERATE = auto()
    SEVERE = auto()
    EXTREME = auto()

    @classmethod
    def from_string(cls, value: str) -> 'AlertSeverity':
        """Convert a string severity to an AlertSeverity enum value."""
        mapping = {
            "unknown": cls.UNKNOWN,
            "minor": cls.MINOR,
            "moderate": cls.MODERATE,
            "severe": cls.SEVERE,
            "extreme": cls.EXTREME
        }
        return mapping.get(value.lower(), cls.UNKNOWN)


class AlertUrgency(Enum):
    """Enum representing the urgency of a weather alert."""
    UNKNOWN = auto()
    FUTURE = auto()
    EXPECTED = auto()
    IMMEDIATE = auto()

    @classmethod
    def from_string(cls, value: str) -> 'AlertUrgency':
        """Convert a string urgency to an AlertUrgency enum value."""
        mapping = {
            "unknown": cls.UNKNOWN,
            "future": cls.FUTURE,
            "expected": cls.EXPECTED,
            "immediate": cls.IMMEDIATE
        }
        return mapping.get(value.lower(), cls.UNKNOWN)


class AlertCertainty(Enum):
    """Enum representing the certainty of a weather alert."""
    UNKNOWN = auto()
    UNLIKELY = auto()
    POSSIBLE = auto()
    LIKELY = auto()
    OBSERVED = auto()

    @classmethod
    def from_string(cls, value: str) -> 'AlertCertainty':
        """Convert a string certainty to an AlertCertainty enum value."""
        mapping = {
            "unknown": cls.UNKNOWN,
            "unlikely": cls.UNLIKELY,
            "possible": cls.POSSIBLE,
            "likely": cls.LIKELY,
            "observed": cls.OBSERVED
        }
        return mapping.get(value.lower(), cls.UNKNOWN)


@dataclass
class WeatherAlert:
    """Model representing a weather alert from the National Weather Service API."""
    id: str
    same_codes: List[str]
    event: str
    headline: str
    description: str
    instruction: Optional[str]
    severity: AlertSeverity
    urgency: AlertUrgency
    certainty: AlertCertainty
    onset: Optional[datetime]
    expires: datetime
    
    @property
    def is_expired(self) -> bool:
        """Check if the alert has expired."""
        # Convert current time to UTC
        current_time_utc = datetime.now(timezone.utc)

        # Ensure expires is in UTC (if it has a timezone, convert; if not, assume UTC)
        if self.expires.tzinfo is not None:
            expires_utc = self.expires.astimezone(timezone.utc)
        else:
            expires_utc = self.expires.replace(tzinfo=timezone.utc)

        return current_time_utc > expires_utc
    
    @property
    def importance_score(self) -> int:
        """
        Calculate an importance score for the alert based on severity, urgency, and certainty.
        Higher score means more important.
        """
        severity_score = {
            AlertSeverity.UNKNOWN: 0,
            AlertSeverity.MINOR: 1,
            AlertSeverity.MODERATE: 2,
            AlertSeverity.SEVERE: 3,
            AlertSeverity.EXTREME: 4
        }
        
        urgency_score = {
            AlertUrgency.UNKNOWN: 0,
            AlertUrgency.FUTURE: 1,
            AlertUrgency.EXPECTED: 2,
            AlertUrgency.IMMEDIATE: 3
        }
        
        certainty_score = {
            AlertCertainty.UNKNOWN: 0,
            AlertCertainty.UNLIKELY: 1,
            AlertCertainty.POSSIBLE: 2,
            AlertCertainty.LIKELY: 3,
            AlertCertainty.OBSERVED: 4
        }
        
        return (
            severity_score[self.severity] * 100 +
            urgency_score[self.urgency] * 10 +
            certainty_score[self.certainty] +
            (100 if self.certainty == AlertCertainty.OBSERVED else
             50 if self.certainty == AlertCertainty.LIKELY else 0)
        )
    
    def __str__(self) -> str:
        """Return a string representation of the alert."""
        return (
            f"Weather Alert: {self.headline}\n"
            f"Event: {self.event}\n"
            f"Areas: {', '.join(self.same_codes)}\n"
            f"Severity: {self.severity.name}\n"
            f"Urgency: {self.urgency.name}\n"
            f"Certainty: {self.certainty.name}\n"
            f"Onset: {self.onset.strftime('%Y-%m-%d %H:%M:%S') if self.onset else 'N/A'}\n"
            f"Expires: {self.expires.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Description: {self.description}\n"
            f"Instructions: {self.instruction if self.instruction else 'N/A'}"
        )