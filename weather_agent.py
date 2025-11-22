"""
Weather Agent - Fetches weather information using Open-Meteo API.
"""
import requests
from typing import Dict, Optional
from geocoding import get_coordinates


class WeatherAgent:
    """Agent responsible for fetching weather information."""
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
    
    def get_weather(self, place_name: str) -> Optional[Dict]:
        """
        Get current weather for a given place.
        
        Args:
            place_name: Name of the place
            
        Returns:
            Dictionary with weather information or None if failed
        """
        # First, get coordinates
        coords = get_coordinates(place_name)
        
        if not coords:
            return None
        
        # Fetch weather data
        params = {
            'latitude': coords['lat'],
            'longitude': coords['lon'],
            'current': 'temperature_2m,precipitation_probability,weather_code',
            'timezone': 'auto'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            current = data.get('current', {})
            
            return {
                'temperature': current.get('temperature_2m'),
                'precipitation_probability': current.get('precipitation_probability', 0),
                'weather_code': current.get('weather_code'),
                'place': place_name,
                'display_name': coords.get('display_name', place_name)
            }
            
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None
    
    def format_weather_response(self, weather_data: Dict) -> str:
        """
        Format weather data into a readable response.
        
        Args:
            weather_data: Dictionary containing weather information
            
        Returns:
            Formatted weather string
        """
        if not weather_data:
            return "Unable to fetch weather information."
        
        temp = weather_data.get('temperature', 'N/A')
        precip = weather_data.get('precipitation_probability', 0)
        place = weather_data.get('place', 'the location')
        
        return f"In {place} it's currently {temp}°C with a chance of {precip}% to rain."
