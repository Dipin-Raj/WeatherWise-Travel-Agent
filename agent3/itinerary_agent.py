
import google.generativeai as genai

def get_itinerary(weather_report: str, place: str, days: int, api_key: str) -> tuple[str, list[dict]]:
    """
    Generates a travel itinerary using the Gemini API.

    Args:
        weather_report: A string containing the weather report.
        place: The name of the place.
        days: The number of days for the itinerary.
        api_key: The Gemini API key.

    Returns:
        A tuple containing the travel itinerary string and a list of log entries (list[dict]).
    """
    itinerary_agent_logs = []
    itinerary_agent_logs.append({"step": "Itinerary Agent started", "status": "started", "details": f"Generating {days}-day itinerary for: {place}"})

    if "this place is in-serviceable" in weather_report:
        itinerary_agent_logs.append({"step": "Skipping itinerary generation", "status": "completed", "details": "Location is in-serviceable."})
        return "", itinerary_agent_logs
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"Given the following weather report for {place}:\n{weather_report}\n\nPlease create a {days}-day travel itinerary for {place}. The itinerary should suggest activities that are suitable for the weather. Include a mix of indoor and outdoor activities, and suggest some places to eat."
        itinerary_agent_logs.append({"step": "Calling Gemini model for itinerary", "status": "in_progress", "details": f"Model: 'gemini-2.5-flash', Prompt length: {len(prompt)} characters."})
        
        response = model.generate_content(prompt)
        itinerary = response.text
        
        itinerary_agent_logs.append({"step": "Gemini model response", "status": "completed", "details": "Itinerary generated successfully."})
        return itinerary, itinerary_agent_logs
    except Exception as e:
        itinerary_agent_logs.append({"step": "Error during itinerary generation", "status": "error", "details": str(e)})
        return f"An error occurred while generating the itinerary: {e}", itinerary_agent_logs
