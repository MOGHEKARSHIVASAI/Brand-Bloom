from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import pandas as pd

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
# API endpoints for AI tools
@app.route('/api/generate-website', methods=['POST'])
def api_generate_website():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    print(f"Generating website for user {session['user_id']} with data: {data}")
    
    result = generate_website_content(data)
    
    # Store website in database
    if result.get('html') and result.get('metadata'):
        try:
            # Save initial website (with placeholder)
            website_id = db.save_website(
                session['user_id'],
                result['metadata']['title'],
                result['html'],  # Save original HTML first
                result['metadata']
            )
            
            if website_id:
                print(f"Website saved with ID: {website_id}")
                
                # Now replace ALL possible placeholders in the HTML
                html_content = result['html']
                
                # List of all possible placeholders to replace
                placeholders_to_replace = [
                    'WEBSITE_ID_PLACEHOLDER',
                    '{{WEBSITE_ID}}',
                    '{WEBSITE_ID}',
                    'PLACEHOLDER_WEBSITE_ID'
                ]
                
                # Replace all placeholders
                for placeholder in placeholders_to_replace:
                    if placeholder in html_content:
                        html_content = html_content.replace(placeholder, str(website_id))
                        print(f"Replaced placeholder '{placeholder}' with website ID {website_id}")
                
                # Also ensure we have the hidden input field if it's missing
                if 'id="websiteId"' not in html_content:
                    print("Adding missing websiteId hidden input field")
                    # Add it after the opening form tag
                    form_pattern = r'(<form[^>]*id="feedbackForm"[^>]*>)'
                    replacement = f'$1\n            <input type="hidden" id="websiteId" value="{website_id}">'
                    html_content = re.sub(form_pattern, replacement, html_content)
                
                # Verify the replacement worked
                if str(website_id) in html_content and 'id="websiteId"' in html_content:
                    print("✅ Website ID successfully embedded in HTML")
                    
                    # Update the website with the corrected HTML
                    success = db.update_website(website_id, session['user_id'], html_content=html_content)
                    if success:
                        print("✅ Database updated with corrected HTML")
                    else:
                        print("❌ Failed to update database with corrected HTML")
                else:
                    print("❌ Website ID replacement may have failed")
                    # Let's add some debug info
                    print(f"Looking for website ID '{website_id}' in HTML...")
                    if str(website_id) in html_content:
                        print("✅ Website ID found in HTML")
                    else:
                        print("❌ Website ID NOT found in HTML")
                    
                    if 'id="websiteId"' in html_content:
                        print("✅ websiteId field found in HTML")
                    else:
                        print("❌ websiteId field NOT found in HTML")
                
                result['website_id'] = website_id
                result['success'] = True
                result['html'] = html_content  # Return the updated HTML
                
            else:
                print("Failed to save website to database")
                result['error'] = 'Failed to save website to database'
                
        except Exception as e:
            print(f"Error saving website: {str(e)}")
            import traceback
            traceback.print_exc()
            result['error'] = f'Error saving website: {str(e)}'
    else:
        print("Missing html or metadata in result")
        print(f"HTML present: {'html' in result}")
        print(f"Metadata present: {'metadata' in result}")
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

# Add this route to your app.py file after the existing website route

@app.route('/website/id/<int:website_id>')
def serve_website_by_id(website_id):
    """Serve website content directly by ID"""
    website = db.get_website_by_id(website_id, None)  # Allow public access
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

