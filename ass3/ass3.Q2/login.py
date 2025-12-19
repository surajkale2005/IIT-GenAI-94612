import streamlit as st
import requests
import os
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = ""


def get_weather(city):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )
    response = requests.get(url)
    return response.json()


if not st.session_state.logged_in:
    st.title("Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if username and password and username == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid login (Username and Password must be same)")


else:
    st.title("Weather App")
    st.write(f"Welcome, **{st.session_state.user}**")

    city = st.text_input("Enter City Name")

    if st.button("Get Weather"):
        if city:
            data = get_weather(city)
            if data.get("cod") == 200:
                st.subheader(f"Weather in {city}")
                st.write(f"Temperature: {data['main']['temp']} °C")
                st.write(f"Condition: {data['weather'][0]['description']}")
                st.write(f"Humidity: {data['main']['humidity']}%")
                st.write(f"Wind Speed: {data['wind']['speed']} m/s")
            else:
                st.error("City not found")
        else:
            st.warning("Please enter a city name")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = ""
        st.success("Thanks for using the Weather App!")
        st.rerun()
