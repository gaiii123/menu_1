from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from pymongo import MongoClient
from flask_mail import Mail, Message  # Import Flask-Mail
from datetime import datetime
from bson.objectid import ObjectId
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit  # Import Flask-Mail


# Load environment variables from .env file
load_dotenv()

# Get MongoDB credentials from .env
username = quote_plus(os.getenv("MONGO_USERNAME"))
password = quote_plus(os.getenv("MONGO_PASSWORD"))
cluster = os.getenv("MONGO_CLUSTER")
dbname = os.getenv("MONGO_DBNAME")
admin_email = os.getenv("ADMIN_EMAIL") 

# Check if credentials exist
if not username or not password or not cluster or not admin_email:
    raise ValueError("MongoDB credentials or Admin Email are missing. Set them in the .env file.")


# MongoDB Connection String
connection_string = f"mongodb+srv://{username}:{password}@{cluster}/{dbname}?retryWrites=true&w=majority"
client = MongoClient(connection_string)

app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use your email provider's SMTP server
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")  # Your email address
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")  # Sender's email

mail = Mail(app)

socketio = SocketIO(app, cors_allowed_origins="*")  # Enable real-time support

# MongoDB connection
db = client[dbname]
reviews_collection = db["reviews"]



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    # Fetch package details based on package_id
    
        return render_template('index.html')
@app.route('/destination_details')
def destination_details():
    # Fetch package details based on package_id
    
        return render_template('destination_details.html')
@app.route('/hotels')
def hotels():
    # Fetch package details based on package_id
    
        return render_template('hotels.html')
@app.route('/all_packages')
def all_packages():
    # Fetch package details based on package_id
    
        return render_template('all_packages.html')
@app.route('/family_package')
def family_package():
    # Fetch package details based on package_id
    
        return render_template('family_package.html')
@app.route('/trekking_and_hiking_package')
def trekking_and_hiking_package():
    # Fetch package details based on package_id
    
        return render_template('trekking_and_hiking_package.html')
@app.route('/wildlife_package')
def wildlife_package():
    # Fetch package details based on package_id
    
        return render_template('wildlife_package.html')
@app.route('/Honeymoon_package')
def Honeymoon_package():
    # Fetch package details based on package_id
    
        return render_template('Honeymoon_package.html')
@app.route('/beach_package')
def beach_package():
    # Fetch package details based on package_id
    
        return render_template('beach_package.html')
@app.route('/culture_package')
def culture_package():
    # Fetch package details based on package_id
    
        return render_template('culture_package.html')

@app.route('/book_package', methods=['GET', 'POST'])
def book_package():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        country = request.form.get('country')
        email = request.form.get('email')
        phone = request.form.get('phone')
        plan = request.form.get('plan')

        print("Received Data:", fullname, country, email, phone, plan)  # Debugging

        # Send email to admin
        send_booking_email(fullname, country, email, phone, plan)

        # Return JSON response indicating success
        return jsonify({'status': 'success', 'message': 'Booking submitted successfully! We are reviewing your request and will get back to you soon.'})

    return render_template('book_package.html')

# Function to send an email
import smtplib
from email.mime.text import MIMEText

def send_booking_email(fullname, country, email, phone, plan):
    try:
        admin_email = os.getenv("ADMIN_EMAIL")
        subject = "New Package Booking Request"
        message = f"""
        New package booking request:
        Full Name: {fullname}
        Country: {country}
        Email: {email}
        Phone: {phone}
        Selected Plan: {plan}
        """

        msg = Message(subject=subject, recipients=[admin_email])
        msg.body = message

        mail.send(msg)  # Send email
        print("Email sent successfully!")

    except Exception as e:
        print("Error sending email:", str(e))



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




