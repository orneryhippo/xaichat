# app.py
from flask import Flask, render_template, request, jsonify, session
import os
import requests
from dotenv import load_dotenv
from functools import wraps

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')  # Set this in .env

# Store chat histories (in production, use a proper database)
chat_histories = {}
api_keys = {}

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'api_key' not in session:
            return jsonify({'error': 'API key is not set'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/set-api-key', methods=['POST'])
def set_api_key():
    data = request.json
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'API key is required'}), 400
    
    # Store API key in session
    session['api_key'] = api_key
    
    # Initialize chat history for this session
    session_id = session.get('_id')
    chat_histories[session_id] = [
        {'role': 'system', 'content': 'You are Grok, a helpful assistant.'}
    ]
    
    return jsonify({'message': 'API key set successfully'})

@app.route('/chat', methods=['POST'])
@require_api_key
def chat():
    session_id = session.get('_id')
    api_key = session.get('api_key')
    user_message = request.json.get('message')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Get or initialize chat history
    chat_history = chat_histories.get(session_id, [
        {'role': 'system', 'content': 'You are Grok, a helpful assistant.'}
    ])
    
    # Add user message to history
    chat_history.append({'role': 'user', 'content': user_message})
    
    try:
        # Make request to Grok API
        response = requests.post(
            'https://api.x.ai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'grok-beta',
                'messages': chat_history
            },
            timeout=30  # Add timeout to prevent hanging
        )
        
        response.raise_for_status()  # Raise exception for bad status codes
        data = response.json()
        
        # Extract and store assistant's response
        ai_response = data['choices'][0]['message']['content']
        chat_history.append({'role': 'assistant', 'content': ai_response})
        
        # Update chat history
        chat_histories[session_id] = chat_history
        
        return jsonify({'message': ai_response})
        
    except requests.exceptions.RequestException as e:
        # Log the error in production
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except (KeyError, IndexError) as e:
        # Log the error in production
        return jsonify({'error': f'Invalid API response format: {str(e)}'}), 500
    except Exception as e:
        # Log the error in production
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/clear-chat', methods=['POST'])
@require_api_key
def clear_chat():
    session_id = session.get('_id')
    if session_id in chat_histories:
        chat_histories[session_id] = [
            {'role': 'system', 'content': 'You are Grok, a helpful assistant.'}
        ]
    return jsonify({'message': 'Chat history cleared'})

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)