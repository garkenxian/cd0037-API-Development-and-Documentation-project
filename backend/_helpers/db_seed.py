"""
Database seeding script for populating initial test data.

This script adds sample questions and categories to the trivia database.
Run after creating/resetting the database: python _helpers/db_seed.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path to import from flaskr
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaskr import create_app
from data_access import db, Question, Category, User, GameSession

# Sample data
CATEGORIES = [
    'Science',
    'Art',
    'Geography',
    'History',
    'Entertainment',
    'Sports'
]

QUESTIONS = [
    {
        'question': 'Whose autobiography is entitled "I Know Why the Caged Bird Sings"?',
        'answer': 'Maya Angelou',
        'category': 'Art',
        'difficulty': 2
    },
    {
        'question': 'What actor did author Anne Rice first allow to play a vampire on cinema?',
        'answer': 'Tom Cruise',
        'category': 'Entertainment',
        'difficulty': 3
    },
    {
        'question': 'What is the only mammal in the world that cannot jump?',
        'answer': 'The Elephant',
        'category': 'Science',
        'difficulty': 1
    },
    {
        'question': 'In what year was the "one level header" at the top of the "Designated Survivor" title page added?',
        'answer': '1988',
        'category': 'Entertainment',
        'difficulty': 4
    },
    {
        'question': 'What is the largest lake in Africa?',
        'answer': 'Lake Victoria',
        'category': 'Geography',
        'difficulty': 2
    },
    {
        'question': 'In which royal palace would you find the Hall of Mirrors?',
        'answer': 'The Palace of Versailles',
        'category': 'History',
        'difficulty': 3
    },
    {
        'question': 'The Taj Mahal is located in which Indian city?',
        'answer': 'Agra',
        'category': 'Geography',
        'difficulty': 1
    },
    {
        'question': 'Which American poet is famous for the poem, "The Road Not Taken"?',
        'answer': 'Robert Frost',
        'category': 'Art',
        'difficulty': 2
    },
    {
        'question': 'What is the smallest prime number?',
        'answer': '2',
        'category': 'Science',
        'difficulty': 1
    },
    {
        'question': 'Who won the FIFA World Cup in 1974?',
        'answer': 'West Germany',
        'category': 'Sports',
        'difficulty': 2
    },
    {
        'question': 'What is the chemical symbol for Gold?',
        'answer': 'Au',
        'category': 'Science',
        'difficulty': 1
    },
    {
        'question': 'In what year did World War II end?',
        'answer': '1945',
        'category': 'History',
        'difficulty': 1
    },
]

# Test users for demo/testing
USERS = [
    {
        'username': 'alice_wonder',
        'email': 'alice@example.com'
    },
    {
        'username': 'bob_builder',
        'email': 'bob@example.com'
    },
    {
        'username': 'charlie_brown',
        'email': 'charlie@example.com'
    },
    {
        'username': 'diana_prince',
        'email': 'diana@example.com'
    },
]

# Test game sessions (will reference created users and categories)
GAME_SESSIONS_DATA = [
    {
        'username': 'alice_wonder',
        'category': 'Science',
        'score': 95
    },
    {
        'username': 'alice_wonder',
        'category': 'History',
        'score': 87
    },
    {
        'username': 'bob_builder',
        'category': 'Art',
        'score': 78
    },
    {
        'username': 'charlie_brown',
        'category': 'Geography',
        'score': 92
    },
    {
        'username': 'diana_prince',
        'category': None,  # General quiz
        'score': 88
    },
]


def seed_database():
    """Seed the database with initial data."""
    app = create_app()
    
    with app.app_context():
        print("Seeding database...")
        
        # Add categories
        print("Adding categories...")
        for category_name in CATEGORIES:
            # Check if category already exists
            existing = Category.query.filter_by(type=category_name).first()
            if not existing:
                category = Category(type=category_name)
                db.session.add(category)
            else:
                print(f"  Category '{category_name}' already exists, skipping...")
        
        db.session.commit()
        print(f"✓ Added {len(CATEGORIES)} categories")
        
        # Add questions
        print("Adding questions...")
        added_count = 0
        for q_data in QUESTIONS:
            # Check if question already exists
            existing = Question.query.filter_by(
                question=q_data['question']
            ).first()
            if not existing:
                # Look up category ID by name
                category_obj = Category.query.filter_by(type=q_data['category']).first()
                if not category_obj:
                    print(f"  Warning: Category '{q_data['category']}' not found, skipping question...")
                    continue
                
                question = Question(
                    question=q_data['question'],
                    answer=q_data['answer'],
                    category=category_obj.id,
                    difficulty=q_data['difficulty']
                )
                db.session.add(question)
                added_count += 1
            else:
                print(f"  Question '{q_data['question'][:50]}...' already exists, skipping...")
        
        db.session.commit()
        print(f"✓ Added {added_count} questions")
        
        # Add test users
        print("Adding test users...")
        added_users = 0
        for user_data in USERS:
            existing = User.query.filter_by(username=user_data['username']).first()
            if not existing:
                user = User(
                    username=user_data['username'],
                    email=user_data['email']
                )
                db.session.add(user)
                added_users += 1
            else:
                print(f"  User '{user_data['username']}' already exists, skipping...")
        
        db.session.commit()
        print(f"✓ Added {added_users} test users")
        
        # Add game sessions
        print("Adding game sessions...")
        added_sessions = 0
        for session_data in GAME_SESSIONS_DATA:
            # Look up user by username
            user = User.query.filter_by(username=session_data['username']).first()
            if not user:
                print(f"  Warning: User '{session_data['username']}' not found, skipping game session...")
                continue
            
            # Look up category if specified
            category_id = None
            if session_data['category']:
                category_obj = Category.query.filter_by(type=session_data['category']).first()
                if category_obj:
                    category_id = category_obj.id
                else:
                    print(f"  Warning: Category '{session_data['category']}' not found, creating session without category...")
            
            game_session = GameSession(
                user_id=user.id,
                score=session_data['score'],
                category_id=category_id
            )
            db.session.add(game_session)
            
            # Update user stats
            user.games_played += 1
            user.total_score += session_data['score']
            added_sessions += 1
        
        db.session.commit()
        print(f"✓ Added {added_sessions} game sessions")
        
        print("\n✓ Database seeding completed successfully!")


if __name__ == '__main__':
    seed_database()
