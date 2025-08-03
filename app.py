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
    
    # Get feedback statistics
    feedback_stats = db.get_feedback_stats(session['user_id'])
    
    return render_template('dashboard.html', business=business_info, feedback_stats=feedback_stats)

@app.route('/tools/website')
def website_tool():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('tools/website.html')

@app.route('/tools/feedback')
def feedback_tool():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get all feedback for user's websites
    all_feedback = db.get_user_all_feedback(session['user_id'])
    
    return render_template('tools/feedback.html', feedback_list=all_feedback)



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
    
# Add these imports and routes to your app.py file

# Additional imports for speech processing
import re
import json
from speech_processor import SpeechProcessor

# Initialize speech processor
speech_processor = SpeechProcessor()

# Add these routes to your app.py file

@app.route('/api/process-speech', methods=['POST'])
def api_process_speech():
    """Process speech input with Gemini AI and return form instructions"""
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
                'error': 'No speech transcript provided'
            }), 400
        
        # Add user context
        user_context = {
            'user_id': session['user_id'],
            'user_email': session.get('user_email'),
            'timestamp': datetime.now().isoformat()
        }
        context.update(user_context)
        
        # Process with speech processor
        result = speech_processor.process_speech_input(transcript, page, context)
        
        # Log speech interaction
        print(f"Speech processed for user {session['user_id']}: '{transcript}' on {page}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Speech processing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Speech processing failed: {str(e)}'
        }), 500

@app.route('/api/speech-capabilities', methods=['GET'])
def api_speech_capabilities():
    """Return available speech processing capabilities"""
    return jsonify({
        'gemini_available': speech_processor.model is not None,
        'supported_pages': ['website', 'email', 'feedback', 'poster', 'sales', 'dashboard'],
        'supported_actions': ['fill_form', 'navigate', 'execute_tool', 'combination'],
        'fallback_available': True,
        'browser_support': {
            'chrome': True,
            'firefox': True,
            'safari': True,
            'edge': True
        }
    })

@app.route('/api/speech-test', methods=['POST'])
def api_speech_test():
    """Test endpoint for speech processing (development only)"""
    if app.debug:  # Only available in debug mode
        try:
            data = request.get_json()
            transcript = data.get('transcript', '')
            page = data.get('page', 'website')
            
            result = speech_processor.process_speech_input(transcript, page)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    else:
        return jsonify({'error': 'Not available in production'}), 404

# Enhanced website generation with speech metadata
@app.route('/api/generate-website-speech', methods=['POST'])
def api_generate_website_speech():
    """Generate website with speech input processing"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        
        # Check if this came from speech input
        speech_metadata = data.get('speech_metadata', {})
        
        # Log speech-generated websites
        if speech_metadata.get('from_speech'):
            print(f"Website generated via speech: '{speech_metadata.get('original_transcript')}'")
        
        # Use existing website generation logic
        result = generate_website_content(data)
        
        # Add speech metadata to result
        if speech_metadata:
            result['speech_metadata'] = speech_metadata
            result['metadata']['generated_via'] = 'speech'
            result['metadata']['original_transcript'] = speech_metadata.get('original_transcript')
        
        # Store website with speech info
        if result.get('html') and result.get('metadata'):
            try:
                # Save website with speech metadata
                website_id = db.save_website(
                    session['user_id'],
                    result['metadata']['title'],
                    result['html'],
                    result['metadata']
                )
                
                if website_id:
                    # Fix website ID in HTML (same as original logic)
                    html_content = result['html']
                    placeholders_to_replace = [
                        'WEBSITE_ID_PLACEHOLDER',
                        '{{WEBSITE_ID}}',
                        '{WEBSITE_ID}',
                        'PLACEHOLDER_WEBSITE_ID'
                    ]
                    
                    for placeholder in placeholders_to_replace:
                        if placeholder in html_content:
                            html_content = html_content.replace(placeholder, str(website_id))
                    
                    # Ensure websiteId field exists
                    if 'id="websiteId"' not in html_content:
                        import re
                        form_pattern = r'(<form[^>]*id="feedbackForm"[^>]*>)'
                        replacement = f'$1\n            <input type="hidden" id="websiteId" value="{website_id}">'
                        html_content = re.sub(form_pattern, replacement, html_content)
                    
                    # Update website with corrected HTML
                    db.update_website(website_id, session['user_id'], html_content=html_content)
                    
                    result['website_id'] = website_id
                    result['success'] = True
                    result['html'] = html_content
                    
                    # If generated via speech, show special success message
                    if speech_metadata.get('from_speech'):
                        result['speech_success'] = True
                        result['speech_message'] = f"Website successfully created from your voice command: '{speech_metadata.get('original_transcript')}'"
                else:
                    result['error'] = 'Failed to save website to database'
                    
            except Exception as e:
                print(f"Error saving speech-generated website: {str(e)}")
                result['error'] = f'Error saving website: {str(e)}'
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in speech website generation: {str(e)}")
        return jsonify({'error': f'Website generation failed: {str(e)}'}), 500

# Enhanced feedback processing for speech
@app.route('/api/analyze-feedback-speech', methods=['POST'])
def api_analyze_feedback_speech():
    """Analyze feedback with speech input processing"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        feedback_text = data.get('feedback')
        speech_metadata = data.get('speech_metadata', {})
        
        if not feedback_text:
            return jsonify({'error': 'No feedback text provided'}), 400
        
        # Log speech-submitted feedback
        if speech_metadata.get('from_speech'):
            print(f"Feedback analyzed via speech: '{speech_metadata.get('original_transcript')}'")
        
        # Use existing feedback analysis
        result = analyze_feedback(feedback_text)
        
        # Add speech metadata
        if speech_metadata and result.get('status') == 'success':
            result['speech_metadata'] = speech_metadata
            result['analysis']['input_method'] = 'speech'
            result['analysis']['original_transcript'] = speech_metadata.get('original_transcript')
            result['speech_message'] = f"Feedback analyzed from your voice input: '{speech_metadata.get('original_transcript')}'"
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in speech feedback analysis: {str(e)}")
        return jsonify({'error': f'Feedback analysis failed: {str(e)}'}), 500

