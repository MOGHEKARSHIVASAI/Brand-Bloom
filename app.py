from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

# Import database
from database import get_db, init_db

# Import AI tools modules (with error handling)
try:
    from modules.ai_tools.website_builder import generate_website_content
except ImportError:
    def generate_website_content(data):
        return {"status": "error", "message": "Website builder not available"}

try:
    from modules.ai_tools.feedback_analyzer import analyze_feedback
except ImportError:
    def analyze_feedback(text):
        return {"status": "error", "message": "Feedback analyzer not available"}

try:
    from modules.ai_tools.email_drafter import draft_email
except ImportError:
    def draft_email(data):
        return {"status": "error", "message": "Email drafter not available"}

try:
    from modules.ai_tools.poster_maker import create_poster_content
except ImportError:
    def create_poster_content(data):
        return {"status": "error", "message": "Poster maker not available"}

try:
    from modules.ai_tools.sales_insights import analyze_sales_data
except ImportError:
    def analyze_sales_data(filepath):
        return {"status": "error", "message": "Sales insights not available"}

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize database
db = init_db()

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = db.authenticate_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        user_id = db.create_user(name, email, password)
        if user_id:
            session['user_id'] = user_id
            session['user_email'] = email
            return redirect(url_for('onboarding'))
        else:
            flash('Registration failed - email may already exist')
    
    return render_template('register.html')

@app.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        business_name = request.form['business_name']
        industry = request.form['industry']
        description = request.form['description']
        target_audience = request.form['target_audience']
        goals = request.form.getlist('goals')  # Get multiple checkbox values
        
        db.create_business(
            session['user_id'],
            business_name,
            industry,
            description,
            target_audience,
            goals
        )
        return redirect(url_for('dashboard'))
    
    return render_template('onboarding.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_with_business = db.get_user_with_business(session['user_id'])
    business_info = user_with_business.get('business') if user_with_business else None
    
    return render_template('dashboard.html', business=business_info)

@app.route('/tools/website')
def website_tool():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('tools/website.html')

@app.route('/tools/feedback')
def feedback_tool():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('tools/feedback.html')

@app.route('/tools/email')
def email_tool():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('tools/email.html')

@app.route('/tools/poster')
def poster_tool():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('tools/poster.html')

@app.route('/tools/sales')
def sales_tool():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('tools/sales.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_with_business = db.get_user_with_business(session['user_id'])
    business_info = user_with_business.get('business') if user_with_business else None
    
    return render_template('profile.html', business=business_info)

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# API endpoints for AI tools
@app.route('/api/generate-website', methods=['POST'])
def api_generate_website():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    result = generate_website_content(data)
    return jsonify(result)

@app.route('/api/analyze-feedback', methods=['POST'])
def api_analyze_feedback():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    result = analyze_feedback(data['feedback'])
    return jsonify(result)

@app.route('/api/draft-email', methods=['POST'])
def api_draft_email():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    result = draft_email(data)
    return jsonify(result)

@app.route('/api/create-poster', methods=['POST'])
def api_create_poster():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    result = create_poster_content(data)
    return jsonify(result)

@app.route('/api/upload-sales', methods=['POST'])
def api_upload_sales():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        result = analyze_sales_data(filepath)
        return jsonify(result)
    
    return jsonify({'error': 'Invalid file format'}), 400

if __name__ == '__main__':
    app.run(debug=True)