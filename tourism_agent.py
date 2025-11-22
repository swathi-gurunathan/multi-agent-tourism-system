"""
Tourism AI Agent - Parent agent that orchestrates weather and places agents.
"""
import re
from weather_agent import WeatherAgent
from places_agent import PlacesAgent
from geocoding import get_coordinates


class TourismAgent:
    """Parent agent that orchestrates child agents based on user queries."""
    
    def __init__(self, api_key: str = None):
        self.weather_agent = WeatherAgent()
        self.places_agent = PlacesAgent()
    
    def extract_intent_and_place(self, user_input: str) -> dict:
        """
        Extract user intent and place name using pattern matching.
        
        Args:
            user_input: User's query
            
        Returns:
            Dictionary with place name and required actions
        """
        import re
        
        user_input_lower = user_input.lower()
        
        # Determine if weather is requested
        weather_keywords = ['weather', 'temperature', 'temp', 'climate', 'forecast', 'hot', 'cold', 'rain']
        needs_weather = any(keyword in user_input_lower for keyword in weather_keywords)
        
        # Determine if places/attractions are requested
        places_keywords = ['place', 'places', 'attraction', 'attractions', 'visit', 'see', 'tourist', 'tourism', 'plan', 'trip', 'things to do', 'sightseeing']
        needs_places = any(keyword in user_input_lower for keyword in places_keywords)
        
        # Extract place name using common patterns (case-insensitive)
        place = None
        
        # Patterns to extract place names - more specific patterns first
        patterns = [
            # "in <place>" or "to <place>"
            r'\b(?:in|to|at)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+){0,2})\s*[?,]?',
            # "weather in <place>"
            r'\b(?:weather|temperature|temp|climate)\s+(?:in|at|for)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+){0,2})\b',
            # "going to <place>"
            r'\b(?:go|going|visit|visiting)\s+(?:to\s+)?([a-zA-Z]+(?:\s+[a-zA-Z]+){0,2})\b',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                place = match.group(1).strip()
                
                # Remove common words that shouldn't be part of place names
                stop_words = ['the', 'what', 'is', 'are', 'a', 'an', 'my', 'your', 'let', 'me', 'i', 'you']
                words = place.split()
                filtered_words = [w for w in words if w.lower() not in stop_words]
                
                if filtered_words:
                    place = ' '.join(filtered_words)
                    # Capitalize first letter of each word
                    place = place.title()
                    break
        
        # If no pattern matched, look for capitalized words (proper nouns)
        if not place:
            words = user_input.split()
            capitalized = [w for w in words if w and len(w) > 2 and w[0].isupper() and w.lower() not in ['what', 'the', 'and', 'or']]
            if capitalized:
                place = ' '.join(capitalized)
        
        result = {
            'place': place,
            'needs_weather': needs_weather,
            'needs_places': needs_places,
            'place_exists': place is not None
        }
        
        return result
    
    def process_query(self, user_input: str) -> str:
        """
        Process user query and coordinate child agents.
        
        Args:
            user_input: User's query
            
        Returns:
            Response string
        """
        # Extract intent and place
        intent = self.extract_intent_and_place(user_input)
        
        if not intent['place_exists'] or not intent['place']:
            return "I don't know if this place exists. Please provide a valid location name."
        
        place_name = intent['place']
        
        # Verify place exists using geocoding
        coords = get_coordinates(place_name)
        if not coords:
            return f"I don't know if {place_name} exists. Please check the spelling or try a different location."
        
        responses = []
        
        # Get weather if requested
        if intent['needs_weather']:
            weather_data = self.weather_agent.get_weather(place_name)
            if weather_data:
                weather_response = self.weather_agent.format_weather_response(weather_data)
                responses.append(weather_response)
            else:
                responses.append(f"Unable to fetch weather information for {place_name}.")
        
        # Get places if requested
        if intent['needs_places']:
            places = self.places_agent.get_tourist_places(place_name, limit=5)
            if places:
                places_response = self.places_agent.format_places_response(places, place_name)
                responses.append(places_response)
            else:
                responses.append(f"Unable to find tourist attractions in {place_name}.")
        
        # If neither was requested, provide both (default behavior for trip planning)
        if not intent['needs_weather'] and not intent['needs_places']:
            places = self.places_agent.get_tourist_places(place_name, limit=5)
            if places:
                places_response = self.places_agent.format_places_response(places, place_name)
                responses.append(places_response)
            else:
                responses.append(f"Unable to find tourist attractions in {place_name}.")
        
        # Format the combined response properly
        if len(responses) > 1 and intent['needs_weather'] and intent['needs_places']:
            # Both weather and places requested
            return responses[0] + " And these are the places you can go:\n" + responses[1].split(':\n', 1)[1]
        else:
            # Single response or default
            return "\n\n".join(responses)
