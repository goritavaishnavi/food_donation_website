"""
Food Donation Web Application - Main Flask Application
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid
import re

# ==================== Initialize Flask App ====================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'foodshare-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///foodshare_new.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# ==================== Initialize SocketIO ====================

socketio = SocketIO(app, cors_allowed_origins="*")

# ==================== Create Upload Folder ====================

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== Initialize Extensions ====================

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# ==================== Database Models ====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # donor, ngo, volunteer, admin
    bio = db.Column(db.Text, default="")
    profile_image = db.Column(db.String(200), default="default.png")
    contact_no = db.Column(db.String(20), default="")
    organization_name = db.Column(db.String(100), default="")
    address = db.Column(db.String(300), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    donations = db.relationship('Donation', backref='donor', lazy=True)

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default="")
    quantity = db.Column(db.String(50), nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    pickup_location = db.Column(db.String(200), nullable=False)
    pickup_time = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='available')  # available, requested, accepted, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    requests = db.relationship('FoodRequest', backref='donation', lazy=True)
    ratings = db.relationship('Rating', backref='donation', lazy=True)

class FoodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey('donation.id'), nullable=False)
    ngo_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, picked_up, in_transit, delivered, completed
    tracking_status = db.Column(db.String(50), default='pending')  # pending, accepted, volunteer_assigned, picked_up, in_transit, delivered, completed
    pickup_time = db.Column(db.DateTime, nullable=True)
    delivery_time = db.Column(db.DateTime, nullable=True)
    tracking_notes = db.Column(db.Text, default="")
    # Delivery confirmation fields
    delivery_confirmation_photo = db.Column(db.String(200), default="")
    delivery_review = db.Column(db.Text, default="")
    delivery_rating = db.Column(db.Integer, default=5)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime, nullable=True)
    
    ngo_user = db.relationship('User', foreign_keys=[ngo_id])
    volunteer = db.relationship('User', foreign_keys=[volunteer_id])

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey('donation.id'), nullable=False)
    ngo_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text, default="")
    photos = db.Column(db.String(500), default="")  # Comma-separated photo paths
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    donor = db.relationship('User', foreign_keys=[donor_id])
    ngo_user = db.relationship('User', foreign_keys=[ngo_id])

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(100), default="")
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

import re

# ==================== Password Validation ====================

def validate_password(password):
    """
    Validate password requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$%^&*...)"
    
    return True, ""

