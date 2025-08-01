import json
from datetime import datetime

def generate_website_content(data):
    """
    Generate website content based on business information
    """
    # Extract data
    website_type = data.get('websiteType', 'business')
    business_name = data.get('businessName', 'Your Business')
    description = data.get('businessDescription', '')
    services = data.get('keyServices', '').split(',') if data.get('keyServices') else []
    target_audience = data.get('targetAudience', '')
    color_scheme = data.get('colorScheme', 'professional')
    
    # Generate website structure
    website_content = {
        'html': generate_html_content(business_name, description, services, website_type, color_scheme),
        'css': generate_css_styles(color_scheme),
        'metadata': {
            'title': f"{business_name} - Professional {website_type.title()} Website",
            'description': description or f"Professional {website_type} website for {business_name}",
            'generated_at': datetime.now().isoformat()
        }
    }
    
    return website_content

def generate_html_content(business_name, description, services, website_type, color_scheme):
    """
    Generate HTML content for the website
    """
    colors = get_color_scheme(color_scheme)
    
    # Clean services list
    services = [service.strip() for service in services if service.strip()]
    if not services:
        services = get_default_services(website_type)
    
    # Generate services HTML
    services_html = ""
    for service in services[:6]:  # Limit to 6 services
        services_html += f"""
        <div class="service-card">
            <div class="service-icon">
                <i class="fas fa-star"></i>
            </div>
            <h3>{service}</h3>
            <p>Professional {service.lower()} services tailored to meet your specific needs and exceed expectations.</p>
        </div>
        """
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{business_name}</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            {generate_inline_css(colors)}
        </style>
    </head>
    <body>
        <header class="hero">
            <nav class="navbar">
                <div class="nav-brand">
                    <h2>{business_name}</h2>
                </div>
                <ul class="nav-links">
                    <li><a href="#home">Home</a></li>
                    <li><a href="#services">Services</a></li>
                    <li><a href="#about">About</a></li>
                    <li><a href="#contact">Contact</a></li>
                </ul>
            </nav>
            
            <div class="hero-content">
                <h1>Welcome to {business_name}</h1>
                <p class="hero-description">{description or f"Your trusted partner for professional {website_type} services"}</p>
                <div class="hero-buttons">
                    <a href="#services" class="btn-primary">Our Services</a>
                    <a href="#contact" class="btn-secondary">Get In Touch</a>
                </div>
            </div>
        </header>
        
        <section id="services" class="services-section">
            <div class="container">
                <h2 class="section-title">Our Services</h2>
                <p class="section-subtitle">We provide comprehensive solutions to help your business thrive</p>
                <div class="services-grid">
                    {services_html}
                </div>
            </div>
        </section>
        
        <section id="about" class="about-section">
            <div class="container">
                <div class="about-content">
                    <div class="about-text">
                        <h2>About {business_name}</h2>
                        <p>{description or f"We are a professional {website_type} company dedicated to providing exceptional services to our clients. With years of experience and a commitment to excellence, we strive to exceed expectations in everything we do."}</p>
                        <div class="features">
                            <div class="feature">
                                <i class="fas fa-check-circle"></i>
                                <span>Professional Excellence</span>
                            </div>
                            <div class="feature">
                                <i class="fas fa-users"></i>
                                <span>Expert Team</span>
                            </div>
                            <div class="feature">
                                <i class="fas fa-clock"></i>
                                <span>Timely Delivery</span>
                            </div>
                        </div>
                    </div>
                    <div class="about-image">
                        <div class="placeholder-image">
                            <i class="fas fa-building fa-4x"></i>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <section id="contact" class="contact-section">
            <div class="container">
                <h2 class="section-title">Get In Touch</h2>
                <p class="section-subtitle">Ready to start your project? Contact us today!</p>
                <div class="contact-content">
                    <div class="contact-info">
                        <div class="contact-item">
                            <i class="fas fa-phone"></i>
                            <div>
                                <h4>Phone</h4>
                                <p>+1 (555) 123-4567</p>
                            </div>
                        </div>
                        <div class="contact-item">
                            <i class="fas fa-envelope"></i>
                            <div>
                                <h4>Email</h4>
                                <p>info@{business_name.lower().replace(' ', '')}.com</p>
                            </div>
                        </div>
                        <div class="contact-item">
                            <i class="fas fa-map-marker-alt"></i>
                            <div>
                                <h4>Address</h4>
                                <p>123 Business Street<br>City, State 12345</p>
                            </div>
                        </div>
                    </div>
                    <div class="contact-form">
                        <form>
                            <div class="form-group">
                                <input type="text" placeholder="Your Name" required>
                            </div>
                            <div class="form-group">
                                <input type="email" placeholder="Your Email" required>
                            </div>
                            <div class="form-group">
                                <textarea placeholder="Your Message" rows="5" required></textarea>
                            </div>
                            <button type="submit" class="btn-primary">Send Message</button>
                        </form>
                    </div>
                </div>
            </div>
        </section>
        
        <footer class="footer">
            <div class="container">
                <div class="footer-content">
                    <div class="footer-info">
                        <h3>{business_name}</h3>
                        <p>Your trusted partner for professional services.</p>
                    </div>
                    <div class="footer-links">
                        <div class="footer-column">
                            <h4>Services</h4>
                            <ul>
                                {chr(10).join([f'<li><a href="#">{service}</a></li>' for service in services[:4]])}
                            </ul>
                        </div>
                        <div class="footer-column">
                            <h4>Company</h4>
                            <ul>
                                <li><a href="#about">About Us</a></li>
                                <li><a href="#contact">Contact</a></li>
                                <li><a href="#">Privacy Policy</a></li>
                                <li><a href="#">Terms of Service</a></li>
                            </ul>
                        </div>
                        <div class="footer-column">
                            <h4>Follow Us</h4>
                            <div class="social-links">
                                <a href="#"><i class="fab fa-facebook"></i></a>
                                <a href="#"><i class="fab fa-twitter"></i></a>
                                <a href="#"><i class="fab fa-linkedin"></i></a>
                                <a href="#"><i class="fab fa-instagram"></i></a>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="footer-bottom">
                    <p>&copy; 2024 {business_name}. All rights reserved.</p>
                </div>
            </div>
        </footer>
    </body>
    </html>
    """
    
    return html_template

def generate_inline_css(colors):
    """
    Generate inline CSS styles
    """
    return f"""
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: {colors['text']};
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        /* Header Styles */
        .hero {{
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
        }}
        
        .nav-brand h2 {{
            font-size: 1.8rem;
        }}
        
        .nav-links {{
            display: flex;
            list-style: none;
            gap: 2rem;
        }}
        
        .nav-links a {{
            color: white;
            text-decoration: none;
            transition: opacity 0.3s;
        }}
        
        .nav-links a:hover {{
            opacity: 0.8;
        }}
        
        .hero-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 2rem;
        }}
        
        .hero-content h1 {{
            font-size: 3.5rem;
            margin-bottom: 1rem;
        }}
        
        .hero-description {{
            font-size: 1.2rem;
            margin-bottom: 2rem;
            max-width: 600px;
            opacity: 0.9;
        }}
        
        .hero-buttons {{
            display: flex;
            gap: 1rem;
        }}
        
        .btn-primary, .btn-secondary {{
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            text-decoration: none;
            font-size: 1.1rem;
            transition: transform 0.3s;
            cursor: pointer;
        }}
        
        .btn-primary {{
            background: {colors['accent']};
            color: white;
        }}
        
        .btn-secondary {{
            background: transparent;
            color: white;
            border: 2px solid white;
        }}
        
        .btn-primary:hover, .btn-secondary:hover {{
            transform: translateY(-2px);
        }}
        
        /* Services Section */
        .services-section {{
            padding: 80px 0;
            background: #f8f9fa;
        }}
        
        .section-title {{
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 1rem;
            color: {colors['primary']};
        }}
        
        .section-subtitle {{
            text-align: center;
            font-size: 1.1rem;
            margin-bottom: 3rem;
            color: #666;
        }}
        
        .services-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }}
        
        .service-card {{
            background: white;
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .service-card:hover {{
            transform: translateY(-5px);
        }}
        
        .service-icon {{
            width: 60px;
            height: 60px;
            background: {colors['primary']};
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem;
            font-size: 1.5rem;
        }}
        
        .service-card h3 {{
            color: {colors['primary']};
            margin-bottom: 1rem;
        }}
        
        /* About Section */
        .about-section {{
            padding: 80px 0;
        }}
        
        .about-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            align-items: center;
        }}
        
        .about-text h2 {{
            color: {colors['primary']};
            margin-bottom: 1rem;
        }}
        
        .features {{
            margin-top: 2rem;
        }}
        
        .feature {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        
        .feature i {{
            color: {colors['accent']};
            font-size: 1.2rem;
        }}
        
        .placeholder-image {{
            background: {colors['light']};
            height: 300px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: {colors['primary']};
        }}
        
        /* Contact Section */
        .contact-section {{
            padding: 80px 0;
            background: {colors['light']};
        }}
        
        .contact-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
        }}
        
        .contact-item {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .contact-item i {{
            width: 50px;
            height: 50px;
            background: {colors['primary']};
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .form-group {{
            margin-bottom: 1rem;
        }}
        
        .form-group input, .form-group textarea {{
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
        }}
        
        /* Footer */
        .footer {{
            background: {colors['dark']};
            color: white;
            padding: 40px 0 20px;
        }}
        
        .footer-content {{
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        
        .footer-links {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2rem;
        }}
        
        .footer-column ul {{
            list-style: none;
        }}
        
        .footer-column a {{
            color: #ccc;
            text-decoration: none;
            transition: color 0.3s;
        }}
        
        .footer-column a:hover {{
            color: white;
        }}
        
        .social-links {{
            display: flex;
            gap: 1rem;
        }}
        
        .social-links a {{
            width: 40px;
            height: 40px;
            background: {colors['primary']};
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.3s;
        }}
        
        .social-links a:hover {{
            transform: scale(1.1);
        }}
        
        .footer-bottom {{
            border-top: 1px solid #444;
            padding-top: 1rem;
            text-align: center;
            color: #ccc;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .nav-links {{
                display: none;
            }}
            
            .hero-content h1 {{
                font-size: 2.5rem;
            }}
            
            .hero-buttons {{
                flex-direction: column;
                align-items: center;
            }}
            
            .about-content,
            .contact-content,
            .footer-content {{
                grid-template-columns: 1fr;
            }}
            
            .footer-links {{
                grid-template-columns: 1fr;
                text-align: center;
            }}
        }}
    """

def get_color_scheme(scheme):
    """
    Get color palette based on selected scheme
    """
    schemes = {
        'professional': {
            'primary': '#2563eb',
            'secondary': '#1e40af',
            'accent': '#f59e0b',
            'text': '#1f2937',
            'light': '#f8fafc',
            'dark': '#111827'
        },
        'modern': {
            'primary': '#000000',
            'secondary': '#374151',
            'accent': '#ef4444',
            'text': '#111827',
            'light': '#f9fafb',
            'dark': '#000000'
        },
        'warm': {
            'primary': '#ea580c',
            'secondary': '#dc2626',
            'accent': '#fbbf24',
            'text': '#1f2937',
            'light': '#fef3c7',
            'dark': '#92400e'
        },
        'nature': {
            'primary': '#059669',
            'secondary': '#047857',
            'accent': '#84cc16',
            'text': '#1f2937',
            'light': '#ecfdf5',
            'dark': '#064e3b'
        },
        'creative': {
            'primary': '#7c3aed',
            'secondary': '#5b21b6',
            'accent': '#ec4899',
            'text': '#1f2937',
            'light': '#faf5ff',
            'dark': '#581c87'
        }
    }
    
    return schemes.get(scheme, schemes['professional'])

def get_default_services(website_type):
    """
    Get default services based on website type
    """
    defaults = {
        'business': ['Consulting', 'Strategy', 'Implementation', 'Support'],
        'portfolio': ['Design', 'Development', 'Branding', 'Photography'],
        'ecommerce': ['Product Sales', 'Customer Service', 'Shipping', 'Returns'],
        'blog': ['Content Creation', 'SEO Optimization', 'Social Media', 'Analytics'],
        'restaurant': ['Dine-in', 'Takeout', 'Catering', 'Events'],
        'services': ['Professional Services', 'Consultation', 'Custom Solutions', 'Support']
    }
    
    return defaults.get(website_type, defaults['business'])

def generate_css_styles(color_scheme):
    """
    Generate separate CSS file content
    """
    colors = get_color_scheme(color_scheme)
    return generate_inline_css(colors)