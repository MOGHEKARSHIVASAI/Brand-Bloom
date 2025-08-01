"""
Quick fix script to recreate the database with the proper schema including keyword column.
Run this script once to fix the database schema issue.
"""

import sqlite3
import os
import shutil
from datetime import datetime

def fix_database():
    db_path = 'ai_toolkit.db'
    
    # Backup existing database
    if os.path.exists(db_path):
        backup_path = f'ai_toolkit_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        shutil.copy2(db_path, backup_path)
        print(f"Created backup: {backup_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add keyword column if it doesn't exist
        cursor.execute("PRAGMA table_info(websites)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'keyword' not in columns:
            print("Adding keyword column...")
            cursor.execute('ALTER TABLE websites ADD COLUMN keyword TEXT')
            print("Keyword column added successfully!")
        else:
            print("Keyword column already exists.")
        
        # Create unique index on keyword (ignore if exists)
        try:
            cursor.execute('CREATE UNIQUE INDEX idx_websites_keyword ON websites(keyword)')
            print("Created unique index on keyword column.")
        except sqlite3.OperationalError:
            print("Unique index on keyword already exists.")
        
        conn.commit()
        print("Database schema updated successfully!")
        
    except Exception as e:
        print(f"Error updating database: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    fix_database()