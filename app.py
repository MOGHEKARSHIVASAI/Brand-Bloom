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

@app.template_filter('format_date')
def format_date(value, format='%B %Y'):
    """Format a date string or datetime object"""
    if not value:
        return 'N/A'
    
    if isinstance(value, str):
        try:
            # Try parsing common formats
            if 'T' in value:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            else:
                # Try other formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d']:
                    try:
                        dt = datetime.strptime(value, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # If all parsing fails, return the string as-is
                    return value[:10] if len(value) > 10 else value
            return dt.strftime(format)
        except:
            return value[:10] if len(value) > 10 else value
    elif hasattr(value, 'strftime'):
        return value.strftime(format)
    else:
        return str(value)

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
    
    try:
        user_with_business = db.get_user_with_business(session['user_id'])
        business_info = user_with_business.get('business') if user_with_business else None
        
        # Convert string dates to datetime objects if needed
        if business_info:
            for date_field in ['created_at', 'updated_at']:
                if date_field in business_info and business_info[date_field]:
                    if isinstance(business_info[date_field], str):
                        try:
                            # Try parsing common datetime formats
                            from datetime import datetime
                            # Common SQLite datetime format
                            if 'T' in business_info[date_field]:
                                business_info[date_field] = datetime.fromisoformat(business_info[date_field].replace('Z', '+00:00'))
                            else:
                                # Try other common formats
                                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d']:
                                    try:
                                        business_info[date_field] = datetime.strptime(business_info[date_field], fmt)
                                        break
                                    except ValueError:
                                        continue
                        except (ValueError, TypeError) as date_error:
                            print(f"Could not parse {date_field}: {business_info[date_field]} - {date_error}")
                            business_info[date_field] = None
        
        # Debug: Print to console to check data
        print(f"User ID: {session['user_id']}")
        print(f"User with business: {user_with_business}")
        print(f"Business info: {business_info}")
        
        return render_template('profile.html', business=business_info)
    
    except Exception as e:
        print(f"Error in profile route: {str(e)}")
        flash(f'Error loading profile: {str(e)}')
        return redirect(url_for('dashboard'))

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
    
    # Store website in database
    if result.get('html') and result.get('metadata'):
        try:
            website_id = db.save_website(
                session['user_id'],
                result['metadata']['title'],
                result['html'],
                result['metadata']
            )
            if website_id:
                result['website_id'] = website_id
                result['success'] = True
                print(f"Website saved successfully with ID: {website_id}")
            else:
                print("Failed to save website to database")
                result['error'] = 'Failed to save website to database'
        except Exception as e:
            print(f"Error saving website: {str(e)}")
            result['error'] = f'Error saving website: {str(e)}'
    else:
        print("Missing html or metadata in result")
        result['error'] = 'Missing html or metadata in generated content'
    
    return jsonify(result)

# Add new endpoint to serve websites directly
@app.route('/website/<keyword>')
def serve_website_by_keyword(keyword):
    """Serve website content directly by keyword"""
    website = db.get_website_by_keyword(keyword, None)  # Allow public access
    if not website:
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Website Not Found</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1>Website Not Found</h1>
            <p>No website found with keyword: <strong>{keyword}</strong></p>
        </body>
        </html>
        """, 404
    
    return website['html_content']

@app.route('/website/id/<int:website_id>')
def serve_website_by_id(website_id):
    """Serve website content directly by ID"""
    website = db.get_website_by_id(website_id, None)  # Allow public access for demo
    if not website:
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Website Not Found</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1>Website Not Found</h1>
            <p>No website found with ID: <strong>{website_id}</strong></p>
        </body>
        </html>
        """, 404
    
    return website['html_content']


@app.route('/api/deploy-website', methods=['POST'])
def api_deploy_website():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    website_id = data.get('website_id')
    keyword = data.get('keyword')
    
    if not website_id or not keyword:
        return jsonify({'error': 'Website ID and keyword are required'}), 400
    
    website = db.get_website_by_id(website_id, session['user_id'])
    if not website:
        return jsonify({'error': 'Website not found or unauthorized'}), 404
    
    # Check if keyword is unique
    if db.get_website_by_keyword(keyword):
        return jsonify({'error': 'Keyword already in use'}), 400
    
    # Update website with keyword
    metadata = website['metadata']
    metadata['keyword'] = keyword
    
    success = db.update_website(website_id, session['user_id'], metadata=metadata)
    if success:
        return jsonify({'success': True, 'keyword': keyword})
    return jsonify({'error': 'Failed to deploy website'}), 500

@app.route('/api/get-website/<int:website_id>', methods=['GET'])
def api_get_website(website_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    website = db.get_website_by_id(website_id, session['user_id'])
    if website:
        return jsonify({
            'website_id': website['id'],
            'title': website['title'],
            'html': website['html_content'],
            'metadata': website['metadata'],
            'created_at': website['created_at'],
            'updated_at': website['updated_at']
        })
    return jsonify({'error': 'Website not found or unauthorized'}), 404

@app.route('/api/get-user-websites', methods=['GET'])
def api_get_user_websites():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    websites = db.get_user_websites(session['user_id'])
    return jsonify([{
        'website_id': w['id'],
        'title': w['title'],
        'metadata': w['metadata'],
        'created_at': w['created_at'],
        'updated_at': w['updated_at']
    } for w in websites])

@app.route('/api/get-website-by-keyword/<keyword>', methods=['GET'])
def api_get_website_by_keyword(keyword):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    website = db.get_website_by_keyword(keyword, session['user_id'])
    if website:
        return jsonify({
            'website_id': website['id'],
            'title': website['title'],
            'html': website['html_content'],
            'metadata': website['metadata'],
            'created_at': website['created_at'],
            'updated_at': website['updated_at']
        })
    return jsonify({'error': 'Website not found for this keyword'}), 404

@app.route('/api/delete-website/<int:website_id>', methods=['DELETE'])
def api_delete_website(website_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    website = db.get_website_by_id(website_id, session['user_id'])
    if not website:
        return jsonify({'error': 'Website not found or unauthorized'}), 404
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM websites WHERE id = ? AND user_id = ?', 
                      (website_id, session['user_id']))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/get-deployed-websites-count', methods=['GET'])
def api_get_deployed_websites_count():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    count = db.count_deployed_websites(session['user_id'])
    return jsonify({'count': count})

@app.route('/api/update-profile', methods=['POST'])
def api_update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    try:
        success = db.update_business(
            session['user_id'],
            business_name=data.get('business_name'),
            industry=data.get('industry'),
            description=data.get('description'),
            target_audience=data.get('target_audience')
        )
        if success:
            return jsonify({'message': 'Profile updated successfully'})
        return jsonify({'error': 'Failed to update profile'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update-preferences', methods=['POST'])
def api_update_preferences():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    # Note: This is a placeholder. In a real app, you'd save preferences to a user settings table
    try:
        # For now, just return success since preferences aren't stored
        return jsonify({'message': 'Preferences updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/view-website/<int:website_id>')
def view_website(website_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    website = db.get_website_by_id(website_id, session['user_id'])
    if not website:
        flash('Website not found or unauthorized')
        return redirect(url_for('profile'))
    
    return website['html_content']

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
    app.run(debug=True,port=5001)