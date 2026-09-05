# Database Seed Data Documentation

**Date**: September 4, 2026  
**Status**: ✅ Complete

---

## Overview

The database seeding system has been completely updated to provide realistic sample data for development and testing. The seed data includes users, categories, questions, and game sessions with full statistics.

---

## Seed Data Contents

### 1. Categories (6 total)

```
1. Science
2. Art
3. Geography
4. History
5. Entertainment
6. Sports
```

### 2. Questions (20 total)

Each question includes:
- **Question text**: The trivia question
- **Answer**: The correct answer
- **Category**: Science, Art, Geography, History, Entertainment, or Sports
- **Difficulty**: 1-4 rating (1=easy, 4=hard)

**Examples:**
- "What is the smallest prime number?" → Answer: "2", Category: Science, Difficulty: 1
- "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?" → Answer: "Maya Angelou", Category: Art, Difficulty: 2
- "Who painted the Mona Lisa?" → Answer: "Leonardo da Vinci", Category: Art, Difficulty: 2

### 3. Test Users (5 total)

Ready-to-use test accounts for development and manual testing:

1. **alice_wonder** (`alice@example.com`)
   - Total Games: 4
   - Total Score: 367
   - Average Score: 91.8

2. **bob_builder** (`bob@example.com`)
   - Total Games: 3
   - Total Score: 255
   - Average Score: 85.0

3. **charlie_brown** (`charlie@example.com`)
   - Total Games: 3
   - Total Score: 252
   - Average Score: 84.0

4. **diana_prince** (`diana@example.com`)
   - Total Games: 3
   - Total Score: 263
   - Average Score: 87.7

5. **eve_scientist** (`eve@scientist.com`)
   - Total Games: 3
   - Total Score: 287
   - Average Score: 95.7

### 4. Game Sessions (15 total)

Realistic game play history with:
- **User**: Which user played the game
- **Category**: Which category (or general if None)
- **Score**: Points earned (0-100)
- **Date**: When the game was played (relative to now)

**Sample Game Sessions:**
```
alice_wonder + Science (95 points) - 5 days ago
alice_wonder + History (87 points) - 4 days ago
bob_builder + Sports (92 points) - 2 days ago
eve_scientist + Science (99 points) - 4 days ago
eve_scientist + Science (97 points) - 2 days ago
```

---

## How to Use the Seed Data

### Quick Start (SQLite - Development)

Initialize and populate the database in one command:

```bash
cd backend
python _helpers/db_init.py --seed
```

### Reset Database (Start Fresh)

Drop all tables and recreate with seed data:

```bash
cd backend
python _helpers/db_init.py --force --seed
```

### Manual Seeding Only

If tables already exist and you just need to add sample data:

```bash
cd backend
python _helpers/db_seed.py
```

### Seed Output

When seeding completes, you'll see:

```
🌱 Seeding database with sample data...

📁 Adding categories...
   ✓ Added 6 categories

❓ Adding questions...
   ✓ Added 20 questions

👥 Adding test users...
   ✓ Added 5 test users

🎮 Adding game sessions...
   ✓ Added 15 game sessions

============================================================
✅ Database seeding completed successfully!
============================================================

📊 Summary:
   • Categories: 6
   • Questions: 20
   • Users: 5
   • Game Sessions: 15

👤 User Statistics:
   • alice_wonder: 4 games, 367 total pts, 91.8 avg
   • bob_builder: 3 games, 255 total pts, 85.0 avg
   • charlie_brown: 3 games, 252 total pts, 84.0 avg
   • diana_prince: 3 games, 263 total pts, 87.7 avg
   • eve_scientist: 3 games, 287 total pts, 95.7 avg

✨ Ready to play!
```

---

## Customizing Seed Data

To add or modify seed data, edit `backend/_helpers/db_seed.py`:

### Adding Questions

```python
QUESTIONS = [
    # ... existing questions
    {
        'question': 'Your question here?',
        'answer': 'The answer',
        'category': 'Science',  # Must match a category
        'difficulty': 2  # 1-4 scale
    },
    # ... more questions
]
```

### Adding Users

