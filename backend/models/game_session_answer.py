"""GameSessionAnswer model - Immutable audit trail for game answers"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint, CheckConstraint
from . import db


class GameSessionAnswer(db.Model):
    """
    GameSessionAnswer model for recording player answers with immutable snapshots.
    
    This table creates an audit trail where each answer submission is persisted:
    - Original question and answer snapshots (immutable)
    - User's submitted answer
    - Correctness result
    
    This ensures game flow is deterministic and replayable.
    Use GameSessionAnswerRepository and GameSessionAnswerService for operations.
    """
    __tablename__ = 'game_session_answers'
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('game_session_id', 'question_number', name='uq_game_question_number'),
        CheckConstraint('question_number >= 1', name='ck_question_number_positive'),
        CheckConstraint('length(question_snapshot) >= 1', name='ck_question_snapshot_not_empty'),
        CheckConstraint('length(answer_snapshot) >= 1', name='ck_answer_snapshot_not_empty'),
    )

    id = Column(Integer, primary_key=True)
    game_session_id = Column(Integer, ForeignKey('game_sessions.id', ondelete='CASCADE'), nullable=False)
    question_number = Column(Integer, nullable=False)  # 1-based: 1..N
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='RESTRICT'), nullable=False)
    question_snapshot = Column(String, nullable=False)  # Immutable copy of question text
    answer_snapshot = Column(String, nullable=False)  # Immutable copy of correct answer
    user_answer = Column(String, nullable=False)  # What user submitted
    is_correct = Column(Boolean, nullable=False)  # Result of comparison
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __init__(self, game_session_id, question_number, question_id, question_snapshot, 
                 answer_snapshot, user_answer, is_correct):
        self.game_session_id = game_session_id
        self.question_number = question_number
        self.question_id = question_id
        self.question_snapshot = question_snapshot
        self.answer_snapshot = answer_snapshot
        self.user_answer = user_answer
        self.is_correct = is_correct

    def format(self):
        """Return formatted answer record as dictionary"""
        return {
            'id': self.id,
            'game_session_id': self.game_session_id,
            'question_number': self.question_number,
            'question_id': self.question_id,
            'question_snapshot': self.question_snapshot,
            'answer_snapshot': self.answer_snapshot,
            'user_answer': self.user_answer,
            'is_correct': self.is_correct,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<GameSessionAnswer game_session={self.game_session_id}, question={self.question_number}, correct={self.is_correct}>'
