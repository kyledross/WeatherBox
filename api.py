from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
from weatherbox.weather_service import WeatherAlertService
from datetime import timezone

app = FastAPI(title="WeatherBox API",
              description="A simple API for fetching weather alerts from the National Weather Service.  "
                          "Given a city and state, it returns the most important unexpired weather alert for that location, if any.",
              version="1.0.0")
service = WeatherAlertService()

class WeatherAlertResponse(BaseModel):
    city: str
    state: str
    latitude: float
    longitude: float
    headline: Optional[str] = None
    event: Optional[str] = None
    severity: Optional[str] = None
    severity_score: Optional[int] = None
    urgency: Optional[str] = None
    urgency_score: Optional[int] = None
    certainty: Optional[str] = None
    certainty_score: Optional[int] = None
    expires: Optional[str] = None
    description: Optional[str] = None
    instruction: Optional[str] = None
    nws_headline: Optional[str] = None

@app.get("/weather-alert/{state}/{city}", response_model=WeatherAlertResponse)
def get_weather_alert(state: str, city: str):
    try:
        # Get coordinates
        latitude, longitude = service.get_coordinates(city, state)

        # Get alert
        alert = service.get_most_important_alerts_for_location(city, state)

        response = {
            "city": city,
            "state": state,
            "latitude": latitude,
            "longitude": longitude
        }

        if alert:
            severity_score_map = {
                "UNKNOWN": 0,
                "MINOR": 1,
                "MODERATE": 2,
                "SEVERE": 3,
                "EXTREME": 4
            }
            urgency_score_map = {
                "UNKNOWN": 0,
                "FUTURE": 1,
                "EXPECTED": 2,
                "IMMEDIATE": 3
            }
            certainty_score_map = {
                "UNKNOWN": 0,
                "UNLIKELY": 1,
                "POSSIBLE": 2,
                "LIKELY": 3,
                "OBSERVED": 4
            }
            response.update({
                "headline": alert.headline,
                "event": alert.event,
                "severity": alert.severity.name,
                "severity_score": severity_score_map.get(alert.severity.name, 0),
                "urgency": alert.urgency.name,
                "urgency_score": urgency_score_map.get(alert.urgency.name, 0),
                "certainty": alert.certainty.name,
                "certainty_score": certainty_score_map.get(alert.certainty.name, 0),
                "expires": alert.expires.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
                "description": alert.description,
                "instruction": alert.instruction,
                "nws_headline": alert.nws_headline
            })

        return response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))