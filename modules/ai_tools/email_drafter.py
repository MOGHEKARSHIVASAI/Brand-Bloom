from datetime import datetime
import json

def draft_email(request_data):
    """
    Draft professional emails based on user requirements
    """
    email_type = request_data.get('email_type', 'general')
    recipient_type = request_data.get('recipient_type', 'customer')
    tone = request_data.get('tone', 'professional')
    purpose = request_data.get('purpose', '')
    context = request_data.get('context', '')
    business_name = request_data.get('business_name', 'Your Business')
    sender_name = request_data.get('sender_name', 'Team')
    
    # Generate email based on type and parameters
    email_content = generate_email_content(
        email_type, recipient_type, tone, purpose, context, business_name, sender_name
    )
    
    return {
        'status': 'success',
        'email': email_content,
        'generated_at': datetime.now().isoformat()
    }

def generate_email_content(email_type, recipient_type, tone, purpose, context, business_name, sender_name):
    """
    Generate email content based on parameters
    """
    # Get email template based on type
    template = get_email_template(email_type, recipient_type)
    
    # Customize based on tone
    tone_adjustments = get_tone_adjustments(tone)
    
    # Generate subject line
    subject = generate_subject_line(email_type, purpose, business_name, tone)
    
    # Generate body
    body = generate_email_body(template, tone_adjustments, purpose, context, business_name, sender_name)
    
    # Generate signature
    signature = generate_signature(sender_name, business_name)
    
    return {
        'subject': subject,
        'body': body,
        'signature': signature,
        'full_email': f"Subject: {subject}\n\n{body}\n\n{signature}",
        'type': email_type,
        'tone': tone
    }

def get_email_template(email_type, recipient_type):
    """
    Get appropriate email template
    """
    templates = {
        'marketing': {
            'customer': {
                'greeting': "Dear [Customer Name]",
                'opening': "We hope this email finds you well.",
                'structure': ['introduction', 'value_proposition', 'call_to_action', 'closing'],
                'call_to_action': "Don't miss out on this opportunity!"
            },
            'prospect': {
                'greeting': "Hello [Name]",
                'opening': "I hope you're having a great day.",
                'structure': ['introduction', 'value_proposition', 'social_proof', 'call_to_action', 'closing'],
                'call_to_action': "I'd love to discuss how we can help you."
            }
        },
        'customer_service': {
            'customer': {
                'greeting': "Dear [Customer Name]",
                'opening': "Thank you for reaching out to us.",
                'structure': ['acknowledgment', 'solution', 'additional_help', 'closing'],
                'call_to_action': "Please don't hesitate to contact us if you need further assistance."
            }
        },
        'follow_up': {
            'customer': {
                'greeting': "Hi [Customer Name]",
                'opening': "I wanted to follow up on our recent interaction.",
                'structure': ['recap', 'next_steps', 'availability', 'closing'],
                'call_to_action': "I'm here to help with any questions you might have."
            },
            'prospect': {
                'greeting': "Hello [Name]",
                'opening': "I wanted to circle back on our previous conversation.",
                'structure': ['recap', 'value_reminder', 'next_steps', 'closing'],
                'call_to_action': "Would you like to schedule a brief call to discuss further?"
            }
        },
        'thank_you': {
            'customer': {
                'greeting': "Dear [Customer Name]",
                'opening': "Thank you so much for choosing us!",
                'structure': ['gratitude', 'recap', 'future_relationship', 'closing'],
                'call_to_action': "We look forward to serving you again."
            }
        },
        'announcement': {
            'customer': {
                'greeting': "Dear Valued Customer",
                'opening': "We're excited to share some news with you.",
                'structure': ['announcement', 'benefits', 'details', 'call_to_action', 'closing'],
                'call_to_action': "Learn more about what this means for you."
            }
        },
        'invitation': {
            'customer': {
                'greeting': "Dear [Customer Name]",
                'opening': "You're invited to join us for a special event!",
                'structure': ['invitation', 'event_details', 'benefits', 'rsvp', 'closing'],
                'call_to_action': "Please RSVP by [date] to secure your spot."
            }
        }
    }
    
    return templates.get(email_type, templates['marketing']).get(recipient_type, templates['marketing']['customer'])

