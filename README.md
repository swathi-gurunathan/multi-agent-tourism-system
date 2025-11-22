# Multi-Agent Tourism System

A tourism planning system with AI agents that provide weather information and tourist attraction suggestions.

## Features

- **Weather Agent**: Fetches current weather and forecasts using Open-Meteo API
- **Places Agent**: Suggests tourist attractions using Overpass API and OpenStreetMap data
- **Parent Tourism Agent**: Uses LLMs (Groq/OpenAI/Claude) for intelligent intent recognition with pattern-matching fallback
- **Web Interface**: Modern, responsive web UI for easy interaction
- **Auto-Translation**: Tourist places translated to English
- **Multiple LLM Support**: Groq (FREE), OpenAI, or Anthropic Claude

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. **(Optional)** Get a FREE API key from Groq:
   - Visit: https://console.groq.com
   - Create account and get API key
   - Create `.env` file:
   ```
   LLM_PROVIDER=groq
   GROQ_API_KEY=your_key_here
   ```
   - **Note**: The system works without an API key using pattern matching!

3. Run the web application:
```bash
python app.py
```

4. Open http://localhost:5000 in your browser

## Supported LLM Providers

- **Groq** (Recommended) - FREE, fast inference
- **OpenAI** - GPT-3.5/GPT-4 (Paid)
- **Anthropic** - Claude (Paid)

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
