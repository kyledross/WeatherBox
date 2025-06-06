# WeatherBox

A Python library and API for fetching and processing weather alerts from the National Weather Service (NWS) API.

## Features

- Fetch weather alerts for specific locations using city and state names
- Convert city and state to coordinates using geocoding
- Use coordinates to get weather alerts from the NWS API
- Parse and model weather alerts with detailed information
- Classify alerts by importance based on severity, urgency, and certainty
- Filter alerts to get the single most important non-expired alert for each location
- REST API for accessing weather alerts via HTTP

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/WeatherBox.git
   cd WeatherBox
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Command-line Interface

The project includes test scripts that demonstrate the functionality:

```
python tests/test_location.py
```

This will fetch weather alerts for Washington, DC and display them in the console.

You can modify the script to test different locations by editing the city and state variables in the script.

### Using the Library in Your Code

```python
from weatherbox.weather_service import WeatherAlertService

# Create a weather alert service
service = WeatherAlertService()

# Get coordinates for a location
latitude, longitude = service.get_coordinates("New York", "NY")
print(f"Coordinates: {latitude}, {longitude}")

# Get all alerts for a location
alerts = service.get_alerts_for_location("New York", "NY")
print(f"Found {len(alerts)} alerts")

# Get the most important non-expired alert for a location
important_alert = service.get_most_important_alerts_for_location("New York", "NY")
if important_alert:
    print(f"Most important alert: {important_alert.headline}")
else:
    print("No active alerts for this location")

# You can also get alerts directly using coordinates
alerts_by_coords = service.get_alerts_for_coordinates(40.7128, -74.0060)
```

### REST API

WeatherBox includes a FastAPI-based REST API that allows you to access weather alerts via HTTP requests.

#### Starting the API Server

To start the API server, run:

```
WeatherBox/.venv/bin/python -m uvicorn api:app --reload --host 0.0.0.0 --port 8080
```

This will start the server on `http://localhost:8080` and should be reachable by other clients on the network (assumung no firewall blocking on the host).  

#### API Endpoints

##### GET /weather-alert/{state}/{city}

Get the most important weather alert for a specific city and state.

**Parameters:**
- `state` (path parameter): The state name or abbreviation
- `city` (path parameter): The city name

**Response:**
```json
{
  "city": "New York",
  "state": "NY",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "headline": "Flood Warning issued for New York, NY",
  "event": "Flood Warning",
  "severity": "MODERATE",
  "urgency": "EXPECTED",
  "expires": "2023-07-15 18:00:00 UTC",
  "description": "The National Weather Service has issued a Flood Warning...",
  "instruction": "Move to higher ground. Do not drive through flooded areas..."
}
```

If no alert is active for the location, the alert-specific fields will be `null`.

**Example Request:**
```
GET /weather-alert/NY/New%20York
```

**Error Responses:**
- `404 Not Found`: If the location cannot be found or geocoded
- `500 Internal Server Error`: For server-side errors

#### API Documentation

FastAPI automatically generates interactive API documentation. Once the server is running, you can access:

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Technical Background

### How WeatherBox Works

WeatherBox is designed to simplify the process of fetching and processing weather alerts from the National Weather Service (NWS) API. Here's how it works:

1. **Geocoding**: When you provide a city and state, WeatherBox uses the ArcGIS geocoding service to convert this location into latitude and longitude coordinates.

2. **NWS API Integration**: WeatherBox then queries the NWS API using these coordinates to:
   - First get the forecast office and zone information for the coordinates
   - Then fetch weather alerts for both the county and forecast zone associated with those coordinates

3. **Alert Processing**: The service processes the raw API responses to:
   - Parse the JSON data into structured WeatherAlert objects
   - Extract key information like severity, urgency, and certainty
   - Calculate an "importance score" for each alert based on these factors
   - Filter out expired alerts

4. **Multiple Endpoint Strategy**: The service implements a robust strategy for fetching alerts by trying multiple endpoints and formats:
   - It attempts different URL patterns for SAME codes
   - It handles both county and zone-based alerts
   - It includes fallback mechanisms if certain endpoints fail

5. **Alert Classification**: Alerts are classified using three key factors:
   - **Severity**: How bad the event might be (Minor, Moderate, Severe, Extreme)
   - **Urgency**: How quickly action should be taken (Future, Expected, Immediate)
   - **Certainty**: How confident the NWS is about the event (Unlikely, Possible, Likely, Observed)

6. **Importance Scoring**: A numerical score is calculated for each alert using a weighted formula:
   ```
   score = (severity_value * 100) + (urgency_value * 10) + certainty_value
   ```
   This allows for easy comparison and ranking of alerts.

### Data Models

WeatherBox uses several data models to represent weather alerts and their properties:

1. **WeatherAlert**: The main class representing a weather alert with properties like:
   - ID, event type, headline, description, and instructions
   - Severity, urgency, and certainty classifications
   - Onset and expiration times
   - Methods to check if an alert is expired and calculate its importance

2. **AlertSeverity**: An enum representing the severity levels of alerts:
   - UNKNOWN, MINOR, MODERATE, SEVERE, EXTREME

3. **AlertUrgency**: An enum representing the urgency levels of alerts:
   - UNKNOWN, FUTURE, EXPECTED, IMMEDIATE

4. **AlertCertainty**: An enum representing the certainty levels of alerts:
   - UNKNOWN, UNLIKELY, POSSIBLE, LIKELY, OBSERVED

### API Architecture

The REST API is built using FastAPI, a modern, fast web framework for building APIs with Python. The API:

1. Uses the WeatherAlertService to fetch and process alerts
2. Converts the WeatherAlert objects into JSON-serializable responses
3. Handles errors and edge cases gracefully
4. Provides automatic documentation via Swagger UI and ReDoc

## Library API Documentation

### WeatherAlertService

The main class for interacting with the NWS API.

#### Methods:

- `get_coordinates(city: str, state: str) -> Tuple[float, float]`

  Get the latitude and longitude coordinates for a city and state.

- `get_alerts_for_coordinates(latitude: float, longitude: float) -> List[WeatherAlert]`

  Get weather alerts for specific coordinates.

- `get_alerts_for_location(city: str, state: str) -> List[WeatherAlert]`

  Get weather alerts for a specific city and state.

- `get_most_important_alerts_for_location(city: str, state: str) -> Optional[WeatherAlert]`

  Get the most important non-expired alert for a specific city and state.

- `get_alerts_for_same_codes(same_codes: List[str]) -> List[WeatherAlert]`

  Get all weather alerts for a list of SAME codes.

- `get_most_important_alerts(same_codes: List[str]) -> Dict[str, Optional[WeatherAlert]]`

  Get the most important non-expired alert for each SAME code.

### WeatherAlert

A data class representing a weather alert.

#### Properties:

- `is_expired: bool` - Check if the alert has expired
- `importance_score: int` - Calculate an importance score for the alert

