from datetime import datetime
import json

def create_poster_content(data):
    """
    Create poster content and design suggestions
    """
    poster_type = data.get('poster_type', 'promotional')
    title = data.get('title', 'Your Title Here')
    subtitle = data.get('subtitle', '')
    description = data.get('description', '')
    business_name = data.get('business_name', 'Your Business')
    color_scheme = data.get('color_scheme', 'modern')
    size = data.get('size', 'medium')
    
    # Generate poster design
    poster_design = generate_poster_design(
        poster_type, title, subtitle, description, business_name, color_scheme, size
    )
    
    return {
        'status': 'success',
        'poster': poster_design,
        'generated_at': datetime.now().isoformat()
    }

def generate_poster_design(poster_type, title, subtitle, description, business_name, color_scheme, size):
    """
    Generate poster design with HTML/CSS
    """
    colors = get_poster_colors(color_scheme)
    dimensions = get_poster_dimensions(size)
    layout = get_poster_layout(poster_type)
    
    # Generate HTML structure
    html_content = generate_poster_html(
        layout, title, subtitle, description, business_name, colors, dimensions
    )
    
    # Generate CSS styles
    css_content = generate_poster_css(colors, dimensions, poster_type)
    
    return {
        'html': html_content,
        'css': css_content,
        'colors': colors,
        'dimensions': dimensions,
        'type': poster_type,
        'download_formats': ['PNG', 'JPG', 'PDF'],
        'print_ready': True
    }

def get_poster_colors(color_scheme):
    """
    Get color palette for poster
    """
    color_schemes = {
        'modern': {
            'primary': '#1a1a1a',
            'secondary': '#ffffff',
            'accent': '#ff6b6b',
            'background': '#f8f9fa',
            'text': '#2c3e50',
            'highlight': '#3498db'
        },
        'vibrant': {
            'primary': '#e74c3c',
            'secondary': '#f39c12',
            'accent': '#9b59b6',
            'background': '#ecf0f1',
            'text': '#2c3e50',
            'highlight': '#1abc9c'
        },
        'professional': {
            'primary': '#2c3e50',
            'secondary': '#34495e',
            'accent': '#3498db',
            'background': '#ffffff',
            'text': '#2c3e50',
            'highlight': '#e74c3c'
        },
        'nature': {
            'primary': '#27ae60',
            'secondary': '#2ecc71',
            'accent': '#f39c12',
            'background': '#e8f5e8',
            'text': '#1e3a32',
            'highlight': '#e67e22'
        },
        'creative': {
            'primary': '#8e44ad',
            'secondary': '#9b59b6',
            'accent': '#e74c3c',
            'background': '#f4f1f8',
            'text': '#2c3e50',
            'highlight': '#f39c12'
        },
        'minimalist': {
            'primary': '#000000',
            'secondary': '#ffffff',
            'accent': '#808080',
            'background': '#ffffff',
            'text': '#333333',
            'highlight': '#cccccc'
        }
    }
    
    return color_schemes.get(color_scheme, color_schemes['modern'])

def get_poster_dimensions(size):
    """
    Get poster dimensions based on size
    """
    dimensions = {
        'small': {'width': '400px', 'height': '600px', 'dpi': 300},
        'medium': {'width': '600px', 'height': '800px', 'dpi': 300},
        'large': {'width': '800px', 'height': '1200px', 'dpi': 300},
        'a4': {'width': '595px', 'height': '842px', 'dpi': 300},
        'letter': {'width': '612px', 'height': '792px', 'dpi': 300},
        'social_media': {'width': '1080px', 'height': '1080px', 'dpi': 72}
    }
    
    return dimensions.get(size, dimensions['medium'])

def get_poster_layout(poster_type):
    """
    Get layout structure based on poster type
    """
    layouts = {
        'promotional': {
            'sections': ['header', 'main_content', 'features', 'call_to_action', 'footer'],
            'emphasis': 'call_to_action',
            'image_areas': 2
        },
        'event': {
            'sections': ['title', 'event_details', 'description', 'registration', 'footer'],
            'emphasis': 'event_details',
            'image_areas': 1
        },
        'product': {
            'sections': ['product_image', 'title', 'features', 'price', 'contact'],
            'emphasis': 'product_image',
            'image_areas': 3
        },
        'service': {
            'sections': ['header', 'service_list', 'benefits', 'contact', 'footer'],
            'emphasis': 'service_list',
            'image_areas': 1
        },
        'announcement': {
            'sections': ['announcement', 'details', 'impact', 'next_steps', 'contact'],
            'emphasis': 'announcement',
            'image_areas': 1
        }
    }
    
    return layouts.get(poster_type, layouts['promotional'])

