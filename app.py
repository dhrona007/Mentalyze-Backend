from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Hugging Face Inference API settings
API_URL = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"
API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN")  # Store your API token in an environment variable

# Function to analyze sentiment using Hugging Face API
def analyze_sentiment(text):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    payload = {"inputs": text}
    response = requests.post(API_URL, headers=headers, json=payload)
    
    print("Hugging Face API Response:", response.status_code, response.text)  # Debug log
    
    if response.status_code == 200:
        result = response.json()
        return result[0][0]["label"]  # Returns "POSITIVE" or "NEGATIVE"
    else:
        return f"Error: {response.status_code} - {response.text}"

# Chat endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    # Analyze sentiment using Hugging Face API
    sentiment = analyze_sentiment(user_message)

    # Return the sentiment analysis result
    return jsonify({'reply': f"Sentiment: {sentiment}", 'status': 'analysis'})

# Root endpoint
@app.route('/')
def index():
    return "Welcome to the Mental Health Chatbot Backend!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