# ==================== Routes ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/error')
def error():
    return render_template('error.html', error_code=404, error='Page Not Found')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        organization_name = request.form.get('organization_name', '')
        contact_no = request.form.get('contact_no', '')
        address = request.form.get('address', '')
        
        # Validate password constraints
        is_valid, error_message = validate_password(password)
        if not is_valid:
            flash(error_message, 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken!', 'error')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            organization_name=organization_name,
            contact_no=contact_no,
            address=address
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'donor':
                return redirect(url_for('donor_dashboard'))
            elif user.role == 'ngo':
                return redirect(url_for('ngo_dashboard'))
            elif user.role == 'volunteer':
                return redirect(url_for('volunteer_dashboard'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ==================== Donor Routes ====================

@app.route('/donor/dashboard')
@login_required
def donor_dashboard():
    if current_user.role != 'donor':
        return redirect(url_for('index'))
    
    donations = Donation.query.filter_by(donor_id=current_user.id).order_by(Donation.created_at.desc()).all()
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
    
    # Get ratings for donor
    ratings = Rating.query.filter_by(donor_id=current_user.id).order_by(Rating.created_at.desc()).limit(5).all()
    avg_rating = db.session.query(db.func.avg(Rating.rating)).filter_by(donor_id=current_user.id).scalar() or 0
    
    return render_template('donor_dashboard.html', 
                         donations=donations, 
                         notifications=notifications,
                         ratings=ratings,
                         avg_rating=round(avg_rating, 1))

@app.route('/donor/post-donation', methods=['GET', 'POST'])
@login_required
def post_donation():
    if current_user.role != 'donor':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        donation = Donation(
            donor_id=current_user.id,
            food_type=request.form.get('food_type'),
            description=request.form.get('description'),
            quantity=request.form.get('quantity'),
            expiry_date=datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d').date(),
            pickup_location=request.form.get('pickup_location'),
            pickup_time=request.form.get('pickup_time'),
            status='available'
        )
        db.session.add(donation)
        db.session.commit()
        
        # Notify all NGOs
        ngos = User.query.filter_by(role='ngo').all()
        for ngo in ngos:
            notification = Notification(
                user_id=ngo.id,
                message=f"New donation available: {donation.food_type} from {current_user.username}",
                link=url_for('ngo_dashboard')
            )
            db.session.add(notification)
        db.session.commit()
        
        flash('Donation posted successfully!', 'success')
        return redirect(url_for('donor_dashboard'))
    
    return render_template('post_donation.html')

@app.route('/donation/<int:id>')
@login_required
def donation_details(id):
    donation = Donation.query.get_or_404(id)
    requests = FoodRequest.query.filter_by(donation_id=id).all()
    ratings = Rating.query.filter_by(donation_id=id).all()
    
    return render_template('donation_details.html', donation=donation, requests=requests, ratings=ratings)

@app.route('/donation/<int:id>/respond/<action>')
@login_required
def respond_request(id, action):
    food_request = FoodRequest.query.get_or_404(id)
    
    if food_request.donation.donor_id != current_user.id:
        flash('Unauthorized!', 'error')
        return redirect(url_for('donor_dashboard'))
    
    if action == 'accept':
        food_request.status = 'accepted'
        donation = food_request.donation
        donation.status = 'accepted'
        
        # Notify NGO
        notification = Notification(
            user_id=food_request.ngo_id,
            message=f"Your request for {donation.food_type} has been accepted!",
            link=url_for('ngo_dashboard')
        )
        db.session.add(notification)
        flash('Request accepted!', 'success')
    elif action == 'reject':
        food_request.status = 'rejected'
        
        # Notify NGO
        notification = Notification(
            user_id=food_request.ngo_id,
            message=f"Your request for {food_request.donation.food_type} has been rejected.",
            link=url_for('ngo_dashboard')
        )
        db.session.add(notification)
        flash('Request rejected.', 'info')
    
    food_request.responded_at = datetime.utcnow()
    db.session.commit()
    
    return redirect(url_for('donation_details', id=id))

# ==================== NGO Routes ====================

@app.route('/ngo/dashboard')
@login_required
def ngo_dashboard():
    if current_user.role != 'ngo':
        return redirect(url_for('index'))
    
    # Get available donations
    available_donations = Donation.query.filter_by(status='available').order_by(Donation.created_at.desc()).all()
    
    # Get my requests
    my_requests = FoodRequest.query.filter_by(ngo_id=current_user.id).order_by(FoodRequest.requested_at.desc()).all()
    
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('ngo_dashboard.html', 
                         available_donations=available_donations,
                         my_requests=my_requests,
                         notifications=notifications)

@app.route('/ngo/request/<int:donation_id>', methods=['POST'])
@login_required
def request_food(donation_id):
    if current_user.role != 'ngo':
        return redirect(url_for('index'))
    
    donation = Donation.query.get_or_404(donation_id)
    
    if donation.status != 'available':
        flash('This donation is no longer available!', 'error')
        return redirect(url_for('ngo_dashboard'))
    
    # Check if already requested
    existing = FoodRequest.query.filter_by(donation_id=donation_id, ngo_id=current_user.id).first()
    if existing:
        flash('You have already requested this donation!', 'error')
        return redirect(url_for('ngo_dashboard'))
    
    food_request = FoodRequest(
        donation_id=donation_id,
        ngo_id=current_user.id,
        status='pending'
    )
    db.session.add(food_request)
    db.session.commit()
    
    # Notify donor
    notification = Notification(
        user_id=donation.donor_id,
        message=f"NGO '{current_user.organization_name}' has requested your {donation.food_type} donation.",
        link=url_for('donation_details', id=donation_id)
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Request sent successfully!', 'success')
    return redirect(url_for('ngo_dashboard'))

@app.route('/ngo/rate/<int:donation_id>', methods=['POST'])
@login_required
def rate_donor(donation_id):
    if current_user.role != 'ngo':
        return redirect(url_for('index'))
    
    donation = Donation.query.get_or_404(donation_id)
    
    rating = request.form.get('rating')
    feedback = request.form.get('feedback')
    
    # Handle photo upload
    photo_filename = ""
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename:
            filename = secure_filename(photo.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            photo_filename = unique_filename
    
    new_rating = Rating(
        donation_id=donation_id,
        ngo_id=current_user.id,
        donor_id=donation.donor_id,
        rating=int(rating),
        feedback=feedback,
        photos=photo_filename
    )
    db.session.add(new_rating)
    
    # Update donation status
    donation.status = 'completed'
    db.session.commit()
    
    flash('Thank you for your feedback!', 'success')
    return redirect(url_for('ngo_dashboard'))

# ==================== Volunteer Routes ====================

@app.route('/volunteer/dashboard')
@login_required
def volunteer_dashboard():
    if current_user.role != 'volunteer':
        return redirect(url_for('index'))
    
    # Get assigned deliveries
    assigned_requests = FoodRequest.query.filter_by(volunteer_id=current_user.id).order_by(FoodRequest.requested_at.desc()).all()
    
    # Get available requests (not yet assigned)
    available_requests = FoodRequest.query.filter(
        FoodRequest.volunteer_id == None,
        FoodRequest.status == 'accepted'
    ).order_by(FoodRequest.requested_at.desc()).all()
    
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('volunteer_dashboard.html',
                         assigned_requests=assigned_requests,
                         available_requests=available_requests,
                         notifications=notifications)

@app.route('/volunteer/accept/<int:request_id>')
@login_required
def volunteer_accept(request_id):
    if current_user.role != 'volunteer':
        return redirect(url_for('index'))
    
    food_request = FoodRequest.query.get_or_404(request_id)
    food_request.volunteer_id = current_user.id
    db.session.commit()
    
    # Notify NGO
    notification = Notification(
        user_id=food_request.ngo_id,
        message=f"A volunteer has accepted to deliver the donation.",
        link=url_for('volunteer_dashboard')
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('You have accepted this delivery!', 'success')
    return redirect(url_for('volunteer_dashboard'))

@app.route('/volunteer/complete/<int:request_id>')
@login_required
def volunteer_complete(request_id):
    if current_user.role != 'volunteer':
        return redirect(url_for('index'))
    
    food_request = FoodRequest.query.get_or_404(request_id)
    food_request.status = 'completed'
    food_request.donation.status = 'completed'
    db.session.commit()
    
    flash('Delivery marked as completed!', 'success')
    return redirect(url_for('volunteer_dashboard'))

# ==================== Admin Routes ====================

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    users = User.query.all()
    donations = Donation.query.order_by(Donation.created_at.desc()).all()
    requests = FoodRequest.query.order_by(FoodRequest.requested_at.desc()).all()
    
    stats = {
        'total_users': len(users),
        'total_donations': len(donations),
        'total_requests': len(requests),
        'completed': len([d for d in donations if d.status == 'completed']),
        'donors': len([u for u in users if u.role == 'donor']),
        'ngos': len([u for u in users if u.role == 'ngo']),
        'volunteers': len([u for u in users if u.role == 'volunteer'])
    }
    
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html',
                         users=users,
                         donations=donations,
                         requests=requests,
                         stats=stats,
                         notifications=notifications)

@app.route('/admin/assign-volunteer/<int:request_id>', methods=['POST'])
@login_required
def assign_volunteer(request_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    food_request = FoodRequest.query.get_or_404(request_id)
    volunteer_id = request.form.get('volunteer_id')
    
    food_request.volunteer_id = volunteer_id
    db.session.commit()
    
    # Notify volunteer
    notification = Notification(
        user_id=volunteer_id,
        message=f"You have been assigned a new delivery: {food_request.donation.food_type}",
        link=url_for('volunteer_dashboard')
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Volunteer assigned successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# ==================== Common Routes ====================

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.username = request.form.get('username')
        current_user.bio = request.form.get('bio')
        current_user.contact_no = request.form.get('contact_no')
        current_user.organization_name = request.form.get('organization_name', '')
        current_user.address = request.form.get('address', '')
        
        # Handle profile image upload
        if 'profile_image' in request.files:
            image = request.files['profile_image']
            if image.filename:
                filename = secure_filename(image.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                current_user.profile_image = unique_filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    
    return render_template('profile.html')

@app.route('/history')
@login_required
def history():
    if current_user.role == 'donor':
        donations = Donation.query.filter_by(donor_id=current_user.id).order_by(Donation.created_at.desc()).all()
        return render_template('history.html', donations=donations, title='Donation History')
    elif current_user.role == 'ngo':
        requests = FoodRequest.query.filter_by(ngo_id=current_user.id).order_by(FoodRequest.requested_at.desc()).all()
        return render_template('history.html', requests=requests, title='Request History')
    elif current_user.role == 'volunteer':
        deliveries = FoodRequest.query.filter_by(volunteer_id=current_user.id).order_by(FoodRequest.requested_at.desc()).all()
        return render_template('history.html', deliveries=deliveries, title='Delivery History')
    else:
        return redirect(url_for('admin_dashboard'))

@app.route('/notifications')
@login_required
def notifications():
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=user_notifications)

@app.route('/notifications/mark-read/<int:id>')
@login_required
def mark_read(id):
    notification = Notification.query.get_or_404(id)
    if notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()
    return redirect(url_for('notifications'))

# ==================== Tracking Routes ====================

@app.route('/track/<int:request_id>')
@login_required
def track_donation(request_id):
    food_request = FoodRequest.query.get_or_404(request_id)
    
    # Check if user has access to view tracking
    if current_user.role not in ['admin', 'donor', 'ngo', 'volunteer']:
        flash('Unauthorized!', 'error')
        return redirect(url_for('index'))
    
    # For donors: can only track their own donations
    if current_user.role == 'donor' and food_request.donation.donor_id != current_user.id:
        flash('Unauthorized!', 'error')
        return redirect(url_for('donor_dashboard'))
    
    # For NGOs: can only track their own requests
    if current_user.role == 'ngo' and food_request.ngo_id != current_user.id:
        flash('Unauthorized!', 'error')
        return redirect(url_for('ngo_dashboard'))
    
    # For volunteers: can only track their assigned deliveries
    if current_user.role == 'volunteer' and food_request.volunteer_id != current_user.id:
        flash('Unauthorized!', 'error')
        return redirect(url_for('volunteer_dashboard'))
    
    return render_template('tracking.html', request=food_request)

@app.route('/track/update/<int:request_id>', methods=['POST'])
@login_required
def update_tracking(request_id):
    food_request = FoodRequest.query.get_or_404(request_id)
    
    # Only volunteers can update tracking
    if current_user.role != 'volunteer' or food_request.volunteer_id != current_user.id:
        flash('Only assigned volunteers can update tracking!', 'error')
        return redirect(url_for('volunteer_dashboard'))
    
    new_status = request.form.get('tracking_status')
    notes = request.form.get('tracking_notes', '')
    
    food_request.tracking_status = new_status
    food_request.tracking_notes = notes
    
    if new_status == 'picked_up':
        food_request.pickup_time = datetime.utcnow()
        # Notify donor that food is picked up
        notification = Notification(
            user_id=food_request.donation.donor_id,
            message=f"✅ Your donation '{food_request.donation.food_type}' has been picked up by the volunteer!",
            link=url_for('track_donation', request_id=request_id)
        )
        db.session.add(notification)
        # Notify NGO that pickup is done
        notification2 = Notification(
            user_id=food_request.ngo_id,
            message=f"📦 Volunteer has picked up '{food_request.donation.food_type}'. On the way!",
            link=url_for('track_donation', request_id=request_id)
        )
        db.session.add(notification2)
    elif new_status == 'in_transit':
        # Notify both
        notification = Notification(
            user_id=food_request.donation.donor_id,
            message=f"🚚 Your donation '{food_request.donation.food_type}' is on the way to the NGO!",
            link=url_for('track_donation', request_id=request_id)
        )
        db.session.add(notification)
        notification2 = Notification(
            user_id=food_request.ngo_id,
            message=f"🚚 Your requested '{food_request.donation.food_type}' is on the way!",
            link=url_for('track_donation', request_id=request_id)
        )
        db.session.add(notification2)
    elif new_status == 'delivered':
        food_request.delivery_time = datetime.utcnow()
        food_request.status = 'delivered'
        # Notify donor and NGO
        notification = Notification(
            user_id=food_request.donation.donor_id,
            message=f"🎉 Your donation '{food_request.donation.food_type}' has been delivered successfully!",
            link=url_for('track_donation', request_id=request_id)
        )
        db.session.add(notification)
        notification2 = Notification(
            user_id=food_request.ngo_id,
            message=f"🍽️ Your requested '{food_request.donation.food_type}' has been delivered! Please confirm receipt and upload a photo.",
            link=url_for('confirm_delivery', request_id=request_id)
        )
        db.session.add(notification2)
    
    db.session.commit()
    
    flash('Tracking updated successfully!', 'success')
    return redirect(url_for('track_donation', request_id=request_id))

# ==================== NGO Delivery Confirmation ====================

@app.route('/confirm-delivery/<int:request_id>', methods=['GET', 'POST'])
@login_required
def confirm_delivery(request_id):
    if current_user.role != 'ngo':
        return redirect(url_for('index'))
    
    food_request = FoodRequest.query.get_or_404(request_id)
    
    if food_request.ngo_id != current_user.id:
        flash('Unauthorized!', 'error')
        return redirect(url_for('ngo_dashboard'))
    
    if request.method == 'POST':
        # Handle delivery photo and review
        delivery_photo = ""
        if 'delivery_photo' in request.files:
            photo = request.files['delivery_photo']
            if photo.filename:
                filename = secure_filename(photo.filename)
                unique_filename = f"delivery_{uuid.uuid4()}_{filename}"
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                delivery_photo = unique_filename
        
        # Save delivery confirmation
        food_request.delivery_confirmation_photo = delivery_photo
        food_request.delivery_review = request.form.get('review', '')
        food_request.delivery_rating = request.form.get('delivery_rating', 5)
        food_request.status = 'completed'
        food_request.donation.status = 'completed'
        
        # Create rating for donor
        new_rating = Rating(
            donation_id=food_request.donation_id,
            ngo_id=current_user.id,
            donor_id=food_request.donation.donor_id,
            rating=int(request.form.get('donor_rating', 5)),
            feedback=request.form.get('feedback', ''),
            photos=delivery_photo
        )
        db.session.add(new_rating)
        
        # Notify donor about the review
        notification = Notification(
            user_id=food_request.donation.donor_id,
            message=f"⭐ Thank you! The NGO has confirmed delivery and rated your donation.",
            link=url_for('donor_dashboard')
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Delivery confirmed! Thank you for your feedback.', 'success')
        return redirect(url_for('ngo_dashboard'))
    
    return render_template('confirm_delivery.html', request=food_request)

# ==================== Chatbot API ====================

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    message = data.get('message', '').lower()
    
    # Simple rule-based responses
    responses = {
        'hello': "Hello! I'm FoodShare Bot. How can I help you today?",
        'hi': "Hi there! How can I assist you with food donation?",
        'how to donate': "To donate food: 1) Register as a Donor 2) Login to your dashboard 3) Click 'Post Donation' 4) Fill in the details about your food donation",
        'donate': "Great! To donate food, register as a Donor and use the 'Post Donation' feature on your dashboard.",
        'ngo': "NGOs can register on our platform to request food donations. Once registered, you'll receive notifications about available donations and can request them.",
        'volunteer': "Volunteers help transport food from donors to NGOs. Register as a Volunteer to start accepting delivery assignments.",
        'what is foodshare': "FoodShare is a platform that connects food donors with NGOs and volunteers to ensure surplus food reaches those in need.",
        'how it works': "1. Donors post available food\n2. NGOs receive notifications and request\n3. Volunteers help transport\n4. NGOs rate the donors",
        'contact': "You can contact us at support@foodshare.org or call 1800-FOOD-SHARE",
        'rating': "After receiving donations, NGOs can rate donors with 1-5 stars and provide feedback with photos.",
        'profile': "Update your profile by clicking on your name in the top right and selecting 'Profile'.",
        'logout': "Click on your profile icon in the top right and select 'Sign Out' to logout.",
        'default': "I'm here to help! You can ask me about:\n- How to donate\n- NGO registration\n- Volunteer opportunities\n- How the platform works\n- Rating system\n- Profile management"
    }
    
    # Check for keyword matches
    for key, response in responses.items():
        if key in message:
            return jsonify({'response': response})
    
    return jsonify({'response': responses['default']})

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Server error'), 500

# ==================== WebSocket Events ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    if current_user.is_authenticated:
        # Join a room specific to the user for targeted notifications
        emit('connected', {'message': 'Connected to notification server'}, room=f'user_{current_user.id}')
        print(f'User {current_user.id} connected to WebSocket')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('join')
def handle_join(data):
    """Handle user joining their notification room"""
    if current_user.is_authenticated:
        room = f'user_{current_user.id}'
        print(f'User {current_user.id} joined room {room}')

# ==================== Real-time Notification Helper ====================

def broadcast_notification(user_id, message, link=''):
    """
    Send real-time notification to a specific user via WebSocket
    Also saves notification to database
    """
    # Save to database
    notification = Notification(
        user_id=user_id,
        message=message,
        link=link
    )
    db.session.add(notification)
    db.session.commit()
    
    # Send real-time notification via WebSocket
    socketio.emit('new_notification', {
        'id': notification.id,
        'message': message,
        'link': link,
        'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }, room=f'user_{user_id}')
    
    return notification

def broadcast_to_role(role, message, link=''):
    """
    Send real-time notification to all users of a specific role
    """
    users = User.query.filter_by(role=role).all()
    for user in users:
        broadcast_notification(user.id, message, link)

# ==================== Initialize Database ====================

with app.app_context():
    db.create_all()
    
    # Create admin user if not exists
    admin = User.query.filter_by(email='admin@foodshare.com').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@foodshare.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            organization_name='FoodShare Admin',
            bio='Platform Administrator'
        )
        db.session.add(admin)
        db.session.commit()
      #  print("Admin user created: admin@foodshare.com / admin123")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

