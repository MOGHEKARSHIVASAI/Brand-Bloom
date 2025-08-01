import re
import json
from datetime import datetime
from collections import Counter

def analyze_feedback(feedback_text):
    """
    Analyze customer feedback and return insights
    """
    if not feedback_text or not feedback_text.strip():
        return {
            'error': 'No feedback text provided',
            'status': 'error'
        }
    
    # Clean and prepare text
    cleaned_text = clean_text(feedback_text)
    
    # Perform analysis
    sentiment_analysis = analyze_sentiment(cleaned_text)
    keyword_analysis = extract_keywords(cleaned_text)
    theme_analysis = identify_themes(cleaned_text)
    emotion_analysis = analyze_emotions(cleaned_text)
    actionable_insights = generate_insights(sentiment_analysis, keyword_analysis, theme_analysis)
    
    # Generate summary
    summary = generate_summary(sentiment_analysis, theme_analysis, len(cleaned_text.split()))
    
    return {
        'status': 'success',
        'analysis': {
            'sentiment': sentiment_analysis,
            'keywords': keyword_analysis,
            'themes': theme_analysis,
            'emotions': emotion_analysis,
            'insights': actionable_insights,
            'summary': summary,
            'word_count': len(cleaned_text.split()),
            'analyzed_at': datetime.now().isoformat()
        }
    }

