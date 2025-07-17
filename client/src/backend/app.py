from flask import Flask, request, jsonify
from flask_cors import CORS
from db import save_user_data, save_answer_data, get_user_data, get_user_answers, save_session_data
from firebase_admin import auth, credentials, initialize_app

app = Flask(__name__)
CORS(app)

cred = credentials.Certificate("client/src/backend/secret/personalized-llm-39f52-firebase-adminsdk-fbsvc-48417fdd4b.json")  
initialize_app(cred)


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
    id_token = data.get("id_token")
    try:
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token["uid"]
        email = decoded_token.get("email", "")
        return jsonify({"status": "success", "message": "User signed up successfully", "user_id": user_id})
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

if __name__ == "__main__":
    app.run(debug=True, port=5000)
