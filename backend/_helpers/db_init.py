"""
Database initialization script using SQLAlchemy.

Creates all database tables from SQLAlchemy models.
Run this instead of executing SQL scripts manually.
Usage: python _helpers/db_init.py [--seed]
       python _helpers/db_init.py --help
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path to import from flaskr
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaskr import create_app
from data_access import db


def init_database(seed=False):
    """Initialize database by creating all tables defined in models."""
    app = create_app()
    
    with app.app_context():
        print("Initializing database with SQLAlchemy...")
        
        try:
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully!")
            
            if seed:
                print("\nSeeding database with sample data...")
                from db_seed import seed_database
                seed_database()
                
        except Exception as e:
            print(f"✗ Error initializing database: {e}")
            sys.exit(1)


def main():
    """Parse command line arguments and initialize database."""
    parser = argparse.ArgumentParser(
        description='Initialize database using SQLAlchemy models'
    )
    parser.add_argument(
        '--seed',
        action='store_true',
        help='Seed database with sample data after initialization'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Drop all tables before creating (use with caution)'
    )
    
    args = parser.parse_args()
    
    app = create_app()
    
    with app.app_context():
        if args.force:
            print("WARNING: Dropping all existing tables...")
            db.drop_all()
            print("✓ All tables dropped")
        
        init_database(seed=args.seed)


if __name__ == '__main__':
    main()
