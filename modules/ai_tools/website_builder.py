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

Generate a modern, responsive single-page website in raw HTML with internal CSS and JavaScript. The website must be tailored to the following business:

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
   - Minimum sections: Hero, Services, About, Testimonials, Contact, Feedback, Footer

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

7. **Customer Feedback Section** (CRITICAL - ENSURE FUNCTIONALITY):
   - Add a dedicated "Customer Feedback" section with id="feedback"
   - Include a feedback form with the following fields:
     * Customer Name (required, text input, id="customerName")
     * Customer Email (required, email input, id="customerEmail")
     * Rating (required, radio buttons for 1-5 stars, name="rating")
     * Feedback Message (required, textarea, id="feedbackMessage")
     * Submit button (id="submitFeedback")
   - Form must have id="feedbackForm"
   - Add a hidden input field for website ID: `<input type="hidden" id="websiteId" value="WEBSITE_ID_PLACEHOLDER">`
   - Add JavaScript to handle form submission with proper website ID handling
   - Form styling: match website's color scheme, use primary color for button, secondary for borders
   - Include a "Share Your Experience" heading (h2)
   - Ensure form is WCAG 2.1 AA compliant (labels, aria attributes)

8. **Footer**:
   - 3-column layout: Business info, Quick Links, Social Icons
   - Social icons as Unicode or SVG (e.g., Twitter, LinkedIn, Instagram)
   - Copyright notice with current year
   - Back-to-top link with smooth scroll

9. **Styling**:
   - Use Flexbox and CSS Grid for layouts
   - Google Fonts: Roboto (headings) and Open Sans (body)
   - Typography: h1: 2.5rem (mobile: 2rem), h2: 2rem (mobile: 1.5rem), body: 1rem
   - Responsive breakpoints: mobile (<768px), tablet (768-1024px), desktop (>1024px)
   - Smooth transitions for hover effects (0.3s)
   - Soft shadows, rounded corners (8px), subtle gradients
   - Use {colors['primary']} for buttons/CTAs, {colors['secondary']} for accents
   - Ensure high contrast (WCAG 2.1 AA compliant)

10. **JavaScript Requirements**:
    - Add smooth scrolling for navigation links
    - Add form validation for the feedback form (client-side)
    - Add star rating interaction (highlight on hover/click)
    - Add feedback form submission with fetch API
    - Show loading states and success/error messages
    - Handle website ID properly from hidden input field

11. **Responsive Design**:
    - Mobile-first approach
    - Collapsible mobile menu (hamburger icon using CSS/JS)
    - Stack all multi-column layouts on mobile
    - Touch-friendly buttons (min 44x44px)
    - Adjust font sizes for mobile

12. **Output**:
    - Clean, well-commented HTML/CSS/JS code
    - Use `<style>` block in `<head>` for all styling
    - Use `<script>` block before `</body>` for all JavaScript
    - No external resources except Google Fonts
    - Ensure valid HTML5 (properly nested tags, closed elements)

