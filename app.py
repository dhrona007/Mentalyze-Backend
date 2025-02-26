from flask import Flask, request, jsonify
from flask_cors import CORS  # Enable CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Together API settings
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")  # Store your API key in an environment variable

def analyze_responses_with_together():
    """
    Send predefined questions to the Together API for mental health analysis.
    """
    questions = [
         "How have you been feeling lately?",
        "Have you experienced any significant changes in your sleep patterns?",
        "Do you often feel anxious or stressed?",
        "Have you lost interest in activities you used to enjoy?",
        "Do you have a support system (friends, family) you can rely on?",
        "How would you rate your overall mood on a scale of 1 to 10?"
    ]
    
    user_query = " ".join(questions)
    
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",  # Replace with correct Together model name
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

# Chat endpoint
@app.route('/api/chat', methods=['GET'])
def chat():
    # Analyze sentiment using Together API
    analysis = analyze_responses_with_together()

    return jsonify({'reply': analysis, 'status': 'analysis'})

# Root endpoint
@app.route('/')
def index():
    return "Welcome to the Mental Health Chatbot Backend using Together API!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
