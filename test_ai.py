#!/usr/bin/env python3
"""
Test script to verify website generation and ID replacement
"""

from database import get_db
import re

def test_html_replacement():
    """Test the HTML replacement logic"""
    
    # Sample HTML with placeholder
    sample_html = '''
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body>
        <form id="feedbackForm">
            <input type="hidden" id="websiteId" value="WEBSITE_ID_PLACEHOLDER">
            <input type="text" id="customerName" required>
            <button id="submitFeedback">Submit</button>
        </form>
        <script>
            const websiteId = document.getElementById('websiteId').value;
            console.log('Website ID:', websiteId);
        </script>
    </body>
    </html>
    '''
    
    print("=== Testing HTML Replacement ===")
    print("Original HTML contains:", 'WEBSITE_ID_PLACEHOLDER' in sample_html)
    
    # Test replacement
    website_id = 123
    updated_html = sample_html.replace('WEBSITE_ID_PLACEHOLDER', str(website_id))
    
    print("After replacement contains placeholder:", 'WEBSITE_ID_PLACEHOLDER' in updated_html)
    print("After replacement contains ID:", str(website_id) in updated_html)
    
    # Extract the value
    match = re.search(r'value="(\d+)".*id="websiteId"', updated_html)
    if match:
        print(f"Extracted ID: {match.group(1)}")
    else:
        print("❌ Could not extract ID from HTML")
    
    return updated_html

def check_latest_website():
    """Check the latest website in database"""
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("\n=== Checking Latest Website ===")
    cursor.execute('SELECT * FROM websites ORDER BY id DESC LIMIT 1')
    website = cursor.fetchone()
    
    if website:
        website_dict = dict(website)
        website_id = website_dict['id']
        html_content = website_dict['html_content']
        
        print(f"Website ID: {website_id}")
        print(f"Title: {website_dict['title']}")
        print(f"HTML length: {len(html_content)}")
        
        # Check for placeholder
        if 'WEBSITE_ID_PLACEHOLDER' in html_content:
            print("❌ HTML still contains WEBSITE_ID_PLACEHOLDER")
        else:
            print("✅ Placeholder has been replaced")
        
        # Check for websiteId field
        if 'id="websiteId"' in html_content:
            print("✅ HTML contains websiteId field")
            
            # Extract the value
            match = re.search(r'<input[^>]*id="websiteId"[^>]*value="([^"]*)"', html_content)
            if match:
                found_id = match.group(1)
                print(f"Found website ID in HTML: {found_id}")
                if found_id == str(website_id):
                    print("✅ Website ID matches database ID")
                else:
                    print(f"❌ Website ID mismatch! DB: {website_id}, HTML: {found_id}")
            else:
                print("❌ Could not extract website ID from HTML")
        else:
            print("❌ HTML missing websiteId field")
            
        # Look for any form of website ID reference
        print("\nSearching for any website ID references...")
        id_patterns = [
            rf'value="{website_id}"',
            rf'websiteId.*{website_id}',
            rf'{website_id}.*websiteId',
            'WEBSITE_ID_PLACEHOLDER'
        ]
        
        for pattern in id_patterns:
            if re.search(pattern, html_content):
                print(f"✅ Found pattern: {pattern}")
            else:
                print(f"❌ Missing pattern: {pattern}")
    
    else:
        print("❌ No websites found in database")
    
    conn.close()

def fix_latest_website():
    """Fix the latest website by manually replacing the placeholder"""
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("\n=== Fixing Latest Website ===")
    cursor.execute('SELECT * FROM websites ORDER BY id DESC LIMIT 1')
    website = cursor.fetchone()
    
    if website:
        website_dict = dict(website)
        website_id = website_dict['id']
        html_content = website_dict['html_content']
        
        if 'WEBSITE_ID_PLACEHOLDER' in html_content:
            print(f"Fixing website ID: {website_id}")
            
            # Replace placeholder
            fixed_html = html_content.replace('WEBSITE_ID_PLACEHOLDER', str(website_id))
            
            # Update database
            cursor.execute('UPDATE websites SET html_content = ? WHERE id = ?', 
                         (fixed_html, website_id))
            conn.commit()
            
            print("✅ Website fixed! Placeholder replaced with actual ID.")
        else:
            print("Website doesn't need fixing - no placeholder found")
    
    conn.close()

if __name__ == "__main__":
    print("🔧 Testing Website Generation and ID Replacement\n")
    
    # Test the replacement logic
    test_html_replacement()
    
    # Check current state
    check_latest_website()
    
    # Ask if user wants to fix
    response = input("\nDo you want to fix the latest website? (y/N): ")
    if response.lower() == 'y':
        fix_latest_website()
        print("\nRechecking after fix...")
        check_latest_website()
    
    print("\n✅ Test complete!")