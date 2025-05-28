# WeatherBox

A Python library for fetching and processing weather alerts from the National Weather Service (NWS) API.

## Features

- Fetch weather alerts for specific locations using city and state names
- Convert city and state to coordinates using geocoding
- Use coordinates to get weather alerts from the NWS API
- Parse and model weather alerts with detailed information
- Classify alerts by importance based on severity, urgency, and certainty
- Filter alerts to get the most important non-expired alert for each location
- Simple command-line interface for demonstration

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

The project includes a sample command-line program that demonstrates the functionality:

```
python main.py <CITY> <STATE>
```

Replace `<CITY>` with the name of the city and `<STATE>` with the name or abbreviation of the state you want to get alerts for.

Example:
```
python main.py "New York" NY
```

This will fetch the most important active weather alert for the specified location and display it in the console.

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

## API Documentation

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

  Get all weather alerts for a list of SAME codes (legacy method).

- `get_most_important_alerts(same_codes: List[str]) -> Dict[str, Optional[WeatherAlert]]`

  Get the most important non-expired alert for each SAME code (legacy method).

### WeatherAlert

A data class representing a weather alert.

#### Properties:

- `is_expired: bool` - Check if the alert has expired
- `importance_score: int` - Calculate an importance score for the alert

## License

This project is licensed under the MIT License - see the LICENSE file for details.
