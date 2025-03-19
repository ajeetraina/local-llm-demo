from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Simple HTML interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Local LLM Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .chat-container { border: 1px solid #ddd; border-radius: 5px; padding: 20px; height: 400px; overflow-y: auto; margin-bottom: 20px; background: white; }
        .message { margin-bottom: 10px; padding: 10px; border-radius: 5px; max-width: 80%; }
        .user { background-color: #e1f5fe; margin-left: auto; text-align: right; }
        .bot { background-color: #f5f5f5; }
        .input-container { display: flex; }
        input[type="text"] { flex-grow: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background-color: #2196F3; color: white; border: none; cursor: pointer; margin-left: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Local LLM Demo</h1>
    <div class="chat-container" id="chatContainer"></div>
    <div class="input-container">
        <input type="text" id="userInput" placeholder="Type your message...">
        <button onclick="sendMessage()" id="sendButton">Send</button>
    </div>

    <script>
        // Add initial message
        document.addEventListener('DOMContentLoaded', function() {
            addMessage("Hello! I'm a local language model running in Docker. How can I help you today?", false);
            document.getElementById('userInput').focus();
        });
    
        function addMessage(text, isUser) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message');
            messageDiv.classList.add(isUser ? 'user' : 'bot');
            messageDiv.textContent = text;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function sendMessage() {
            const userInput = document.getElementById('userInput');
            const sendButton = document.getElementById('sendButton');
            const message = userInput.value.trim();
            
            if (message) {
                // Disable input while processing
                userInput.disabled = true;
                sendButton.disabled = true;
                
                addMessage(message, true);
                userInput.value = '';
                
                // Show thinking message
                const thinkingDiv = document.createElement('div');
                thinkingDiv.classList.add('message', 'bot');
                thinkingDiv.textContent = "Thinking...";
                document.getElementById('chatContainer').appendChild(thinkingDiv);
                
                fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ prompt: message }),
                })
                .then(response => response.json())
                .then(data => {
                    // Remove thinking message
                    thinkingDiv.remove();
                    addMessage(data.response, false);
                })
                .catch(error => {
                    thinkingDiv.remove();
                    addMessage("Sorry, there was an error processing your request.", false);
                    console.error('Error:', error);
                })
                .finally(() => {
                    // Re-enable input
                    userInput.disabled = false;
                    sendButton.disabled = false;
                    userInput.focus();
                });
            }
        }
        
        // Allow Enter key to send messages
        document.getElementById('userInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    user_prompt = data.get('prompt', '')
    
    # Simple rule-based responses
    if "hello" in user_prompt.lower():
        return jsonify({'response': "Hello! I'm a local language model running in Docker."})
    elif "what can you do" in user_prompt.lower():
        return jsonify({'response': "I can demonstrate how a language model can be deployed locally using Docker. This is a simplified version for demonstration purposes."})
    elif "how are you" in user_prompt.lower():
        return jsonify({'response': "I'm functioning well, thank you for asking!"})
    else:
        return jsonify({'response': f"You said: '{user_prompt}'. This is a demo of a local LLM. In a real implementation, this would be connected to an actual language model."})

if __name__ == '__main__':
    print("Starting demo server on http://0.0.0.0:7860")
    app.run(host='0.0.0.0', port=7860)
