import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os
load_dotenv()


st.title("Weather Explanation using Local LLM")

# User input
city = st.text_input("Enter city name:")

if city:
    YOUR_WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

    # Fetch current weather
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={YOUR_WEATHER_API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        st.error("City not found or Weather API error")
    else:
        data = response.json()
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        condition = data["weather"][0]["description"]

        st.subheader("Current Weather")
        st.write(f"Temperature: {temp} °C")
        st.write(f"Feels Like: {feels} °C")
        st.write(f"Humidity: {humidity}%")
        st.write(f"Condition: {condition}")

        
        prompt = f"""
City: {city}
Temperature: {temp} °C
Feels Like: {feels} °C
Humidity: {humidity}%
Condition: {condition}

Instruction:
Explain today's weather in simple English, 
in 3–5 lines, friendly and easy to understand.
"""

        
        llm_url = "http://127.0.0.1:1234/v1/completions"  
        payload = {
            "model": "phi-3-mini-4k-instruct",
            "prompt": prompt,
            "max_tokens": 300
        }
with st.spinner("AI is explaining the weather..."):
    llm_response = requests.post(llm_url, json=payload)
    if llm_response.status_code == 200:
        result = llm_response.json()
        
        explanation = result['choices'][0]['text'].strip()
        st.subheader(" AI Explanation")
        st.success(explanation)
    else:
        st.error(f"LLM request failed: {llm_response.text}")
