from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API")

def detect_language(text):
    return 'en' if all(ord(c) < 128 for c in text) else 'non-en'

def translate_to_english(text):
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GOOGLE_API_KEY
    )
    prompt = f"Translate the following to English. Only output the English translation.\n\n{text}"
    response = model.invoke(prompt)
    if isinstance(response, dict) and 'content' in response:
        return response['content']
    return str(response)

def route_query(query):
    lang = detect_language(query)
    if lang == 'en':
        return query
    else:
        return translate_to_english(query)
