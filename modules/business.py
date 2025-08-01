from datetime import datetime

def save_business_info(user_id, business_data, business_db):
    """
    Save business information for a user
    """
    business_db[user_id] = {
        'business_name': business_data.get('business_name', ''),
        'industry': business_data.get('industry', ''),
        'description': business_data.get('description', ''),
        'target_audience': business_data.get('target_audience', ''),
        'goals': business_data.get('goals', []),
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    return True

def get_business_info(user_id, business_db):
    """
    Get business information for a user
    """
    return business_db.get(user_id)

def update_business_info(user_id, updates, business_db):
    """
    Update business information
    """
    if user_id in business_db:
        business_db[user_id].update(updates)
        business_db[user_id]['updated_at'] = datetime.now()
        return True
    return False

def get_business_profile(user_id, business_db):
    """
    Get formatted business profile
    """
    business_info = business_db.get(user_id)
    if not business_info:
        return None
    
    # Format goals list
    if isinstance(business_info.get('goals'), list):
        goals_formatted = ', '.join(business_info['goals'])
    else:
        goals_formatted = business_info.get('goals', '')
    
    return {
        'business_name': business_info.get('business_name', 'Not specified'),
        'industry': business_info.get('industry', 'Not specified'),
        'description': business_info.get('description', 'No description provided'),
        'target_audience': business_info.get('target_audience', 'Not specified'),
        'goals': goals_formatted,
        'created_at': business_info.get('created_at'),
        'updated_at': business_info.get('updated_at')
    }

def get_industry_insights(industry):
    """
    Get insights and tips based on industry
    """
    industry_tips = {
        'retail': [
            'Focus on visual merchandising and product photography',
            'Implement customer loyalty programs',
            'Use social media for product showcases'
        ],
        'food_beverage': [
            'Highlight fresh ingredients and preparation methods',
            'Showcase customer reviews and testimonials',
            'Create seasonal menu promotions'
        ],
        'healthcare': [
            'Emphasize credentials and certifications',
            'Focus on patient testimonials and success stories',
            'Highlight safety and hygiene protocols'
        ],
        'technology': [
            'Showcase technical expertise and case studies',
            'Highlight innovation and cutting-edge solutions',
            'Focus on problem-solving capabilities'
        ],
        'consulting': [
            'Demonstrate expertise through thought leadership',
            'Showcase client success stories',
            'Highlight specialized knowledge areas'
        ]
    }
    
    return industry_tips.get(industry, [
        'Focus on your unique value proposition',
        'Build strong customer relationships',
        'Maintain consistent brand messaging'
    ])

def generate_business_summary(business_info):
    """
    Generate a business summary for AI tools
    """
    if not business_info:
        return "A professional business"
    
    summary = f"{business_info.get('business_name', 'This business')}"
    
    if business_info.get('industry'):
        summary += f" in the {business_info['industry']} industry"
    
    if business_info.get('description'):
        summary += f". {business_info['description']}"
    
    if business_info.get('target_audience'):
        summary += f" They serve {business_info['target_audience']}"
    
    return summary