def get_tone_adjustments(tone):
    """
    Get tone-specific language adjustments
    """
    adjustments = {
        'professional': {
            'formality': 'high',
            'pronouns': 'formal',
            'vocabulary': 'business',
            'punctuation': 'standard'
        },
        'friendly': {
            'formality': 'medium',
            'pronouns': 'casual',
            'vocabulary': 'conversational',
            'punctuation': 'relaxed'
        },
        'casual': {
            'formality': 'low',
            'pronouns': 'informal',
            'vocabulary': 'everyday',
            'punctuation': 'minimal'
        },
        'urgent': {
            'formality': 'medium',
            'pronouns': 'direct',
            'vocabulary': 'action-oriented',
            'punctuation': 'emphatic'
        },
        'formal': {
            'formality': 'very_high',
            'pronouns': 'formal',
            'vocabulary': 'sophisticated',
            'punctuation': 'precise'
        }
    }
    
    return adjustments.get(tone, adjustments['professional'])

def generate_subject_line(email_type, purpose, business_name, tone):
    """
    Generate appropriate subject line
    """
    subject_templates = {
        'marketing': [
            f"Exclusive offer from {business_name}",
            f"Transform your business with {business_name}",
            f"Special announcement from {business_name}",
            f"Don't miss out - {business_name}",
            f"Your solution is here - {business_name}"
        ],
        'customer_service': [
            f"Re: Your inquiry - {business_name}",
            f"Resolution for your concern - {business_name}",
            f"Update on your request - {business_name}",
            f"We're here to help - {business_name}"
        ],
        'follow_up': [
            f"Following up on our conversation",
            f"Next steps with {business_name}",
            f"Checking in - {business_name}",
            f"Your questions answered - {business_name}"
        ],
        'thank_you': [
            f"Thank you from {business_name}!",
            f"We appreciate you - {business_name}",
            f"Grateful for your business",
            f"Thank you for choosing us!"
        ],
        'announcement': [
            f"Important update from {business_name}",
            f"Exciting news from {business_name}",
            f"New announcement - {business_name}",
            f"What's new at {business_name}"
        ],
        'invitation': [
            f"You're invited! - {business_name}",
            f"Special event invitation - {business_name}",
            f"Join us for something special",
            f"Exclusive invitation from {business_name}"
        ]
    }
    
    # If purpose is provided, create custom subject
    if purpose:
        if tone == 'urgent':
            return f"URGENT: {purpose} - {business_name}"
        elif tone == 'friendly':
            return f"Hey! {purpose} - {business_name}"
        else:
            return f"{purpose} - {business_name}"
    
    # Use template
    templates = subject_templates.get(email_type, subject_templates['marketing'])
    return templates[0]  # Return the first template for consistency

def generate_email_body(template, tone_adjustments, purpose, context, business_name, sender_name):
    """
    Generate email body content
    """
    body_parts = []
    
    # Greeting
    body_parts.append(template['greeting'])
    body_parts.append("")  # Empty line
    
    # Opening
    body_parts.append(template['opening'])
    body_parts.append("")
    
    # Main content based on structure
    for section in template['structure']:
        section_content = generate_section_content(section, purpose, context, business_name, tone_adjustments)
        if section_content:
            body_parts.extend(section_content)
            body_parts.append("")
    
    # Call to action
    body_parts.append(template['call_to_action'])
    body_parts.append("")
    
    # Closing
    closing = get_closing_phrase(tone_adjustments['formality'])
    body_parts.append(closing)
    
    return "\n".join(body_parts)

def generate_section_content(section, purpose, context, business_name, tone_adjustments):
    """
    Generate content for specific email sections
    """
    formality = tone_adjustments['formality']
    
    content_generators = {
        'introduction': lambda: generate_introduction(business_name, purpose, formality),
        'value_proposition': lambda: generate_value_proposition(business_name, context, formality),
        'social_proof': lambda: generate_social_proof(business_name, formality),
        'call_to_action': lambda: generate_call_to_action(purpose, formality),
        'acknowledgment': lambda: generate_acknowledgment(context, formality),
        'solution': lambda: generate_solution(context, purpose, formality),
        'additional_help': lambda: generate_additional_help(formality),
        'recap': lambda: generate_recap(context, formality),
        'next_steps': lambda: generate_next_steps(purpose, formality),
        'availability': lambda: generate_availability(formality),
        'gratitude': lambda: generate_gratitude(formality),
        'future_relationship': lambda: generate_future_relationship(business_name, formality),
        'announcement': lambda: generate_announcement(purpose, context, formality),
        'benefits': lambda: generate_benefits(context, formality),
        'details': lambda: generate_details(context, formality),
        'invitation': lambda: generate_invitation(purpose, context, formality),
        'event_details': lambda: generate_event_details(context, formality),
        'rsvp': lambda: generate_rsvp(formality)
    }
    
    generator = content_generators.get(section, lambda: [])
    return generator()

