from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit


# Load environment variables from .env file
load_dotenv()

# Get MongoDB credentials from .env
username = quote_plus(os.getenv("MONGO_USERNAME"))
password = quote_plus(os.getenv("MONGO_PASSWORD"))
cluster = os.getenv("MONGO_CLUSTER")
dbname = os.getenv("MONGO_DBNAME")

# Check if credentials exist
if not username or not password or not cluster:
    raise ValueError("MongoDB credentials are missing. Set them in the .env file.")

# MongoDB Connection String
connection_string = f"mongodb+srv://{username}:{password}@{cluster}/{dbname}?retryWrites=true&w=majority"
client = MongoClient(connection_string)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable real-time support

# MongoDB connection
db = client[dbname]
reviews_collection = db["reviews"]

packages = {
    "family": {
        "title": "FAMILY PACKAGE",
        "description": "A family that travels together stays together.",
        "images": [
            "../static/img/photo/family/2.jpeg",
            "../static/img/photo/family/3.jpeg",
            "../static/img/photo/family/4.jpeg"
        ]
    },
    "hiking": {
        "title": "TREKKING AND HIKING",
        "description": "Life is a daring adventure or nothing.",
        "images": [
            "../static/img/photo/hiking/5.jpeg",
            "../static/img/photo/hiking/6.jpeg",
            "../static/img/photo/hiking/4.jpeg"
        ]
    },
    "love": {
        "title": "HONEYMOON",
        "description": "Lets travel together and get lost in this beautiful island",
        "images": [
            "../static/img/photo/love/1.jpeg",
            "../static/img/photo/love/2.jpeg",
            "../static/img/photo/love/3.jpeg"
        ]
    },
    "wild": {
        "title": "WILD LIFE",
        "description": "The only man i envy is the man who has not yet been to the wild",
        "images": [
            "../static/img/photo/wild/1.jpeg",
            "../static/img/photo/wild/2.jpeg",
            "../static/img/photo/wild/3.jpeg"
        ]
},"culture": {
        "title": "CULTURE",
        "description": "You have to taste a culture to understand it",
        "images": [
            "../static/img/photo/culture/1.jpeg",
            "../static/img/photo/culture/2.jpeg",
            "../static/img/photo/culture/3.jpeg"
        ]
},
"beach": {
        "title": "BEACH",
        "description": "Sky above, sand below, Peace within",
        "images": [
            "../static/img/photo/beach/1.jpeg",
            "../static/img/photo/beach/2.jpeg",
            "../static/img/photo/beach/3.jpeg"
        ]
},
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/package/<package_id>')
def package_details(package_id):
    # Fetch package details based on package_id
    package = packages.get(package_id)
    if package:
        return render_template('package_details.html', package=package)
    else:
        return "Package not found", 404


@app.route('/add_review', methods=['POST'])
def add_review():
    name = request.form.get('name')
    rating = request.form.get('rating')
    comment = request.form.get('comment')

    if not name or not rating or not comment:
        return jsonify({'status': 'error', 'message': 'All fields are required'}), 400

    review = {
        "name": name,
        "rating": int(rating),
        "comment": comment,
        "created_at": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }

    result = reviews_collection.insert_one(review)

    if result.inserted_id:
        review["_id"] = str(result.inserted_id)  # Convert ObjectId to string before emitting
        socketio.emit('new_review', review)  # Emit the updated review
        return jsonify({'status': 'success', 'review': review})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to save review'}), 500

@app.route('/get_reviews', methods=['GET'])
def get_reviews():
    reviews = list(reviews_collection.find({}))
    
    # Convert ObjectId to string for JSON serialization
    for review in reviews:
        review["_id"] = str(review["_id"])

    return jsonify(reviews)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)


