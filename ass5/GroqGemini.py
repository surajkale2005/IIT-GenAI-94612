import os
import requests
import json
import time
from dotenv import load_dotenv
from google import genai


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)


groq_url = "https://api.groq.com/openai/v1/chat/completions"
groq_headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

print("Type 'exit' to quit.")

while True:
    user_prompt = input("\nYou: ")
    if user_prompt.lower() == "exit":
        break

  
    groq_body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }

    start_groq = time.perf_counter()
    groq_resp = requests.post(groq_url, headers=groq_headers, json=groq_body)
    end_groq = time.perf_counter()
    if groq_resp.ok:
        groq_text = groq_resp.json()["choices"][0]["message"]["content"]
    else:
        groq_text = f"Groq API error: {groq_resp.status_code}"


    start_gem = time.perf_counter()
    try:
        gemini_resp = gemini_client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=[{"text": user_prompt}],
        )
        gemini_text = gemini_resp.text
    except Exception as e:
        gemini_text = f"Gemini API error: {str(e)}"
    end_gem = time.perf_counter()


    print("\n=== Groq Response ===")
    print(groq_text)
    print(f"Time: {end_groq - start_groq:.2f} sec")

    print("\n=== Gemini Response ===")
    print(gemini_text)
    print(f"Time: {end_gem - start_gem:.2f} sec")

    
    if "error" not in gemini_text.lower():
        faster = "Groq" if (end_groq - start_groq) < (end_gem - start_gem) else "Gemini"
        print(f"\nFaster response: {faster}")