# Feedback API endpoints
@app.route('/api/submit-feedback', methods=['POST'])
def api_submit_feedback():
    """Handle feedback submission from generated websites"""
    try:
        data = request.json
        print(f"Received feedback data: {data}")
        
        # Validate required fields
        required_fields = ['customer_name', 'customer_email', 'rating', 'feedback_text', 'website_id']
        for field in required_fields:
            if not data.get(field):
                print(f"Missing required field: {field}")
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate rating
        try:
            rating = int(data['rating'])
            if rating < 1 or rating > 5:
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid rating value'}), 400
        
        # Validate website_id
        try:
            website_id = int(data['website_id'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid website ID'}), 400
        
        # Verify website exists
        website = db.get_website_by_id(website_id)
        if not website:
            print(f"Website not found for ID: {website_id}")
            return jsonify({'error': 'Website not found'}), 404
        
        print(f"Website found: {website['title']} (ID: {website_id})")
        
        # Get additional data
        user_agent = request.headers.get('User-Agent')
        ip_address = request.remote_addr
        page_url = request.headers.get('Referer')
        
        # Save feedback
        feedback_id = db.save_feedback(
            website_id=website_id,
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            rating=rating,
            feedback_text=data['feedback_text'],
            page_url=page_url,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        if feedback_id:
            print(f"Feedback saved successfully with ID: {feedback_id}")
            
            # Analyze feedback immediately in the background
            try:
                analysis_result = analyze_feedback(data['feedback_text'])
                if analysis_result.get('status') == 'success':
                    # Store analysis in database
                    db.update_feedback_analysis(feedback_id, analysis_result['analysis'])
                    print(f"Feedback analysis completed for feedback ID: {feedback_id}")
            except Exception as e:
                print(f"Error analyzing feedback: {str(e)}")
                # Continue even if analysis fails
            
            return jsonify({'success': True, 'feedback_id': feedback_id})
        else:
            print("Failed to save feedback to database")
            return jsonify({'error': 'Failed to save feedback'}), 500
            
    except Exception as e:
        print(f"Error in feedback submission: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/get-website-feedback/<int:website_id>')
def api_get_website_feedback(website_id):
    """Get all feedback for a specific website"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    feedback_list = db.get_website_feedback(website_id, session['user_id'])
    return jsonify({
        'feedback': feedback_list,
        'total_count': len(feedback_list),
        'average_rating': sum(f['rating'] for f in feedback_list) / len(feedback_list) if feedback_list else 0
    })

@app.route('/api/get-all-feedback')
def api_get_all_feedback():
    """Get all feedback for user's websites"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    feedback_list = db.get_user_all_feedback(session['user_id'])
    return jsonify({
        'feedback': feedback_list,
        'total_count': len(feedback_list)
    })

@app.route('/api/analyze-stored-feedback/<int:feedback_id>')
def api_analyze_stored_feedback(feedback_id):
    """Analyze a specific stored feedback"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get feedback and verify ownership
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT f.*, w.user_id 
        FROM feedback f
        JOIN websites w ON f.website_id = w.id
        WHERE f.id = ? AND w.user_id = ?
    ''', (feedback_id, session['user_id']))
    
    feedback = cursor.fetchone()
    conn.close()
    
    if not feedback:
        return jsonify({'error': 'Feedback not found or unauthorized'}), 404
    
    feedback_dict = dict(feedback)
    
    # Analyze if not already analyzed
    if not feedback_dict['is_analyzed']:
        try:
            analysis_result = analyze_feedback(feedback_dict['feedback_text'])
            if analysis_result.get('status') == 'success':
                # Store analysis in database
                db.update_feedback_analysis(feedback_id, analysis_result['analysis'])
                return jsonify(analysis_result)
        except Exception as e:
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
    else:
        # Return existing analysis
        return jsonify({
            'status': 'success',
            'analysis': json.loads(feedback_dict['analysis_data']) if feedback_dict['analysis_data'] else {}
        })

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
    
# Complete Speech Integration for app.py
# Add these imports at the top of your existing app.py file

import os
import json
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response

# Import the enhanced speech processor (you'll need to create this file)
try:
    from enhanced_speech_processor import EnhancedSpeechProcessor
    SPEECH_PROCESSOR_AVAILABLE = True
except ImportError:
    print("⚠️ Enhanced Speech Processor not found. Speech features will be limited.")
    SPEECH_PROCESSOR_AVAILABLE = False

# Initialize the enhanced speech processor globally
enhanced_speech_processor = None

def initialize_speech_system():
    """Initialize the enhanced speech processing system"""
    global enhanced_speech_processor
    if enhanced_speech_processor is None and SPEECH_PROCESSOR_AVAILABLE:
        try:
            enhanced_speech_processor = EnhancedSpeechProcessor()
            print("✅ Enhanced Speech System initialized successfully!")
        except Exception as e:
            print(f"❌ Speech system initialization failed: {e}")
            enhanced_speech_processor = None
    return enhanced_speech_processor

# SPEECH API ENDPOINTS - Add these to your existing app.py

@app.route('/api/process-speech', methods=['POST'])
def api_process_speech():
    """Enhanced speech processing endpoint"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        transcript = data.get('transcript', '').strip()
        page = data.get('page', 'unknown')
        context = data.get('context', {})
        
        if not transcript:
            return jsonify({
                'success': False,
                'error': 'No transcript provided'
            }), 400
        
        # Add user context
        context.update({
            'user_id': session['user_id'],
            'user_email': session.get('user_email'),
            'timestamp': datetime.now().isoformat()
        })
        
        # Get or initialize speech processor
        processor = initialize_speech_system()
        
        if processor:
            # Process speech input with AI
            result = processor.process_speech_input(transcript, page, context)
        else:
            # Fallback to basic processing
            result = basic_speech_processing(transcript, page)
        
        # Log successful interactions
        if result.get('success'):
            print(f"Speech processed for user {session['user_id']}: '{transcript[:50]}...' -> {result['instructions']['action']}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Speech processing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Speech processing failed',
            'details': str(e) if app.debug else None
        }), 500

def basic_speech_processing(transcript, page):
    """Basic speech processing fallback when AI processor is not available"""
    transcript_lower = transcript.lower()
    
    # Basic navigation commands
    if any(nav in transcript_lower for nav in ['go to', 'open', 'show']):
        if 'website' in transcript_lower:
            return {
                'success': True,
                'instructions': {
                    'action': 'navigate',
                    'navigation': '/tools/website',
                    'message': 'Navigating to website builder...',
                    'confidence': 0.8
                }
            }
        elif 'email' in transcript_lower:
            return {
                'success': True,
                'instructions': {
                    'action': 'navigate',
                    'navigation': '/tools/email',
                    'message': 'Navigating to email composer...',
                    'confidence': 0.8
                }
            }
        elif 'feedback' in transcript_lower:
            return {
                'success': True,
                'instructions': {
                    'action': 'navigate',
                    'navigation': '/tools/feedback',
                    'message': 'Navigating to feedback analyzer...',
                    'confidence': 0.8
                }
            }
        elif 'poster' in transcript_lower:
            return {
                'success': True,
                'instructions': {
                    'action': 'navigate',
                    'navigation': '/tools/poster',
                    'message': 'Navigating to poster maker...',
                    'confidence': 0.8
                }
            }
        elif 'dashboard' in transcript_lower:
            return {
                'success': True,
                'instructions': {
                    'action': 'navigate',
                    'navigation': '/dashboard',
                    'message': 'Navigating to dashboard...',
                    'confidence': 0.8
                }
            }
    
    # Basic form filling
    fields = {}
    
    # Extract business name
    business_match = re.search(r'(?:for|called|named)\s+([^,.\n]+)', transcript, re.IGNORECASE)
    if business_match:
        fields['businessName'] = business_match.group(1).strip()
        fields['senderName'] = business_match.group(1).strip()
        fields['posterTitle'] = business_match.group(1).strip()
    
    # Website specific
    if 'website' in transcript_lower or page == 'website':
        if 'restaurant' in transcript_lower:
            fields['websiteType'] = 'restaurant'
        elif 'business' in transcript_lower:
            fields['websiteType'] = 'business'
        elif 'portfolio' in transcript_lower:
            fields['websiteType'] = 'portfolio'
    
    # Email specific
    if 'email' in transcript_lower or page == 'email':
        if 'marketing' in transcript_lower:
            fields['emailType'] = 'marketing'
        elif 'professional' in transcript_lower:
            fields['emailTone'] = 'professional'
        elif 'friendly' in transcript_lower:
            fields['emailTone'] = 'friendly'
    
    # Feedback specific
    if 'analyze' in transcript_lower and 'feedback' in transcript_lower:
        feedback_match = re.search(r'feedback[:\s]+(.+)', transcript, re.IGNORECASE)
        if feedback_match:
            fields['feedbackText'] = feedback_match.group(1).strip()
            return {
                'success': True,
                'instructions': {
                    'action': 'fill_form',
                    'fields': fields,
                    'tool_execution': {'tool': 'feedback', 'auto_submit': True},
                    'message': 'Analyzing feedback from speech...',
                    'confidence': 0.7
                }
            }
    
    # Return form filling result
    if fields:
        return {
            'success': True,
            'instructions': {
                'action': 'fill_form',
                'fields': fields,
                'message': f'Filled {len(fields)} field(s) from speech.',
                'confidence': 0.6
            }
        }
    
    # Default response
    return {
        'success': True,
        'instructions': {
            'action': 'fill_form',
            'fields': {},
            'message': 'Could not extract specific information from speech.',
            'confidence': 0.3
        }
    }

@app.route('/api/speech-capabilities', methods=['GET'])
def api_speech_capabilities():
    """Get speech processing capabilities and status"""
    processor = initialize_speech_system()
    
    status = {
        'initialized': processor is not None,
        'gemini_available': False,
        'fallback_available': True,
        'supported_languages': ['en-US', 'en-GB', 'hi-IN', 'te-IN']
    }
    
    if processor:
        status = processor.get_status()
    
    return jsonify({
        **status,
        'user_authenticated': 'user_id' in session,
        'supported_pages': ['website', 'email', 'feedback', 'poster', 'sales', 'dashboard'],
        'available_actions': ['fill_form', 'navigate', 'execute_tool', 'combination'],
        'keyboard_shortcuts': {
            'toggle_speech': 'Ctrl+Space',
            'cancel_speech': 'Escape',
            'show_help': 'Alt+H'
        }
    })

@app.route('/api/speech-test', methods=['POST'])
def api_speech_test():
    """Test speech processing with sample inputs (debug only)"""
    if not app.debug:
        return jsonify({'error': 'Test endpoint only available in debug mode'}), 404
    
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required for testing'}), 401
    
    try:
        data = request.get_json()
        test_cases = data.get('test_cases', [])
        
        # Default test cases if none provided
        if not test_cases:
            test_cases = [
                {'transcript': 'Create a website for my pizza restaurant called Tony\'s Place', 'page': 'website'},
                {'transcript': 'Generate a professional marketing email for new customers', 'page': 'email'},
                {'transcript': 'Analyze this feedback: great food but slow service', 'page': 'feedback'},
                {'transcript': 'Make a promotional poster for grand opening sale', 'page': 'poster'},
                {'transcript': 'Go to email composer', 'page': 'dashboard'},
                {'transcript': 'Fill business name with Tech Solutions Inc', 'page': 'website'}
            ]
        
        processor = initialize_speech_system()
        results = []
        
        for case in test_cases:
            if processor:
                result = processor.process_speech_input(
                    case['transcript'], 
                    case['page'], 
                    {'user_id': session['user_id'], 'test_mode': True}
                )
            else:
                result = basic_speech_processing(case['transcript'], case['page'])
            
            results.append({
                'input': case,
                'output': result,
                'success': result.get('success', False),
                'confidence': result.get('instructions', {}).get('confidence', 0.0),
                'action': result.get('instructions', {}).get('action', 'unknown'),
                'processed_by': result.get('processed_by', 'fallback')
            })
        
        # Calculate summary statistics
        successful = sum(1 for r in results if r['success'])
        avg_confidence = sum(r['confidence'] for r in results) / len(results) if results else 0
        ai_processed = sum(1 for r in results if r['processed_by'] == 'gemini')
        
        return jsonify({
            'success': True,
            'test_results': results,
            'summary': {
                'total_tests': len(results),
                'successful': successful,
                'failed': len(results) - successful,
                'success_rate': (successful / len(results)) * 100 if results else 0,
                'average_confidence': round(avg_confidence, 2),
                'ai_processed': ai_processed,
                'fallback_processed': len(results) - ai_processed
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/speech-analytics', methods=['POST'])
def api_speech_analytics():
    """Store speech usage analytics"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        # Create analytics record
        analytics_data = {
            'user_id': session['user_id'],
            'action': data.get('action'),
            'form_id': data.get('form_id'),
            'speech_data': data.get('speech_data', {}),
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'user_agent': request.headers.get('User-Agent'),
            'ip_address': request.remote_addr,
            'viewport': data.get('viewport', {}),
            'success': data.get('speech_data', {}).get('success', False),
            'confidence': data.get('speech_data', {}).get('confidence', 0.0)
        }
        
        # In a production app, you would save this to a database
        # For now, we'll just log it
        print(f"📊 Speech Analytics: User {analytics_data['user_id']} - {analytics_data['action']} - Success: {analytics_data['success']}")
        
        # You could save to database like this:
        # db.save_speech_analytics(analytics_data)
        
        return jsonify({'success': True, 'message': 'Analytics recorded'})
        
    except Exception as e:
        print(f"Analytics error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to record analytics'}), 500

@app.route('/api/speech-settings', methods=['GET', 'POST'])
def api_speech_settings():
    """Get or update user speech settings"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    processor = initialize_speech_system()
    
    if request.method == 'GET':
        # Return current settings
        settings = {
            'language': 'en-US',
            'confidence_threshold': 0.7,
            'auto_submit': True,
            'notifications': True,
            'keyboard_shortcuts': True,
            'supported_languages': ['en-US', 'en-GB', 'hi-IN', 'te-IN']
        }
        
        if processor:
            settings['supported_languages'] = processor.get_supported_languages()
            settings['current_status'] = processor.get_status()
        
        return jsonify(settings)
    
    else:  # POST - Update settings
        try:
            settings = request.get_json()
            
            # Validate settings
            if 'confidence_threshold' in settings:
                threshold = float(settings['confidence_threshold'])
                if not (0.1 <= threshold <= 1.0):
                    return jsonify({'error': 'Confidence threshold must be between 0.1 and 1.0'}), 400
                
                if processor:
                    processor.set_confidence_threshold(threshold)
            
            if 'language' in settings:
                supported_languages = ['en-US', 'en-GB', 'hi-IN', 'te-IN']
                if processor:
                    supported_languages = processor.get_supported_languages()
                
                if settings['language'] not in supported_languages:
                    return jsonify({'error': 'Unsupported language'}), 400
            
            # In production, save settings to database
            # db.update_user_speech_settings(session['user_id'], settings)
            
            print(f"🎤 Speech settings updated for user {session['user_id']}: {settings}")
            
            return jsonify({
                'success': True, 
                'message': 'Settings updated successfully',
                'updated_settings': settings
            })
            
        except Exception as e:
            return jsonify({'error': f'Failed to update settings: {str(e)}'}), 500

# ENHANCED API ENDPOINTS WITH SPEECH SUPPORT

@app.route('/api/generate-website-speech', methods=['POST'])
def api_generate_website_speech():
    """Enhanced website generation with speech metadata support"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        speech_metadata = data.get('speech_metadata', {})
        
        # Log speech-generated requests
        if speech_metadata.get('fromSpeech'):
            print(f"🎤 Website generation via speech: '{speech_metadata.get('originalTranscript', '')[:50]}...'")
        
        # Use existing website generation logic
        result = generate_website_content(data)
        
        # Add speech metadata to result
        if speech_metadata:
            result['speech_metadata'] = speech_metadata
            if 'metadata' not in result:
                result['metadata'] = {}
            result['metadata']['generated_via'] = 'speech'
            result['metadata']['original_transcript'] = speech_metadata.get('originalTranscript')
            result['metadata']['speech_confidence'] = speech_metadata.get('confidence', 0.0)
        
        # Save website as usual but with speech metadata
        if result.get('html') and result.get('metadata'):
            try:
                website_id = db.save_website(
                    session['user_id'],
                    result['metadata']['title'],
                    result['html'],
                    result['metadata']
                )
                
                if website_id:
                    # Update HTML with website ID (existing logic)
                    html_content = result['html']
                    placeholders = ['WEBSITE_ID_PLACEHOLDER', '{{WEBSITE_ID}}', '{WEBSITE_ID}']
                    
                    for placeholder in placeholders:
                        html_content = html_content.replace(placeholder, str(website_id))
                    
                    # Ensure websiteId field exists
                    if 'id="websiteId"' not in html_content:
                        form_pattern = r'(<form[^>]*id="feedbackForm"[^>]*>)'
                        replacement = f'$1\n            <input type="hidden" id="websiteId" value="{website_id}">'
                        html_content = re.sub(form_pattern, replacement, html_content)
                    
                    # Update database
                    db.update_website(website_id, session['user_id'], html_content=html_content)
                    
                    result['website_id'] = website_id
                    result['success'] = True
                    result['html'] = html_content
                    
                    # Add speech-specific success message
                    if speech_metadata.get('fromSpeech'):
                        result['speech_success'] = True
                        result['speech_message'] = f"Website created from speech: '{speech_metadata.get('originalTranscript', '')[:50]}...'"
                else:
                    result['error'] = 'Failed to save website'
                    
            except Exception as e:
                print(f"Error saving speech-generated website: {str(e)}")
                result['error'] = f'Error saving website: {str(e)}'
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in speech website generation: {str(e)}")
        return jsonify({'error': f'Website generation failed: {str(e)}'}), 500

@app.route('/api/analyze-feedback-speech', methods=['POST'])
def api_analyze_feedback_speech():
    """Enhanced feedback analysis with speech support"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        feedback_text = data.get('feedback')
        speech_metadata = data.get('speech_metadata', {})
        
        if not feedback_text:
            return jsonify({'error': 'No feedback text provided'}), 400
        
        # Log speech-submitted feedback
        if speech_metadata.get('fromSpeech'):
            print(f"🎤 Feedback analysis via speech: '{speech_metadata.get('originalTranscript', '')[:50]}...'")
        
        # Use existing feedback analysis
        result = analyze_feedback(feedback_text)
        
        # Add speech metadata
        if speech_metadata and result.get('status') == 'success':
            result['speech_metadata'] = speech_metadata
            result['analysis']['input_method'] = 'speech'
            result['analysis']['original_transcript'] = speech_metadata.get('originalTranscript')
            result['speech_message'] = f"Analyzed from speech: '{speech_metadata.get('originalTranscript', '')[:50]}...'"
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in speech feedback analysis: {str(e)}")
        return jsonify({'error': f'Feedback analysis failed: {str(e)}'}), 500

@app.route('/api/draft-email-speech', methods=['POST'])
def api_draft_email_speech():
    """Enhanced email drafting with speech support"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        speech_metadata = data.get('speech_metadata', {})
        
        # Log speech-generated emails
        if speech_metadata.get('fromSpeech'):
            print(f"🎤 Email drafting via speech: '{speech_metadata.get('originalTranscript', '')[:50]}...'")
        
        # Use existing email drafting
        result = draft_email(data)
        
        # Add speech metadata
        if speech_metadata and result.get('status') == 'success':
            result['speech_metadata'] = speech_metadata
            result['email']['input_method'] = 'speech'
            result['email']['original_transcript'] = speech_metadata.get('originalTranscript')
            result['speech_message'] = f"Email drafted from speech: '{speech_metadata.get('originalTranscript', '')[:50]}...'"
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in speech email drafting: {str(e)}")
        return jsonify({'error': f'Email drafting failed: {str(e)}'}), 500

@app.route('/api/create-poster-speech', methods=['POST'])
def api_create_poster_speech():
    """Enhanced poster creation with speech support"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        speech_metadata = data.get('speech_metadata', {})
        
        # Log speech-generated posters
        if speech_metadata.get('fromSpeech'):
            print(f"🎤 Poster creation via speech: '{speech_metadata.get('originalTranscript', '')[:50]}...'")
        
        # Use existing poster creation
        result = create_poster_content(data)
        
        # Add speech metadata
        if speech_metadata and result.get('status') == 'success':
            result['speech_metadata'] = speech_metadata
            result['poster']['input_method'] = 'speech'
            result['poster']['original_transcript'] = speech_metadata.get('originalTranscript')
            result['speech_message'] = f"Poster created from speech: '{speech_metadata.get('originalTranscript', '')[:50]}...'"
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in speech poster creation: {str(e)}")
        return jsonify({'error': f'Poster creation failed: {str(e)}'}), 500

# APP INITIALIZATION AND CONTEXT PROCESSORS

def initialize_app():
    """Initialize app components including speech system"""
    print("🚀 Initializing Brand Bloom application...")
    
    # Initialize database (existing)
    init_db()
    
    # Initialize enhanced speech system
    try:
        initialize_speech_system()
        print("✅ Speech system ready")
    except Exception as e:
        print(f"⚠️ Speech system initialization failed: {e}")
    
    print("🎉 Brand Bloom is ready!")

@app.context_processor
def inject_speech_status():
    """Inject speech system status into all templates"""
    speech_available = False
    speech_status = {}
    
    if 'user_id' in session:
        try:
            processor = initialize_speech_system()
            if processor:
                speech_status = processor.get_status()
                speech_available = speech_status.get('initialized', False)
            else:
                speech_status = {'initialized': False, 'fallback_available': True}
                speech_available = True  # Basic speech still available
        except:
            pass
    
    return {
        'speech_available': speech_available,
        'speech_status': speech_status
    }

# ENHANCED ERROR HANDLERS

@app.errorhandler(500)
def internal_error(error):
    """Enhanced error handler that considers speech context"""
    # Check if error occurred during speech processing
    is_speech_request = request.path.startswith('/api/') and 'speech' in request.path
    
    if is_speech_request:
        return jsonify({
            'success': False,
            'error': 'Speech processing temporarily unavailable',
            'fallback_available': True,
            'message': 'Please try typing your request or use the manual form controls.'
        }), 500
    
    # Regular error handling for non-speech requests
    try:
        return render_template('error.html', error=error), 500
    except:
        return f"Internal Server Error: {error}", 500

# MIDDLEWARE AND LOGGING

@app.before_request
def log_speech_requests():
    """Log speech-related requests for monitoring"""
    if request.path.startswith('/api/') and 'speech' in request.path:
        user_id = session.get('user_id', 'anonymous')
        print(f"🎤 Speech API Request: {request.method} {request.path} - User: {user_id}")

# DEVELOPMENT AND DEBUG ROUTES

if app.config.get('DEBUG', False):
    @app.route('/debug/speech-status')
    def debug_speech_status():
        """Debug endpoint to check speech system status"""
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        try:
            processor = initialize_speech_system()
            
            status_info = {
                'speech_processor_available': processor is not None,
                'basic_fallback_available': True,
                'session_info': {
                    'user_id': session.get('user_id'),
                    'user_email': session.get('user_email')
                },
                'request_info': {
                    'user_agent': request.headers.get('User-Agent'),
                    'accept_language': request.headers.get('Accept-Language'),
                    'remote_addr': request.remote_addr
                },
                'app_config': {
                    'debug': app.debug,
                    'testing': app.testing
                }
            }
            
            if processor:
                status_info['processor_status'] = processor.get_status()
            
            return jsonify(status_info)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# TEMPLATE HELPERS

def render_speech_template(template_name, **context):
    """Enhanced template renderer that adds speech context"""
    if 'user_id' in session:
        try:
            processor = initialize_speech_system()
            if processor:
                context['speech_capabilities'] = processor.get_status()
            context['speech_enabled'] = True
        except:
            context['speech_enabled'] = False
    else:
        context['speech_enabled'] = False
    
    return render_template(template_name, **context)

# UPDATE EXISTING ROUTE HANDLERS TO USE SPEECH-ENABLED TEMPLATES
# Replace your existing tool routes with these:

@app.route('/tools/website')
def website_tool():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_speech_template('tools/website.html')

@app.route('/tools/email')  
def email_tool():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_speech_template('tools/email.html')

@app.route('/tools/feedback')
def feedback_tool():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    all_feedback = db.get_user_all_feedback(session['user_id'])
    return render_speech_template('tools/feedback.html', feedback_list=all_feedback)

@app.route('/tools/poster')
def poster_tool():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_speech_template('tools/poster.html')

@app.route('/tools/sales')
def sales_tool():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_speech_template('tools/sales.html')

# ENHANCED DASHBOARD WITH SPEECH ANALYTICS

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_with_business = db.get_user_with_business(session['user_id'])
    business_info = user_with_business.get('business') if user_with_business else None
    
    # Get feedback statistics
    feedback_stats = db.get_feedback_stats(session['user_id'])
    
    # Add speech usage statistics (placeholder for now)
    speech_stats = {
        'total_interactions': 0,
        'successful_commands': 0,
        'most_used_tools': [],
        'recent_activity': []
    }
    
    return render_speech_template('dashboard.html', 
                                business=business_info, 
                                feedback_stats=feedback_stats,
                                speech_stats=speech_stats)

# SERVE SPEECH CONTROLLER JAVASCRIPT

@app.route('/static/js/enhanced-speech-controller.js')
def speech_controller_js():
    """Serve the enhanced speech controller JavaScript"""
    js_content = """
// Enhanced Speech Controller - Basic Implementation
console.log('🎤 Enhanced Speech Controller loaded');

// This would normally load the full Enhanced Speech Controller
// For now, providing a basic implementation

class BasicSpeechController {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.init();
    }
    
    init() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.processTranscript(transcript);
            };
            
            console.log('🎤 Basic Speech Recognition initialized');
        }
    }
    
    async processTranscript(transcript) {
        console.log('Processing transcript:', transcript);
        
        try {
            const response = await fetch('/api/process-speech', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    transcript: transcript,
                    page: this.getCurrentPage()
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.executeInstructions(result.instructions);
            }
        } catch (error) {
            console.error('Speech processing error:', error);
        }
    }
    
    getCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('/tools/website')) return 'website';
        if (path.includes('/tools/email')) return 'email';
        if (path.includes('/tools/feedback')) return 'feedback';
        if (path.includes('/tools/poster')) return 'poster';
        if (path.includes('/tools/sales')) return 'sales';
        if (path === '/' || path.includes('dashboard')) return 'dashboard';
        return 'unknown';
    }
    
    executeInstructions(instructions) {
        console.log('Executing instructions:', instructions);
        
        switch (instructions.action) {
            case 'navigate':
                if (instructions.navigation) {
                    window.location.href = instructions.navigation;
                }
                break;
                
            case 'fill_form':
                this.fillForm(instructions.fields);
                break;
        }
        
        if (instructions.message) {
            this.showNotification(instructions.message);
        }
    }
    
    fillForm(fields) {
        for (const [fieldId, value] of Object.entries(fields)) {
            const field = document.getElementById(fieldId);
            if (field) {
                if (field.tagName === 'SELECT') {
                    // Find matching option
                    const options = Array.from(field.options);
                    const match = options.find(opt => 
                        opt.value.toLowerCase().includes(value.toLowerCase()) ||
                        opt.text.toLowerCase().includes(value.toLowerCase())
                    );
                    if (match) {
                        field.value = match.value;
                    }
                } else {
                    field.value = value;
                }
                
                // Trigger change event
                field.dispatchEvent(new Event('input', { bubbles: true }));
                field.dispatchEvent(new Event('change', { bubbles: true }));
                
                // Visual feedback
                field.style.backgroundColor = '#e8f5e9';
                setTimeout(() => {
                    field.style.backgroundColor = '';
                }, 2000);
            }
        }
    }
    
    showNotification(message) {
        // Create notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4caf50;
            color: white;
            padding: 16px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            font-weight: 500;
            max-width: 300px;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 4000);
    }
    
    startListening() {
        if (this.recognition && !this.isListening) {
            this.recognition.start();
            this.isListening = true;
        }
    }
}

// Initialize speech controller when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (window.speechConfig) {
        window.basicSpeechController = new BasicSpeechController();
        
        // Add keyboard shortcut
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.code === 'Space') {
                e.preventDefault();
                window.basicSpeechController.startListening();
            }
        });
        
        console.log('🎤 Speech controller initialized with config:', window.speechConfig);
    }
});
"""
    
    return Response(js_content, mimetype='application/javascript')

# TEMPLATE FILTERS

@app.template_filter('speech_status')
def speech_status_filter(status_obj):
    """Template filter to format speech status for display"""
    if not status_obj:
        return "Unavailable"
    
    if status_obj.get('initialized') and status_obj.get('gemini_available'):
        return "AI-Powered"
    elif status_obj.get('initialized'):
        return "Basic Mode"
    else:
        return "Offline"

@app.template_filter('speech_confidence')
def speech_confidence_filter(confidence):
    """Template filter to format confidence scores"""
    if confidence is None:
        return "N/A"
    
    try:
        confidence = float(confidence)
        if confidence >= 0.9:
            return f"Excellent ({confidence:.0%})"
        elif confidence >= 0.7:
            return f"Good ({confidence:.0%})"
        elif confidence >= 0.5:
            return f"Fair ({confidence:.0%})"
        else:
            return f"Poor ({confidence:.0%})"
    except:
        return "N/A"

# CLI COMMANDS FOR SPEECH SYSTEM MANAGEMENT

@app.cli.command()
def init_speech():
    """Initialize the speech processing system"""
    print("Initializing speech processing system...")
    try:
        processor = initialize_speech_system()
        
        if processor:
            status = processor.get_status()
            print(f"✅ Speech system initialized")
            print(f"   Gemini AI: {'Available' if status.get('gemini_available') else 'Unavailable'}")
            print(f"   Fallback: {'Available' if status.get('fallback_available') else 'Unavailable'}")
            print(f"   Languages: {', '.join(status.get('supported_languages', []))}")
        else:
            print(f"✅ Basic speech system initialized")
            print(f"   Gemini AI: Unavailable")
            print(f"   Fallback: Available")
            print(f"   Languages: en-US, en-GB, hi-IN, te-IN")
        
    except Exception as e:
        print(f"❌ Failed to initialize speech system: {e}")

@app.cli.command()
def test_speech():
    """Test speech processing with sample inputs"""
    print("Testing speech processing system...")
    
    try:
        processor = initialize_speech_system()
        
        test_cases = [
            {'transcript': 'Create a website for my restaurant', 'page': 'website'},
            {'transcript': 'Generate marketing email', 'page': 'email'},
            {'transcript': 'Analyze feedback about slow service', 'page': 'feedback'},
        ]
        
        results = []
        for case in test_cases:
            if processor:
                result = processor.test_processing([case])
                results.extend(result)
            else:
                result = basic_speech_processing(case['transcript'], case['page'])
                results.append({
                    'input': case,
                    'output': result,
                    'success': result.get('success', False),
                    'confidence': result.get('instructions', {}).get('confidence', 0.0)
                })
        
        print(f"\nTest Results:")
        print(f"Total tests: {len(results)}")
        print(f"Successful: {sum(1 for r in results if r['success'])}")
        if results:
            avg_confidence = sum(r['confidence'] for r in results) / len(results)
            print(f"Average confidence: {avg_confidence:.2f}")
        
        for i, result in enumerate(results, 1):
            status = "✅" if result['success'] else "❌"
            transcript = result['input']['transcript'][:30]
            action = result['output']['instructions'].get('action', 'unknown')
            print(f"{status} Test {i}: {transcript}... -> {action}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

# ADD TO YOUR EXISTING APP INITIALIZATION

# Add this to the end of your app.py file, BEFORE if __name__ == '__main__':

# Initialize speech system on app startup
initialize_speech_system()

print("🎤 Enhanced Speech System Integration Complete!")
print("=" * 60)
print("✅ Speech API endpoints added")
print("✅ Enhanced form processing")
print("✅ Debug tools available")
print("✅ Analytics tracking ready")
print("✅ Multi-language support")
print("")
print("🎤 Available Speech Commands:")
print("   • 'Create website for [business name]'")
print("   • 'Generate [type] email for [recipients]'") 
print("   • 'Analyze this feedback: [text]'")
print("   • 'Make poster for [event]'")
print("   • 'Go to [tool name]'")
print("")
print("🔧 Debug Endpoints (when DEBUG=True):")
print("   • GET  /debug/speech-status")
print("   • POST /api/speech-test")
print("")
print("🌐 API Endpoints:")
print("   • POST /api/process-speech")
print("   • GET  /api/speech-capabilities")
print("   • POST /api/speech-analytics")
print("   • GET/POST /api/speech-settings")
print("")
print("💡 Press Ctrl+Space to activate speech control")
print("   (Available on all authenticated pages)")
print("=" * 60)

# STARTUP INSTRUCTIONS FOR USERS

"""
INSTALLATION INSTRUCTIONS:
==========================

1. Add this code to your existing app.py file (merge with your existing code)

2. Create the enhanced_speech_processor.py file with the content from the previous artifact

3. Update your base.html template with the enhanced version provided

4. Your existing routes will automatically get speech support!

5. Test the system:
   - Visit /debug/speech-status to check system health
   - Use Ctrl+Space to activate speech on any page
   - Try commands like "Create website for my restaurant"

6. Optional: Add the Enhanced Speech Controller JavaScript file to /static/js/

The system will work with basic speech recognition even without the Gemini AI processor!
"""

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

# Add these imports to your existing app.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import tempfile
import os

# Email configuration (add these to your app.py)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "assetmanager1910@gmail.com")  # Set your email
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "dhyi ybud ibgw lgsp")  # Set your app password

def send_email(receiver_email, subject, body, receiver_name=None):
    """Simple function to send email"""
    # Personalize the email
    if receiver_name:
        body = body.replace('[Recipient Name]', receiver_name)
        body = body.replace('Dear [Recipient Name]', f'Dear {receiver_name}')
        body = body.replace('Hi [Recipient Name]', f'Hi {receiver_name}')
    else:
        body = body.replace('[Recipient Name]', 'Valued Customer')
        body = body.replace('Dear [Recipient Name]', 'Dear Valued Customer')
        body = body.replace('Hi [Recipient Name]', 'Hi there')
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email to {receiver_email}: {e}")
        return False

def send_bulk_emails_from_csv(csv_file, subject, body):
    """Send emails to multiple recipients from CSV file"""
    successful_emails = 0
    failed_emails = 0
    errors = []
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        for index, row in df.iterrows():
            # Get email and name from CSV (flexible column names)
            email = None
            name = None
            
            # Try different column name variations
            for col in df.columns:
                col_lower = col.lower().strip()
                if 'email' in col_lower and not email:
                    email = row[col]
                elif 'name' in col_lower and not name:
                    name = row[col]
            
            if email and pd.notna(email):
                if send_email(email, subject, body, name):
                    successful_emails += 1
                else:
                    failed_emails += 1
                    errors.append(f"Failed to send to {email}")
            else:
                failed_emails += 1
                errors.append(f"Row {index + 1}: Missing or invalid email")
    
    except Exception as e:
        errors.append(f"CSV processing error: {str(e)}")
    
    return {
        'successful': successful_emails,
        'failed': failed_emails,
        'errors': errors
    }

# Add these routes to your existing app.py

@app.route('/api/send-email', methods=['POST'])
def api_send_email():
    """Send single email"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        
        # Get email data
        recipient_email = data.get('email')
        recipient_name = data.get('name', '')
        subject = data.get('subject', '')
        body = data.get('body', '')
        
        if not recipient_email or not subject or not body:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Send email
        success = send_email(recipient_email, subject, body, recipient_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Email sent successfully to {recipient_email}'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to send email to {recipient_email}'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/send-bulk-emails', methods=['POST'])
def api_send_bulk_emails():
    """Send bulk emails from CSV file"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Check if file was uploaded
        if 'csv_file' not in request.files:
            return jsonify({'error': 'No CSV file uploaded'}), 400
        
        csv_file = request.files['csv_file']
        subject = request.form.get('subject', '')
        body = request.form.get('body', '')
        
        if csv_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not subject or not body:
            return jsonify({'error': 'Missing subject or body'}), 400
        
        # Save file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        csv_file.save(temp_file.name)
        
        try:
            # Send bulk emails
            result = send_bulk_emails_from_csv(temp_file.name, subject, body)
            
            return jsonify({
                'success': True,
                'message': f'Sent {result["successful"]} emails successfully. {result["failed"]} failed.',
                'successful': result['successful'],
                'failed': result['failed'],
                'errors': result['errors']
            })
        
        finally:
            # Clean up temp file
            os.unlink(temp_file.name)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
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
    app.run(debug=True,port=5003)

