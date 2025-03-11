from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv  # Add this line

# Load environment variables from .env file
load_dotenv()  # Add this line

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://your-netlify-app.netlify.app"}})

# Together API settings
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")  # Load API key from environment variable

os.environ["TOGETHER_API_KEY"] = "your_new_api_key"

# List of professional mental health questions
mental_health_questions = [
    "On a scale of 1 to 10, how would you rate your overall mood today?",
    "Have you been experiencing frequent stress or anxiety in the past week?",
    "Are you having trouble sleeping or experiencing changes in your sleep pattern?",
    "Do you feel socially connected, or are you feeling isolated?",
    "Have you noticed any significant changes in your appetite or weight?",
    "Are you experiencing difficulty concentrating or making decisions?",
    "Do you often feel fatigued or low on energy throughout the day?",
    "Have you lost interest in activities that you used to enjoy?",
    "Do you feel overwhelmed by responsibilities in your personal or professional life?",
    "Are you currently facing any major life changes or stressful events?",
    "Have you had thoughts of self-harm or felt hopeless recently?",
    "Would you like any resources or guidance on coping strategies for mental well-being?"
]

user_responses = {}  # Dictionary to store user responses

def analyze_responses_with_together(user_id):
    """
    Send all user responses to the Together API for analysis.
    Ensures the response is formatted using bullet points and proper line breaks.
    """
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = [
    {
        "role": "system",
        "content": (
            "You are a highly professional mental health assistant. Your role is to provide structured, empathetic, and evidence-based psychological support. "
            "Follow the standard workflow of a licensed mental health expert, including assessment, diagnosis, therapeutic intervention, progress tracking, and crisis management. "
            "Maintain a warm, professional, and non-judgmental tone in all interactions.\n\n"
            
            "### Guidelines:\n"
            "- **Structured Responses:** Format responses in a clear and structured way using bullet points, numbered lists, and line breaks.\n"
            "- **Bold text** for emphasis.\n"
                "- Bullet points (`•`) for lists.\n"
                "- Numbered lists (`1., 2.`) where appropriate.\n"
                "- Line breaks (`\\n`) for readability.\n"
                "Make the response clear and structured."
            "- **Markdown Formatting:** Use Markdown to improve readability and ensure clarity in all responses.\n"
            "- **Human-Like Interaction:** Ensure responses feel natural, engaging, and supportive.\n"
            "- **Therapeutic Techniques:** Apply cognitive-behavioral therapy (CBT), mindfulness techniques, and evidence-based mental health practices.\n"
            "- **Assessment & Progress Tracking:** Gather information, provide insights, and track user well-being over time.\n"
            "- **Crisis Handling:** If the user indicates distress or harm, offer immediate support and suggest seeking professional help.\n"
            "- **Confidentiality & Ethics:** Prioritize privacy and provide non-judgmental, ethical support without giving medical prescriptions.\n\n"
            
            "Always respond with clarity, empathy, and professionalism, ensuring a supportive experience for the user."
        )
    }
]
    
    for i, question in enumerate(mental_health_questions):
        messages.append({"role": "user", "content": f"{question}: {user_responses[user_id][i]}"})

    data = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "messages": messages,
        "temperature": 0.7
    }

    try:
        response = requests.post(TOGETHER_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            formatted_response = response.json()["choices"][0]["message"]["content"]
            return formatted_response.replace("\n", "<br>")  # Preserve new lines
        else:
            return f"❌ Error with Together API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Error with Together API: {e}"


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat requests from the frontend.
    """
    user_message = request.json.get('message')
    user_id = request.json.get('user_id', 'default')  # Identify users (for multiple user support)

    if user_id not in user_responses:
        user_responses[user_id] = []

    # Check if user has answered all questions
    if len(user_responses[user_id]) < len(mental_health_questions):
        user_responses[user_id].append(user_message)  # Store response
        
        if len(user_responses[user_id]) == len(mental_health_questions):
            # If all questions are answered, analyze and provide feedback
            feedback = analyze_responses_with_together(user_id)
            return jsonify({'reply': feedback, 'status': 'analysis'})
        else:
            # Ask the next question
            next_question = mental_health_questions[len(user_responses[user_id])]
            return jsonify({'reply': next_question, 'status': 'question'})
    else:
        return jsonify({'reply': "You've already completed the assessment.", 'status': 'done'})

# Root endpoint
@app.route('/')
def index():
    return "Welcome to the Mental Health Chatbot Backend using Together API! "

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use PORT environment variable if available, otherwise default to 5000
    app.run(host="0.0.0.0", port=port)
