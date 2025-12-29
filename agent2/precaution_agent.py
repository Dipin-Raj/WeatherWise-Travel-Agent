
import google.generativeai as genai

def get_precautions(weather_report: str, place: str, api_key: str) -> tuple[str, list[dict]]:
    """
    Analyzes the weather report and suggests precautions using the Gemini API.

    Args:
        weather_report: A string containing the weather report.
        place: The name of the place.
        api_key: The Gemini API key.

    Returns:
        A tuple containing the precautions string and a list of log entries (list[dict]).
    """
    precautions_agent_logs = []
    precautions_agent_logs.append({"step": "Precaution Agent started", "status": "started", "details": f"Analyzing weather for: {place}"})

    if "this place is in-serviceable" in weather_report:
        precautions_agent_logs.append({"step": "Skipping precaution generation", "status": "completed", "details": "Location is in-serviceable."})
        return "", precautions_agent_logs
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"Given the following weather report for {place}:\n{weather_report}\n\nPlease provide a list of precautions to take. Focus on practical advice for a tourist."
        precautions_agent_logs.append({"step": "Calling Gemini model for precautions", "status": "in_progress", "details": f"Model: 'gemini-2.5-flash', Prompt length: {len(prompt)} characters."})
        
        response = model.generate_content(prompt)
        precautions = response.text
        
        precautions_agent_logs.append({"step": "Gemini model response", "status": "completed", "details": "Precautions generated successfully."})
        return precautions, precautions_agent_logs
    except Exception as e:
        precautions_agent_logs.append({"step": "Error during precaution generation", "status": "error", "details": str(e)})
        return f"An error occurred while generating precautions: {e}", precautions_agent_logs
