from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
import time
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable not set")

openai.api_key = OPENAI_API_KEY

# Proxy endpoint for creating threads
@app.route('/proxy/threads', methods=['POST'])
def create_thread():
    try:
        # Create a thread using OpenAI API
        thread = openai.beta.threads.create()
        return jsonify({"thread_id": thread.id})
    except Exception as e:
        print(f"Error creating thread: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Proxy endpoint for adding messages to threads
@app.route('/proxy/threads/<thread_id>/messages', methods=['POST'])
def add_message(thread_id):
    try:
        data = request.json
        role = data.get('role', 'user')
        content = data.get('content', '')
        
        # Add message to thread using OpenAI API
        message = openai.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content
        )
        
        return jsonify({"message_id": message.id})
    except Exception as e:
        print(f"Error adding message: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Proxy endpoint for creating runs
@app.route('/proxy/threads/<thread_id>/runs', methods=['POST'])
def create_run(thread_id):
    try:
        data = request.json
        assistant_id = data.get('assistant_id')
        
        # Create a run using OpenAI API
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        
        return jsonify({"run_id": run.id})
    except Exception as e:
        print(f"Error creating run: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Proxy endpoint for retrieving run status
@app.route('/proxy/threads/<thread_id>/runs/<run_id>', methods=['GET'])
def get_run(thread_id, run_id):
    try:
        # Retrieve run status using OpenAI API
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        
        return jsonify({
            "status": run.status,
            "last_error": run.last_error if hasattr(run, 'last_error') else None
        })
    except Exception as e:
        print(f"Error retrieving run: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Proxy endpoint for listing messages
@app.route('/proxy/threads/<thread_id>/messages', methods=['GET'])
def list_messages(thread_id):
    try:
        # List messages using OpenAI API
        messages = openai.beta.threads.messages.list(
            thread_id=thread_id
        )
        
        # Convert messages to a serializable format
        messages_data = []
        for msg in messages.data:
            content_data = []
            for content in msg.content:
                if content.type == "text":
                    content_data.append({
                        "type": "text",
                        "text": content.text.value
                    })
            
            messages_data.append({
                "id": msg.id,
                "role": msg.role,
                "content": content_data
            })
        
        return jsonify({"messages": messages_data})
    except Exception as e:
        print(f"Error listing messages: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
