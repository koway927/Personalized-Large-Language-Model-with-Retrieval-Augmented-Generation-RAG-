from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from sentence_transformers import SentenceTransformer
import lancedb
import torch
import os
from backend.setup import initialize_system
# from backend.services.db import save_user_data, save_answer_data
from backend.services.db import save_user_data, save_answer_data, get_user_data, get_user_answers, save_session_data
from backend.services.embedder import embed
import backend.services.rag as rag
from firebase_admin import auth, credentials, initialize_app

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(BASE_DIR, "secret/personalized-llm-39f52-firebase-adminsdk-fbsvc-56fc515094.json")
cred = credentials.Certificate(cred_path)
initialize_app(cred)

initialize_system()

@app.route('/query-llm', methods=['POST'])
def query(): # query llm and output the response for user's query
    print("request")
    data = request.get_json()
    response = rag.generate_response(data)
    return jsonify({"response": response})

@app.route('/switch-session', methods=['POST'])
def switch_sessions(): # when switching over to a new session deleted information is cleared from disk
    data = request.get_json()
    rag.delete_session_data(data)

@app.route('/manage-personal-info', methods=['POST'])
def manage_personal_info(): # periodically called to delete information from personal_info table to maintain size
    data = request.get_json()
    return jsonify(rag.clear_personal_table(data))

@app.route('/extract-info', methods=['POST'])
def extract_info(): # extract query specific information as well as personal information from user's query
    data = request.get_json()
    extracted_info = rag.extract_info(data)
    return jsonify({"extracted_info": extracted_info})

@app.route("/api/save_user", methods=["POST"])
def save_user():
    data = request.json
    print("Received data:", data)
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "User ID is required"}), 400
    result = save_user_data(data, user_id)
    return jsonify({"status": result})

@app.route("/api/save_answer", methods=["POST"])
def save_answer():
    data = request.json
    print("Received data:", data)
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "User ID is required"}), 400
    result = save_answer_data(data, user_id)
    return jsonify({"status": result})


@app.route("/api/fetch_user_data", methods=["POST"])
def fetch_user_data():
    
    data = request.json  
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "User ID is required"}), 400
    result = get_user_data(user_id)
    if result["status"] == "error":
        return jsonify(result), 404
    return {"status": "success", "data":result["data"][0]["info_chunk"]}

@app.route("/api/fetch_user_answer", methods=["POST"])
def fetch_user_answer():
    data = request.json  
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "User ID is required"}), 400
    result = get_user_answers(user_id)
    if result["status"] == "error":
        return jsonify(result), 404
    return {"status": "success", "data":result["data"][0]["info_chunk"]}

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        user = auth.create_user(
            email=email,
            password=password,

        )
        return jsonify({"status": "success", "message": "User signed up successfully", "user_id": user.uid})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    id_token = data.get("id_token")  
    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token["uid"]
        email = decoded_token.get("email", "")
        return jsonify({"status": "success", "message": "Login successful", "user_id": user_id, "email": email})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 401


@app.route("/api/logoff", methods=["POST"])
def logoff():
    data = request.json
    id_token = data.get("id_token")

    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token["uid"]

        

        return jsonify({"status": "success", "message": "User logged off successfully", "user_id": user_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 401

if __name__ == '__main__':
    app.run(port=5000, debug=True) # change port from llm_api