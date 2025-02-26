from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Together API settings
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")  # Load API key from environment

def analyze_responses_with_together(user_message):
    """
    Send user's query to the Together API for mental health analysis.
    """
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are a mental health assistant. Provide empathetic and helpful responses."},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(TOGETHER_API_URL, headers=headers, json=data)
        response_json = response.json()  # Convert response to JSON

        if response.status_code == 200 and "choices" in response_json:
            return response_json["choices"][0].get("message", {}).get("content", "Sorry, I couldn't process your request.")
        else:
            return f"Error with Together API: {response.status_code} - {response_json.get('error', 'Unknown error')}"
    
    except Exception as e:
        return f"Error with Together API: {e}"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"reply": "Please enter a valid message.", "status": "error"}), 400

    analysis = analyze_responses_with_together(user_message)

    return jsonify({'reply': analysis, 'status': 'response'})

@app.route('/api/questions', methods=['GET'])
def get_questions():
    questions = [
        "How have you been feeling lately?",
        "Have you experienced any significant changes in your sleep patterns?",
        "Do you often feel anxious or stressed?",
        "Have you lost interest in activities you used to enjoy?",
        "Do you have a support system (friends, family) you can rely on?",
        "How would you rate your overall mood on a scale of 1 to 10?"
    ]
    return jsonify({'questions': questions})

@app.route('/')
def index():
    return "Welcome to the Mental Health Chatbot Backend using Together API!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