```python
USERS = [
    # ... existing users
    {
        'username': 'new_user',
        'email': 'new@example.com'
    },
    # ... more users
]
```

### Adding Game Sessions

```python
GAME_SESSIONS_DATA = [
    # ... existing sessions
    {
        'username': 'alice_wonder',  # Must match a user
        'category': 'Science',  # Can be None for general quiz
        'score': 85,  # 0-100
        'days_ago': 3  # How long ago the game was played
    },
    # ... more sessions
]
```

---

## Database Initialization Files

### File Structure

```
backend/_helpers/
├── db_init.py      ← Main initialization script
├── db_seed.py      ← Seed data definitions and logic
└── trivia.psql     ← Legacy PostgreSQL dump (deprecated)
```

### db_init.py

Handles database creation and schema initialization using SQLAlchemy.

**Usage:**
```bash
python db_init.py              # Create tables only
python db_init.py --seed       # Create tables + seed data
python db_init.py --force      # Drop all + recreate (caution!)
python db_init.py --force --seed  # Full reset + seed
```

### db_seed.py

Contains all seed data definitions and seeding logic. Can be run standalone:

```bash
python db_seed.py
```

**Features:**
- Duplicate detection (won't re-add existing data)
- Referential integrity checking (validates foreign keys)
- User stats calculation (games_played, total_score)
- Rich output with emoji indicators

---

## Testing with Seed Data

### In-Memory Database for Tests

Tests use an in-memory SQLite database (`sqlite:///:memory:`) that's automatically cleaned for each test. This ensures:
- ✅ Tests are isolated and independent
- ✅ No side effects between tests
- ✅ Fast test execution
- ✅ No production data affected

### Seeded Database for Manual Testing

For manual API testing (e.g., with Postman/curl):

1. Seed the development database:
   ```bash
   python _helpers/db_init.py --seed
   ```

2. Start the Flask development server:
   ```bash
   flask run
   ```

3. Test endpoints using the sample user credentials:
   ```bash
   curl -X POST http://localhost:5000/games \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "category_id": 1, "number_of_questions": 5}'
   ```

---

## Migration from Legacy System

The old `trivia.psql` PostgreSQL dump is now deprecated. To migrate existing data:

1. Export data from PostgreSQL
2. Transform to match the new ORM models
3. Update `db_seed.py` with the data
4. Run `python _helpers/db_init.py --seed`

---

## Performance Considerations

- **Seed Performance**: ~2-5 seconds on typical development machine
- **Test Database Init**: ~100ms per test (in-memory SQLite is very fast)
- **Duplicate Detection**: O(n) database queries, negligible for seed size

### Optimization Tips

For large seed datasets:
1. Batch commits to reduce transaction overhead
2. Use bulk insert operations
3. Disable indexes during initial load, rebuild after

---

## Troubleshooting

### "Category not found" Warning

If you see: `⚠️ Category 'SomeName' not found, skipping question...`

**Solution**: 
1. Check category name in `QUESTIONS` matches exactly in `CATEGORIES`
2. Ensure you're using the predefined categories

### Duplicate Data Error

If tests fail due to unique constraint violations:

**Solution**:
```bash
# Reset the database completely
python _helpers/db_init.py --force --seed
```

### Database Locked

If you get "database is locked" errors during testing:

**Solution**:
1. Stop the Flask development server
2. Kill any running pytest processes
3. Delete `trivia.db` if using file-based SQLite
4. Run initialization again

---

## Database Schema Reference

See [API_SPECIFICATION.md](../API_SPECIFICATION.md) for complete schema with column definitions and relationships.

**Quick Reference**:

| Table | Records | Purpose |
|-------|---------|---------|
| **categories** | 6 | Question categories |
| **users** | 5 | Player accounts |
| **questions** | 20 | Trivia questions |
| **game_sessions** | 15 | Game play history |

---

## Next Steps

1. ✅ Seed the database: `python _helpers/db_init.py --seed`
2. ✅ Start development server: `flask run`
3. ✅ Test API endpoints with sample user data
4. ✅ Run test suite: `pytest`

**Happy testing!** 🎮✨
