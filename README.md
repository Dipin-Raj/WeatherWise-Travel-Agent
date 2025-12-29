# 🌍 WeatherWise Travel Agent ✈️

[![GitHub](https://img.shields.io/badge/GitHub-Repo-blue?style=flat&logo=github)](https://github.com/Dipin-Raj/WeatherWise-Travel-Agent.git)

---

## Overview 📝

This project is a Python-based multi-agent system designed to provide a comprehensive travel assistant service. Given a location and a number of days, the system leverages a series of specialized agents to fetch a weather report, provide safety and practical precautions, and generate a detailed travel itinerary.

## 🌐 Live Demo

Experience the live deployed version here: [WeatherWise Travel Agent](https://weatherwise-travel-agent.streamlit.app/)

## Features ✨

-   **Natural Language Queries:** Understands natural language queries to extract location information (e.g., "planning a trip to Paris").
-   **Agent 1: Weather Reporter:** Fetches real-time weather forecast data.
-   **Agent 2: Precaution Advisor:** Analyzes the weather and location to provide practical advice and safety precautions.
-   **Agent 3: Itinerary Planner:** Generates a day-by-day travel itinerary with suggestions for activities and dining, tailored to the weather and location.
-   **Interactive Input:** Prompts the user for location and duration.
-   **Secure API Key Management:** Uses a `.env` file to securely manage API keys.

## Architecture 🏛️

The system is designed with a simple, sequential multi-agent architecture. The output of each agent serves as the input for the next, creating a processing pipeline.

1.  **`main.py` (Orchestrator):** The main script that takes user input, manages the flow of data, and calls each agent in order.
2.  **Agent 1 (`weather_agent.py`):**
    -   Receives a query and `days`.
    -   Uses a generative model to extract the location from the user's query.
    -   Uses the Nominatim API to geocode the place name into latitude and longitude.
    -   Uses the OpenWeatherMap API to fetch the weather forecast.
    -   Passes a formatted weather report string to the next agent.
3.  **Agent 2 (`precaution_agent.py`):**
    -   Receives the `weather_report` and `place`.
    -   Uses the Google Gemini API to analyze the information and generate a list of relevant precautions.
    -   Passes the generated precautions to the next step.
4.  **Agent 3 (`itinerary_agent.py`):**
    -   Receives the `weather_report`, `place`, and `days`.
    -   Uses the Google Gemini API to generate a detailed, day-by-day travel itinerary.
    -   The final output is then printed to the user.

## Technologies & Libraries Used 🛠️

-   **Python 3:** The core programming language.
-   **`requests`:** A standard library for making HTTP requests to the various APIs.
-   **`google-genai`:** The official Google Python SDK for interacting with the Gemini family of models, used for the intelligent analysis and generation tasks.
-   **`python-dotenv`:** Used to load environment variables from a `.env` file, allowing for secure and flexible management of API keys.

## APIs Used 🌐

-   **Nominatim (OpenStreetMap):** A free geocoding service used to convert location names (e.g., "London") into geographical coordinates (latitude and longitude).
-   **OpenWeatherMap API:** Used to fetch current and forecasted weather data for the specified coordinates. Requires a free API key.
-   **Google Gemini API:** A powerful large language model (LLM) used by Agent 1, Agent 2 and Agent 3 to generate human-like text for precautions and itineraries based on the provided context. Requires a free API key from Google AI Studio.


### 🚀 Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Dipin-Raj/WeatherWise-Travel-Agent.git
    cd WeatherWise-Travel-Agent
    ```

2.  **Create Virtual Environment:**
    ```bash
    python -m venv venv
    ```

3.  **Activate Environment:**
    -   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    -   **macOS / Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 🔐 Configure API Keys

Create a `.env` file in the project root:

```
WEATHER_API_KEY="YOUR_OPENWEATHERMAP_API_KEY"
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Get your keys from:
-   🌦️ **OpenWeatherMap:** [https://openweathermap.org/api](https://openweathermap.org/api)
-   🤖 **Google Gemini:** [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### ▶️ How to Run

**Console Application:**
```bash
python main.py
```
*Enter Location & Number of Days when prompted.*

**Streamlit Web App:**
```bash
streamlit run app.py
```
*App runs at: [http://localhost:8501](http://localhost:8501)*

### 📂 Project Structure

```
.
├── app.py                # Streamlit web application interface
├── main.py               # Orchestrates the multi-agent system
├── README.md             # Project README
├── requirements.txt      # Python dependencies
├── agent1/
│   ├── __init__.py
│   └── weather_agent.py  # Agent for fetching weather data
├── agent2/
│   ├── __init__.py
│   └── precaution_agent.py # Agent for providing precautions
└── agent3/
    ├── __init__.py
    └── itinerary_agent.py  # Agent for generating travel itineraries
```

### ❤️ Contributing

Contributions are welcome! Feel free to:
-   ⭐ Star the repo
-   🐛 Report bugs
-   💡 Suggest features

### 📜 License

This project is for educational and learning purposes.
