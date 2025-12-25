from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.agents.middleware import wrap_model_call
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()


@tool
def calculator(expression: str):
    """
    Solve arithmetic expressions like 2+3*4
    """
    try:
        return str(eval(expression))
    except:
        return "Error: Invalid expression"


@tool
def file_reader(filepath: str):
    """
    Read content of a text file
    """
    try:
        with open(filepath, "r") as f:
            return f.read()
    except:
        return "Error: File not found"


@tool
def current_weather(city: str):
    """
    Get current weather of a city using OpenWeather API
    """
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
        response = requests.get(url)
        return json.dumps(response.json())
    except:
        return "Error: Weather not available"


@tool
def knowledge_lookup(topic: str):
    """
    Simple knowledge lookup tool
    """
    knowledge = {
        "AI": "Artificial Intelligence enables machines to think and learn.",
        "ML": "Machine Learning is a subset of AI that learns from data.",
        "Python": "Python is a popular programming language."
    }
    return knowledge.get(topic, "No information found")




@wrap_model_call
def logging_middleware(request, handler):
    print("\n--- BEFORE MODEL CALL ---")
    print("Messages sent to model:")
    for msg in request.messages:
        print(msg)
    
    response = handler(request)

    print("\n--- AFTER MODEL CALL ---")
    print("Model response:")
    print(response.result[0].content)

    return response




llm = init_chat_model(
    model="phi-3-mini-4k-instruct",
    model_provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key="dummy_key"
)



agent = create_agent(
    model=llm,
    tools=[
        calculator,
        file_reader,
        current_weather,
        knowledge_lookup
    ],
    middleware=[logging_middleware],
    system_prompt="You are a helpful assistant. Answer in short."
)



conversation = []

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    conversation.append({"role": "user", "content": user_input})

    result = agent.invoke({
        "messages": conversation
    })

    ai_msg = result["messages"][-1]
    print("AI:", ai_msg.content)


    print("\n--- MESSAGE HISTORY ---")
    for msg in result["messages"]:
        print(msg)

    conversation = result["messages"]
