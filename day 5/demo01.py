from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import os
import dotenv as load_dotenv

load_dotenv.load_dotenv()

# api_key = os.getenv("GEMINI_API_KEY")
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=api_key)

# llm_url = "http://127.0.0.1:1234/v1"
# llm = ChatOpenAI(
#     base_url=llm_url,
#     model="phi-3-mini-4k-instruct",
#     api_key="dummy-key"
# )

# result = llm.invoke(user_input)
# print("AI: ", result.content)




api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="openai/gpt-oss-120b", api_key=api_key)


user_input = input("You: ")

result = llm.stream(user_input)
for chunk in result:
    print(chunk.content, end="")