def generate_poster_html(layout, title, subtitle, description, business_name, colors, dimensions):
    """
    Generate HTML structure for poster
    """
    sections_html = []
    
    for section in layout['sections']:
        section_html = generate_section_html(
            section, title, subtitle, description, business_name, layout['emphasis'] == section
        )
        if section_html:
            sections_html.append(section_html)
    
    html_template = f"""
    <div class="poster-container" style="width: {dimensions['width']}; height: {dimensions['height']};">
        <div class="poster-content">
            {''.join(sections_html)}
        </div>
    </div>
    """
    
    return html_template

def generate_section_html(section, title, subtitle, description, business_name, is_emphasis):
    """
    Generate HTML for individual sections
    """
    emphasis_class = 'emphasis-section' if is_emphasis else ''
    
    section_generators = {
        'header': f'''
        <div class="section header-section {emphasis_class}">
            <h1 class="poster-title">{title}</h1>
            {f'<h2 class="poster-subtitle">{subtitle}</h2>' if subtitle else ''}
        </div>
        ''',
        
        'main_content': f'''
        <div class="section main-content-section {emphasis_class}">
            <div class="content-text">
                <p class="description">{description or "Transform your business with our professional services. We deliver exceptional results that exceed expectations."}</p>
            </div>
        </div>
        ''',
        
        'features': f'''
        <div class="section features-section {emphasis_class}">
            <h3>Why Choose Us?</h3>
            <ul class="feature-list">
                <li><i class="icon">✓</i> Professional Excellence</li>
                <li><i class="icon">✓</i> Proven Results</li>
                <li><i class="icon">✓</i> Customer Satisfaction</li>
                <li><i class="icon">✓</i> Competitive Pricing</li>
            </ul>
        </div>
        ''',
        
        'call_to_action': f'''
        <div class="section cta-section {emphasis_class}">
            <div class="cta-content">
                <h3 class="cta-title">Ready to Get Started?</h3>
                <p class="cta-text">Contact us today for a free consultation!</p>
                <div class="cta-button">CALL NOW</div>
            </div>
        </div>
        ''',
        
        'footer': f'''
        <div class="section footer-section">
            <div class="business-info">
                <h4 class="business-name">{business_name}</h4>
                <div class="contact-info">
                    <p>📞 (555) 123-4567</p>
                    <p>✉️ info@{business_name.lower().replace(' ', '')}.com</p>
                    <p>🌐 www.{business_name.lower().replace(' ', '')}.com</p>
                </div>
            </div>
        </div>
        ''',
        
        'title': f'''
        <div class="section title-section {emphasis_class}">
            <h1 class="event-title">{title}</h1>
            {f'<p class="event-subtitle">{subtitle}</p>' if subtitle else ''}
        </div>
        ''',
        
        'event_details': f'''
        <div class="section event-details-section {emphasis_class}">
            <div class="event-info">
                <div class="detail-item">
                    <span class="detail-label">📅 Date:</span>
                    <span class="detail-value">Coming Soon</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">🕐 Time:</span>
                    <span class="detail-value">TBA</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">📍 Location:</span>
                    <span class="detail-value">To Be Announced</span>
                </div>
            </div>
        </div>
        ''',
        
        'product_image': f'''
        <div class="section product-image-section {emphasis_class}">
            <div class="product-placeholder">
                <div class="placeholder-content">
                    <i class="product-icon">📦</i>
                    <p>Product Image</p>
                </div>
            </div>
        </div>
        ''',
        
        'service_list': f'''
        <div class="section services-section {emphasis_class}">
            <h3>Our Services</h3>
            <div class="services-grid">
                <div class="service-item">
                    <i class="service-icon">🔧</i>
                    <h4>Professional Service</h4>
                </div>
                <div class="service-item">
                    <i class="service-icon">⭐</i>
                    <h4>Quality Guarantee</h4>
                </div>
                <div class="service-item">
                    <i class="service-icon">🚀</i>
                    <h4>Fast Delivery</h4>
                </div>
                <div class="service-item">
                    <i class="service-icon">💼</i>
                    <h4>Expert Support</h4>
                </div>
            </div>
        </div>
        '''
    }
    
    return section_generators.get(section, f'<div class="section {section}-section"></div>')

