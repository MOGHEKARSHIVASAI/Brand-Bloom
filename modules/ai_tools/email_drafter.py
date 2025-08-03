"""
A command-line tool to draft professional emails using the Google Gemini API.
"""
from datetime import datetime
import json
import os
from typing import Dict, Any

# Try importing Gemini AI with error handling
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    print("FATAL: google-generativeai is not installed. Please install it using: pip install google-generativeai")
    GEMINI_AVAILABLE = False

def configure_gemini_api() -> bool:
    """
    Configures the Gemini API with the key from environment variables.
    """
    if not GEMINI_AVAILABLE:
        return False
    
    api_key = 'AIzaSyDd3d3Dv5tVxXRieMDDo5ZHqacP9XPa0oU'
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set it using the appropriate command for your terminal.")
        return False
    
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        return False

def draft_email(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Drafts a professional email using the Gemini API based on user requirements.
    """
    if not configure_gemini_api():
        return {
            'status': 'error',
            'message': 'Gemini API is not available or configured correctly.',
            'generated_at': datetime.now().isoformat()
        }
    
    try:
        email_content = generate_ai_email(request_data)
        return {
            'status': 'success',
            'email': email_content,
            'generated_at': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"An error occurred during AI email generation: {str(e)}",
            'generated_at': datetime.now().isoformat()
        }

def generate_ai_email(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates personalized email content by calling the Gemini API.
    """
    prompt = create_email_prompt(request_data)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    generation_config = genai.types.GenerationConfig(
        temperature=0.7,
        max_output_tokens=1024,
        top_p=0.9,
        response_mime_type="application/json"
    )
    
    response = model.generate_content(prompt, generation_config=generation_config)
    
    if not response.text:
        raise Exception("Received an empty response from the Gemini API.")
    
    email_data = parse_ai_response(response.text)
    
    # Add metadata
    email_data.update({
        'type': request_data.get('email_type', 'general'),
        'tone': request_data.get('tone', 'professional'),
        'ai_generated': True,
        'model': 'gemini-1.5-flash'
    })
    
    return email_data

def create_email_prompt(data: Dict[str, Any]) -> str:
    """
    Creates a comprehensive and structured prompt for AI email generation.
    """
    recipient_display = data.get('recipient_name') or 'Valued Customer'
    
    prompt = f"""
You are an expert email writer. Your task is to generate a professional email based on the following details.
You must return your response *only* as a valid JSON object, without any surrounding text or markdown formatting.

**Email Details:**
- **Business Name:** {data.get('business_name', 'Your Business')}
- **Sender Name:** {data.get('sender_name', 'Team')}
- **Recipient Name:** {recipient_display}
- **Email Type:** {data.get('email_type', 'general')}
- **Purpose:** {data.get('purpose', 'Business communication')}
- **Desired Tone:** {data.get('tone', 'professional')}

**JSON Output Requirements:**
Please create a JSON object with the following keys:
- `subject`: A compelling and concise subject line (under 60 characters).
- `body`: The full email body text. Use \\n for new paragraphs.
- `signature`: A professional signature formatted as "Best regards,\\n{data.get('sender_name')}\\n{data.get('business_name')}".
- `key_points`: A JSON array of 2-3 main bullet points from the email.
- `call_to_action`: A clear, specific action for the recipient to take.
"""
    return prompt

def parse_ai_response(response_text: str) -> Dict[str, Any]:
    """
    Parses the JSON response from the AI and validates it.
    """
    try:
        email_data = json.loads(response_text)
        # 👇 **THIS IS THE FIX:** Call the helper function to process the data
        return validate_and_clean_email_data(email_data)
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed. Raw response: {response_text}")
        raise json.JSONDecodeError(f"Failed to decode AI response into JSON. Error: {e.msg}", e.doc, e.pos)

# 👇 **THIS IS THE FIX:** The missing function has been added back.
def validate_and_clean_email_data(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates required fields in the parsed email data and applies cleaning.
    """
    # Define required fields and their default values
    defaults = {
        'subject': 'Important Message',
        'body': 'Thank you for your interest.',
        'signature': 'Best regards,\n[Your Name]',
        'key_points': [],
        'call_to_action': 'Please contact us for more information.'
    }
    
    # Ensure all required fields exist, applying defaults if missing
    for field, default_value in defaults.items():
        if field not in email_data or not email_data[field]:
            email_data[field] = default_value
    
    # Clean string fields by replacing escaped newlines
    for field in ['body', 'signature']:
        if isinstance(email_data.get(field), str):
            email_data[field] = email_data[field].replace('\\n', '\n')
    
    # Ensure key_points is a list
    if not isinstance(email_data.get('key_points'), list):
        email_data['key_points'] = [str(email_data.get('key_points'))]
    
    # Construct the full, ready-to-send email string
    email_data['full_email'] = f"Subject: {email_data['subject']}\n\n{email_data['body']}\n\n{email_data['signature']}"
    
    return email_data

# --- Main Execution ---
if __name__ == "__main__":
    print("🔧 Initializing Gemini Email Drafter...")
    
    # Check for API key and quit if not found
    if not configure_gemini_api():
        print("\n❌ Exiting due to configuration error.")
        exit()
    
    # Define a sample request for testing
    test_request = {
        'email_type': 'marketing',
        'recipient_name': 'Dr. Evelyn Reed',
        'tone': 'friendly but professional',
        'purpose': 'Introduce our new AI-powered email drafting service',
        'business_name': 'Innovate AI',
        'sender_name': 'Alex Ray',
    }
    
    print(f"\n📧 Generating a '{test_request['email_type']}' email...")
    result = draft_email(test_request)
    
    print("-" * 50)
    if result['status'] == 'success':
        email = result['email']
        print("✅ Email generated successfully!\n")
        print(email.get('full_email', 'Full email content not available.'))
        
        print("\n--- Additional Data ---")
        print(f"Key Points: {email.get('key_points')}")
        print(f"Call to Action: {email.get('call_to_action')}")

    else:
        print(f"❌ Error during email generation.")
        print(f"Message: {result.get('message', 'An unknown error occurred.')}")
    print("=" * 50)