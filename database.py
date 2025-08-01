import sqlite3
import hashlib
from datetime import datetime
import json
import os

class Database:
    def __init__(self, db_path='ai_toolkit.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This allows dict-like access to rows
        return conn
    
    def init_database(self):
        """Initialize database with tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create business table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                business_name TEXT NOT NULL,
                industry TEXT,
                description TEXT,
                target_audience TEXT,
                goals TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create websites table with keyword
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS websites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                html_content TEXT NOT NULL,
                metadata TEXT,
                keyword TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully!")
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        return hashlib.sha256(password.encode()).hexdigest() == password_hash
    
    # User operations
    def create_user(self, name, email, password):
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (name, email, password_hash)
                VALUES (?, ?, ?)
            ''', (name, email, password_hash))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None  # Email already exists
    
    def get_user_by_email(self, email):
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None
    
    def authenticate_user(self, email, password):
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        if user and self.verify_password(password, user['password_hash']):
            return user
        return None
    
    # Business operations
    def create_business(self, user_id, business_name, industry=None, description=None, 
                       target_audience=None, goals=None):
        """Create business information for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert goals list to JSON string if provided
        goals_json = json.dumps(goals) if goals else None
        
        cursor.execute('''
            INSERT INTO business (user_id, business_name, industry, description, 
                                target_audience, goals)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, business_name, industry, description, target_audience, goals_json))
        
        business_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return business_id
    
    def get_business_by_user_id(self, user_id):
        """Get business information by user ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM business WHERE user_id = ?', (user_id,))
        business = cursor.fetchone()
        conn.close()
        
        if business:
            business_dict = dict(business)
            # Parse goals JSON back to list
            if business_dict['goals']:
                try:
                    business_dict['goals'] = json.loads(business_dict['goals'])
                except:
                    business_dict['goals'] = []
            return business_dict
        return None
    
    def update_business(self, user_id, **kwargs):
        """Update business information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        # Convert goals to JSON if provided
        if 'goals' in kwargs and kwargs['goals']:
            kwargs['goals'] = json.dumps(kwargs['goals'])
        
        # Build dynamic update query
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        
        try:
            cursor.execute(f'''
                UPDATE business 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', values)
            
            conn.commit()
            success = cursor.rowcount > 0
        except Exception as e:
            success = False
            print(f"Error updating business: {str(e)}")
        finally:
            conn.close()
        
        return success
    
    def get_user_with_business(self, user_id):
        """Get user with their business information"""
        user = self.get_user_by_id(user_id)
        if user:
            business = self.get_business_by_user_id(user_id)
            user['business'] = business
        return user
    
    # Website operations
    def save_website(self, user_id, title, html_content, metadata, keyword=None):
        """Save generated website to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        try:
            cursor.execute('''
                INSERT INTO websites (user_id, title, html_content, metadata, keyword)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, title, html_content, metadata_json, keyword))
            
            website_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return website_id
        except sqlite3.IntegrityError:
            conn.close()
            return None  # Keyword already exists
    
    def get_website_by_id(self, website_id, user_id=None):
        """Get website by ID for specific user (or public if user_id is None)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id is not None:
            cursor.execute('SELECT * FROM websites WHERE id = ? AND user_id = ?', 
                          (website_id, user_id))
        else:
            cursor.execute('SELECT * FROM websites WHERE id = ?', (website_id,))
        
        website = cursor.fetchone()
        conn.close()
        
        if website:
            website_dict = dict(website)
            if website_dict['metadata']:
                try:
                    website_dict['metadata'] = json.loads(website_dict['metadata'])
                except:
                    website_dict['metadata'] = {}
            return website_dict
        return None
    
    def get_website_by_keyword(self, keyword, user_id=None):
        """Get website by keyword for specific user (or public if user_id is None)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id is not None:
            cursor.execute('SELECT * FROM websites WHERE keyword = ? AND user_id = ?', 
                          (keyword, user_id))
        else:
            cursor.execute('SELECT * FROM websites WHERE keyword = ?', (keyword,))
        
        website = cursor.fetchone()
        conn.close()
        
        if website:
            website_dict = dict(website)
            if website_dict['metadata']:
                try:
                    website_dict['metadata'] = json.loads(website_dict['metadata'])
                except:
                    website_dict['metadata'] = {}
            return website_dict
        return None
    def get_user_websites(self, user_id):
        """Get all websites for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM websites WHERE user_id = ?', (user_id,))
        websites = cursor.fetchall()
        conn.close()
        
        result = []
        for website in websites:
            website_dict = dict(website)
            if website_dict['metadata']:
                try:
                    website_dict['metadata'] = json.loads(website_dict['metadata'])
                except:
                    website_dict['metadata'] = {}
            result.append(website_dict)
        return result
    
    def count_deployed_websites(self, user_id):
        """Count websites with non-null keywords for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM websites WHERE user_id = ? AND keyword IS NOT NULL', (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def update_website(self, website_id, user_id, **kwargs):
        """Update website information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        # Convert metadata to JSON if provided
        if 'metadata' in kwargs and kwargs['metadata']:
            kwargs['metadata'] = json.dumps(kwargs['metadata'])
        
        # Build dynamic update query
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [website_id, user_id]
        
        try:
            cursor.execute(f'''
                UPDATE websites 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            ''', values)
            
            conn.commit()
            success = cursor.rowcount > 0
        except Exception as e:
            success = False
            print(f"Error updating website: {str(e)}")
        finally:
            conn.close()
        
        return success

# Initialize database instance
db = Database()

# Helper functions for Flask app
def init_db():
    """Initialize database - can be called from app.py"""
    global db
    db = Database()
    return db

def get_db():
    """Get database instance"""
    return db

# Sample data creation for testing
def create_sample_data():
    """Create sample users and businesses for testing"""
    print("Creating sample data...")
    
    # Sample users
    sample_users = [
        {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'password123',
            'business': {
                'business_name': 'Tech Solutions Inc',
                'industry': 'technology',
                'description': 'We provide innovative technology solutions for small businesses.',
                'target_audience': 'Small business owners, entrepreneurs',
                'goals': ['increase_sales', 'improve_marketing', 'online_presence']
            }
        },
        {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'password': 'password123',
            'business': {
                'business_name': 'Green Garden Cafe',
                'industry': 'food_beverage',
                'description': 'Organic cafe serving fresh, locally-sourced meals.',
                'target_audience': 'Health-conscious consumers',
                'goals': ['customer_service', 'online_presence']
            }
        }
    ]
    
    for user_data in sample_users:
        # Create user
        user_id = db.create_user(
            user_data['name'], 
            user_data['email'], 
            user_data['password']
        )
        
        if user_id:
            # Create business
            business_data = user_data['business']
            db.create_business(
                user_id,
                business_data['business_name'],
                business_data['industry'],
                business_data['description'],
                business_data['target_audience'],
                business_data['goals']
            )
            print(f"Created user: {user_data['name']} with business: {business_data['business_name']}")
        else:
            print(f"Failed to create user: {user_data['name']} (email might already exist)")

if __name__ == '__main__':
    # Initialize database and create sample data
    init_db()
    create_sample_data()
    
    # Test database operations
    print("\n--- Testing Database Operations ---")
    
    # Test user authentication
    user = db.authenticate_user('john@example.com', 'password123')
    if user:
        print(f"Authentication successful for: {user['name']}")
        
        # Get user with business
        user_with_business = db.get_user_with_business(user['id'])
        if user_with_business['business']:
            print(f"Business: {user_with_business['business']['business_name']}")
    
    print("Database setup complete!")