import random # Import the random module
from flask import Flask, request, jsonify
from flask_cors import CORS
from arguments import args
from classifier import Classifier
from preprocessor import Preprocessor

preprocessor = Preprocessor()

args.model_name_or_path = "./models/3_epochs_distilbert"
classifier = Classifier(for_training=False, args=args)

# 1. Create an instance of the Flask class
app = Flask(__name__)

# 2. Enable CORS
CORS(app)

# 3. Define a route that accepts POST requests
@app.route('/process_tweet', methods=['POST'])
def process_tweet():
    """
    Receives tweet text via POST request, classifies the text,
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

    preprocessed_text = preprocessor.preprocess_sample(original_text)

    # Generate a random decision (0 or 1)
    result = classifier.classify_sentiment(preprocessed_text)
    
    print(f"Generated decision: {result} for text: {original_text[:50]}...")

    # Return the decision and original text in a JSON response
    return jsonify({
        "original_text": original_text, # Send original text back for context
        "decision": result    # Send the decision
    })

# Keep the root route for basic testing
@app.route('/', methods=['GET'])
def hello_world():
    return "Flask API for tweet random decision is running!"

# 4. Run the application server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
