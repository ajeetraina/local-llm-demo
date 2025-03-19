from flask import Flask, request, jsonify, render_template_string
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import gc
import os

app = Flask(__name__)

# Initialize model and tokenizer
print("Loading model and tokenizer...")
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

print("Downloading and loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_id)

print("Downloading and loading model...")
# Use low_cpu_mem_usage for better memory efficiency
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    low_cpu_mem_usage=True,
    torch_dtype=torch.float32
)

# Free up some memory
gc.collect()
torch.cuda.empty_cache() if torch.cuda.is_available() else None

# Chat history for persistent conversations
conversation_history = {}

# HTML interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Local LLM Demo - Real Model</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .chat-container { border: 1px solid #ddd; border-radius: 5px; padding: 20px; height: 400px; overflow-y: auto; margin-bottom: 20px; background: white; }
        .message { margin-bottom: 10px; padding: 10px; border-radius: 5px; max-width: 80%; }
        .user { background-color: #e1f5fe; margin-left: auto; text-align: right; }
        .bot { background-color: #f5f5f5; }
        .input-container { display: flex; }
        input[type="text"] { flex-grow: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background-color: #2196F3; color: white; border: none; cursor: pointer; margin-left: 10px; border-radius: 5px; }
        h1 { color: #333; }
        .model-info { background-color: #e8f5e9; padding: 10px; border-radius: 5px; margin-bottom: 20px; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>Local LLM Demo - Real Model</h1>
    <div class="model-info">
        <strong>Model:</strong> TinyLlama-1.1B-Chat-v1.0 | <strong>Status:</strong> Running locally in Docker
    </div>
    <div class="chat-container" id="chatContainer"></div>
    <div class="input-container">
        <input type="text" id="userInput" placeholder="Type your message...">
        <button onclick="sendMessage()" id="sendButton">Send</button>
    </div>

    <script>
        // Add initial message
        document.addEventListener('DOMContentLoaded', function() {
            addMessage("Hello! I'm TinyLlama, a lightweight language model running locally in your Docker container. How can I help you today?", false);
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

        let sessionId = Date.now().toString();

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
                    body: JSON.stringify({ prompt: message, session_id: sessionId }),
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

def generate_response(prompt, history=[]):
    # Format for TinyLlama chat format
    full_prompt = "<|system|>\nYou are a helpful AI assistant.\n"
    
    # Add conversation history
    for turn in history:
        full_prompt += f"<|user|>\n{turn['user']}\n<|assistant|>\n{turn['assistant']}\n"
    
    # Add current prompt
    full_prompt += f"<|user|>\n{prompt}\n<|assistant|>\n"
    
    try:
        # Tokenize input
        inputs = tokenizer(full_prompt, return_tensors="pt")
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=200,  # Adjust based on your needs
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode the output
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the assistant's response
        response_text = response_text[len(full_prompt):]
        
        # Clean up any special tokens that might remain
        special_tokens = ['<|user|>', '<|system|>', '<|assistant|>']
        for token in special_tokens:
            if token in response_text:
                response_text = response_text.split(token)[0]
        
        return response_text.strip()
    
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return f"Sorry, I encountered an error processing your request. Technical details: {str(e)}"

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    user_prompt = data.get('prompt', '')
    session_id = data.get('session_id', 'default')
    
    # Initialize session history if it doesn't exist
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    # Generate response based on conversation history
    response = generate_response(user_prompt, conversation_history[session_id])
    
    # Update conversation history
    conversation_history[session_id].append({
        'user': user_prompt,
        'assistant': response
    })
    
    # Limit history length to prevent memory issues
    if len(conversation_history[session_id]) > 10:
        conversation_history[session_id] = conversation_history[session_id][-10:]
    
    return jsonify({'response': response})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    print(f"Starting server on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)