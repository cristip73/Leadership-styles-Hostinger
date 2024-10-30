import os
import psycopg2
from psycopg2.extras import DictCursor
import uuid
import re

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ['PGHOST'],
            database=os.environ['PGDATABASE'],
            user=os.environ['PGUSER'],
            password=os.environ['PGPASSWORD'],
            port=os.environ['PGPORT']
        )
        self.create_tables()

    def create_tables(self):
        try:
            with self.conn.cursor() as cur:
                # Drop UNIQUE constraint from email
                cur.execute("""
                    DO $$ 
                    BEGIN 
                        IF EXISTS (
                            SELECT 1 FROM information_schema.table_constraints 
                            WHERE constraint_name = 'users_email_key'
                            AND table_name = 'users'
                        ) THEN
                            ALTER TABLE users DROP CONSTRAINT users_email_key;
                        END IF;
                    END $$;
                """)

                # Users table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id UUID PRIMARY KEY,
                        first_name VARCHAR(100),
                        last_name VARCHAR(100),
                        email VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Responses table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS responses (
                        id UUID PRIMARY KEY,
                        user_id UUID REFERENCES users(id),
                        question_id INTEGER,
                        answer VARCHAR(1),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Results table with style score columns
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS results (
                        id UUID PRIMARY KEY,
                        user_id UUID REFERENCES users(id),
                        primary_style VARCHAR(50),
                        secondary_style VARCHAR(50),
                        adequacy_score INTEGER,
                        adequacy_level VARCHAR(50),
                        directiv_score INTEGER,
                        persuasiv_score INTEGER,
                        participativ_score INTEGER,
                        delegativ_score INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def validate_email(self, email: str) -> bool:
        """Validate email format using regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def create_user(self, first_name, last_name, email):
        if not self.validate_email(email):
            raise ValueError("Invalid email format")
            
        try:
            user_id = uuid.uuid4()
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (id, first_name, last_name, email) VALUES (%s::uuid, %s, %s, %s) RETURNING id",
                    (str(user_id), first_name, last_name, email)
                )
                self.conn.commit()
                return user_id
        except Exception as e:
            self.conn.rollback()
            raise e

    def save_response(self, user_id, question_id, answer):
        try:
            response_id = uuid.uuid4()
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO responses (id, user_id, question_id, answer) VALUES (%s::uuid, %s::uuid, %s, %s)",
                    (str(response_id), str(user_id), question_id, answer)
                )
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def save_results(self, user_id, primary_style, secondary_style, adequacy_score, adequacy_level, style_scores):
        try:
            result_id = uuid.uuid4()
            with self.conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO results 
                    (id, user_id, primary_style, secondary_style, adequacy_score, adequacy_level,
                     directiv_score, persuasiv_score, participativ_score, delegativ_score)
                    VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (str(result_id), str(user_id), primary_style, secondary_style, adequacy_score, adequacy_level,
                     style_scores['Directiv'], style_scores['Persuasiv'], style_scores['Participativ'], style_scores['Delegativ'])
                )
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_user_results(self, user_id):
        try:
            with self.conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(
                    """SELECT u.*, r.* FROM users u 
                    JOIN results r ON u.id = r.user_id 
                    WHERE u.id = %s::uuid""",
                    (str(user_id),)
                )
                result = cur.fetchone()
                return dict(result) if result else None
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_all_results(self):
        try:
            with self.conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(
                    """SELECT u.*, r.* FROM users u 
                    JOIN results r ON u.id = r.user_id 
                    ORDER BY r.created_at DESC"""
                )
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_user_responses(self, user_id):
        try:
            with self.conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(
                    '''SELECT r.*, u.first_name, u.last_name, u.email 
                    FROM responses r
                    JOIN users u ON r.user_id = u.id
                    WHERE r.user_id = %s::uuid
                    ORDER BY r.question_id''',
                    (str(user_id),)
                )
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            self.conn.rollback()
            raise e
