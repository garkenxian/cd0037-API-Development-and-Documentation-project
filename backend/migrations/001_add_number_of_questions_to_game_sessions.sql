-- Migration: Add number_of_questions column to game_sessions table
-- This column tracks how many questions were in each game session (1-20)
-- Default value is 5 to match the application default

ALTER TABLE game_sessions
ADD COLUMN number_of_questions INTEGER NOT NULL DEFAULT 5;

-- Add constraint to ensure value is between 1 and 20
ALTER TABLE game_sessions
ADD CONSTRAINT ck_number_of_questions_range 
CHECK (number_of_questions >= 1 AND number_of_questions <= 20);

-- Note: If you need to backfill existing records with different values,
-- update them before applying this constraint:
-- UPDATE game_sessions SET number_of_questions = <value> WHERE <condition>;
