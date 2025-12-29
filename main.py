import os
import warnings
from dotenv import load_dotenv
from agent1.weather_agent import get_weather
from agent2.precaution_agent import get_precautions
from agent3.itinerary_agent import get_itinerary

def main():
    warnings.filterwarnings("ignore", category=FutureWarning)
    load_dotenv() # Load environment variables from .env file

    weather_api_key = os.getenv("WEATHER_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not weather_api_key:
        print("Error: WEATHER_API_KEY not found in .env file or environment variables.")
        return
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY not found in .env file or environment variables.")
        return
        
    query = input("Enter your query (e.g., 'I am planning a trip to Kochi'): ")
    days = int(input("Enter the number of days for the forecast and itinerary: "))

    weather_report, extracted_place_name, weather_logs = get_weather(query, days, weather_api_key, gemini_api_key)
    
    if not extracted_place_name:
        print("Weather Report:")
        print(weather_report)
        return

    print(f"\nGetting weather for {extracted_place_name} for {days} days...")
    print("Weather Report:")
    print(weather_report)

    if "this place is in-serviceable" in weather_report:
        return

    print("\nAnalyzing weather and suggesting precautions...")
    precautions, precautions_logs = get_precautions(weather_report, extracted_place_name, gemini_api_key)
    print("Precautions:")
    print(precautions)

    print("\nGenerating travel itinerary...")
    itinerary, itinerary_logs = get_itinerary(weather_report, extracted_place_name, days, gemini_api_key)
    print("Travel Itinerary:")
    print(itinerary)

if __name__ == "__main__":
    main()