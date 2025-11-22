# Multi-Agent Tourism System

A tourism planning system with AI agents that provide weather information and tourist attraction suggestions.

## Features

- **Weather Agent**: Fetches current weather and forecasts using Open-Meteo API
- **Places Agent**: Suggests tourist attractions using Overpass API and OpenStreetMap data
- **Parent Tourism Agent**: Orchestrates both child agents based on user queries using pattern matching
- **Web Interface**: Modern, responsive web UI for easy interaction

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the web application:
```bash
python app.py
```

3. Open http://localhost:5000 in your browser

## Usage Examples

**Example 1: Get tourist places**
```
Input: I'm going to go to Bangalore, let's plan my trip.
```

**Example 2: Get weather**
```
Input: I'm going to go to Bangalore, what is the temperature there
```

**Example 3: Get both weather and places**
```
Input: I'm going to go to Bangalore, what is the temperature there? And what are the places I can visit?
```

## APIs Used

- **Nominatim API**: Geocoding (place name to coordinates)
- **Open-Meteo API**: Weather data
- **Overpass API**: Tourist attractions from OpenStreetMap