def generate_introduction(business_name, purpose, formality):
    """Generate introduction section"""
    if formality == 'high' or formality == 'very_high':
        return [f"I am writing to you on behalf of {business_name} regarding {purpose or 'our services'}."]
    elif formality == 'low':
        return [f"Hope you're doing well! I wanted to tell you about {purpose or 'what we do at ' + business_name}."]
    else:
        return [f"I wanted to reach out and tell you about {purpose or 'how ' + business_name + ' can help you'}."]

def generate_value_proposition(business_name, context, formality):
    """Generate value proposition section"""
    if context:
        base_text = f"At {business_name}, we understand that {context.lower()}."
    else:
        base_text = f"At {business_name}, we specialize in delivering exceptional results for our clients."
    
    if formality == 'low':
        return [base_text + " We'd love to help you out!"]
    else:
        return [base_text + " We would be delighted to assist you in achieving your goals."]

def generate_social_proof(business_name, formality):
    """Generate social proof section"""
    if formality == 'high' or formality == 'very_high':
        return ["We have successfully served numerous clients across various industries, consistently delivering outstanding results."]
    else:
        return ["We've helped tons of businesses just like yours succeed and grow."]

def generate_call_to_action(purpose, formality):
    """Generate call to action section"""
    if formality == 'low':
        return ["Ready to get started? Let's chat!"]
    elif formality == 'high' or formality == 'very_high':
        return ["We would welcome the opportunity to discuss how we can assist you further."]
    else:
        return ["I'd love to discuss how we can help you achieve your goals."]

# Additional section generators
def generate_acknowledgment(context, formality):
    if context:
        return [f"I acknowledge your concern regarding {context.lower()}."]
    return ["I acknowledge your inquiry and appreciate you taking the time to contact us."]

def generate_solution(context, purpose, formality):
    if purpose:
        return [f"To address this, I recommend {purpose.lower()}."]
    return ["I have reviewed your situation and have identified the best solution for you."]

def generate_additional_help(formality):
    if formality == 'low':
        return ["Need anything else? Just let me know!"]
    return ["Should you require any additional assistance, please do not hesitate to reach out."]

def generate_recap(context, formality):
    if context:
        return [f"As we discussed, {context.lower()}."]
    return ["Following our recent conversation, I wanted to summarize the key points."]

def generate_next_steps(purpose, formality):
    if purpose:
        return [f"The next step would be to {purpose.lower()}."]
    return ["I suggest we schedule a follow-up meeting to discuss the next steps."]

def generate_availability(formality):
    if formality == 'low':
        return ["I'm available anytime this week if you want to chat!"]
    return ["I am available at your convenience to discuss this further."]

def generate_gratitude(formality):
    if formality == 'low':
        return ["Thanks so much for being awesome!"]
    return ["We sincerely appreciate your business and trust in our services."]

def generate_future_relationship(business_name, formality):
    if formality == 'low':
        return [f"Can't wait to work with you again soon!"]
    return [f"We look forward to continuing our partnership with you."]

def generate_announcement(purpose, context, formality):
    if purpose:
        return [f"We are pleased to announce that {purpose.lower()}."]
    return ["We have an exciting announcement to share with you."]

def generate_benefits(context, formality):
    if context:
        return [f"This means {context.lower()} for you."]
    return ["This development brings several benefits to our valued customers."]

def generate_details(context, formality):
    if context:
        return [f"Here are the important details: {context}"]
    return ["Please find the relevant details below."]

def generate_invitation(purpose, context, formality):
    if purpose:
        return [f"We would like to invite you to {purpose.lower()}."]
    return ["We cordially invite you to join us for this special occasion."]

