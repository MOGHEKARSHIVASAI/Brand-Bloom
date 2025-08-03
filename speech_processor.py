# speech_processor.py - Gemini AI Speech Processing Module

import os
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class SpeechProcessor:
    def __init__(self):
        self.model = None
        self.initialize_gemini()
        
    def initialize_gemini(self):
        """Initialize Gemini AI with API key"""
        if not GEMINI_AVAILABLE:
            print("Warning: Gemini AI not available. Using fallback processing.")
            return
            
        api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyDd3d3Dv5tVxXRieMDDo5ZHqacP9XPa0oU')
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("Gemini AI initialized successfully")
            except Exception as e:
                print(f"Failed to initialize Gemini AI: {e}")
                self.model = None
        else:
            print("No Gemini API key found")

    def process_speech_input(self, transcript: str, page: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process speech input using Gemini AI and return structured instructions
        """
        try:
            if self.model:
                return self.process_with_gemini(transcript, page, context)
            else:
                return self.fallback_processing(transcript, page)
        except Exception as e:
            print(f"Error processing speech: {e}")
            return self.fallback_processing(transcript, page)
    
    def process_with_gemini(self, transcript: str, page: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process speech using Gemini AI"""
        prompt = self.build_processing_prompt(transcript, page, context)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1024,
                    top_p=0.8,
                    response_mime_type="application/json"
                )
            )
            
            if response.text:
                instructions = json.loads(response.text)
                return {
                    'success': True,
                    'instructions': instructions,
                    'processed_by': 'gemini',
                    'transcript': transcript
                }
            else:
                raise Exception("Empty response from Gemini")
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return self.fallback_processing(transcript, page)
        except Exception as e:
            print(f"Gemini processing error: {e}")
            return self.fallback_processing(transcript, page)

    def build_processing_prompt(self, transcript: str, page: str, context: Dict[str, Any] = None) -> str:
        """Build comprehensive prompt for Gemini AI"""
        
        page_contexts = {
            'website': {
                'form_fields': {
                    'websiteType': ['business', 'portfolio', 'ecommerce', 'blog', 'restaurant', 'services'],
                    'businessName': 'text',
                    'businessDescription': 'text',
                    'keyServices': 'text',
                    'targetAudience': 'text',
                    'colorScheme': ['professional', 'modern', 'warm', 'nature', 'creative']
                },
                'examples': [
                    '"Create a website for my restaurant called Pizza Palace" -> {"action": "fill_form", "fields": {"websiteType": "restaurant", "businessName": "Pizza Palace"}}',
                    '"Make a professional business site for consulting services" -> {"action": "fill_form", "fields": {"websiteType": "business", "keyServices": "consulting services", "colorScheme": "professional"}}'
                ]
            },
            'email': {
                'form_fields': {
                    'emailType': ['marketing', 'customer_service', 'follow_up', 'thank_you', 'announcement', 'invitation'],
                    'recipientType': ['customer', 'prospect', 'partner'],
                    'emailTone': ['professional', 'friendly', 'casual', 'formal', 'urgent'],
                    'emailPurpose': 'text',
                    'emailContext': 'text',
                    'senderName': 'text'
                },
                'examples': [
                    '"Generate a marketing email for new customers" -> {"action": "fill_form", "fields": {"emailType": "marketing", "recipientType": "customer"}}',
                    '"Create a professional thank you email" -> {"action": "fill_form", "fields": {"emailType": "thank_you", "emailTone": "professional"}}'
                ]
            },
            'feedback': {
                'form_fields': {
                    'feedbackText': 'text',
                    'feedbackTitle': 'text'
                },
                'examples': [
                    '"Analyze this feedback: the service was terrible and slow" -> {"action": "fill_form", "fields": {"feedbackText": "the service was terrible and slow"}, "tool_execution": {"tool": "feedback", "auto_submit": true}}'
                ]
            },
            'poster': {
                'form_fields': {
                    'posterType': ['promotional', 'event', 'product', 'service', 'announcement'],
                    'posterTitle': 'text',
                    'posterSubtitle': 'text',
                    'posterDescription': 'text',
                    'businessName': 'text',
                    'colorScheme': ['modern', 'vibrant', 'professional', 'nature', 'creative', 'minimalist'],
                    'posterSize': ['medium', 'large', 'a4', 'social_media']
                },
                'examples': [
                    '"Make a poster for grand opening sale" -> {"action": "fill_form", "fields": {"posterType": "promotional", "posterTitle": "Grand Opening Sale"}}',
                    '"Create an event poster for workshop" -> {"action": "fill_form", "fields": {"posterType": "event", "posterTitle": "Workshop"}}'
                ]
            },
            'sales': {
                'actions': ['upload', 'analyze'],
                'examples': [
                    '"Analyze sales data" -> {"action": "execute_tool", "tool_execution": {"tool": "sales"}}'
                ]
            },
            'dashboard': {
                'navigation_options': [
                    '/tools/website', '/tools/email', '/tools/feedback', 
                    '/tools/poster', '/tools/sales', '/profile', '/settings'
                ],
                'examples': [
                    '"Go to website builder" -> {"action": "navigate", "navigation": "/tools/website"}',
                    '"Open email tool" -> {"action": "navigate", "navigation": "/tools/email"}'
                ]
            }
        }
        
        current_context = page_contexts.get(page, {})
        
        prompt = f"""
You are an AI assistant for a business toolkit web application. You help users interact with the application through voice commands.

USER SPEECH: "{transcript}"
CURRENT PAGE: {page}
TIMESTAMP: {datetime.now().isoformat()}

PAGE CONTEXT:
{json.dumps(current_context, indent=2)}

TASK: Analyze the user's speech and provide JSON instructions to:
1. Fill form fields with appropriate values
2. Navigate to different pages if needed  
3. Execute tools automatically when requested

RESPONSE FORMAT (JSON only, no other text):
{{
    "action": "fill_form" | "navigate" | "execute_tool" | "combination",
    "fields": {{
        "fieldId": "extracted_value_from_speech"
    }},
    "navigation": "url_path_if_navigation_needed",
    "tool_execution": {{
        "tool": "website|email|feedback|poster|sales",
        "auto_submit": true|false
    }},
    "message": "user_friendly_confirmation_message",
    "confidence": 0.0-1.0
}}

FIELD EXTRACTION RULES:
1. Extract business/company names from phrases like "for [name]", "called [name]", "named [name]"
2. Identify types from keywords: restaurant, business, portfolio, marketing, promotional, event, etc.
3. Extract descriptive text for description fields
4. Infer appropriate color schemes and tones from context
5. Handle variations in speech (e.g., "make a site" = "create website")

NAVIGATION RULES:
- If user mentions a tool not on current page, navigate there first
- Common phrases: "go to", "open", "show me", "navigate to"

AUTO-EXECUTION RULES:
- Set auto_submit=true for feedback analysis requests
- Set auto_submit=false for form filling that needs user review
- Execute tools directly for commands like "analyze", "generate", "create"

CONFIDENCE SCORING:
- 0.9-1.0: Clear, unambiguous commands with specific details
- 0.7-0.8: Good match with some assumptions
- 0.5-0.6: Partial match, may need clarification
- 0.0-0.4: Unclear or insufficient information

EXAMPLE RESPONSES:

Input: "Create a website for my pizza restaurant called Tony's Pizza"
Output:
{{
    "action": "fill_form",
    "fields": {{
        "websiteType": "restaurant",
        "businessName": "Tony's Pizza",
        "businessDescription": "A pizza restaurant",
        "targetAudience": "pizza lovers, families"
    }},
    "tool_execution": {{"tool": "website", "auto_submit": false}},
    "message": "I've filled in your restaurant website details. Please review and submit when ready.",
    "confidence": 0.95
}}

Input: "Generate a professional marketing email for new customers"
Output:
{{
    "action": "fill_form", 
    "fields": {{
        "emailType": "marketing",
        "recipientType": "customer", 
        "emailTone": "professional",
        "emailPurpose": "welcoming new customers"
    }},
    "tool_execution": {{"tool": "email", "auto_submit": false}},
    "message": "I've set up your marketing email parameters. Review and generate when ready.",
    "confidence": 0.9
}}

Input: "Analyze this feedback: the service was really slow and the staff was rude"
Output:
{{
    "action": "fill_form",
    "fields": {{
        "feedbackText": "the service was really slow and the staff was rude"
    }},
    "tool_execution": {{"tool": "feedback", "auto_submit": true}},
    "message": "Analyzing your feedback for sentiment and insights...",
    "confidence": 1.0
}}

Now process the user's speech and provide the JSON response:
        """
        
        return prompt

    def fallback_processing(self, transcript: str, page: str) -> Dict[str, Any]:
        """Fallback processing without Gemini AI"""
        transcript_lower = transcript.lower()
        
        # Basic keyword extraction
        instructions = {
            'action': 'fill_form',
            'fields': {},
            'tool_execution': {'tool': page, 'auto_submit': False},
            'message': 'Processed with basic keyword matching.',
            'confidence': 0.6
        }
        
        # Website processing
        if page == 'website' or 'website' in transcript_lower or 'site' in transcript_lower:
            instructions.update(self.extract_website_info(transcript))
            if page != 'website':
                instructions['action'] = 'navigate'
                instructions['navigation'] = '/tools/website'
                
        # Email processing  
        elif page == 'email' or 'email' in transcript_lower or 'mail' in transcript_lower:
            instructions.update(self.extract_email_info(transcript))
            if page != 'email':
                instructions['action'] = 'navigate'
                instructions['navigation'] = '/tools/email'
                
        # Feedback processing
        elif page == 'feedback' or 'feedback' in transcript_lower or 'review' in transcript_lower:
            instructions.update(self.extract_feedback_info(transcript))
            if page != 'feedback':
                instructions['action'] = 'navigate'
                instructions['navigation'] = '/tools/feedback'
                
        # Poster processing
        elif page == 'poster' or 'poster' in transcript_lower or 'flyer' in transcript_lower:
            instructions.update(self.extract_poster_info(transcript))
            if page != 'poster':
                instructions['action'] = 'navigate'
                instructions['navigation'] = '/tools/poster'
                
        # Navigation commands
        elif any(nav_word in transcript_lower for nav_word in ['go to', 'open', 'show', 'navigate']):
            instructions.update(self.extract_navigation_intent(transcript))
            
        return {
            'success': True,
            'instructions': instructions,
            'processed_by': 'fallback',
            'transcript': transcript
        }

    def extract_website_info(self, transcript: str) -> Dict[str, Any]:
        """Extract website information from speech"""
        fields = {}
        transcript_lower = transcript.lower()
        
        # Business name extraction
        name_patterns = [
            r'(?:for|called|named)\s+([^,.\n]+)',
            r'(?:my|our)\s+([^,.\n]+?)(?:\s+(?:business|company|restaurant|shop))',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, transcript, re.IGNORECASE)
            if match:
                fields['businessName'] = match.group(1).strip()
                break
        
        # Website type detection
        type_keywords = {
            'restaurant': ['restaurant', 'cafe', 'food', 'dining', 'pizza', 'burger'],
            'business': ['business', 'company', 'corporate', 'consulting'],
            'portfolio': ['portfolio', 'personal', 'showcase', 'work'],
            'ecommerce': ['store', 'shop', 'sell', 'products', 'ecommerce'],
            'services': ['services', 'service', 'professional']
        }
        
        for website_type, keywords in type_keywords.items():
            if any(keyword in transcript_lower for keyword in keywords):
                fields['websiteType'] = website_type
                break
        
        # Color scheme detection
        color_keywords = {
            'professional': ['professional', 'business', 'corporate'],
            'modern': ['modern', 'contemporary', 'sleek'],
            'warm': ['warm', 'friendly', 'welcoming'],
            'creative': ['creative', 'artistic', 'colorful'],
            'nature': ['natural', 'green', 'eco', 'organic']
        }
        
        for scheme, keywords in color_keywords.items():
            if any(keyword in transcript_lower for keyword in keywords):
                fields['colorScheme'] = scheme
                break
        
        # Services extraction
        if 'services' in transcript_lower or 'service' in transcript_lower:
            service_match = re.search(r'(?:services?|provide|offer)(?:\s+(?:like|such as))?\s+([^,.]+)', transcript, re.IGNORECASE)
            if service_match:
                fields['keyServices'] = service_match.group(1).strip()
        
        return {
            'fields': fields,
            'message': f"Extracted website information for {fields.get('businessName', 'your business')}."
        }

    def extract_email_info(self, transcript: str) -> Dict[str, Any]:
        """Extract email information from speech"""
        fields = {}
        transcript_lower = transcript.lower()
        
        # Email type detection
        type_keywords = {
            'marketing': ['marketing', 'promotional', 'advertisement', 'promote'],
            'customer_service': ['customer service', 'support', 'help', 'assistance'],
            'thank_you': ['thank you', 'thanks', 'appreciation'],
            'follow_up': ['follow up', 'followup', 'follow-up', 'check in'],
            'announcement': ['announcement', 'announce', 'news', 'update'],
            'invitation': ['invitation', 'invite', 'event']
        }
        
        for email_type, keywords in type_keywords.items():
            if any(keyword in transcript_lower for keyword in keywords):
                fields['emailType'] = email_type
                break
        
        # Recipient type detection
        recipient_keywords = {
            'customer': ['customers', 'clients', 'existing'],
            'prospect': ['prospects', 'potential', 'new', 'leads'],
            'partner': ['partners', 'vendors', 'suppliers']
        }
        
        for recipient_type, keywords in recipient_keywords.items():
            if any(keyword in transcript_lower for keyword in keywords):
                fields['recipientType'] = recipient_type
                break
        
        # Tone detection
        tone_keywords = {
            'professional': ['professional', 'business', 'formal'],
            'friendly': ['friendly', 'warm', 'personal'],
            'casual': ['casual', 'informal', 'relaxed'],
            'urgent': ['urgent', 'important', 'immediate']
        }
        
        for tone, keywords in tone_keywords.items():
            if any(keyword in transcript_lower for keyword in keywords):
                fields['emailTone'] = tone
                break
        
        # Purpose extraction
        purpose_match = re.search(r'(?:about|for|regarding)\s+([^,.]+)', transcript, re.IGNORECASE)
        if purpose_match:
            fields['emailPurpose'] = purpose_match.group(1).strip()
        
        return {
            'fields': fields,
            'message': f"Set up email configuration for {fields.get('emailType', 'general')} email."
        }

    def extract_feedback_info(self, transcript: str) -> Dict[str, Any]:
        """Extract feedback information from speech"""
        # For feedback, look for the actual feedback content
        feedback_indicators = ['feedback:', 'review:', 'comment:', 'this feedback', 'analyze this']
        
        feedback_text = transcript
        for indicator in feedback_indicators:
            if indicator in transcript.lower():
                parts = transcript.lower().split(indicator, 1)
                if len(parts) > 1:
                    feedback_text = parts[1].strip()
                break
        
        return {
            'fields': {'feedbackText': feedback_text},
            'tool_execution': {'tool': 'feedback', 'auto_submit': True},
            'message': 'Analyzing the provided feedback for sentiment and insights.'
        }

    def extract_poster_info(self, transcript: str) -> Dict[str, Any]:
        """Extract poster information from speech"""
        fields = {}
        transcript_lower = transcript.lower()
        
        # Poster type detection
        type_keywords = {
            'promotional': ['sale', 'promotion', 'discount', 'offer', 'deal'],
            'event': ['event', 'opening', 'launch', 'workshop', 'conference'],
            'product': ['product', 'new product', 'launch'],
            'announcement': ['announcement', 'news', 'update']
        }
        
        for poster_type, keywords in type_keywords.items():
            if any(keyword in transcript_lower for keyword in keywords):
                fields['posterType'] = poster_type
                break
        
        # Title extraction
        title_patterns = [
            r'(?:for|called|titled)\s+([^,.\n]+)',
            r'(?:poster|flyer)\s+(?:for|about)\s+([^,.\n]+)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, transcript, re.IGNORECASE)
            if match:
                fields['posterTitle'] = match.group(1).strip()
                break
        
        # Common titles based on type
        if not fields.get('posterTitle'):
            if 'grand opening' in transcript_lower:
                fields['posterTitle'] = 'Grand Opening'
            elif 'sale' in transcript_lower:
                fields['posterTitle'] = 'Special Sale'
            elif 'workshop' in transcript_lower:
                fields['posterTitle'] = 'Workshop Event'
        
        # Business name extraction
        business_match = re.search(r'(?:for|at)\s+([^,.\n]+?)(?:\s+(?:business|company|store))', transcript, re.IGNORECASE)
        if business_match:
            fields['businessName'] = business_match.group(1).strip()
        
        return {
            'fields': fields,
            'message': f"Set up poster configuration for {fields.get('posterTitle', 'your poster')}."
        }

    def extract_navigation_intent(self, transcript: str) -> Dict[str, Any]:
        """Extract navigation intent from speech"""
        transcript_lower = transcript.lower()
        
        # Navigation mapping
        nav_keywords = {
            '/tools/website': ['website', 'site builder', 'web'],
            '/tools/email': ['email', 'mail'],
            '/tools/feedback': ['feedback', 'reviews', 'comments'],
            '/tools/poster': ['poster', 'flyer', 'design'],
            '/tools/sales': ['sales', 'analytics', 'data'],
            '/dashboard': ['dashboard', 'home', 'main'],
            '/profile': ['profile', 'settings', 'account']
        }
        
        for url, keywords in nav_keywords.items():
            if any(keyword in transcript_lower for keyword in keywords):
                return {
                    'action': 'navigate',
                    'navigation': url,
                    'message': f'Navigating to {keywords[0]} page.'
                }
        
        return {
            'action': 'fill_form',
            'message': 'Could not determine navigation intent.'
        }


# Flask route integration
def integrate_speech_routes(app):
    """Add speech processing routes to Flask app"""
    
    speech_processor = SpeechProcessor()
    
    @app.route('/api/process-speech', methods=['POST'])
    def process_speech():
        """Process speech input and return instructions"""
        try:
            data = request.get_json()
            transcript = data.get('transcript', '')
            page = data.get('page', 'unknown')
            context = data.get('context', {})
            
            if not transcript:
                return jsonify({
                    'success': False,
                    'error': 'No transcript provided'
                }), 400
            
            result = speech_processor.process_speech_input(transcript, page, context)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/speech-capabilities', methods=['GET'])
    def speech_capabilities():
        """Return speech processing capabilities"""
        return jsonify({
            'gemini_available': speech_processor.model is not None,
            'supported_pages': ['website', 'email', 'feedback', 'poster', 'sales', 'dashboard'],
            'supported_actions': ['fill_form', 'navigate', 'execute_tool'],
            'fallback_available': True
        })


# Example usage and testing
if __name__ == "__main__":
    processor = SpeechProcessor()
    
    # Test cases
    test_cases = [
        {
            'transcript': "Create a website for my pizza restaurant called Tony's Pizza",
            'page': 'website'
        },
        {
            'transcript': "Generate a professional marketing email for new customers",
            'page': 'email'
        },
        {
            'transcript': "Analyze this feedback: the service was really slow and the staff was rude",
            'page': 'feedback'
        },
        {
            'transcript': "Make a poster for grand opening sale",
            'page': 'poster'
        },
        {
            'transcript': "Go to email tool",
            'page': 'dashboard'
        }
    ]
    
    print("Testing Speech Processor...")
    print("=" * 50)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Input: '{test['transcript']}' (Page: {test['page']})")
        
        result = processor.process_speech_input(test['transcript'], test['page'])
        
        print(f"Success: {result['success']}")
        print(f"Processed by: {result['processed_by']}")
        if result['success']:
            instructions = result['instructions']
            print(f"Action: {instructions['action']}")
            print(f"Fields: {instructions.get('fields', {})}")
            print(f"Message: {instructions['message']}")
            print(f"Confidence: {instructions.get('confidence', 'N/A')}")
        
        print("-" * 30)