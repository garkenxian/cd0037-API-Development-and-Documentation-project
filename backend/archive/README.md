# Archived Files - Legacy SQL Dumps

This directory contains deprecated PostgreSQL dump files that are **no longer used** in the current codebase.

## What's Here

- **trivia.psql** — Original PostgreSQL dump (deprecated)
- **trivia_helpers.psql** — Copy from _helpers directory (deprecated)

## Why Archived?

The project has migrated from direct SQL database bootstrapping to a Python-based ORM approach using SQLAlchemy. The new setup provides:

- **Platform independence**: Works with SQLite (dev), PostgreSQL (prod), MySQL, etc.
- **Schema versioning**: Database structure defined in Python models, not SQL dumps
- **Better maintenance**: Schema changes can be reviewed in code, not raw SQL
- **Automatic migrations**: Easy to track and version control schema changes

## Current Database Setup

All database initialization is now handled by:
- [backend/_helpers/db_init.py](../_helpers/db_init.py) — Creates tables from ORM models
- [backend/_helpers/db_seed.py](../_helpers/db_seed.py) — Populates seed data
- See [backend/DATABASE_SEED.md](../DATABASE_SEED.md) for complete setup instructions

## If You Need the Old SQL

These files are preserved here for reference or emergency recovery only:

```bash
# To restore from PostgreSQL dump (not recommended):
createdb trivia
psql trivia < archive/trivia.psql
```

However, **this is NOT the recommended approach**. Use the SQLAlchemy-based setup instead:

```bash
# Recommended way:
python _helpers/db_init.py --seed
```

## Migration

If you have existing PostgreSQL data:
1. Export from old database
2. Transform to match new ORM models in `models/` directory
3. Add data definitions to `_helpers/db_seed.py`
4. Run `python _helpers/db_init.py --seed` to load into new database

See [DATABASE_SEED.md](../DATABASE_SEED.md) for migration details.
