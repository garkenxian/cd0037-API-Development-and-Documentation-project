"""GameSessionAnswer Service - Business logic for game answer operations"""

import re
from data_access import db, GameSessionAnswerRepository, GameSessionRepository


class GameSessionAnswerService:
    """Service layer for game answer operations - ensures deterministic, auditable game flow"""

    @staticmethod
    def record_answer(game_session_id, question_number, question, user_answer):
        """
        Record or update an answer submission for a game question.
        
        If answer already exists (question was served but not yet answered),
        this updates the existing record with the user's answer.
        
        If answer doesn't exist (next question, first access), this creates a new record.
        
        Ensures:
        - Question number is in valid range
        - Answer is validated against stored question snapshot
        - Result is persisted for audit trail
        
        Args:
            game_session_id: Game session ID
            question_number: Question number (1-based)
            question: Question object with question/answer text
            user_answer: User's submitted answer (string, can be empty for first served question)
            
        Returns:
            Dict with: {
                'game_session_id': int,
                'question_number': int,
                'is_correct': bool,
                'correct_answer': str,
                'answered_question_number': int
            }
            
        Raises:
            ValueError: If validation fails (out of range, etc)
        """
        if not game_session_id or not question or user_answer is None:
            raise ValueError("game_session_id, question, and user_answer are required")
        
        if not isinstance(question_number, int) or question_number < 1:
            raise ValueError("question_number must be a positive integer")
        
        # Get game session to check bounds
        game_session = GameSessionRepository.get_by_id(game_session_id)
        if not game_session:
            raise ValueError(f"Game session {game_session_id} not found")
        
        if question_number > game_session.number_of_questions:
            raise ValueError(
                f"question_number {question_number} exceeds game length {game_session.number_of_questions}"
            )
        
        # Check if answer record already exists (question was served)
        existing_record = GameSessionAnswerRepository.get_by_game_and_question(game_session_id, question_number)
        
        # Normalize and compare answers
        is_correct = GameSessionAnswerService._compare_answers(question.answer, user_answer)
        
        if existing_record:
            # Update existing record with user answer
            existing_record.user_answer = user_answer
            existing_record.is_correct = is_correct
            # Note: question_id, question_snapshot, answer_snapshot should not change
        else:
            # Create new record (for next question, first access)
            existing_record = GameSessionAnswerRepository.create(
                game_session_id=game_session_id,
                question_number=question_number,
                question_id=question.id,
                question_snapshot=question.question,
                answer_snapshot=question.answer,
                user_answer=user_answer,
                is_correct=is_correct
            )
        
        # Note: Caller is responsible for db.session.commit()
        
        return {
            'game_session_id': game_session_id,
            'question_number': question_number,
            'is_correct': is_correct,
            'correct_answer': question.answer,
            'answered_question_number': question_number,
            'answer_record': existing_record
        }

    @staticmethod
    def _compare_answers(correct_answer, user_answer):
        """
        Normalize and compare answers.
        
        Normalization:
        - Convert to lowercase
        - Remove punctuation
        - Collapse whitespace
        - Match exact normalized string OR all words present
        
        Args:
            correct_answer: Expected answer text
            user_answer: User's submitted answer
            
        Returns:
            Boolean indicating correctness
        """
        def normalize(text):
            if not text:
                return ""
            text = text.lower()
            text = re.sub(r'[^a-z0-9\s]', '', text)
            text = ' '.join(text.split())
            return text
        
        correct_normalized = normalize(correct_answer)
        user_normalized = normalize(user_answer)
        
        # Exact match or all words present
        return (
            user_normalized == correct_normalized or
            all(word in user_normalized for word in correct_normalized.split())
        )

    @staticmethod
    def get_game_answers(game_session_id):
        """
        Retrieve all answers for a game session.
        
        Args:
            game_session_id: Game session ID
            
        Returns:
            List of GameSessionAnswer objects
        """
        return GameSessionAnswerRepository.get_by_game(game_session_id, order_by_question=True)

    @staticmethod
    def compute_game_score(game_session_id):
        """
        Compute current score by counting correct answers.
        
        Args:
            game_session_id: Game session ID
            
        Returns:
            Integer count of correct answers
        """
        return GameSessionAnswerRepository.count_correct_by_game(game_session_id)

    @staticmethod
    def get_total_answered(game_session_id):
        """
        Get count of questions actually answered by user (with non-empty user_answer).
        
        Args:
            game_session_id: Game session ID
            
        Returns:
            Integer count of submitted answers
        """
        answers = GameSessionAnswerRepository.get_by_game(game_session_id)
        return sum(1 for ans in answers if ans.user_answer and ans.user_answer.strip())

    @staticmethod
    def has_submitted_answer(game_session_id, question_number):
        """
        Check if a non-empty answer was already submitted for a question.
        
        Note: A record may exist with empty user_answer (served but not yet answered).
        This method returns True only if an actual user submission exists.
        
        Args:
            game_session_id: Game session ID
            question_number: Question number to check
            
        Returns:
            Boolean - True if non-empty answer already submitted
        """
        record = GameSessionAnswerRepository.get_by_game_and_question(game_session_id, question_number)
        if not record:
            return False
        return bool(record.user_answer and record.user_answer.strip())

    @staticmethod
    def get_next_question_number(game_session_id, number_of_questions):
        """
        Find the first unanswered question number.
        
        A question is considered "answered" if it has a non-empty user_answer.
        A question is "unanswered" if it doesn't exist in audit trail, or exists with empty user_answer.
        
        Args:
            game_session_id: Game session ID
            number_of_questions: Total questions in game (1..N)
            
        Returns:
            Integer question_number of first unanswered, or None if all answered
        """
        # Get all answer records
        answers = GameSessionAnswerRepository.get_by_game(game_session_id)
        
        # Build map of question_number -> has_user_answer
        answered_map = {}
        for answer in answers:
            has_answer = answer.user_answer is not None and answer.user_answer.strip() != ''
            answered_map[answer.question_number] = has_answer
        
        # Find first unanswered question
        for q_num in range(1, number_of_questions + 1):
            # If not in audit trail at all, or has empty user_answer, it's unanswered
            if q_num not in answered_map or not answered_map[q_num]:
                return q_num
        
        # All questions answered
        return None

    @staticmethod
    def is_game_complete(game_session_id, number_of_questions):
        """
        Check if all questions in a game have been answered (have non-empty user_answer).
        
        Args:
            game_session_id: Game session ID
            number_of_questions: Total questions in game
            
        Returns:
            Boolean - True if all questions answered by user
        """
        # Get all answer records
        answers = GameSessionAnswerRepository.get_by_game(game_session_id)
        
        # Count how many have non-empty user_answer
        answered_count = sum(1 for ans in answers if ans.user_answer and ans.user_answer.strip())
        
        return answered_count >= number_of_questions

    @staticmethod
    def get_game_state_summary(game_session_id):
        """
        Get summary of game state for display.
        
        Args:
            game_session_id: Game session ID
            
        Returns:
            Dict with: {
                'correct': int,
                'total_answered': int,
                'total_questions': int  # from GameSession
            }
        """
        game_session = GameSessionRepository.get_by_id(game_session_id)
        if not game_session:
            raise ValueError(f"Game session {game_session_id} not found")
        
        correct = GameSessionAnswerService.compute_game_score(game_session_id)
        total_answered = GameSessionAnswerService.get_total_answered(game_session_id)
        
        return {
            'correct': correct,
            'total_answered': total_answered,
            'total_questions': game_session.number_of_questions
        }
