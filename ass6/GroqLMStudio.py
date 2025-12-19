import streamlit as st
import requests
import os
import json
import time
from dotenv import load_dotenv

# Load API keys 
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

#  Streamlit app
st.title("Groq + LM Studio Chat")
st.sidebar.title("Settings")

model_choice = st.sidebar.selectbox("Choose LLM Model", ["Groq", "LM Studio"])

# Initialize chat history 
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

#  User input 
user_prompt = st.chat_input("Ask anything:")

if user_prompt:
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    
    if model_choice == "Groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        req_data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 200,
            "temperature": 0.7
        }
        start = time.perf_counter()
        try:
            response = requests.post(url, data=json.dumps(req_data), headers=headers)
            response.raise_for_status()
            resp_json = response.json()
            answer = resp_json["choices"][0]["message"]["content"]
        except Exception as e:
            answer = f"Groq API error: {e}"
        end = time.perf_counter()
        answer += f"\n\n_(Response time: {end-start:.2f} sec)_"

    elif model_choice == "LM Studio":
        local_url = "http://127.0.0.1:1234/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        req_data = {
            "model": "local-llm",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_prompt}
            ]
        }
        start = time.perf_counter()
        try:
            response = requests.post(local_url, data=json.dumps(req_data), headers=headers)
            response.raise_for_status()
            resp_json = response.json()
            answer = resp_json["choices"][0]["message"]["content"]
        except Exception as e:
            answer = f"LM Studio API error: {e}"
        end = time.perf_counter()
        answer += f"\n\n_(Response time: {end-start:.2f} sec)_"

    st.session_state.chat_history.append({"role": "assistant", "content": answer})

# Display chat history 
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.chat_message("user").write(chat["content"])
    else:
        st.chat_message("assistant").write(chat["content"])
