from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend requests

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("message", "")
    
    # Dummy response logic
    response = f"You said: {user_input}"
    
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
