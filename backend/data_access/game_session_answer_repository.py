"""GameSessionAnswer Repository - Data access for game answer audit trail"""

from models import GameSessionAnswer
from data_access import db


class GameSessionAnswerRepository:
    """Data access layer for GameSessionAnswer records"""

    @staticmethod
    def create(game_session_id, question_number, question_id, question_snapshot,
               answer_snapshot, user_answer, is_correct):
        """
        Create a new answer record
        
        Args:
            game_session_id: Game session ID
            question_number: Question number in sequence (1-based)
            question_id: ID of the question
            question_snapshot: Immutable copy of question text
            answer_snapshot: Immutable copy of correct answer
            user_answer: User's submitted answer
            is_correct: Whether answer is correct
            
        Returns:
            Created GameSessionAnswer object (uncommitted)
            
        Note: Caller is responsible for committing
        """
        answer = GameSessionAnswer(
            game_session_id=game_session_id,
            question_number=question_number,
            question_id=question_id,
            question_snapshot=question_snapshot,
            answer_snapshot=answer_snapshot,
            user_answer=user_answer,
            is_correct=is_correct
        )
        db.session.add(answer)
        return answer

    @staticmethod
    def get_by_id(answer_id):
        """Get a specific answer record by ID"""
        return db.session.query(GameSessionAnswer).filter(GameSessionAnswer.id == answer_id).first()

    @staticmethod
    def get_by_game_and_question(game_session_id, question_number):
        """Get answer for a specific game and question number"""
        return db.session.query(GameSessionAnswer).filter(
            GameSessionAnswer.game_session_id == game_session_id,
            GameSessionAnswer.question_number == question_number
        ).first()

    @staticmethod
    def get_by_game(game_session_id, order_by_question=True):
        """
        Get all answers for a game session
        
        Args:
            game_session_id: Game session ID
            order_by_question: Whether to order by question_number (default True)
            
        Returns:
            List of GameSessionAnswer objects
        """
        query = db.session.query(GameSessionAnswer).filter(
            GameSessionAnswer.game_session_id == game_session_id
        )
        if order_by_question:
            query = query.order_by(GameSessionAnswer.question_number)
        return query.all()

    @staticmethod
    def count_correct_by_game(game_session_id):
        """
        Count number of correct answers in a game
        
        Args:
            game_session_id: Game session ID
            
        Returns:
            Integer count of correct answers
        """
        return db.session.query(GameSessionAnswer).filter(
            GameSessionAnswer.game_session_id == game_session_id,
            GameSessionAnswer.is_correct == True
        ).count()

    @staticmethod
    def count_total_by_game(game_session_id):
        """
        Count total number of answers submitted in a game
        
        Args:
            game_session_id: Game session ID
            
        Returns:
            Integer count of total answers
        """
        return db.session.query(GameSessionAnswer).filter(
            GameSessionAnswer.game_session_id == game_session_id
        ).count()

    @staticmethod
    def get_by_game_paginated(game_session_id, page=1, per_page=50):
        """Get answers for a game with pagination"""
        return db.session.query(GameSessionAnswer).filter(
            GameSessionAnswer.game_session_id == game_session_id
        ).order_by(GameSessionAnswer.question_number).paginate(page=page, per_page=per_page)

    @staticmethod
    def update(answer, **kwargs):
        """Update answer fields (minimal use - answers should be immutable after creation)"""
        for key, value in kwargs.items():
            if hasattr(answer, key):
                setattr(answer, key, value)
        return answer

    @staticmethod
    def delete(answer):
        """Delete an answer record"""
        db.session.delete(answer)
        return answer

    @staticmethod
    def delete_by_game(game_session_id):
        """Delete all answers for a game session (cascade should handle this)"""
        db.session.query(GameSessionAnswer).filter(
            GameSessionAnswer.game_session_id == game_session_id
        ).delete()
        return True

    @staticmethod
    def exists_by_game_and_question(game_session_id, question_number):
        """Check if answer exists for a game and question number"""
        return db.session.query(GameSessionAnswer).filter(
            GameSessionAnswer.game_session_id == game_session_id,
            GameSessionAnswer.question_number == question_number
        ).first() is not None
