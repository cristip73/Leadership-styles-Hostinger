import sqlite3
import uuid
import re
from datetime import datetime
import os
import shutil

class Database:
    def __init__(self, db_path=None):
        # Use DATABASE_PATH from environment, fallback to local data folder
        if db_path is None:
            db_path = os.environ.get('DATABASE_PATH', 'data/assessment.db')
            
            # Auto-seed for dev environment if database doesn't exist
            if not os.path.exists(db_path) and os.path.exists('seed/assessment.db'):
                print("Initializing development database from seed...")
                os.makedirs('data', exist_ok=True)
                shutil.copy2('seed/assessment.db', db_path)
                print(f"Database copied to {db_path}")
        
        self.db_path = db_path
        
        # Create directory if it doesn't exist
        db_dir = os.path.dirname(db_path)
        if db_dir:  # Only create if there's a directory part
            os.makedirs(db_dir, exist_ok=True)
        
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
                informativ_score INTEGER,
                participativ_score INTEGER,
                delegativ_score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Migration: Handle persuasiv_score -> informativ_score transition
        self._migrate_persuasiv_to_informativ(cursor)
        
        conn.commit()
        conn.close()
    
    def _migrate_persuasiv_to_informativ(self, cursor):
        """Migrate from persuasiv_score to informativ_score column and update style names"""
        try:
            # Check if results table exists first
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='results'")
            if not cursor.fetchone():
                print("✅ New database - no migration needed")
                return
            
            # Check current column structure
            cursor.execute("PRAGMA table_info(results)")
            columns = [row[1] for row in cursor.fetchall()]
            
            has_informativ = 'informativ_score' in columns
            has_persuasiv = 'persuasiv_score' in columns
            
            if not has_informativ and has_persuasiv:
                # Migration needed: persuasiv_score -> informativ_score
                print("🔄 Running database migration: persuasiv_score -> informativ_score")
                
                # Add new column
                cursor.execute("ALTER TABLE results ADD COLUMN informativ_score INTEGER")
                
                # Copy data from old column
                cursor.execute("UPDATE results SET informativ_score = persuasiv_score")
                
                # Update style names in existing data
                cursor.execute("""UPDATE results SET 
                    primary_style = REPLACE(primary_style, 'Persuasiv', 'Informativ'),
                    secondary_style = REPLACE(secondary_style, 'Persuasiv', 'Informativ')""")
                
                print("✅ Migration completed successfully")
                
            elif has_informativ and has_persuasiv:
                # Both columns exist - check if data needs to be migrated
                cursor.execute("SELECT COUNT(*) FROM results WHERE informativ_score IS NULL AND persuasiv_score IS NOT NULL")
                unmigrated_count = cursor.fetchone()[0]
                
                if unmigrated_count > 0:
                    print(f"🔄 Completing data migration for {unmigrated_count} records")
                    cursor.execute("UPDATE results SET informativ_score = persuasiv_score WHERE informativ_score IS NULL")
                    cursor.execute("""UPDATE results SET 
                        primary_style = REPLACE(primary_style, 'Persuasiv', 'Informativ'),
                        secondary_style = REPLACE(secondary_style, 'Persuasiv', 'Informativ')
                        WHERE primary_style LIKE '%Persuasiv%' OR secondary_style LIKE '%Persuasiv%'""")
                    print("✅ Data migration completed")
                    
            elif has_informativ and not has_persuasiv:
                # Already fully migrated - check if style names need updating
                cursor.execute("SELECT COUNT(*) FROM results WHERE primary_style LIKE '%Persuasiv%' OR secondary_style LIKE '%Persuasiv%'")
                old_style_count = cursor.fetchone()[0]
                
                if old_style_count > 0:
                    print(f"🔄 Updating style names for {old_style_count} records")
                    cursor.execute("""UPDATE results SET 
                        primary_style = REPLACE(primary_style, 'Persuasiv', 'Informativ'),
                        secondary_style = REPLACE(secondary_style, 'Persuasiv', 'Informativ')""")
                    print("✅ Style names updated")
                else:
                    print("✅ Database already fully migrated")
                    
            else:
                print("✅ New database - no migration needed")
                
        except Exception as e:
            print(f"❌ Migration error: {e}")
            raise
    
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
                 directiv_score, informativ_score, participativ_score, delegativ_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (result_id, str(user_id), primary_style, secondary_style, 
                 adequacy_score, adequacy_level,
                 style_scores['Directiv'], style_scores['Informativ'], 
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
    
    def get_all_results_with_responses(self):
        """Get all results with raw response patterns"""
        results = self.get_all_results()
        
        for result in results:
            responses = self.get_user_responses(result['user_id'])
            # Format as "1.A, 2.B, 3.C, ..."
            response_pattern = ", ".join([f"{r['question_id']}.{r['answer']}" for r in responses])
            result['response_pattern'] = response_pattern
        
        return results
    
    def delete_user_completely(self, user_id):
        """Delete user and all associated data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Delete in order: responses first (due to foreign key), then results, then user
            cursor.execute("DELETE FROM responses WHERE user_id = ?", (str(user_id),))
            cursor.execute("DELETE FROM results WHERE user_id = ?", (str(user_id),))
            cursor.execute("DELETE FROM users WHERE id = ?", (str(user_id),))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()