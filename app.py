from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from config import Config
from firebase_service import firebase_service
from models import get_user, verify_password
from detection import detect_fill
from firebase_service import update_bin_fill
from flask import send_from_directory
from flask import request, jsonify
from firebase_service import save_admin_fcm_token, get_admin_fcm_token
from firebase_admin import messaging
from detection import detect_fill
from firebase_service import update_bin_fill, send_bin_full_notification
import base64
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if verify_password(username, password):
            user = get_user(username)
            login_user(user)
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/bins/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_bin():
    if request.method == 'POST':
        bin_data = {
            'location': request.form.get('location'),
            'fill_level': int(request.form.get('fill_level', 0)),
            'capacity': int(request.form.get('capacity', 100)),
            'type': request.form.get('type', 'General')
        }
        
        bin_id = firebase_service.add_bin(bin_data)
        if bin_id:
            flash('Bin added successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Error adding bin. Please try again.', 'danger')
    
    return render_template('add_bin.html')

@app.route('/bins/edit/<bin_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_bin(bin_id):
    if request.method == 'POST':
        bin_data = {
            'location': request.form.get('location'),
            'fill_level': int(request.form.get('fill_level', 0)),
            'capacity': int(request.form.get('capacity', 100)),
            'type': request.form.get('type', 'General')
        }
        
        result = firebase_service.update_bin(bin_id, bin_data)
        if result is not None:
            flash('Bin updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Error updating bin. Please try again.', 'danger')
    
    bin_data = firebase_service.get_bin(bin_id)
    if not bin_data:
        flash('Bin not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    bin_data['id'] = bin_id
    return render_template('edit_bin.html', bin=bin_data)

@app.route('/bins/delete/<bin_id>', methods=['POST'])
@login_required
@admin_required
def delete_bin(bin_id):
    result = firebase_service.delete_bin(bin_id)
    if result is not None:
        flash('Bin deleted successfully!', 'success')
    else:
        flash('Error deleting bin. Please try again.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/detect', methods=['POST'])
@login_required
def detect():
    file = request.files.get('image')

    if not file:
        return "No image uploaded", 400

    path = "temp.jpg"
    file.save(path)

    fill_percent = detect_fill(path)

    bin_id = "bin_id_1"  # or whichever bin you're updating
    update_bin_fill(bin_id, fill_percent)

    # Trigger push notification if full (>= 80%)
    if fill_percent >= 80:
        send_bin_full_notification(bin_id, fill_percent)

    return redirect('/dashboard')

@app.route('/detect_webcam', methods=['POST'])
@login_required
def detect_webcam():
    data = request.form.get('image_data')

    if not data:
        return "No image data", 400

    img_data = data.split(",")[1]
    img_bytes = base64.b64decode(img_data)

    path = "temp_cam.jpg"
    with open(path, "wb") as f:
        f.write(img_bytes)

    fill_percent = detect_fill(path)
    update_bin_fill("bin_id_1", fill_percent)

    return "OK"

@app.route('/firebase-messaging-sw.js')
def firebase_sw():
    # File is in project root
    return send_from_directory('.', 'firebase-messaging-sw.js')

@app.route("/save_fcm_token", methods=["POST"])
@login_required
def save_fcm_token_route():
    data = request.get_json()
    token = data.get("token")

    if not token:
        return "No token", 400

    save_admin_fcm_token(token)
    print("Saved admin FCM token:", token)
    return "OK"

# API Routes
@app.route('/api/bins')
@login_required
def api_get_bins():
    bins = firebase_service.get_all_bins()
    stats = firebase_service.get_bin_statistics()
    return jsonify({
        'bins': bins,
        'stats': stats
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)