### Feedback Form JavaScript Template:
```javascript
document.addEventListener('DOMContentLoaded', function() {{
    // Star rating functionality
    const ratingInputs = document.querySelectorAll('input[name="rating"]');
    const ratingLabels = document.querySelectorAll('label[for^="rating"]');
    
    ratingInputs.forEach((input, index) => {{
        input.addEventListener('change', function() {{
            updateStarDisplay(parseInt(this.value));
        }});
    }});
    
    ratingLabels.forEach((label, index) => {{
        label.addEventListener('mouseenter', function() {{
            const rating = parseInt(this.getAttribute('for').replace('rating', ''));
            updateStarDisplay(rating, true);
        }});
        
        label.addEventListener('mouseleave', function() {{
            const checkedRating = document.querySelector('input[name="rating"]:checked');
            const rating = checkedRating ? parseInt(checkedRating.value) : 0;
            updateStarDisplay(rating);
        }});
    }});
    
    function updateStarDisplay(rating, isHover = false) {{
        ratingLabels.forEach((label, index) => {{
            const starRating = index + 1;
            if (starRating <= rating) {{
                label.style.color = isHover ? '{colors['primary']}' : '{colors['accent']}';
            }} else {{
                label.style.color = '#ddd';
            }}
        }});
    }}
    
    // Form submission
    document.getElementById('feedbackForm').addEventListener('submit', async function(e) {{
        e.preventDefault();
        
        // Get form elements
        const customerName = document.getElementById('customerName').value.trim();
        const customerEmail = document.getElementById('customerEmail').value.trim();
        const rating = document.querySelector('input[name="rating"]:checked');
        const feedbackMessage = document.getElementById('feedbackMessage').value.trim();
        const websiteId = document.getElementById('websiteId').value;
        const submitButton = document.getElementById('submitFeedback');
        
        // Validation
        if (!customerName) {{
            alert('Please enter your name');
            document.getElementById('customerName').focus();
            return;
        }}
        if (!customerEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(customerEmail)) {{
            alert('Please enter a valid email address');
            document.getElementById('customerEmail').focus();
            return;
        }}
        if (!rating) {{
            alert('Please select a rating');
            return;
        }}
        if (!feedbackMessage) {{
            alert('Please enter your feedback');
            document.getElementById('feedbackMessage').focus();
            return;
        }}
        
        // Check if website ID exists
        if (!websiteId || websiteId === 'WEBSITE_ID_PLACEHOLDER') {{
            alert('Error: Website ID not found. Please refresh the page and try again.');
            return;
        }}
        
        // Prepare form data
        const formData = {{
            customer_name: customerName,
            customer_email: customerEmail,
            rating: parseInt(rating.value),
            feedback_text: feedbackMessage,
            website_id: parseInt(websiteId)
        }};
        
        console.log('Submitting feedback data:', formData);
        
        // Show loading state
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = 'Submitting...';
        
        try {{
            const response = await fetch('/api/submit-feedback', {{
                method: 'POST',
                headers: {{ 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }},
                body: JSON.stringify(formData)
            }});
            
            console.log('Response status:', response.status);
            const result = await response.json();
            console.log('Response data:', result);
            
            if (response.ok && result.success) {{
                // Success message
                const successDiv = document.createElement('div');
                successDiv.style.cssText = `
                    background: #d4edda;
                    color: #155724;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;
                    border: 1px solid #c3e6cb;
                `;
                successDiv.innerHTML = '✅ Thank you for your feedback! We appreciate your input.';
                
                const form = document.getElementById('feedbackForm');
                form.parentNode.insertBefore(successDiv, form.nextSibling);
                
                // Reset form
                form.reset();
                updateStarDisplay(0);
                
                // Remove success message after 5 seconds
                setTimeout(() => {{
                    if (successDiv.parentNode) {{
                        successDiv.parentNode.removeChild(successDiv);
                    }}
                }}, 5000);
            }} else {{
                alert('Error submitting feedback: ' + (result.error || 'Please try again later'));
            }}
        }} catch (error) {{
            console.error('Error submitting feedback:', error);
            alert('Error submitting feedback: Network error. Please check your connection and try again.');
        }} finally {{
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }}
    }});
}});
```

### Additional Guidelines:
- Derive content tone from {audience} (e.g., professional for B2B, friendly for consumers)
- Use {color_scheme} colors consistently
- Optimize for fast loading (minimal code)
- Ensure cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- Make the feedback form prominent but not intrusive
- Use placeholder text that encourages honest feedback
- Ensure form submission works reliably and provides user feedback
- Include aria-labels and proper form validation for accessibility
- The hidden input field for website ID will be populated by the server after website creation

Generate only the HTML code with internal CSS and JavaScript, no explanatory text or markdown formatting.
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
        
        # Clean the HTML content
        html = html.replace('```html', '').replace('```', '').strip()
        if html.startswith('"') and html.endswith('"'):
            html = html[1:-1]
        if html.startswith("'") and html.endswith("'"):
            html = html[1:-1]
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
            "generated_at": datetime.now().isoformat(),
            "has_feedback_form": True
        }
    }