from flask import Flask, request, jsonify
from chatgpt_interaction import ChatGPTInteraction
import time
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
chat_interaction = ChatGPTInteraction()

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    try:
        # Check Content-Type header
        if request.headers.get('Content-Type') != 'application/json':
            return jsonify({"error": "Content-Type must be application/json"}), 415

        # Check Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Invalid or missing Authorization header"}), 401

        api_key = auth_header.split(' ')[1]
        # Here you should validate the API key
        # For now, we'll just check if it's not empty
        if not api_key:
            return jsonify({"error": "Invalid API key"}), 401
        # 检查 api_key 是否在 apikeys.txt 种，每行是一个key
        with open('apikeys.txt', 'r') as file:
            api_keys = file.readlines()
        if api_key not in api_keys:
            return jsonify({"error": "Invalid API key"}), 401

        data = request.json
        model = data.get('model', 'gpt-3.5-turbo-0125')
        messages = data.get('messages', [])
        
        if not messages or messages[-1]['role'] != 'user':
            return jsonify({"error": "Invalid messages format"}), 400
        
        content = messages[-1]['content']
        response_content = chat_interaction.interact_with_chatgpt(content)
        
        response = {
            "model": model,
            "object": "chat.completion",
            "usage": {
                "prompt_tokens": 25,  # These are placeholder values
                "completion_tokens": 711,
                "total_tokens": 736
            },
            "id": f"chatcmpl-{int(time.time())}",
            "created": int(time.time()),
            "choices": [
                {
                    "index": 0,
                    "delta": None,
                    "message": {
                        "role": "assistant",
                        "content": response_content
                    },
                    "finish_reason": "stop"
                }
            ]
        }
        
        return jsonify(response)
    except Exception as e:
        logger.exception("An error occurred: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
