"""
Tourism AI Agent - Parent agent that orchestrates weather and places agents.
"""
import re
import os
from weather_agent import WeatherAgent
from places_agent import PlacesAgent
from geocoding import get_coordinates

# Try to import LLM providers (optional dependencies)
try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class TourismAgent:
    """Parent agent that orchestrates child agents based on user queries."""
    
    def __init__(self, api_key: str = None):
        self.weather_agent = WeatherAgent()
        self.places_agent = PlacesAgent()
        self.conversation_history = []  # Track conversation for context
        
        # Try to initialize LLM if API key is provided
        self.llm = None
        self.use_ai = False
        
        if api_key:
            try:
                # Use Groq LLM (best compatibility with free tier)
                provider = os.getenv('LLM_PROVIDER', 'groq').lower()
                
                if provider == 'groq' and GROQ_AVAILABLE:
                    # Using llama-3.3-70b-versatile (current recommended model)
                    self.llm = ChatGroq(api_key=api_key, model="llama-3.3-70b-versatile")
                    self.use_ai = True
                    print("✓ Groq LLM initialized successfully - Dynamic AI responses enabled!")
                else:
                    print(f"⚠ Groq not available. Install with: pip install langchain-groq")
            except Exception as e:
                print(f"⚠ Failed to initialize LLM: {e}")
                print("  Falling back to pattern-based responses")
                self.llm = None
                self.use_ai = False
    
    def extract_intent_and_place(self, user_input: str) -> dict:
        """
        Extract user intent and place name using AI or pattern matching.
        
        Args:
            user_input: User's query
            
        Returns:
            Dictionary with place name and required actions
        """
        # Try AI-based extraction if available
        if self.use_ai and self.llm:
            try:
                prompt = f"""Analyze this tourism query and extract:
1. The place/city name (return NONE if no place mentioned)
2. Whether weather info is requested (true/false)
3. Whether tourist places/attractions are requested (true/false)

Query: "{user_input}"

Respond in this exact format:
PLACE: [place name or NONE]
WEATHER: [true/false]
PLACES: [true/false]"""

                response = self.llm.invoke(prompt)
                text = response.content.strip()
                
                result = {
                    'place': None,
                    'needs_weather': False,
                    'needs_places': False,
                    'place_exists': True
                }
                
                for line in text.split('\n'):
                    if line.startswith('PLACE:'):
                        place = line.replace('PLACE:', '').strip()
                        if place.upper() != 'NONE':
                            result['place'] = place
                            result['place_exists'] = True
                        else:
                            result['place_exists'] = False
                    elif line.startswith('WEATHER:'):
                        result['needs_weather'] = 'true' in line.lower()
                    elif line.startswith('PLACES:'):
                        result['needs_places'] = 'true' in line.lower()
                
                return result
            except Exception as e:
                print(f"AI extraction failed, falling back to patterns: {e}")
        
        # Fallback to pattern matching
        return self._extract_with_patterns(user_input)
    
    def _extract_with_patterns(self, user_input: str) -> dict:
        """Fallback pattern-based extraction."""
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
            # "<place> trip/weather/places" - place name at the beginning
            r'^([a-zA-Z]+(?:\s+[a-zA-Z]+){0,2})\s+(?:trip|weather|temperature|places|attractions|visit)',
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
    
    def process_query(self, user_input: str, conversation_history: list = None) -> str:
        """
        Process user query and coordinate child agents.
        
        Args:
            user_input: User's query
            conversation_history: Optional list of previous messages
            
        Returns:
            Response string
        """
        # Use provided history or instance history
        if conversation_history is not None:
            self.conversation_history = conversation_history
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Extract intent and place
        intent = self.extract_intent_and_place(user_input)
        
        # Handle queries without a clear place name
        if not intent['place_exists'] or not intent['place']:
            # Use LLM for dynamic conversational responses if available
            if self.llm:
                try:
                    # Build context from conversation history
                    history_context = ""
                    if len(self.conversation_history) > 1:
                        recent_history = self.conversation_history[-5:]  # Last 5 messages
                        history_context = "\n\nPrevious conversation:\n"
                        for msg in recent_history[:-1]:  # Exclude current message
                            role = "User" if msg["role"] == "user" else "Assistant"
                            history_context += f"{role}: {msg['content']}\n"
                    
                    prompt = f"""You are a friendly travel planning assistant. {history_context}

The user just asked: "{user_input}"

This query doesn't specify a clear destination. Respond naturally and conversationally, explaining that you need to know which city or place they're interested in to provide weather information and tourist attractions. Give 1-2 example queries they could ask.

Keep your response concise (2-3 sentences) and helpful."""
                    
                    response = self.llm.invoke(prompt)
                    response_text = response.content
                    
                    # Add assistant response to history
                    self.conversation_history.append({"role": "assistant", "content": response_text})
                    
                    return response_text
                except Exception as e:
                    print(f"LLM error for vague query: {str(e)}")
            
            # Fallback to pattern-based response if LLM unavailable
            duration_keywords = ['how many days', 'how long', 'duration', 'stay']
            if any(keyword in user_input.lower() for keyword in duration_keywords):
                response_text = "I'd be happy to help you plan your trip duration! However, I need to know which destination you're interested in. Could you please tell me which city or place you're planning to visit? For example, 'How many days should I stay in Tokyo?' or 'Plan a trip to Paris'."
                self.conversation_history.append({"role": "assistant", "content": response_text})
                return response_text
            
            general_keywords = ['trip', 'travel', 'vacation', 'holiday', 'tour']
            if any(keyword in user_input.lower() for keyword in general_keywords):
                response_text = "I'd love to help you plan your trip! Please tell me which destination you're interested in, and I can provide weather information and suggest tourist attractions. For example, try asking: 'What's the weather in Paris?' or 'Plan a trip to Tokyo'."
                self.conversation_history.append({"role": "assistant", "content": response_text})
                return response_text
            
            response_text = "I'm here to help you plan your trip! Please specify a destination, and I can provide weather information and tourist attraction suggestions. For example, you can ask: 'What's the weather in London?' or 'What places can I visit in Tokyo?'"
            self.conversation_history.append({"role": "assistant", "content": response_text})
            return response_text
        
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
