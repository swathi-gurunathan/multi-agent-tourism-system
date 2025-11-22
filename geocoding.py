"""
Geocoding utility using Nominatim API to convert place names to coordinates.
"""
import requests
from typing import Optional, Dict


def get_coordinates(place_name: str) -> Optional[Dict[str, float]]:
    """
    Get latitude and longitude for a given place name using Nominatim API.
    
    Args:
        place_name: Name of the place to geocode
        
    Returns:
        Dictionary with 'lat' and 'lon' keys, or None if place not found
    """
    base_url = "https://nominatim.openstreetmap.org/search"
    
    params = {
        'q': place_name,
        'format': 'json',
        'limit': 1
    }
    
    headers = {
        'User-Agent': 'TourismAIAgent/1.0'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if data and len(data) > 0:
            return {
                'lat': float(data[0]['lat']),
                'lon': float(data[0]['lon']),
                'display_name': data[0].get('display_name', place_name)
            }
        return None
        
    except Exception as e:
        print(f"Error geocoding place: {e}")
        return None