def generate_event_details(context, formality):
    if context:
        return [f"Event details: {context}"]
    return ["Please see the event details below:"]

def generate_rsvp(formality):
    if formality == 'low':
        return ["Let us know if you can make it!"]
    return ["Kindly confirm your attendance at your earliest convenience."]

def get_closing_phrase(formality):
    """
    Get appropriate closing phrase based on formality
    """
    closings = {
        'very_high': "I remain, respectfully yours,",
        'high': "Thank you for your time and consideration.",
        'medium': "Thank you, and I look forward to hearing from you.",
        'low': "Thanks again, and talk soon!"
    }
    
    return closings.get(formality, closings['medium'])

def generate_signature(sender_name, business_name):
    """
    Generate email signature
    """
    signature_lines = [
        f"Best regards,",
        f"{sender_name}",
        f"{business_name}",
        "",
        "---",
        f"Email: info@{business_name.lower().replace(' ', '')}.com",
        f"Phone: +1 (555) 123-4567",
        f"Website: www.{business_name.lower().replace(' ', '')}.com"
    ]
    
    return "\n".join(signature_lines)

def get_email_suggestions(email_type, business_industry=None):
    """
    Get email suggestions and best practices
    """
    suggestions = {
        'marketing': {
            'best_practices': [
                "Keep subject lines under 50 characters",
                "Personalize the greeting with recipient's name",
                "Include a clear call-to-action",
                "Use bullet points for easy scanning",
                "Test different send times"
            ],
            'common_mistakes': [
                "Using too many exclamation points",
                "Writing overly long paragraphs",
                "Forgetting to include contact information",
                "Not mobile-optimizing the content"
            ]
        },
        'customer_service': {
            'best_practices': [
                "Acknowledge the customer's concern first",
                "Provide a clear solution or next steps",
                "Include relevant contact information",
                "Follow up to ensure satisfaction",
                "Maintain a helpful and empathetic tone"
            ],
            'common_mistakes': [
                "Being too formal or cold",
                "Not addressing the specific issue",
                "Providing generic responses",
                "Not following up"
            ]
        },
        'follow_up': {
            'best_practices': [
                "Reference previous conversation",
                "Provide additional value in each follow-up",
                "Be persistent but not pushy",
                "Include specific next steps",
                "Time follow-ups appropriately"
            ],
            'common_mistakes': [
                "Following up too frequently",
                "Not adding new value",
                "Being too aggressive",
                "Forgetting to follow up entirely"
            ]
        }
    }
    
    return suggestions.get(email_type, suggestions['marketing'])

def validate_email_content(email_content):
    """
    Validate and score email content quality
    """
    subject = email_content.get('subject', '')
    body = email_content.get('body', '')
    
    score = 0
    feedback = []
    
    # Subject line validation
    if len(subject) > 0:
        score += 10
        if len(subject) <= 50:
            score += 10
        else:
            feedback.append("Subject line is too long (over 50 characters)")
    else:
        feedback.append("Subject line is missing")
    
    # Body validation
    if len(body) > 0:
        score += 20
        
        # Check for greeting
        if any(greeting in body.lower() for greeting in ['dear', 'hello', 'hi']):
            score += 10
        else:
            feedback.append("Consider adding a personal greeting")
        
        # Check for call to action
        if any(cta in body.lower() for cta in ['contact', 'call', 'click', 'visit', 'schedule', 'book']):
            score += 15
        else:
            feedback.append("Consider adding a clear call-to-action")
        
        # Check for closing
        if any(closing in body.lower() for closing in ['regards', 'sincerely', 'thanks', 'best']):
            score += 10
        else:
            feedback.append("Consider adding a professional closing")
        
        # Check length (not too short, not too long)
        word_count = len(body.split())
        if 50 <= word_count <= 200:
            score += 15
        elif word_count < 50:
            feedback.append("Email might be too brief")
        else:
            feedback.append("Email might be too long")
    else:
        feedback.append("Email body is missing")
    
    # Determine grade
    if score >= 80:
        grade = 'A'
    elif score >= 70:
        grade = 'B'
    elif score >= 60:
        grade = 'C'
    else:
        grade = 'D'
    
    return {
        'score': score,
        'grade': grade,
        'feedback': feedback,
        'word_count': len(body.split()) if body else 0,
        'subject_length': len(subject)
    }