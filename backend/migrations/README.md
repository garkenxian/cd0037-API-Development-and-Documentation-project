# Database Migrations

This directory contains SQL migration scripts for updating the PostgreSQL production database schema.

## Current Migrations

### 001_add_number_of_questions_to_game_sessions.sql
Adds the `number_of_questions` column to the `game_sessions` table to track the number of questions in each game session.

**Status**: Required if you're seeing `UndefinedColumn: column game_sessions.number_of_questions does not exist` errors

**When to apply**: After upgrading to the version that introduced the `number_of_questions` feature

## How to Apply a Migration

### Option 1: Using psql (Recommended)
```bash
psql -U your_db_user -d your_database_name -h localhost -f migrations/001_add_number_of_questions_to_game_sessions.sql
```

### Option 2: Using a database client (pgAdmin, DBeaver, etc.)
1. Open your database management tool
2. Connect to your PostgreSQL database
3. Open the SQL file from this directory
4. Execute the migration

### Option 3: From Python (if needed)
```python
from sqlalchemy import text
from data_access import db

with open('migrations/001_add_number_of_questions_to_game_sessions.sql', 'r') as f:
    migration_sql = f.read()
    
db.session.execute(text(migration_sql))
db.session.commit()
```

## Migration Checklist

- [ ] Backup your production database before applying migrations
- [ ] Test the migration on a development/staging database first
- [ ] Review the migration SQL for any custom changes needed for your environment
- [ ] Apply the migration
- [ ] Verify the changes with: `\d game_sessions` in psql
- [ ] Restart the Flask application if it's running

## Verification

After applying the migration, verify the column exists:

```sql
-- In psql or your SQL client:
\d game_sessions

-- Or query the information schema:
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'game_sessions' 
AND column_name = 'number_of_questions';
```

Expected output should show:
- Column name: `number_of_questions`
- Data type: `integer`
- Nullable: `NO` (or `false`)