# Enhanced email generation for speech
@app.route('/api/draft-email-speech', methods=['POST'])
def api_draft_email_speech():
    """Draft email with speech input processing"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        speech_metadata = data.get('speech_metadata', {})
        
        # Log speech-generated emails
        if speech_metadata.get('from_speech'):
            print(f"Email drafted via speech: '{speech_metadata.get('original_transcript')}'")
        
        # Use existing email drafting
        result = draft_email(data)
        
        # Add speech metadata
        if speech_metadata and result.get('status') == 'success':
            result['speech_metadata'] = speech_metadata
            result['email']['input_method'] = 'speech'
            result['email']['original_transcript'] = speech_metadata.get('original_transcript')
            result['speech_message'] = f"Email drafted from your voice command: '{speech_metadata.get('original_transcript')}'"
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in speech email drafting: {str(e)}")
        return jsonify({'error': f'Email drafting failed: {str(e)}'}), 500

# Enhanced poster creation for speech
@app.route('/api/create-poster-speech', methods=['POST'])
def api_create_poster_speech():
    """Create poster with speech input processing"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        speech_metadata = data.get('speech_metadata', {})
        
        # Log speech-generated posters
        if speech_metadata.get('from_speech'):
            print(f"Poster created via speech: '{speech_metadata.get('original_transcript')}'")
        
        # Use existing poster creation
        result = create_poster_content(data)
        
        # Add speech metadata
        if speech_metadata and result.get('status') == 'success':
            result['speech_metadata'] = speech_metadata
            result['poster']['input_method'] = 'speech'
            result['poster']['original_transcript'] = speech_metadata.get('original_transcript')
            result['speech_message'] = f"Poster created from your voice command: '{speech_metadata.get('original_transcript')}'"
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in speech poster creation: {str(e)}")
        return jsonify({'error': f'Poster creation failed: {str(e)}'}), 500

# Speech analytics endpoint
@app.route('/api/speech-analytics', methods=['GET'])
def api_speech_analytics():
    """Get speech usage analytics for the user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # This would ideally come from a speech_logs table in the database
        # For now, return mock analytics
        analytics = {
            'total_speech_interactions': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'most_used_tools': [],
            'success_rate': 0.0,
            'recent_interactions': []
        }
        
        return jsonify(analytics)
        
    except Exception as e:
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

@app.route('/tools/email')
def email_tool():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('tools/email.html')


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
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "assetmanger1910@gmail.com")  # Set your email
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

