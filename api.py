from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
from weatherbox.weather_service import WeatherAlertService
from datetime import timezone

app = FastAPI(title="WeatherBox API",
              description="A simple API for fetching weather alerts from the National Weather Service."
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
    urgency: Optional[str] = None
    expires: Optional[str] = None
    description: Optional[str] = None
    instruction: Optional[str] = None

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
            response.update({
                "headline": alert.headline,
                "event": alert.event,
                "severity": alert.severity.name,
                "urgency": alert.urgency.name,
                "expires": alert.expires.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
                "description": alert.description,
                "instruction": alert.instruction
            })

        return response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))