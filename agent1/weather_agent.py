import google.generativeai as genai
import requests
from datetime import datetime

def extract_location(query: str, api_key: str) -> tuple[str, list[dict]]:
    """
    Extracts the location from a natural language query using a generative model.

    Args:
        query: The user's query.
        api_key: The Google AI API key.

    Returns:
        A tuple containing the extracted location name (str) and a list of log entries (list[dict]).
    """
    logs = []
    logs.append({"step": "Starting location extraction", "status": "started", "details": f"Query: '{query}'"})
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        logs.append({"step": "Calling Gemini model for location extraction", "status": "in_progress", "details": "Model: 'gemini-2.5-flash'"})
        
        response = model.generate_content(f"From the following sentence, extract ONLY the name of the location. If no location is explicitly mentioned or it's unclear, respond with 'None'. Sentence: '{query}'")
        
        location = response.text.strip()
        
        if location.lower() == 'none':
            logs.append({"step": "Gemini model response", "status": "completed", "details": f"No location found. Model returned: '{location}'"})
            return "", logs
        else:
            logs.append({"step": "Gemini model response", "status": "completed", "details": f"Location extracted: '{location}'"})
            return location, logs
    except Exception as e:
        logs.append({"step": "Error during location extraction", "status": "error", "details": str(e)})
        return "", logs

def get_weather(place: str, days: int, api_key: str, google_ai_api_key: str) -> tuple[list[dict], str, list[dict]]:
    """
    Gets the weather forecast for a given place and number of days.

    Args:
        place: The name of the place or a query containing the place.
        days: The number of days for the forecast.
        api_key: The OpenWeatherMap API key.
        google_ai_key: The Google AI API key for location extraction.

    Returns:
        A tuple containing:
        - A list of dictionaries, each representing a daily forecast.
        - The extracted location name (str).
        - A list of log entries (list[dict]).
    """
    weather_agent_logs = []
    weather_agent_logs.append({"step": "Weather Agent started", "status": "started", "details": f"Query: '{place}', Days: {days}"})

    location_name, extract_logs = extract_location(place, google_ai_api_key)
    weather_agent_logs.extend(extract_logs)

    if not location_name:
        weather_agent_logs.append({"step": "Location extraction failed", "status": "completed", "details": "No valid location extracted."})
        return [], "", weather_agent_logs # Return empty list for structured data

    try:
        # Geocoding using Nominatim
        weather_agent_logs.append({"step": "Geocoding location", "status": "in_progress", "details": f"Using Nominatim API for '{location_name}'"})
        geocode_url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json"
        headers = {'User-Agent': 'Multi-Agent-Weather-App/1.0'}
        geocode_response = requests.get(geocode_url, headers=headers)
        geocode_response.raise_for_status()
        location_data = geocode_response.json()

        if not location_data:
            weather_agent_logs.append({"step": "Geocoding failed", "status": "completed", "details": f"Could not find coordinates for {location_name}"})
            return [], "", weather_agent_logs # Return empty list
        
        lat = location_data[0]["lat"]
        lon = location_data[0]["lon"]
        weather_agent_logs.append({"step": "Geocoding completed", "status": "completed", "details": f"Lat: {lat}, Lon: {lon}"})

        # Weather forecast using OpenWeatherMap 5-day/3-hour forecast
        weather_agent_logs.append({"step": "Fetching weather forecast", "status": "in_progress", "details": "Using OpenWeatherMap 5-day/3-hour forecast API"})
        weather_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        if not weather_data.get("list"):
            weather_agent_logs.append({"step": "Weather data retrieval failed", "status": "completed", "details": "API returned no forecast list."})
            return [], "", weather_agent_logs # Return empty list

        weather_agent_logs.append({"step": "Weather data retrieved", "status": "completed", "details": "Successfully fetched forecast data."})

        structured_weather_data = []
        
        # Process the 3-hour forecast to get daily summary
        weather_agent_logs.append({"step": "Processing daily forecasts", "status": "in_progress", "details": "Aggregating 3-hour data into daily summaries."})
        daily_forecasts = {}
        for forecast in weather_data["list"]:
            date = datetime.fromtimestamp(forecast["dt"]).strftime('%Y-%m-%d')
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    "temps": [],
                    "weather": []
                }
            daily_forecasts[date]["temps"].append(forecast["main"]["temp"])
            daily_forecasts[date]["weather"].append(forecast["weather"][0]["description"])

        day_count = 0
        for date, data in daily_forecasts.items():
            if day_count >= days:
                break
            
            min_temp = min(data["temps"])
            max_temp = max(data["temps"])
            weather_description = max(set(data["weather"]), key=data["weather"].count)
            
            structured_weather_data.append({
                "Date": date,
                "Weather": weather_description.capitalize(),
                "High Temp (°C)": f"{max_temp:.2f}",
                "Low Temp (°C)": f"{min_temp:.2f}"
            })
            day_count += 1
        
        weather_agent_logs.append({"step": "Daily forecasts processed", "status": "completed", "details": "Generated structured summary for each day."})
        
        return structured_weather_data, location_name, weather_agent_logs

    except requests.exceptions.RequestException as e:
        weather_agent_logs.append({"step": "API request error", "status": "error", "details": str(e)})
        return [], "", weather_agent_logs
    except (KeyError, IndexError) as e:
        weather_agent_logs.append({"step": "Data parsing error", "status": "error", "details": str(e)})
        return [], "", weather_agent_logs

def get_weather_description(weather_code: int) -> str:
    # This function is no longer used with OpenWeatherMap's text descriptions
    # but is kept for reference or future use with other APIs.
    wmo_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog",
        48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        56: "Light freezing drizzle", 57: "Dense freezing drizzle", 61: "Slight rain",
        63: "Moderate rain", 65: "Heavy rain", 66: "Light freezing rain", 67: "Heavy freezing rain",
        71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall", 77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers", 95: "Thunderstorm",
        96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
    }
    return wmo_codes.get(weather_code, "Unknown weather")