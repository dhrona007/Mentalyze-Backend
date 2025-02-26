from flask import Flask, request, jsonify
from flask_cors import CORS  # Enable CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Together API settings
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")  # Store your API key in an environment variable

def analyze_responses_with_together(user_query):
    """
    Send user's message to the Together API for mental health analysis.
    """
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are a mental health assistant. Analyze the user's responses and provide helpful advice."},
            {"role": "user", "content": user_query}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(TOGETHER_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error with Together API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error with Together API: {e}"

# Chat endpoint now supports POST requests
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"reply": "Please enter a valid message.", "status": "error"}), 400

    analysis = analyze_responses_with_together(user_message)

    return jsonify({'reply': analysis, 'status': 'analysis'})

# Root endpoint
@app.route('/')
def index():
    return "Welcome to the Mental Health Chatbot Backend using Together API!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
