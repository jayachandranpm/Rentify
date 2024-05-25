from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from datetime import datetime, timedelta
import secrets
import smtplib
from email.mime.text import MIMEText
from flask_mail import Mail, Message
import logging

app = Flask(__name__)
# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app.config['SECRET_KEY'] = secrets.token_hex(16)  # Generate a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/rentify_db'  # Update with your MySQL details
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define User and Property models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_seller = db.Column(db.Boolean, default=False)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller = db.relationship('User', backref=db.backref('properties', lazy=True))
    likes = db.Column(db.Integer, default=0)

# Configure Flask app for email sending
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_TIMEOUT'] = 30  # Set the timeout to 30 seconds (or adjust as needed)
app.config['MAIL_DEBUG'] = True
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jayachandranpm2001@gmail.com'
app.config['MAIL_PASSWORD'] = 'yxrq piyw geje suti'
app.config['MAIL_DEFAULT_SENDER'] = 'jayachandranpm2001@gmail.com' 

# Initialize Flask-Mail
mail = Mail(app)

# Updated email sending function
def send_email(to, subject, body):
    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[to])
    msg.body = body
    mail.send(msg)


# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = generate_password_hash(request.form['password'])
        is_seller = True if request.form.get('is_seller') else False

        new_user = User(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number, password=password, is_seller=is_seller)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('index'))

@app.route('/buyer_dashboard')
def buyer_dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if not user.is_seller:
            return render_template('buyer.html')
    return redirect(url_for('login'))

@app.route('/seller_dashboard')
def seller_dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.is_seller:
            return render_template('seller.html')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/properties', methods=['GET'])
def get_properties():
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of properties per page
    properties = Property.query.paginate(page=page, per_page=per_page, error_out=False)

    
    is_logged_in = 'user_id' in session

    property_list = [{
        'id': prop.id,
        'title': prop.title,
        'description': prop.description,
        'price': prop.price,
        'location': prop.location,
        'bedrooms': prop.bedrooms,
        'bathrooms': prop.bathrooms,
        'likes':prop.likes,
        
        'seller_id': prop.seller_id if is_logged_in else None,
        'seller_contact': prop.seller.phone_number if is_logged_in else 'Login to view',
        'Email':prop.seller.email if is_logged_in else 'Login to view'
    } for prop in properties.items]

    return jsonify({
        'properties': property_list,
        'total_pages': properties.pages,
        'current_page': properties.page
    })

@app.route('/post_property', methods=['POST'])
def post_property():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    user = User.query.get(session['user_id'])
    if not user.is_seller:
        return jsonify({'message': 'Unauthorized'}), 401

    title = request.form['title']
    description = request.form['description']
    price = float(request.form['price'])
    location = request.form['location']
    bedrooms = int(request.form['bedrooms'])
    bathrooms = int(request.form['bathrooms'])

    new_property = Property(title=title, description=description, price=price, location=location, bedrooms=bedrooms, bathrooms=bathrooms, seller=user)
    db.session.add(new_property)
    db.session.commit()
    return jsonify({'message': 'Property posted successfully'}), 201

@app.route('/like_property/<int:property_id>', methods=['POST'])
def like_property(property_id):
    property = Property.query.get_or_404(property_id)
    property.likes += 1
    db.session.commit()
    return jsonify({'likes': property.likes})

@app.route('/interested/<int:property_id>', methods=['POST'])
def interested(property_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    user = User.query.get(session['user_id'])
    property = Property.query.get_or_404(property_id)
    seller = property.seller

    # Render the email template with user details
    email_body = render_template('interested_email.html', user_email=user.email, user_phone=user.phone_number)

    # Create a message object for the email
    msg = Message(subject='Interest in Property', recipients=[seller.email], html=email_body)

    # Send the email
    try:
        mail.send(msg)
        logger.info("Email sent to %s about interest in property ID %d", seller.email, property.id)
        return jsonify({'message': 'Contact details sent to the property owner'})
    except Exception as e:
        logger.error("Failed to send email to %s: %s", seller.email, str(e))
        return jsonify({'message': 'Failed to send email'}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
