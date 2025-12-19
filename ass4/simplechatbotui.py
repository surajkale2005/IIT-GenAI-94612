import streamlit as st
import time

st.set_page_config(page_title="Chatbot UI", layout="centered")
st.title("Simple Chatbot UI")


if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


user_input = st.chat_input("Type your message...")

def stream_reply(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.2)

if user_input:
   
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.write(user_input)

   
    bot_reply = f"{user_input}"

    with st.chat_message("assistant"):
        st.write_stream(stream_reply(bot_reply))

    st.session_state.messages.append(
        {"role": "assistant", "content": bot_reply}
    )