def clean_text(text):
    """
    Clean and normalize text for analysis
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove special characters but keep punctuation for sentiment
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    return text

def analyze_sentiment(text):
    """
    Basic sentiment analysis using keyword matching
    """
    positive_words = [
        'excellent', 'amazing', 'fantastic', 'great', 'wonderful', 'outstanding',
        'perfect', 'love', 'awesome', 'brilliant', 'superb', 'good', 'best',
        'happy', 'satisfied', 'pleased', 'impressed', 'recommend', 'helpful',
        'friendly', 'professional', 'quality', 'fast', 'efficient', 'reliable'
    ]
    
    negative_words = [
        'terrible', 'awful', 'horrible', 'bad', 'worst', 'hate', 'disappointing',
        'poor', 'useless', 'broken', 'slow', 'expensive', 'rude', 'unprofessional',
        'delayed', 'frustrated', 'angry', 'upset', 'dissatisfied', 'complaint',
        'problem', 'issue', 'error', 'wrong', 'failed', 'difficult'
    ]
    
    neutral_words = [
        'okay', 'average', 'normal', 'standard', 'typical', 'regular',
        'fine', 'acceptable', 'adequate', 'decent'
    ]
    
    words = text.split()
    
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    neutral_count = sum(1 for word in words if word in neutral_words)
    
    total_sentiment_words = positive_count + negative_count + neutral_count
    
    if total_sentiment_words == 0:
        sentiment_score = 0
        sentiment_label = 'neutral'
    else:
        sentiment_score = (positive_count - negative_count) / max(total_sentiment_words, 1)
        
        if sentiment_score > 0.2:
            sentiment_label = 'positive'
        elif sentiment_score < -0.2:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
    
    confidence = min(total_sentiment_words / max(len(words), 1), 1.0)
    
    return {
        'label': sentiment_label,
        'score': round(sentiment_score, 3),
        'confidence': round(confidence, 3),
        'positive_words': positive_count,
        'negative_words': negative_count,
        'neutral_words': neutral_count
    }

def extract_keywords(text):
    """
    Extract important keywords and phrases
    """
    # Common stop words to filter out
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'was', 'are', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us',
        'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'this',
        'that', 'these', 'those', 'very', 'really', 'quite', 'just', 'only'
    }
    
    # Split into words and filter
    words = [word for word in text.split() if len(word) > 2 and word not in stop_words]
    
    # Count word frequency
    word_freq = Counter(words)
    
    # Get top keywords
    top_keywords = word_freq.most_common(10)
    
    # Identify business-related keywords
    business_keywords = identify_business_keywords(words)
    
    return {
        'top_keywords': [{'word': word, 'count': count} for word, count in top_keywords],
        'business_keywords': business_keywords,
        'total_unique_words': len(word_freq)
    }

def identify_business_keywords(words):
    """
    Identify business-related keywords
    """
    business_categories = {
        'service': ['service', 'support', 'help', 'assistance', 'staff', 'team', 'employee'],
        'product': ['product', 'item', 'goods', 'merchandise', 'quality', 'features'],
        'price': ['price', 'cost', 'expensive', 'cheap', 'value', 'money', 'affordable'],
        'delivery': ['delivery', 'shipping', 'fast', 'slow', 'quick', 'delayed', 'arrived'],
        'experience': ['experience', 'visit', 'time', 'process', 'easy', 'difficult', 'smooth'],
        'communication': ['communication', 'response', 'contact', 'email', 'phone', 'chat']
    }
    
    found_keywords = {}
    for category, keywords in business_categories.items():
        matches = [word for word in words if word in keywords]
        if matches:
            found_keywords[category] = list(set(matches))
    
    return found_keywords

def identify_themes(text):
    """
    Identify main themes in the feedback
    """
    theme_patterns = {
        'customer_service': [
            'staff', 'service', 'help', 'support', 'employee', 'representative',
            'friendly', 'rude', 'helpful', 'professional', 'unprofessional'
        ],
        'product_quality': [
            'quality', 'product', 'item', 'goods', 'broken', 'defective',
            'excellent', 'poor', 'good', 'bad', 'working', 'faulty'
        ],
        'pricing': [
            'price', 'cost', 'expensive', 'cheap', 'value', 'money',
            'affordable', 'overpriced', 'reasonable', 'worth'
        ],
        'delivery_shipping': [
            'delivery', 'shipping', 'arrived', 'delayed', 'fast', 'slow',
            'quick', 'on time', 'late', 'package', 'order'
        ],
        'user_experience': [
            'easy', 'difficult', 'simple', 'complicated', 'smooth', 'frustrating',
            'confusing', 'clear', 'website', 'app', 'interface'
        ],
        'communication': [
            'communication', 'response', 'contact', 'reply', 'answer',
            'information', 'update', 'notification', 'email', 'phone'
        ]
    }
    
    theme_scores = {}
    words = text.split()
    
    for theme, keywords in theme_patterns.items():
        score = sum(1 for word in words if word in keywords)
        if score > 0:
            theme_scores[theme] = {
                'score': score,
                'percentage': round((score / len(words)) * 100, 2),
                'matched_words': [word for word in words if word in keywords]
            }
    
    # Sort themes by score
    sorted_themes = dict(sorted(theme_scores.items(), key=lambda x: x[1]['score'], reverse=True))
    
    return sorted_themes

def analyze_emotions(text):
    """
    Analyze emotional tone of the feedback
    """
    emotion_keywords = {
        'joy': ['happy', 'excited', 'thrilled', 'delighted', 'pleased', 'satisfied', 'love'],
        'anger': ['angry', 'furious', 'mad', 'irritated', 'frustrated', 'annoyed', 'upset'],
        'sadness': ['sad', 'disappointed', 'unhappy', 'depressed', 'hurt', 'devastated'],
        'fear': ['worried', 'concerned', 'anxious', 'scared', 'nervous', 'afraid'],
        'surprise': ['surprised', 'amazed', 'shocked', 'astonished', 'unexpected'],
        'disgust': ['disgusted', 'appalled', 'revolted', 'sickened', 'awful', 'terrible']
    }
    
    detected_emotions = {}
    words = text.split()
    
    for emotion, keywords in emotion_keywords.items():
        count = sum(1 for word in words if word in keywords)
        if count > 0:
            detected_emotions[emotion] = {
                'intensity': count,
                'keywords_found': [word for word in words if word in keywords]
            }
    
    # Determine primary emotion
    if detected_emotions:
        primary_emotion = max(detected_emotions.items(), key=lambda x: x[1]['intensity'])
        primary_emotion_name = primary_emotion[0]
        primary_emotion_intensity = primary_emotion[1]['intensity']
    else:
        primary_emotion_name = 'neutral'
        primary_emotion_intensity = 0
    
    return {
        'primary_emotion': primary_emotion_name,
        'intensity': primary_emotion_intensity,
        'all_emotions': detected_emotions
    }

def generate_insights(sentiment, keywords, themes):
    """
    Generate actionable insights based on analysis
    """
    insights = []
    
    # Sentiment-based insights
    if sentiment['label'] == 'positive':
        insights.append({
            'type': 'positive',
            'category': 'sentiment',
            'message': 'Customer sentiment is positive! Consider highlighting the praised aspects in marketing.',
            'priority': 'low'
        })
    elif sentiment['label'] == 'negative':
        insights.append({
            'type': 'negative',
            'category': 'sentiment',
            'message': 'Negative sentiment detected. Immediate attention needed to address customer concerns.',
            'priority': 'high'
        })
    
    # Theme-based insights
    for theme, data in themes.items():
        if data['score'] >= 2:  # Significant mention
            if theme == 'customer_service' and any(word in ['rude', 'unprofessional', 'unhelpful'] for word in data['matched_words']):
                insights.append({
                    'type': 'improvement',
                    'category': 'customer_service',
                    'message': 'Customer service issues mentioned. Consider additional staff training.',
                    'priority': 'medium'
                })
            elif theme == 'product_quality' and any(word in ['broken', 'defective', 'poor'] for word in data['matched_words']):
                insights.append({
                    'type': 'improvement',
                    'category': 'product_quality',
                    'message': 'Product quality concerns raised. Review quality control processes.',
                    'priority': 'high'
                })
            elif theme == 'pricing' and any(word in ['expensive', 'overpriced'] for word in data['matched_words']):
                insights.append({
                    'type': 'improvement',
                    'category': 'pricing',
                    'message': 'Pricing concerns mentioned. Consider value communication or pricing review.',
                    'priority': 'medium'
                })
    
    # Keyword-based insights
    business_keywords = keywords.get('business_keywords', {})
    if 'delivery' in business_keywords:
        insights.append({
            'type': 'neutral',
            'category': 'delivery',
            'message': 'Delivery mentioned frequently. Monitor shipping performance metrics.',
            'priority': 'low'
        })
    
    return insights

def generate_summary(sentiment, themes, word_count):
    """
    Generate a summary of the feedback analysis
    """
    summary_parts = []
    
    # Sentiment summary
    sentiment_desc = {
        'positive': 'The feedback shows positive sentiment',
        'negative': 'The feedback shows negative sentiment',
        'neutral': 'The feedback shows neutral sentiment'
    }
    summary_parts.append(sentiment_desc[sentiment['label']])
    
    # Theme summary
    if themes:
        top_theme = list(themes.keys())[0]
        theme_names = {
            'customer_service': 'customer service',
            'product_quality': 'product quality',
            'pricing': 'pricing',
            'delivery_shipping': 'delivery and shipping',
            'user_experience': 'user experience',
            'communication': 'communication'
        }
        theme_name = theme_names.get(top_theme, top_theme.replace('_', ' '))
        summary_parts.append(f"with primary focus on {theme_name}")
    
    # Word count summary
    if word_count < 50:
        length_desc = "This is a brief feedback"
    elif word_count < 150:
        length_desc = "This is a moderate-length feedback"
    else:
        length_desc = "This is a detailed feedback"
    
    summary_parts.append(f"({length_desc} with {word_count} words)")
    
    return '. '.join(summary_parts) + '.'