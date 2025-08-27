import sqlite3
import uuid
import re
from datetime import datetime
import os

class Database:
    def __init__(self, db_path='instance/assessment.db'):
        self.db_path = db_path
        
        # Create instance directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Responses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                question_id INTEGER NOT NULL,
                answer TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Results table with style score columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                primary_style TEXT NOT NULL,
                secondary_style TEXT NOT NULL,
                adequacy_score INTEGER NOT NULL,
                adequacy_level TEXT NOT NULL,
                directiv_score INTEGER,
                persuasiv_score INTEGER,
                participativ_score INTEGER,
                delegativ_score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def validate_email(self, email: str) -> bool:
        """Validate email format using regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def create_user(self, first_name, last_name, email):
        """Create a new user"""
        if not self.validate_email(email):
            raise ValueError("Invalid email format")
        
        user_id = str(uuid.uuid4())
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (id, first_name, last_name, email) VALUES (?, ?, ?, ?)",
                (user_id, first_name, last_name, email)
            )
            conn.commit()
            return user_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def save_response(self, user_id, question_id, answer):
        """Save user's response to a question"""
        response_id = str(uuid.uuid4())
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO responses (id, user_id, question_id, answer) VALUES (?, ?, ?, ?)",
                (response_id, str(user_id), question_id, answer)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def save_results(self, user_id, primary_style, secondary_style, adequacy_score, adequacy_level, style_scores):
        """Save assessment results"""
        result_id = str(uuid.uuid4())
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                '''INSERT INTO results 
                (id, user_id, primary_style, secondary_style, adequacy_score, adequacy_level,
                 directiv_score, persuasiv_score, participativ_score, delegativ_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (result_id, str(user_id), primary_style, secondary_style, 
                 adequacy_score, adequacy_level,
                 style_scores['Directiv'], style_scores['Persuasiv'], 
                 style_scores['Participativ'], style_scores['Delegativ'])
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_user_results(self, user_id):
        """Get results for a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """SELECT u.*, r.* FROM users u 
                JOIN results r ON u.id = r.user_id 
                WHERE u.id = ?""",
                (str(user_id),)
            )
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            raise e
        finally:
            conn.close()
    
    def get_all_results(self):
        """Get all results for supervisor view"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """SELECT u.*, r.* FROM users u 
                JOIN results r ON u.id = r.user_id 
                ORDER BY r.created_at DESC"""
            )
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            raise e
        finally:
            conn.close()
    
    def get_user_responses(self, user_id):
        """Get all responses for a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                '''SELECT r.*, u.first_name, u.last_name, u.email 
                FROM responses r
                JOIN users u ON r.user_id = u.id
                WHERE r.user_id = ?
                ORDER BY r.question_id''',
                (str(user_id),)
            )
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            raise e
        finally:
            conn.close()