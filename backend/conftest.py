"""
Pytest configuration and fixtures for backend tests
Handles database cleanup and warning suppression
"""

import warnings
import pytest
import sys
import os


# Suppress warnings immediately on import
warnings.simplefilter('ignore', ResourceWarning)
warnings.simplefilter('ignore', DeprecationWarning)


# Configure warning filters for known SQLite/SQLAlchemy issues in tests
def pytest_configure(config):
    """Configure pytest with warning filters"""
    # Suppress ResourceWarnings for unclosed SQLite connections in tests
    # These are expected in test fixtures with in-memory databases
    warnings.simplefilter('ignore', ResourceWarning)
    warnings.filterwarnings('ignore', category=ResourceWarning, message='.*unclosed database.*')
    
    # Suppress DeprecationWarning about datetime.utcnow from SQLAlchemy internals
    # This is from SQLAlchemy's schema.py internal code, not from our application
    warnings.simplefilter('ignore', DeprecationWarning)
    warnings.filterwarnings(
        'ignore',
        message='.*datetime.utcnow.*is deprecated.*',
        category=DeprecationWarning
    )
