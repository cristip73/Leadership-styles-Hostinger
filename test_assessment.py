from models.database import Database
from datetime import datetime
import uuid

def create_test_data():
    db = Database()
    
    # Create test user
    user_id = db.create_user(
        first_name="Test",
        last_name="User",
        email="test@example.com"
    )
    
    # Create test responses
    for question_id in range(1, 13):
        db.save_response(user_id, question_id, "A")
    
    # Save test results
    db.save_results(
        user_id=user_id,
        primary_style="Directiv",
        secondary_style="Persuasiv",
        adequacy_score=15,
        adequacy_level="Bun"
    )
    
    print("Test data created successfully!")

if __name__ == "__main__":
    create_test_data()
