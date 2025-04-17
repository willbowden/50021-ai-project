import random # Import the random module
from flask import Flask, request, jsonify
from flask_cors import CORS
from preprocessor import Preprocessor

# 0. Setup text preprocessor
preprocessor = Preprocessor()

# 1. Create an instance of the Flask class
app = Flask(__name__)

# 2. Enable CORS
CORS(app)

# 3. Define a route that accepts POST requests
@app.route('/process_tweet', methods=['POST'])
def process_tweet():
    """
    Receives tweet text via POST request, generates a random decision (0 or 1),
    and returns the decision along with the original text.
    """
    print("Received request on /process_tweet")

    if not request.is_json:
        print("Error: Request is not JSON")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    print(f"Received data: {data}")

    if 'tweet_text' not in data:
        print("Error: 'tweet_text' key missing")
        return jsonify({"error": "'tweet_text' key missing in JSON data"}), 400

    original_text = data['tweet_text']

    # Generate a random decision (0 or 1)
    random_decision = random.randint(0, 1)
    print(f"Generated decision: {random_decision} for text: {original_text[:50]}...")

    # Return the decision and original text in a JSON response
    return jsonify({
        "original_text": original_text, # Send original text back for context
        "decision": random_decision    # Send the random decision
    })

# Keep the root route for basic testing
@app.route('/', methods=['GET'])
def hello_world():
    return "Flask API for tweet random decision is running!"

# 4. Run the application server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
