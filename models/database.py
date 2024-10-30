import os
import psycopg2
from psycopg2.extras import DictCursor
import uuid

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
        with self.conn.cursor() as cur:
            # Users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    email VARCHAR(255) UNIQUE,
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
            
            # Results table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id UUID PRIMARY KEY,
                    user_id UUID REFERENCES users(id),
                    primary_style VARCHAR(50),
                    secondary_style VARCHAR(50),
                    adequacy_score INTEGER,
                    adequacy_level VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()

    def create_user(self, first_name, last_name, email):
        user_id = uuid.uuid4()
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (id, first_name, last_name, email) VALUES (%s::uuid, %s, %s, %s) RETURNING id",
                (str(user_id), first_name, last_name, email)
            )
            self.conn.commit()
            return user_id

    def save_response(self, user_id, question_id, answer):
        response_id = uuid.uuid4()
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO responses (id, user_id, question_id, answer) VALUES (%s::uuid, %s::uuid, %s, %s)",
                (str(response_id), str(user_id), question_id, answer)
            )
            self.conn.commit()

    def save_results(self, user_id, primary_style, secondary_style, adequacy_score, adequacy_level):
        result_id = uuid.uuid4()
        with self.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO results 
                (id, user_id, primary_style, secondary_style, adequacy_score, adequacy_level)
                VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s)""",
                (str(result_id), str(user_id), primary_style, secondary_style, adequacy_score, adequacy_level)
            )
            self.conn.commit()

    def get_user_results(self, user_id):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                """SELECT u.*, r.* FROM users u 
                JOIN results r ON u.id = r.user_id 
                WHERE u.id = %s::uuid""",
                (str(user_id),)
            )
            return dict(cur.fetchone())

    def get_all_results(self):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                """SELECT u.*, r.* FROM users u 
                JOIN results r ON u.id = r.user_id 
                ORDER BY r.created_at DESC"""
            )
            return [dict(row) for row in cur.fetchall()]