def generate_poster_css(colors, dimensions, poster_type):
    """
    Generate CSS styles for poster
    """
    css_template = f"""
    .poster-container {{
        width: {dimensions['width']};
        height: {dimensions['height']};
        background: {colors['background']};
        color: {colors['text']};
        font-family: 'Arial', sans-serif;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-radius: 8px;
    }}
    
    .poster-content {{
        height: 100%;
        display: flex;
        flex-direction: column;
        padding: 30px;
        box-sizing: border-box;
    }}
    
    .section {{
        margin-bottom: 20px;
        text-align: center;
    }}
    
    /* Header Styles */
    .header-section {{
        background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
        color: {colors['secondary']};
        padding: 40px 20px;
        margin: -30px -30px 30px -30px;
        border-radius: 8px 8px 0 0;
    }}
    
    .poster-title {{
        font-size: 2.5em;
        font-weight: bold;
        margin: 0 0 10px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        color: white;
    }}
    
    .poster-subtitle {{
        font-size: 1.2em;
        margin: 0;
        opacity: 0.9;
        color: white;
    }}
    
    /* Main Content */
    .main-content-section {{
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    
    .description {{
        font-size: 1.1em;
        line-height: 1.6;
        margin: 0;
        max-width: 80%;
    }}
    
    /* Features */
    .features-section h3 {{
        color: {colors['primary']};
        font-size: 1.5em;
        margin-bottom: 20px;
    }}
    
    .feature-list {{
        list-style: none;
        padding: 0;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        max-width: 80%;
        margin: 0 auto;
    }}
    
    .feature-list li {{
        display: flex;
        align-items: center;
        font-size: 1em;
        padding: 10px;
        background: rgba({hex_to_rgb(colors['accent'])}, 0.1);
        border-radius: 5px;
    }}
    
    .feature-list .icon {{
        color: {colors['accent']};
        font-weight: bold;
        margin-right: 10px;
        font-size: 1.2em;
    }}
    
    /* Call to Action */
    .cta-section {{
        background: {colors['accent']};
        color: white;
        padding: 30px;
        margin: 20px -30px -30px -30px;
        border-radius: 0 0 8px 8px;
    }}
    
    .cta-title {{
        font-size: 1.8em;
        margin: 0 0 10px 0;
        font-weight: bold;
    }}
    
    .cta-text {{
        font-size: 1.1em;
        margin: 0 0 20px 0;
    }}
    
    .cta-button {{
        background: white;
        color: {colors['accent']};
        padding: 15px 30px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.1em;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        cursor: pointer;
        transition: transform 0.3s ease;
    }}
    
    .cta-button:hover {{
        transform: translateY(-2px);
    }}
    
    /* Footer */
    .footer-section {{
        background: {colors['primary']};
        color: white;
        padding: 20px;
        margin: 20px -30px -30px -30px;
    }}
    
    .business-name {{
        font-size: 1.3em;
        margin: 0 0 15px 0;
        font-weight: bold;
    }}
    
    .contact-info p {{
        margin: 5px 0;
        font-size: 0.9em;
    }}
    
    /* Event Styles */
    .event-title {{
        font-size: 2.2em;
        color: {colors['primary']};
        margin: 0 0 15px 0;
        font-weight: bold;
    }}
    
    .event-subtitle {{
        font-size: 1.1em;
        color: {colors['text']};
        margin: 0;
    }}
    
    .event-details-section {{
        background: rgba({hex_to_rgb(colors['primary'])}, 0.1);
        padding: 30px;
        border-radius: 10px;
        margin: 20px 0;
    }}
    
    .detail-item {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid rgba({hex_to_rgb(colors['primary'])}, 0.2);
        font-size: 1.1em;
    }}
    
    .detail-item:last-child {{
        border-bottom: none;
    }}
    
    .detail-label {{
        font-weight: bold;
        color: {colors['primary']};
    }}
    
    /* Product Styles */
    .product-placeholder {{
        background: {colors['highlight']};
        height: 200px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.2em;
    }}
    
    .product-icon {{
        font-size: 3em;
        display: block;
        margin-bottom: 10px;
    }}
    
    /* Services Grid */
    .services-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-top: 20px;
    }}
    
    .service-item {{
        background: rgba({hex_to_rgb(colors['primary'])}, 0.1);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }}
    
    .service-icon {{
        font-size: 2em;
        display: block;
        margin-bottom: 10px;
    }}
    
    .service-item h4 {{
        margin: 0;
        color: {colors['primary']};
        font-size: 1em;
    }}
    
    /* Emphasis Section */
    .emphasis-section {{
        position: relative;
        overflow: visible;
    }}
    
    .emphasis-section::before {{
        content: '';
        position: absolute;
        top: -5px;
        left: -5px;
        right: -5px;
        bottom: -5px;
        background: linear-gradient(45deg, {colors['accent']}, {colors['highlight']});
        z-index: -1;
        border-radius: 10px;
        opacity: 0.3;
    }}
    
    /* Responsive adjustments for smaller posters */
    @media (max-width: 500px) {{
        .poster-title {{
            font-size: 2em;
        }}
        
        .feature-list {{
            grid-template-columns: 1fr;
        }}
        
        .services-grid {{
            grid-template-columns: 1fr;
        }}
    }}
    """
    
    return css_template

