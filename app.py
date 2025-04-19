from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from pymongo import MongoClient
from flask_mail import Mail, Message
from datetime import datetime
from bson.objectid import ObjectId
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import base64


# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') # Change this to a secure secret key

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

# MongoDB collections
db = client[dbname]
reviews_collection = db["reviews"]
admin_collection = db["admin"]
settings_collection = db["settings"]
bookings_collection = db["bookings"]

# Initialize admin account if not exists
def initialize_admin():
    if admin_collection.count_documents({}) == 0:
        hashed_password = generate_password_hash('admin123')
        admin_collection.insert_one({
            'username': 'admin',
            'password': hashed_password,
            'name': 'Admin User',
            'email': admin_email,
            'created_at': datetime.now()
        })
    
    # Initialize settings if not exists
    if settings_collection.count_documents({}) == 0:
        with open('static/img/favicon.ico', 'rb') as f:
            logo_data = f.read()
            logo_base64 = base64.b64encode(logo_data).decode('utf-8')
        
        settings_collection.insert_one({
            'site_name': 'Manthra Travel',
            'logo': logo_base64,
            'logo_filename': 'favicon.ico',
            'updated_at': datetime.now()
        })

initialize_admin()


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

@app.route('/admin/reviews')

def admin_reviews():
    reviews = list(reviews_collection.find().sort("created_at", -1))  # Get all reviews, newest first
    return render_template('admin_review_section.html', reviews=reviews)

@app.route('/admin/delete_review/<review_id>', methods=['DELETE'])

def delete_review(review_id):
    try:
        result = reviews_collection.delete_one({'_id': ObjectId(review_id)})
        if result.deleted_count == 1:
            socketio.emit('review_deleted', {'review_id': review_id})
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Review not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = admin_collection.find_one({'username': username})
        if admin and check_password_hash(admin['password'], password):
            session['logged_in'] = True
            session['username'] = username
            session['name'] = admin['name']
            session['admin_id'] = str(admin['_id'])
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    settings = settings_collection.find_one()
    
    # Get counts from MongoDB
    total_bookings = bookings_collection.count_documents({})
    total_reviews = reviews_collection.count_documents({})
    
    # Get recent bookings (last 5)
    recent_bookings = list(bookings_collection.find()
                         .sort("created_at", -1)
                         .limit(5))
    
    return render_template('admin_dashboard.html', 
                         name=session.get('name'),
                         settings=settings,
                         total_bookings=total_bookings,
                         total_reviews=total_reviews,
                         recent_bookings=recent_bookings)

@app.route('/admin/update_settings', methods=['POST'])
@login_required
def update_settings():
    site_name = request.form.get('site_name')
    logo = request.files.get('logo')
    
    update_data = {
        'site_name': site_name,
        'updated_at': datetime.now()
    }
    
    if logo:
        logo_data = logo.read()
        logo_base64 = base64.b64encode(logo_data).decode('utf-8')
        update_data['logo'] = logo_base64
        update_data['logo_filename'] = logo.filename
    
    settings_collection.update_one({}, {'$set': update_data})
    flash('Settings updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    admin = admin_collection.find_one({'_id': ObjectId(session['admin_id'])})
    if not admin or not check_password_hash(admin['password'], current_password):
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    hashed_password = generate_password_hash(new_password)
    admin_collection.update_one(
        {'_id': ObjectId(session['admin_id'])},
        {'$set': {'password': hashed_password}}
    )
    
    flash('Password changed successfully!', 'success')
    return redirect(url_for('admin_dashboard'))



# Update your book_package route to store bookings in MongoDB
@app.route('/book_package', methods=['GET', 'POST'])
def book_package():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        country = request.form.get('country')
        email = request.form.get('email')
        phone = request.form.get('phone')
        plan = request.form.get('plan')

        # Store booking in MongoDB
        booking = {
            "fullname": fullname,
            "country": country,
            "email": email,
            "phone": phone,
            "plan": plan,
            "status": "Pending",
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        result = bookings_collection.insert_one(booking)
        booking_id = str(result.inserted_id)
        
        # Send email to admin
        send_booking_email(fullname, country, email, phone, plan)
        
        # Emit socket.io event for real-time update
        socketio.emit('new_booking', {
            'booking_id': booking_id,
            'fullname': fullname,
            'plan': plan,
            'status': 'Pending'
        })

        return jsonify({
            'status': 'success', 
            'message': 'Booking submitted successfully!'
        })

    return render_template('book_package.html')

# Add these new routes for admin booking management
@app.route('/admin/bookings')
@login_required
def admin_bookings():
    bookings = list(bookings_collection.find().sort("created_at", -1))
    return render_template('admin_booking_section.html', bookings=bookings)

@app.route('/admin/update_booking_status/<booking_id>', methods=['POST'])
@login_required
def update_booking_status(booking_id):
    new_status = request.form.get('status')
    bookings_collection.update_one(
        {'_id': ObjectId(booking_id)},
        {'$set': {'status': new_status}}
    )
    socketio.emit('booking_updated', {'booking_id': booking_id, 'status': new_status})
    return jsonify({'status': 'success'})

@app.route('/admin/delete_booking/<booking_id>', methods=['DELETE'])
@login_required
def delete_booking(booking_id):
    bookings_collection.delete_one({'_id': ObjectId(booking_id)})
    socketio.emit('booking_deleted', {'booking_id': booking_id})
    return jsonify({'status': 'success'})

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
@app.context_processor
def inject_settings():
    settings = settings_collection.find_one()
    return dict(settings=settings)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)




