"""
Places Agent - Fetches tourist attractions using Overpass API.
"""
import requests
from typing import List, Optional
from geocoding import get_coordinates


class PlacesAgent:
    """Agent responsible for fetching tourist attractions."""
    
    def __init__(self):
        self.base_url = "https://overpass-api.de/api/interpreter"
    
    def get_tourist_places(self, place_name: str, limit: int = 5) -> Optional[List[str]]:
        """
        Get tourist attractions for a given place.
        
        Args:
            place_name: Name of the place
            limit: Maximum number of places to return (default: 5)
            
        Returns:
            List of tourist attraction names or None if failed
        """
        # First, get coordinates
        coords = get_coordinates(place_name)
        
        if not coords:
            return None
        
        lat = coords['lat']
        lon = coords['lon']
        
        # Search radius in meters (approximately 20km)
        radius = 20000
        
        # Overpass QL query to find tourist attractions
        query = f"""
        [out:json];
        (
          node["tourism"](around:{radius},{lat},{lon});
          way["tourism"](around:{radius},{lat},{lon});
          node["historic"](around:{radius},{lat},{lon});
          way["historic"](around:{radius},{lat},{lon});
          node["leisure"="park"](around:{radius},{lat},{lon});
          way["leisure"="park"](around:{radius},{lat},{lon});
        );
        out body {limit * 3};
        """
        
        try:
            response = requests.post(self.base_url, data=query, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            elements = data.get('elements', [])
            
            # Extract place names
            places = []
            seen_names = set()
            
            for element in elements:
                tags = element.get('tags', {})
                name = tags.get('name')
                
                if name and name not in seen_names:
                    places.append(name)
                    seen_names.add(name)
                    
                    if len(places) >= limit:
                        break
            
            return places if places else None
            
        except Exception as e:
            print(f"Error fetching tourist places: {e}")
            return None
    
    def format_places_response(self, places: List[str], place_name: str) -> str:
        """
        Format places data into a readable response.
        
        Args:
            places: List of tourist attraction names
            place_name: Name of the location
            
        Returns:
            Formatted places string
        """
        if not places:
            return f"Unable to find tourist attractions in {place_name}."
        
        places_list = "\n".join([f"- {place}" for place in places])
        return f"In {place_name} these are the places you can go:\n{places_list}"