def hex_to_rgb(hex_color):
    """
    Convert hex color to RGB values
    """
    hex_color = hex_color.lstrip('#')
    return ','.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))

def get_poster_templates():
    """
    Get predefined poster templates
    """
    templates = {
        'business_promotion': {
            'title': 'Transform Your Business Today',
            'subtitle': 'Professional Services That Deliver Results',
            'description': 'We help businesses achieve their goals with expert consultation and proven strategies.',
            'type': 'promotional',
            'color_scheme': 'professional'
        },
        'grand_opening': {
            'title': 'Grand Opening!',
            'subtitle': 'Join Us for Our Special Day',
            'description': 'Celebrate with us as we open our doors to serve the community.',
            'type': 'event',
            'color_scheme': 'vibrant'
        },
        'sale_event': {
            'title': 'MEGA SALE',
            'subtitle': 'Up to 50% Off Everything',
            'description': 'Limited time offer on all products and services.',
            'type': 'promotional',
            'color_scheme': 'modern'
        },
        'workshop': {
            'title': 'Professional Workshop',
            'subtitle': 'Learn From Industry Experts',
            'description': 'Join our comprehensive workshop to enhance your skills.',
            'type': 'event',
            'color_scheme': 'creative'
        },
        'product_launch': {
            'title': 'New Product Launch',
            'subtitle': 'Innovation Meets Excellence',
            'description': 'Introducing our latest product designed for your success.',
            'type': 'product',
            'color_scheme': 'modern'
        }
    }
    
    return templates

def get_design_suggestions(poster_type, business_industry=None):
    """
    Get design suggestions based on poster type and industry
    """
    suggestions = {
        'promotional': {
            'fonts': ['Bold sans-serif for headlines', 'Clean serif for body text'],
            'colors': ['Use contrasting colors', 'Limit to 3-4 colors maximum'],
            'layout': ['Eye-catching headline', 'Clear call-to-action', 'Balanced white space'],
            'images': ['High-quality product photos', 'Professional lifestyle images']
        },
        'event': {
            'fonts': ['Large, readable fonts', 'Consistent font hierarchy'],
            'colors': ['Event-appropriate colors', 'High contrast for readability'],
            'layout': ['Clear event details', 'Easy-to-scan information', 'Prominent date/time'],
            'images': ['Event venue photos', 'Speaker headshots', 'Previous event photos']
        },
        'product': {
            'fonts': ['Modern, clean typography', 'Product name prominence'],
            'colors': ['Brand-consistent colors', 'Product-complementary palette'],
            'layout': ['Product as focal point', 'Feature highlights', 'Clear pricing'],
            'images': ['High-resolution product photos', 'Multiple product angles']
        }
    }
    
    return suggestions.get(poster_type, suggestions['promotional'])