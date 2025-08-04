# Enhanced Speech Processor with Gemini AI Integration
import os
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedSpeechProcessor:
    """Enhanced Speech Processing with Gemini AI and robust fallbacks"""
    
    def __init__(self):
        self.model = None
        self.is_initialized = False
        self.fallback_patterns = {}
        self.confidence_threshold = 0.7
        self.supported_languages = ['en-US', 'en-GB', 'hi-IN', 'te-IN']
        self.initialize()
    
    def initialize(self):
        """Initialize the speech processor with Gemini AI"""
        if self.is_initialized:
            return
            
        logger.info("Initializing Enhanced Speech Processor...")
        
        # Initialize Gemini AI
        self._initialize_gemini()
        
        # Load fallback patterns
        self._load_fallback_patterns()
        
        # Set up page contexts
        self._setup_page_contexts()
        
        self.is_initialized = True
        logger.info("Speech Processor initialized successfully")
    
    def _initialize_gemini(self):
        """Initialize Gemini AI with proper error handling"""
        if not GEMINI_AVAILABLE:
            logger.warning("Gemini AI not available. Using fallback processing only.")
            return
            
        api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyDd3d3Dv5tVxXRieMDDo5ZHqacP9XPa0oU')
        
        if not api_key:
            logger.error("No Gemini API key found")
            return
            
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini AI initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            self.model = None
    
    def _load_fallback_patterns(self):
        """Load pattern matching for fallback processing"""
        self.fallback_patterns = {
            'navigation': {
                'patterns': [
                    (r'(?:go to|open|show|navigate to|switch to)\s+(website|email|feedback|poster|sales|dashboard|profile)', 
                     lambda m: self._get_navigation_url(m.group(1))),
                    (r'(?:show me|open)\s+the\s+([\w\s]+)\s+(?:tool|page)',
                     lambda m: self._get_navigation_url(m.group(1).strip())),
                ]
            },
            'website_creation': {
                'patterns': [
                    (r'(?:create|make|build|generate)\s+(?:a\s+)?website\s+for\s+(.+?)(?:\s+(?:called|named)\s+(.+?))?(?:\.|$)',
                     self._extract_website_info),
                    (r'(?:i want|i need)\s+(?:a\s+)?(.+?)\s+website\s+for\s+(.+?)(?:\.|$)',
                     self._extract_website_type_info),
                ]
            },
            'email_creation': {
                'patterns': [
                    (r'(?:create|generate|draft|write)\s+(?:a\s+)?(.+?)\s+email\s+(?:for|to)\s+(.+?)(?:\.|$)',
                     self._extract_email_info),
                    (r'(?:send|write)\s+(?:an?\s+)?email\s+(?:about|regarding)\s+(.+?)(?:\.|$)',
                     self._extract_email_purpose),
                ]
            },
            'feedback_analysis': {
                'patterns': [
                    (r'(?:analyze|check|review)\s+(?:this\s+)?feedback[:\s]+(.+)',
                     lambda m: {'feedbackText': m.group(1).strip()}),
                    (r'(?:sentiment|analysis|analyze)[:\s]+(.+)',
                     lambda m: {'feedbackText': m.group(1).strip()}),
                ]
            },
            'poster_creation': {
                'patterns': [
                    (r'(?:create|make|design)\s+(?:a\s+)?poster\s+for\s+(.+?)(?:\s+(?:called|titled)\s+(.+?))?(?:\.|$)',
                     self._extract_poster_info),
                    (r'(?:make|create)\s+(?:a\s+)?(.+?)\s+poster(?:\s+for\s+(.+?))?(?:\.|$)',
                     self._extract_poster_type_info),
                ]
            },
            'field_filling': {
                'patterns': [
                    (r'(?:fill|enter|set)\s+(.+?)\s+(?:with|to|as)\s+(.+)',
                     lambda m: {self._normalize_field_name(m.group(1)): m.group(2).strip()}),
                    (r'(?:my\s+)?(.+?)\s+is\s+(.+)',
                     lambda m: {self._normalize_field_name(m.group(1)): m.group(2).strip()}),
                ]
            }
        }
    
    def _setup_page_contexts(self):
        """Setup detailed page contexts for better processing"""
        self.page_contexts = {
            'website': {
                'fields': {
                    'websiteType': {
                        'type': 'select',
                        'options': ['business', 'portfolio', 'ecommerce', 'blog', 'restaurant', 'services'],
                        'keywords': {
                            'business': ['business', 'company', 'corporate', 'office'],
                            'restaurant': ['restaurant', 'cafe', 'food', 'dining', 'kitchen'],
                            'portfolio': ['portfolio', 'personal', 'showcase', 'work'],
                            'ecommerce': ['store', 'shop', 'ecommerce', 'selling', 'products'],
                            'services': ['services', 'consulting', 'professional', 'agency'],
                            'blog': ['blog', 'writing', 'articles', 'content']
                        }
                    },
                    'businessName': {'type': 'text', 'required': True},
                    'businessDescription': {'type': 'textarea'},
                    'keyServices': {'type': 'text'},
                    'targetAudience': {'type': 'text'},
                    'colorScheme': {
                        'type': 'select',
                        'options': ['professional', 'modern', 'warm', 'nature', 'creative'],
                        'keywords': {
                            'professional': ['professional', 'business', 'corporate', 'formal'],
                            'modern': ['modern', 'contemporary', 'sleek', 'minimalist'],
                            'warm': ['warm', 'friendly', 'welcoming', 'cozy'],
                            'nature': ['nature', 'green', 'organic', 'natural', 'eco'],
                            'creative': ['creative', 'artistic', 'colorful', 'vibrant']
                        }
                    }
                },
                'auto_submit': False
            },
            'email': {
                'fields': {
                    'emailType': {
                        'type': 'select',
                        'options': ['marketing', 'customer_service', 'follow_up', 'thank_you', 'announcement', 'invitation'],
                        'keywords': {
                            'marketing': ['marketing', 'promotional', 'advertisement', 'campaign'],
                            'customer_service': ['support', 'service', 'help', 'assistance', 'customer'],
                            'thank_you': ['thank', 'thanks', 'appreciation', 'grateful'],
                            'follow_up': ['follow up', 'followup', 'check in', 'update'],
                            'announcement': ['announcement', 'news', 'update', 'information'],
                            'invitation': ['invitation', 'invite', 'event', 'meeting']
                        }
                    },
                    'recipientType': {
                        'type': 'select',
                        'options': ['customer', 'prospect', 'partner'],
                        'keywords': {
                            'customer': ['customer', 'client', 'existing', 'current'],
                            'prospect': ['prospect', 'potential', 'new', 'lead'],
                            'partner': ['partner', 'vendor', 'supplier', 'collaborator']
                        }
                    },
                    'emailTone': {
                        'type': 'select',
                        'options': ['professional', 'friendly', 'casual', 'formal', 'urgent'],
                        'keywords': {
                            'professional': ['professional', 'business'],
                            'friendly': ['friendly', 'warm', 'personal'],
                            'casual': ['casual', 'informal', 'relaxed'],
                            'formal': ['formal', 'official'],
                            'urgent': ['urgent', 'important', 'immediate']
                        }
                    },
                    'emailPurpose': {'type': 'text'},
                    'emailContext': {'type': 'textarea'},
                    'senderName': {'type': 'text'}
                },
                'auto_submit': False
            },
            'feedback': {
                'fields': {
                    'feedbackText': {'type': 'textarea', 'required': True}
                },
                'auto_submit': True
            },
            'poster': {
                'fields': {
                    'posterType': {
                        'type': 'select',
                        'options': ['promotional', 'event', 'product', 'service', 'announcement'],
                        'keywords': {
                            'promotional': ['sale', 'promotion', 'discount', 'offer', 'deal'],
                            'event': ['event', 'opening', 'launch', 'workshop', 'conference'],
                            'product': ['product', 'new product', 'launch'],
                            'service': ['service', 'services'],
                            'announcement': ['announcement', 'news', 'update']
                        }
                    },
                    'posterTitle': {'type': 'text'},
                    'posterSubtitle': {'type': 'text'},
                    'posterDescription': {'type': 'textarea'},
                    'businessName': {'type': 'text'},
                    'colorScheme': {
                        'type': 'select',
                        'options': ['modern', 'vibrant', 'professional', 'nature', 'creative', 'minimalist']
                    },
                    'posterSize': {
                        'type': 'select',
                        'options': ['medium', 'large', 'a4', 'social_media']
                    }
                },
                'auto_submit': False
            },
            'sales': {
                'actions': ['upload', 'analyze'],
                'auto_submit': False
            }
        }
    
    def process_speech_input(self, transcript: str, page: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main entry point for processing speech input"""
        try:
            logger.info(f"Processing speech: '{transcript}' on page: {page}")
            
            # Clean and validate input
            transcript = self._clean_transcript(transcript)
            if not transcript:
                return self._error_response("Empty or invalid transcript")
            
            # Try Gemini AI processing first
            if self.model:
                try:
                    result = self._process_with_gemini(transcript, page, context)
                    if result.get('success'):
                        logger.info("Successfully processed with Gemini AI")
                        return result
                except Exception as e:
                    logger.warning(f"Gemini processing failed: {e}")
            
            # Fallback to pattern matching
            logger.info("Using fallback pattern matching")
            result = self._process_with_patterns(transcript, page, context)
            
            # Add metadata
            result['processed_by'] = 'fallback' if not self.model else 'gemini_fallback'
            result['processed_at'] = datetime.now().isoformat()
            result['original_transcript'] = transcript
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing speech: {e}")
            return self._error_response(f"Processing failed: {str(e)}")
    
    def _clean_transcript(self, transcript: str) -> str:
        """Clean and normalize transcript"""
        if not transcript:
            return ""
        
        # Remove extra whitespace and normalize
        transcript = re.sub(r'\s+', ' ', transcript.strip())
        
        # Remove common speech artifacts
        transcript = re.sub(r'\b(?:um|uh|er|ah)\b', '', transcript, flags=re.IGNORECASE)
        
        return transcript
    
    def _process_with_gemini(self, transcript: str, page: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process speech using Gemini AI"""
        prompt = self._build_gemini_prompt(transcript, page, context)
        
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
            
            if not response.text:
                raise Exception("Empty response from Gemini")
            
            # Parse JSON response
            instructions = json.loads(response.text)
            
            # Validate and enhance instructions
            instructions = self._validate_instructions(instructions, page)
            
            return {
                'success': True,
                'instructions': instructions,
                'confidence': instructions.get('confidence', 0.8),
                'processed_by': 'gemini'
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise Exception(f"Invalid JSON response from AI: {e}")
        except Exception as e:
            logger.error(f"Gemini processing error: {e}")
            raise e
    
    def _build_gemini_prompt(self, transcript: str, page: str, context: Dict[str, Any] = None) -> str:
        """Build comprehensive prompt for Gemini AI"""
        
        page_context = self.page_contexts.get(page, {})
        
        prompt = f"""
You are an advanced AI assistant for the Brand Bloom business toolkit application. Your job is to process voice commands and convert them into structured instructions for form filling, navigation, or tool execution.

**USER SPEECH:** "{transcript}"
**CURRENT PAGE:** {page}
**TIMESTAMP:** {datetime.now().isoformat()}

**PAGE CONTEXT:**
{json.dumps(page_context, indent=2)}

**TASK:** Analyze the user's speech and return a JSON response with precise instructions.

**RESPONSE FORMAT (JSON only, no markdown):**
{{
    "action": "fill_form" | "navigate" | "execute_tool" | "combination",
    "confidence": 0.0-1.0,
    "fields": {{
        "fieldId": "extracted_value"
    }},
    "navigation": "url_path_if_needed",
    "tool_execution": {{
        "tool": "website|email|feedback|poster|sales",
        "auto_submit": true|false
    }},
    "message": "user_friendly_confirmation_message",
    "reasoning": "brief_explanation_of_processing"
}}

**PROCESSING RULES:**

1. **Field Extraction:**
   - Extract business/entity names from patterns: "for [name]", "called [name]", "my [entity] is [name]"
   - Identify types from keywords (restaurant, business, marketing, promotional, etc.)
   - Map natural language to form field values using the field keywords provided
   - For select fields, choose the closest matching option from the available choices

2. **Confidence Scoring:**
   - 0.9-1.0: Clear, unambiguous commands with specific extractable information
   - 0.7-0.8: Good match with minor assumptions or partial information
   - 0.5-0.6: Reasonable interpretation but requires some guesswork
   - 0.0-0.4: Unclear or insufficient information

3. **Navigation Detection:**
   - Phrases like "go to", "open", "show", "navigate to" indicate navigation intent
   - Map tool names to correct URLs: website→/tools/website, email→/tools/email, etc.

4. **Auto-Submit Logic:**
   - Set auto_submit=true for feedback analysis requests
   - Set auto_submit=false for form filling that needs user review
   - Consider user intent and command clarity

5. **Multi-language Support:**
   - Handle common Hindi/Telugu words mixed with English
   - Translate common business terms appropriately

**EXAMPLES:**

Input: "Create a website for my pizza restaurant called Tony's Kitchen"
Output:
{{
    "action": "fill_form",
    "confidence": 0.95,
    "fields": {{
        "websiteType": "restaurant",
        "businessName": "Tony's Kitchen",
        "businessDescription": "A pizza restaurant",
        "targetAudience": "pizza lovers, families"
    }},
    "tool_execution": {{"tool": "website", "auto_submit": false}},
    "message": "I've filled in your restaurant website details for Tony's Kitchen. Please review and generate when ready.",
    "reasoning": "Clear business type (restaurant) and name (Tony's Kitchen) extracted from speech"
}}

Input: "Generate a professional marketing email for new customers"
Output:
{{
    "action": "fill_form",
    "confidence": 0.9,
    "fields": {{
        "emailType": "marketing",
        "recipientType": "customer",
        "emailTone": "professional",
        "emailPurpose": "welcome new customers"
    }},
    "tool_execution": {{"tool": "email", "auto_submit": false}},
    "message": "I've configured your professional marketing email settings. Ready to generate your email.",
    "reasoning": "Email type (marketing), recipient (customers), and tone (professional) clearly specified"
}}

Input: "Analyze this feedback: the service was really slow and staff seemed uninterested"
Output:
{{
    "action": "fill_form",
    "confidence": 1.0,
    "fields": {{
        "feedbackText": "the service was really slow and staff seemed uninterested"
    }},
    "tool_execution": {{"tool": "feedback", "auto_submit": true}},
    "message": "Analyzing your feedback for sentiment and key insights...",
    "reasoning": "Direct feedback analysis request with clear feedback text provided"
}}

Input: "Go to email tool"
Output:
{{
    "action": "navigate",
    "confidence": 1.0,
    "navigation": "/tools/email",
    "message": "Navigating to email composer...",
    "reasoning": "Clear navigation command to email tool"
}}

Now process the user's speech and provide the JSON response:
        """
        
        return prompt
    
    def _validate_instructions(self, instructions: Dict[str, Any], page: str) -> Dict[str, Any]:
        """Validate and enhance AI-generated instructions"""
        
        # Ensure required fields
        if 'action' not in instructions:
            instructions['action'] = 'fill_form'
        
        if 'confidence' not in instructions:
            instructions['confidence'] = 0.7
        
        # Validate field mappings against page context
        if instructions['action'] == 'fill_form' and 'fields' in instructions:
            page_context = self.page_contexts.get(page, {})
            valid_fields = {}
            
            for field_id, value in instructions['fields'].items():
                if field_id in page_context.get('fields', {}):
                    # Validate select field values
                    field_config = page_context['fields'][field_id]
                    if field_config.get('type') == 'select':
                        options = field_config.get('options', [])
                        if value not in options:
                            # Try to find closest match
                            value = self._find_closest_option(value, options, field_config.get('keywords', {}))
                    
                    valid_fields[field_id] = value
            
            instructions['fields'] = valid_fields
        
        # Set auto_submit based on page defaults if not specified
        if 'tool_execution' in instructions and 'auto_submit' not in instructions['tool_execution']:
            page_context = self.page_contexts.get(page, {})
            instructions['tool_execution']['auto_submit'] = page_context.get('auto_submit', False)
        
        return instructions
    
    def _find_closest_option(self, value: str, options: List[str], keywords: Dict[str, List[str]]) -> str:
        """Find the closest matching option for select fields"""
        value_lower = value.lower()
        
        # Check direct match first
        for option in options:
            if option.lower() == value_lower:
                return option
        
        # Check keyword matches
        for option, option_keywords in keywords.items():
            if option in options:
                for keyword in option_keywords:
                    if keyword in value_lower:
                        return option
        
        # Return first option as fallback
        return options[0] if options else value
    
    def _process_with_patterns(self, transcript: str, page: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process speech using pattern matching fallback"""
        
        transcript_lower = transcript.lower()
        
        # Try navigation patterns first
        nav_result = self._match_navigation_patterns(transcript_lower)
        if nav_result:
            return {
                'success': True,
                'instructions': nav_result,
                'confidence': 0.8
            }
        
        # Try page-specific patterns
        page_result = self._match_page_patterns(transcript, transcript_lower, page)
        if page_result:
            return {
                'success': True,
                'instructions': page_result,
                'confidence': 0.7
            }
        
        # Try generic field filling
        field_result = self._match_field_patterns(transcript, transcript_lower)
        if field_result:
            return {
                'success': True,
                'instructions': field_result,
                'confidence': 0.6
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
    
    def _match_navigation_patterns(self, transcript: str) -> Optional[Dict[str, Any]]:
        """Match navigation patterns"""
        for pattern, handler in self.fallback_patterns['navigation']['patterns']:
            match = re.search(pattern, transcript, re.IGNORECASE)
            if match:
                url = handler(match) if callable(handler) else handler
                if url:
                    return {
                        'action': 'navigate',
                        'navigation': url,
                        'message': f'Navigating to {match.group(1)} page...'
                    }
        return None
    
    def _match_page_patterns(self, transcript: str, transcript_lower: str, page: str) -> Optional[Dict[str, Any]]:
        """Match page-specific patterns"""
        
        # Website patterns
        if page == 'website' or 'website' in transcript_lower:
            for pattern, handler in self.fallback_patterns['website_creation']['patterns']:
                match = re.search(pattern, transcript, re.IGNORECASE)
                if match:
                    fields = handler(match) if callable(handler) else handler
                    return {
                        'action': 'fill_form',
                        'fields': fields,
                        'tool_execution': {'tool': 'website', 'auto_submit': False},
                        'message': f'Website form configured for {fields.get("businessName", "your business")}.'
                    }
        
        # Email patterns
        if page == 'email' or 'email' in transcript_lower:
            for pattern, handler in self.fallback_patterns['email_creation']['patterns']:
                match = re.search(pattern, transcript, re.IGNORECASE)
                if match:
                    fields = handler(match) if callable(handler) else handler
                    return {
                        'action': 'fill_form',
                        'fields': fields,
                        'tool_execution': {'tool': 'email', 'auto_submit': False},
                        'message': 'Email form configured from your speech.'
                    }
        
        # Feedback patterns
        if page == 'feedback' or 'feedback' in transcript_lower or 'analyze' in transcript_lower:
            for pattern, handler in self.fallback_patterns['feedback_analysis']['patterns']:
                match = re.search(pattern, transcript, re.IGNORECASE)
                if match:
                    fields = handler(match) if callable(handler) else handler
                    return {
                        'action': 'fill_form',
                        'fields': fields,
                        'tool_execution': {'tool': 'feedback', 'auto_submit': True},
                        'message': 'Analyzing feedback from your speech...'
                    }
        
        # Poster patterns
        if page == 'poster' or 'poster' in transcript_lower or 'flyer' in transcript_lower:
            for pattern, handler in self.fallback_patterns['poster_creation']['patterns']:
                match = re.search(pattern, transcript, re.IGNORECASE)
                if match:
                    fields = handler(match) if callable(handler) else handler
                    return {
                        'action': 'fill_form',
                        'fields': fields,
                        'tool_execution': {'tool': 'poster', 'auto_submit': False},
                        'message': f'Poster configured for {fields.get("posterTitle", "your event")}.'
                    }
        
        return None
    
    def _match_field_patterns(self, transcript: str, transcript_lower: str) -> Optional[Dict[str, Any]]:
        """Match generic field filling patterns"""
        for pattern, handler in self.fallback_patterns['field_filling']['patterns']:
            match = re.search(pattern, transcript, re.IGNORECASE)
            if match:
                fields = handler(match) if callable(handler) else handler
                return {
                    'action': 'fill_form',
                    'fields': fields,
                    'message': 'Field filled from speech input.'
                }
        return None
    
    # Pattern handler methods
    def _get_navigation_url(self, tool_name: str) -> str:
        """Get navigation URL for tool name"""
        url_mapping = {
            'website': '/tools/website',
            'email': '/tools/email',
            'feedback': '/tools/feedback',
            'poster': '/tools/poster',
            'sales': '/tools/sales',
            'dashboard': '/dashboard',
            'profile': '/profile'
        }
        
        tool_name = tool_name.lower().strip()
        return url_mapping.get(tool_name, '/dashboard')
    
    def _extract_website_info(self, match) -> Dict[str, str]:
        """Extract website information from regex match"""
        fields = {}
        
        business_desc = match.group(1).strip()
        business_name = match.group(2).strip() if match.lastindex >= 2 and match.group(2) else None
        
        if business_name:
            fields['businessName'] = business_name
        
        # Determine website type from description
        desc_lower = business_desc.lower()
        type_mapping = {
            'restaurant': ['restaurant', 'cafe', 'food', 'dining'],
            'business': ['business', 'company', 'corporate'],
            'portfolio': ['portfolio', 'personal'],
            'ecommerce': ['shop', 'store', 'ecommerce'],
            'services': ['service', 'consulting']
        }
        
        for website_type, keywords in type_mapping.items():
            if any(keyword in desc_lower for keyword in keywords):
                fields['websiteType'] = website_type
                break
        
        fields['businessDescription'] = business_desc
        
        return fields
    
    def _extract_website_type_info(self, match) -> Dict[str, str]:
        """Extract website type and business info"""
        website_type = match.group(1).strip().lower()
        business_info = match.group(2).strip()
        
        fields = {
            'businessDescription': business_info
        }
        
        # Map type keywords
        if 'restaurant' in website_type or 'food' in website_type:
            fields['websiteType'] = 'restaurant'
        elif 'business' in website_type or 'corporate' in website_type:
            fields['websiteType'] = 'business'
        elif 'portfolio' in website_type or 'personal' in website_type:
            fields['websiteType'] = 'portfolio'
        
        return fields
    
    def _extract_email_info(self, match) -> Dict[str, str]:
        """Extract email information from regex match"""
        email_type = match.group(1).strip().lower()
        recipient_info = match.group(2).strip().lower()
        
        fields = {}
        
        # Map email types
        if 'marketing' in email_type or 'promotional' in email_type:
            fields['emailType'] = 'marketing'
        elif 'support' in email_type or 'service' in email_type:
            fields['emailType'] = 'customer_service'
        elif 'thank' in email_type:
            fields['emailType'] = 'thank_you'
        
        # Map recipients
        if 'customer' in recipient_info:
            fields['recipientType'] = 'customer'
        elif 'prospect' in recipient_info or 'potential' in recipient_info:
            fields['recipientType'] = 'prospect'
        
        # Set default tone based on type
        if fields.get('emailType') == 'marketing':
            fields['emailTone'] = 'friendly'
        else:
            fields['emailTone'] = 'professional'
        
        return fields
    
    def _extract_email_purpose(self, match) -> Dict[str, str]:
        """Extract email purpose"""
        purpose = match.group(1).strip()
        return {
            'emailPurpose': purpose,
            'emailType': 'announcement',
            'emailTone': 'professional'
        }
    
    def _extract_poster_info(self, match) -> Dict[str, str]:
        """Extract poster information"""
        purpose = match.group(1).strip()
        title = match.group(2).strip() if match.lastindex >= 2 and match.group(2) else None
        
        fields = {
            'posterDescription': purpose
        }
        
        if title:
            fields['posterTitle'] = title
        
        # Determine poster type
        purpose_lower = purpose.lower()
        if 'sale' in purpose_lower or 'promotion' in purpose_lower:
            fields['posterType'] = 'promotional'
        elif 'event' in purpose_lower or 'opening' in purpose_lower:
            fields['posterType'] = 'event'
        elif 'product' in purpose_lower:
            fields['posterType'] = 'product'
        
        return fields
    
    def _extract_poster_type_info(self, match) -> Dict[str, str]:
        """Extract poster type information"""
        poster_type = match.group(1).strip().lower()
        business_info = match.group(2).strip() if match.lastindex >= 2 and match.group(2) else None
        
        fields = {}
        
        if 'promotional' in poster_type or 'sale' in poster_type:
            fields['posterType'] = 'promotional'
            fields['posterTitle'] = 'Special Promotion'
        elif 'event' in poster_type:
            fields['posterType'] = 'event'
            fields['posterTitle'] = 'Special Event'
        
        if business_info:
            fields['businessName'] = business_info
        
        return fields
    
    def _normalize_field_name(self, field_name: str) -> str:
        """Normalize field name for mapping"""
        field_name = field_name.lower().strip()
        
        # Common field mappings
        field_mappings = {
            'name': 'businessName',
            'business name': 'businessName',
            'company name': 'businessName',
            'title': 'posterTitle',
            'subject': 'emailPurpose',
            'description': 'businessDescription',
            'message': 'feedbackText',
            'feedback': 'feedbackText',
            'email': 'customerEmail',
            'type': 'websiteType'
        }
        
        return field_mappings.get(field_name, field_name.replace(' ', ''))
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            'success': False,
            'error': message,
            'instructions': {
                'action': 'error',
                'message': message,
                'confidence': 0.0
            },
            'processed_at': datetime.now().isoformat()
        }
    
    # Public API methods
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.supported_languages
    
    def set_confidence_threshold(self, threshold: float):
        """Set confidence threshold for processing"""
        self.confidence_threshold = max(0.1, min(1.0, threshold))
    
    def get_status(self) -> Dict[str, Any]:
        """Get processor status"""
        return {
            'initialized': self.is_initialized,
            'gemini_available': self.model is not None,
            'fallback_available': True,
            'supported_languages': self.supported_languages,
            'confidence_threshold': self.confidence_threshold
        }
    
    def test_processing(self, test_cases: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Test processing with sample cases"""
        results = []
        
        for case in test_cases:
            transcript = case.get('transcript', '')
            page = case.get('page', 'website')
            
            result = self.process_speech_input(transcript, page)
            results.append({
                'input': case,
                'output': result,
                'success': result.get('success', False),
                'confidence': result.get('instructions', {}).get('confidence', 0.0)
            })
        
        return results


# Flask Integration
def setup_speech_routes(app, db):
    """Setup speech processing routes for Flask app"""
    
    # Initialize processor
    processor = EnhancedSpeechProcessor()
    
    @app.route('/api/process-speech', methods=['POST'])
    def process_speech():
        """Main speech processing endpoint"""
        try:
            data = request.get_json()
            
            # Validate input
            transcript = data.get('transcript', '').strip()
            page = data.get('page', 'unknown')
            context = data.get('context', {})
            
            if not transcript:
                return jsonify({
                    'success': False,
                    'error': 'No transcript provided'
                }), 400
            
            # Add user context if available
            if 'user_id' in session:
                context['user_id'] = session['user_id']
                context['user_email'] = session.get('user_email')
            
            # Process speech
            result = processor.process_speech_input(transcript, page, context)
            
            # Log interaction for analytics
            logger.info(f"Speech processed for user {context.get('user_id')}: '{transcript}' -> {result.get('success')}")
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Speech processing error: {e}")
            return jsonify({
                'success': False,
                'error': 'Internal processing error'
            }), 500
    
    @app.route('/api/speech-capabilities', methods=['GET'])
    def speech_capabilities():
        """Get speech processing capabilities"""
        return jsonify(processor.get_status())
    
    @app.route('/api/speech-test', methods=['POST'])
    def speech_test():
        """Test speech processing (debug mode only)"""
        if not app.debug:
            return jsonify({'error': 'Not available in production'}), 404
        
        try:
            data = request.get_json()
            test_cases = data.get('test_cases', [])
            
            if not test_cases:
                # Default test cases
                test_cases = [
                    {'transcript': 'Create a website for my pizza restaurant', 'page': 'website'},
                    {'transcript': 'Generate a marketing email for customers', 'page': 'email'},
                    {'transcript': 'Analyze this feedback: great service but slow delivery', 'page': 'feedback'},
                    {'transcript': 'Make a poster for grand opening', 'page': 'poster'},
                    {'transcript': 'Go to email tool', 'page': 'dashboard'}
                ]
            
            results = processor.test_processing(test_cases)
            
            return jsonify({
                'success': True,
                'test_results': results,
                'summary': {
                    'total_tests': len(results),
                    'successful': sum(1 for r in results if r['success']),
                    'average_confidence': sum(r['confidence'] for r in results) / len(results) if results else 0
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/speech-analytics', methods=['POST'])
    def speech_analytics():
        """Store speech interaction analytics"""
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            data = request.get_json()
            
            # Store analytics data (you could save this to database)
            analytics_data = {
                'user_id': session['user_id'],
                'action': data.get('action'),
                'form_id': data.get('form_id'),
                'speech_data': data.get('speech_data'),
                'timestamp': data.get('timestamp'),
                'user_agent': data.get('user_agent'),
                'viewport': data.get('viewport')
            }
            
            # Log for now (in production, save to database)
            logger.info(f"Speech analytics: {analytics_data}")
            
            return jsonify({'success': True})
            
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return jsonify({'success': False}), 500
    
    @app.route('/api/speech-settings', methods=['GET', 'POST'])
    def speech_settings():
        """Get or update speech settings"""
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if request.method == 'GET':
            # Return current settings (could be stored in database per user)
            return jsonify({
                'language': 'en-US',
                'confidence_threshold': 0.7,
                'auto_submit': True,
                'notifications': True,
                'supported_languages': processor.get_supported_languages()
            })
        
        else:  # POST
            try:
                settings = request.get_json()
                
                # Update processor settings
                if 'confidence_threshold' in settings:
                    processor.set_confidence_threshold(settings['confidence_threshold'])
                
                # In production, save settings to database per user
                # db.update_user_speech_settings(session['user_id'], settings)
                
                return jsonify({'success': True, 'message': 'Settings updated'})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    return processor


# Example usage and testing
if __name__ == "__main__":
    # Initialize processor
    processor = EnhancedSpeechProcessor()
    
    # Test cases
    test_cases = [
        {
            'transcript': "Create a website for my Italian restaurant called Bella Vista",
            'page': 'website'
        },
        {
            'transcript': "Generate a professional thank you email for our customers",
            'page': 'email'
        },
        {
            'transcript': "Analyze this feedback: The food was excellent but the service was slow and the staff seemed overwhelmed",
            'page': 'feedback'
        },
        {
            'transcript': "Make a promotional poster for our grand opening sale event",
            'page': 'poster'
        },
        {
            'transcript': "Go to the email composer tool",
            'page': 'dashboard'
        },
        {
            'transcript': "Fill business name with Tech Solutions Inc",
            'page': 'website'
        }
    ]
    
    print("Testing Enhanced Speech Processor")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Input: '{test_case['transcript']}' (Page: {test_case['page']})")
        
        result = processor.process_speech_input(test_case['transcript'], test_case['page'])
        
        print(f"Success: {result['success']}")
        print(f"Processed by: {result.get('processed_by', 'unknown')}")
        
        if result['success']:
            instructions = result['instructions']
            print(f"Action: {instructions['action']}")
            print(f"Confidence: {instructions.get('confidence', 0):.2f}")
            print(f"Fields: {instructions.get('fields', {})}")
            print(f"Message: {instructions.get('message', 'No message')}")
            
            if 'navigation' in instructions:
                print(f"Navigation: {instructions['navigation']}")
            
            if 'tool_execution' in instructions:
                print(f"Tool: {instructions['tool_execution']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        print("-" * 30)
    
    # Status check
    print(f"\nProcessor Status:")
    status = processor.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
