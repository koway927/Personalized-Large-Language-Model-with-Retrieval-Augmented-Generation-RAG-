from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = 'AIzaSyChbX9RetszZAMX5crB3QQNcux-n9t6M5o'

headers = {
    "Authorization": f"Bearer {GEMINI_API_KEY}",
    "Content-Type": "application/json"
}
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "models/gemini-2.0-flash"
#model = genai.GenerativeModel("gemini-pro")


@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_id = data.get("user_id")
    
    # context = data.get("context", "")

    full_prompt = data.get("prompt")

    payload = {
        "inputs": full_prompt,
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
            contents=[full_prompt]
        )

        if response.candidates:
            reply = response.candidates[0].content.parts[0].text
        else:
            reply = "No response generated."

        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
