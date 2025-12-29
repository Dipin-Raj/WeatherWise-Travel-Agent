import streamlit as st
import os
import warnings
import pandas as pd # Import pandas for st.dataframe
from dotenv import load_dotenv

# Import agent functions
from agent1.weather_agent import get_weather
from agent2.precaution_agent import get_precautions
from agent3.itinerary_agent import get_itinerary

def display_logs(logs, agent_name):
    with st.expander(f"Detailed logs for {agent_name}"):
        for i, log_entry in enumerate(logs):
            status_icon = "➡️"
            if log_entry["status"] == "started":
                status_icon = "▶️"
            elif log_entry["status"] == "in_progress":
                status_icon = "⏳"
            elif log_entry["status"] == "completed":
                status_icon = "✅"
            elif log_entry["status"] == "error":
                status_icon = "❌"
            
            st.markdown(f"**{status_icon} Step {i+1}: {log_entry['step']}**")
            st.write(f"Status: {log_entry['status']}")
            if "details" in log_entry:
                st.write(f"Details: {log_entry['details']}")
            st.markdown("---")


def run_agents(query, days, weather_api_key, gemini_api_key):
    st.session_state['weather_data_structured'] = [] # Renamed to clearly indicate structured data
    st.session_state['weather_report_error'] = "" # To store error string if any
    st.session_state['precautions'] = ""
    st.session_state['itinerary'] = ""
    st.session_state['extracted_place_name'] = ""
    st.session_state['weather_logs'] = []
    st.session_state['precautions_logs'] = []
    st.session_state['itinerary_logs'] = []


    # Agent 1: Weather Agent
    with st.status("Getting weather information...", expanded=True, state="running") as status:
        st.write(f"Initiating Weather Agent for query: '{query}'")
        structured_weather_data, extracted_place_name, weather_logs = get_weather(query, days, weather_api_key, gemini_api_key)
        st.session_state['extracted_place_name'] = extracted_place_name
        st.session_state['weather_data_structured'] = structured_weather_data
        st.session_state['weather_logs'] = weather_logs
        
        display_logs(weather_logs, "Weather Agent")

        if extracted_place_name and structured_weather_data:
            status.update(label=f"Weather Agent: Fetched data for **{extracted_place_name}**!", state="complete", expanded=False)
        else:
            # If structured_weather_data is empty, it implies an error or no data
            st.session_state['weather_report_error'] = structured_weather_data # structured_weather_data will contain the error string here
            status.update(label="Weather Agent: Failed to extract location or fetch data.", state="error", expanded=True)
            st.error(structured_weather_data) # Display the error message
            return
        

    if st.session_state['weather_report_error']: # Check for error from weather agent before proceeding
        return

    # Agent 2: Precaution Agent
    with st.status("Generating precautions...", expanded=True, state="running") as status:
        st.write(f"Analyzing weather for {extracted_place_name} and generating precautions.")
        
        # Pass formatted weather report string to precaution agent if it expects string
        # Or you can format structured_weather_data into a string here for the LLM prompt
        formatted_weather_string_for_llm = ""
        if st.session_state['weather_data_structured']:
            formatted_weather_string_for_llm = f"Weather forecast for {extracted_place_name} for the next {days} day(s):\n"
            for day_data in st.session_state['weather_data_structured']:
                formatted_weather_string_for_llm += (
                    f"  {day_data['Date']}: {day_data['Weather']}, "
                    f"High: {day_data['High Temp (°C)']}°C, "
                    f"Low: {day_data['Low Temp (°C)']}°C\n"
                )
        
        precautions, precautions_logs = get_precautions(formatted_weather_string_for_llm, extracted_place_name, gemini_api_key)
        st.session_state['precautions'] = precautions
        st.session_state['precautions_logs'] = precautions_logs

        display_logs(precautions_logs, "Precaution Agent")

        if precautions:
            status.update(label="Precaution Agent: Precautions generated!", state="complete", expanded=False)
        else:
            status.update(label="Precaution Agent: No specific precautions generated.", state="complete", expanded=False)

    # Agent 3: Itinerary Agent
    with st.status("Generating travel itinerary...", expanded=True, state="running") as status:
        st.write(f"Creating {days}-day itinerary for {extracted_place_name}.")
        
        # Pass formatted weather report string to itinerary agent
        # Re-using the formatted string from precaution agent
        itinerary, itinerary_logs = get_itinerary(formatted_weather_string_for_llm, extracted_place_name, days, gemini_api_key)
        st.session_state['itinerary'] = itinerary
        st.session_state['itinerary_logs'] = itinerary_logs

        display_logs(itinerary_logs, "Itinerary Agent")

        if itinerary:
            status.update(label="Itinerary Agent: Itinerary generated!", state="complete", expanded=False)
        else:
            status.update(label="Itinerary Agent: No itinerary generated.", state="complete", expanded=False)

# --- Streamlit UI ---
st.set_page_config(page_title="Multi-Agent Weather & Travel Assistant", layout="wide")

st.title("🌍 Multi-Agent Weather & Travel Assistant")
st.markdown("Enter your travel query and number of days to get a weather forecast, travel precautions, and a detailed itinerary.")

# Load API keys
load_dotenv()
weather_api_key = os.getenv("WEATHER_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Suppress FutureWarning from google.generativeai
warnings.filterwarnings("ignore", category=FutureWarning)

if not weather_api_key or not gemini_api_key:
    st.error("API keys not loaded. Please ensure WEATHER_API_KEY and GEMINI_API_KEY are set in your `.env` file.")
else:
    # Input fields
    query = st.text_input("Your travel query (e.g., 'I am planning a trip to Kochi')", key="query_input")
    days = st.number_input("Number of days for the forecast and itinerary", min_value=1, max_value=7, value=3, key="days_input")

    if st.button("Get Travel Plan", key="get_plan_button"):
        if query and days:
            run_agents(query, days, weather_api_key, gemini_api_key)
        else:
            st.warning("Please enter a travel query and number of days.")

    # Display results
    if 'extracted_place_name' in st.session_state and st.session_state['extracted_place_name']:
        st.subheader(f"Travel Plan for {st.session_state['extracted_place_name']}")
        
        if st.session_state['weather_data_structured']: # Check if structured data exists
            st.markdown("### 🌤️ Weather Report")
            # Convert list of dicts to DataFrame for better display
            df_weather = pd.DataFrame(st.session_state['weather_data_structured'])
            st.dataframe(df_weather)
        elif st.session_state['weather_report_error']: # Display error if no structured data but error exists
            st.markdown("### 🌤️ Weather Report")
            st.error(st.session_state['weather_report_error'])


        if st.session_state['precautions']:
            st.markdown("### 🚨 Travel Precautions")
            st.warning(st.session_state['precautions'])

        if st.session_state['itinerary']:
            st.markdown("### 📝 Travel Itinerary")
            st.success(st.session_state['itinerary'])
