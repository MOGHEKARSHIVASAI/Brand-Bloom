import os
from datetime import datetime
import google.generativeai as genai

# Configure Gemini API (requires GEMINI_API_KEY in environment)
genai.configure(api_key="AIzaSyDd3d3Dv5tVxXRieMDDo5ZHqacP9XPa0oU")

def build_prompt(data):
    """
    Build a detailed and contextual prompt for high-quality website generation.
    """
    website_type = data.get("websiteType", "business")
    business_name = data.get("businessName", "Your Brand")
    description = data.get("businessDescription", "A professional and trustworthy business.")
    key_services = data.get("keyServices", "Consulting, Design, Development")
    audience = data.get("targetAudience", "General audience")
    color_scheme = data.get("colorScheme", "professional").lower()

    # Define color palettes for different themes
    color_palettes = {
        "professional": {"primary": "#2B2D42", "secondary": "#8D99AE", "accent": "#EF233C", "background": "#EDF2F4"},
        "modern": {"primary": "#0A2463", "secondary": "#3E92CC", "accent": "#D8315B", "background": "#FFFFFF"},
        "warm": {"primary": "#A8763E", "secondary": "#F4A261", "accent": "#E76F51", "background": "#FDF0E6"},
        "nature": {"primary": "#2A6041", "secondary": "#8B9D83", "accent": "#D4A373", "background": "#F1F1EF"},
        "creative": {"primary": "#5E2BFF", "secondary": "#FF2A6D", "accent": "#05D9E8", "background": "#FCFCFC"}
    }
    colors = color_palettes.get(color_scheme, color_palettes["professional"])

    return f"""
You are an expert frontend web developer and UI/UX designer with 10+ years of experience.

Generate a modern, responsive single-page website in raw HTML with internal CSS (no JavaScript or external resources). The website must be tailored to the following business:

---
🛠 Business Name: {business_name}
📄 Website Type: {website_type}
📝 Description: {description}
🛍 Services/Products: {key_services}
🎯 Target Audience: {audience}
🎨 Color Theme: {color_scheme}
🎨 Color Palette:
  - Primary: {colors['primary']}
  - Secondary: {colors['secondary']}
  - Accent: {colors['accent']}
  - Background: {colors['background']}
---

### Design Requirements:
1. **Structure**:
   - Use semantic HTML5: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`
   - Include a sticky navigation bar with smooth scrolling to sections
   - Minimum sections: Hero, Services, About, Testimonials, Contact, Footer

2. **Hero Section**:
   - Full-width with a subtle gradient overlay
   - Prominent business name (h1) and tagline based on description
   - Clear call-to-action button (e.g., "Get Started", "Contact Us")
   - Minimum height: 80vh, centered content

3. **Services Section**:
   - Display 3–6 service cards in a responsive grid (2-3 columns on desktop, 1 on mobile)
   - Each card includes: icon (use Unicode or simple SVG), title, brief description
   - Hover effects: scale transform, shadow increase
   - Use {key_services} to populate services

4. **About Section**:
   - 2-column layout (text + placeholder image area) on desktop, stacked on mobile
   - 2–3 key points about the business derived from {description}
   - Subtle animation (fade-in) using CSS keyframes

5. **Testimonials Section**:
   - 3 placeholder testimonials in a carousel-like layout (static, no JS)
   - Each includes: quote, name, title (e.g., "John Doe, CEO")
   - Use subtle borders and background contrast

6. **Contact Section**:
   - Form with fields: Name, Email, Message, Submit button
   - Form styling: clean inputs, focus states, error state placeholders
   - Include business email and phone (use placeholders if not provided)
   - Map placeholder (div with background color and "Map Here" text)

7. **Footer**:
   - 3-column layout: Business info, Quick Links, Social Icons
   - Social icons as Unicode or SVG (e.g., Twitter, LinkedIn, Instagram)
   - Copyright notice with current year
   - Back-to-top link with smooth scroll

8. **Styling**:
   - Use Flexbox and CSS Grid for layouts
   - Google Fonts: Choose 2 complementary fonts (e.g., Roboto + Open Sans)
   - Typography: Clear hierarchy (h1: 2.5rem+, h2: 2rem, body: 1rem)
   - Responsive breakpoints: mobile (<768px), tablet (768-1024px), desktop (>1024px)
   - Smooth transitions for hover effects (0.3s)
   - Soft shadows, rounded corners (8px), subtle gradients
   - Ensure high contrast (WCAG 2.1 AA compliant)

9. **Responsive Design**:
   - Mobile-first approach
   - Collapsible mobile menu (hidden links, hamburger icon using CSS)
   - Stack all multi-column layouts on mobile
   - Adjust font sizes: h1 (2rem), h2 (1.5rem) on mobile
   - Ensure touch-friendly buttons (min 44x44px)

10. **Output**:
    - Clean, well-commented HTML/CSS code
    - Use `<style>` block in `<head>` for all styling
    - No external resources or JavaScript
    - Minify CSS where possible (no extra whitespace)
    - Ensure valid HTML5 (properly nested tags, closed elements)

### Additional Guidelines:
- Derive content tone from {audience} (e.g., professional for B2B, friendly for consumers)
- Use {color_scheme} colors consistently (primary for buttons/CTAs, secondary for accents)
- Optimize for fast loading (minimal code, no images)
- Ensure cross-browser compatibility (Chrome, Firefox, Safari, Edge)

Generate only the HTML code with internal CSS, no explanatory text or markdown formatting.
"""

def generate_website_content(data):
    """
    Generate website content using Gemini API and return metadata including keyword.
    """
    prompt = build_prompt(data)
    model = genai.GenerativeModel("gemini-2.0-flash")

    try:
        response = model.generate_content(prompt)
        html = response.text.strip()
        
        # Clean the HTML content - remove any markdown formatting
        # Remove code fences like ```html or ```
        html = html.replace('```html', '').replace('```', '').strip()
        
        # Remove any leading/trailing quotes
        if html.startswith('"') and html.endswith('"'):
            html = html[1:-1]
        if html.startswith("'") and html.endswith("'"):
            html = html[1:-1]
        
        # Ensure it's a proper string
        html = str(html)
        
        print(f"Generated HTML length: {len(html)}")
        print(f"HTML starts with: {html[:100]}...")
        
    except Exception as e:
        print(f"Error generating website content: {str(e)}")
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error - Website Generation Failed</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <h1 class="error">Website Generation Error</h1>
            <p>Sorry, there was an error generating your website: {str(e)}</p>
            <p>Please try again with different parameters.</p>
        </body>
        </html>
        """

    return {
        "html": html,
        "metadata": {
            "title": f"{data.get('businessName', 'Website')} - {data.get('websiteType', 'Landing Page')}",
            "description": data.get("businessDescription", ""),
            "website_type": data.get("websiteType", "business"),
            "color_scheme": data.get("colorScheme", "professional"),
            "generated_at": datetime.now().isoformat()
        }
    }