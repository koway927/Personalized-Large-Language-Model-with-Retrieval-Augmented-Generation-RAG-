from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from google import genai

# load_dotenv() 
# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_KEY = 'AIzaSyChbX9RetszZAMX5crB3QQNcux-n9t6M5o'
client = None
MODEL_NAME = "models/gemini-2.0-flash"
#model = genai.GenerativeModel("gemini-pro")

def initialize_llm():
    global client
    client = genai.Client(api_key=GEMINI_API_KEY)
    
def ask(prompt):

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "return_full_text": False
        }
    }

    try:
        # 使用 client.models.generate_content 生成响应
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt]
        )

        if response.candidates:
            reply = response.candidates[0].content.parts[0].text
        else:
            reply = "No response generated."

        return reply

    except Exception as e:
        # return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
        return None

