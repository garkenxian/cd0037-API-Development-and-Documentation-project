"""
Database seeding script for populating initial test data.

This script adds sample questions, categories, users, and game sessions to the database.
Run after creating/resetting the database: python _helpers/db_init.py --seed
Or run directly: python _helpers/db_seed.py

Usage:
    # Initialize and seed all at once
    python _helpers/db_init.py --seed
    
    # Or reset and seed from scratch
    python _helpers/db_init.py --force --seed
    
    # Just seed the existing database
    python _helpers/db_seed.py
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path to import from flaskr
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaskr import create_app
from data_access import db, Question, Category, User, GameSession

# Sample categories
CATEGORIES = [
    'Science',
    'Art',
    'Geography',
    'History',
    'Entertainment',
    'Sports'
]

# Sample questions (expanded set for better variety)
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
    # Additional questions for more variety
    {
        'question': 'What is the capital of France?',
        'answer': 'Paris',
        'category': 'Geography',
        'difficulty': 1
    },
    {
        'question': 'Who painted the Mona Lisa?',
        'answer': 'Leonardo da Vinci',
        'category': 'Art',
        'difficulty': 2
    },
    {
        'question': 'What is the most abundant gas in the atmosphere?',
        'answer': 'Nitrogen',
        'category': 'Science',
        'difficulty': 2
    },
    {
        'question': 'In which year did the Titanic sink?',
        'answer': '1912',
        'category': 'History',
        'difficulty': 2
    },
    {
        'question': 'How many strings does a violin have?',
        'answer': '4',
        'category': 'Art',
        'difficulty': 1
    },
    {
        'question': 'What is the fastest animal on Earth?',
        'answer': 'Cheetah',
        'category': 'Science',
        'difficulty': 1
    },
    {
        'question': 'Who directed the movie Inception?',
        'answer': 'Christopher Nolan',
        'category': 'Entertainment',
        'difficulty': 2
    },
    {
        'question': 'Which country has the most FIFA World Cup wins?',
        'answer': 'Brazil',
        'category': 'Sports',
        'difficulty': 2
    },
]

# Test users with realistic profile data
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
    {
        'username': 'eve_scientist',
        'email': 'eve@example.com'
    },
]

# Test game sessions with realistic data (multiple games per user)
# Each entry creates a game session and updates user stats
GAME_SESSIONS_DATA = [
    # Alice's games
    {
        'username': 'alice_wonder',
        'category': 'Science',
        'score': 95,
        'days_ago': 5
    },
    {
        'username': 'alice_wonder',
        'category': 'History',
        'score': 87,
        'days_ago': 4
    },
    {
        'username': 'alice_wonder',
        'category': 'Geography',
        'score': 92,
        'days_ago': 3
    },
    {
        'username': 'alice_wonder',
        'category': None,  # General quiz
        'score': 88,
        'days_ago': 2
    },
    # Bob's games
    {
        'username': 'bob_builder',
        'category': 'Art',
        'score': 78,
        'days_ago': 6
    },
    {
        'username': 'bob_builder',
        'category': 'Entertainment',
        'score': 85,
        'days_ago': 4
    },
    {
        'username': 'bob_builder',
        'category': 'Sports',
        'score': 92,
        'days_ago': 2
    },
    # Charlie's games
    {
        'username': 'charlie_brown',
        'category': 'Geography',
        'score': 92,
        'days_ago': 7
    },
    {
        'username': 'charlie_brown',
        'category': 'Science',
        'score': 76,
        'days_ago': 5
    },
    {
        'username': 'charlie_brown',
        'category': 'Art',
        'score': 84,
        'days_ago': 1
    },
    # Diana's games
    {
        'username': 'diana_prince',
        'category': None,  # General quiz
        'score': 88,
        'days_ago': 6
    },
    {
        'username': 'diana_prince',
        'category': 'History',
        'score': 95,
        'days_ago': 3
    },
    {
        'username': 'diana_prince',
        'category': 'Entertainment',
        'score': 80,
        'days_ago': 1
    },
    # Eve's games
    {
        'username': 'eve_scientist',
        'category': 'Science',
        'score': 99,
        'days_ago': 4
    },
    {
        'username': 'eve_scientist',
        'category': 'Science',
        'score': 97,
        'days_ago': 2
    },
    {
        'username': 'eve_scientist',
        'category': None,  # General quiz
        'score': 91,
        'days_ago': 1
    },
]
def seed_database():
    """Seed the database with initial data."""
    app = create_app()
    
    with app.app_context():
        print("🌱 Seeding database with sample data...\n")
        
        # Add categories
        print("📁 Adding categories...")
        categories_added = 0
        for category_name in CATEGORIES:
            # Check if category already exists
            existing = Category.query.filter_by(type=category_name).first()
            if not existing:
                category = Category(type=category_name)
                db.session.add(category)
                categories_added += 1
            else:
                print(f"   ⚠️  Category '{category_name}' already exists, skipping...")
        
        db.session.commit()
        print(f"   ✓ Added {categories_added} categories\n")
        
        # Add questions
        print("❓ Adding questions...")
        questions_added = 0
        for q_data in QUESTIONS:
            # Check if question already exists
            existing = Question.query.filter_by(
                question=q_data['question']
            ).first()
            if not existing:
                # Look up category ID by name
                category_obj = Category.query.filter_by(type=q_data['category']).first()
                if not category_obj:
                    print(f"   ⚠️  Category '{q_data['category']}' not found, skipping question...")
                    continue
                
                question = Question(
                    question=q_data['question'],
                    answer=q_data['answer'],
                    category=category_obj.id,
                    difficulty=q_data['difficulty']
                )
                db.session.add(question)
                questions_added += 1
            else:
                print(f"   ⚠️  Question '{q_data['question'][:50]}...' already exists, skipping...")
        
        db.session.commit()
        print(f"   ✓ Added {questions_added} questions\n")
        
        # Add test users
        print("👥 Adding test users...")
        users_added = 0
        created_users = {}
        
        for user_data in USERS:
            existing = User.query.filter_by(username=user_data['username']).first()
            if not existing:
                user = User(
                    username=user_data['username'],
                    email=user_data['email']
                )
                db.session.add(user)
                created_users[user_data['username']] = user
                users_added += 1
            else:
                created_users[user_data['username']] = existing
                print(f"   ⚠️  User '{user_data['username']}' already exists, skipping...")
        
        db.session.commit()
        print(f"   ✓ Added {users_added} test users\n")
        
        # Add game sessions
        print("🎮 Adding game sessions...")
        sessions_added = 0
        
        for session_data in GAME_SESSIONS_DATA:
            # Look up user by username
            username = session_data['username']
            user = User.query.filter_by(username=username).first()
            
            if not user:
                print(f"   ⚠️  User '{username}' not found, skipping game session...")
                continue
            
            # Look up category if specified
            category_id = None
            if session_data['category']:
                category_obj = Category.query.filter_by(type=session_data['category']).first()
                if category_obj:
                    category_id = category_obj.id
                else:
                    print(f"   ⚠️  Category '{session_data['category']}' not found, creating session without category...")
            
            # Calculate date_played based on days_ago
            days_ago = session_data.get('days_ago', 0)
            date_played = datetime.now(timezone.utc) - timedelta(days=days_ago)
            
            game_session = GameSession(
                user_id=user.id,
                score=session_data['score'],
                category_id=category_id
            )
            # Manually set the date_played after creation
            game_session.date_played = date_played
            
            db.session.add(game_session)
            
            # Update user stats
            user.games_played += 1
            user.total_score += session_data['score']
            sessions_added += 1
        
        db.session.commit()
        print(f"   ✓ Added {sessions_added} game sessions\n")
        
        # Print summary
        print("=" * 60)
        print("✅ Database seeding completed successfully!")
        print("=" * 60)
        print("\n📊 Summary:")
        print(f"   • Categories: {len(CATEGORIES)}")
        print(f"   • Questions: {len(QUESTIONS)}")
        print(f"   • Users: {len(USERS)}")
        print(f"   • Game Sessions: {len(GAME_SESSIONS_DATA)}")
        
        # Print user statistics
        print("\n👤 User Statistics:")
        all_users = User.query.all()
        for user in all_users:
            if user.games_played > 0:
                avg_score = user.total_score / user.games_played
                print(f"   • {user.username}: {user.games_played} games, {user.total_score} total pts, {avg_score:.1f} avg")
        
        print("\n✨ Ready to play!\n")


if __name__ == '__main__':
    seed_database()
