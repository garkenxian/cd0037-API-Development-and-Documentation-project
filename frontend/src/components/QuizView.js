import React, { Component } from 'react';
import { apiGet, apiPost } from '../utils/api';
import '../stylesheets/QuizView.css';

class QuizView extends Component {
  constructor(props) {
    super(props);
    this.state = {
      // User selection - only show if no user is selected
      showUserSelector: !props.selectedUserId,
      
      // User creation form
      showCreateUserForm: false,
      newUsername: '',
      newEmail: '',
      userCreationError: null,
      isCreatingUser: false,
      
      // Category selection
      quizCategory: null,
      categories: {},
      
      // Game session state
      gameSessionId: null,
      currentQuestionNumber: 1,
      currentScore: {
        correct: 0,
        total_answered: 0,
        total_questions: 5,
      },
      
      // Question and answer state
      currentQuestion: {},
      guess: '',
      showAnswer: false,
      isGameComplete: false,
      wasAnswerCorrect: null,
      correctAnswer: '',
      
      // Error handling
      error: null,
      isLoading: false,
    };
  }

  componentDidMount() {
    apiGet(
      '/categories',
      (result) => {
        this.setState({ categories: result.categories });
      },
      (error) => {
        this.setState({ error: 'Unable to load categories. Please try again.' });
      }
    );
  }

  handleUserSelect = (event) => {
    const userId = parseInt(event.target.value);
    this.props.onSelectUser(userId);
    this.setState({ 
      showUserSelector: false,
      error: null,
    });
  };

  handleCreateUserInputChange = (event) => {
    const { name, value } = event.target;
    this.setState({ [name]: value });
  };

  handleCreateUser = (event) => {
    event.preventDefault();
    const { newUsername, newEmail } = this.state;
    
    if (!newUsername.trim()) {
      this.setState({ userCreationError: 'Username is required' });
      return;
    }

    if (!newEmail.trim()) {
      this.setState({ userCreationError: 'Email is required' });
      return;
    }

    this.setState({ isCreatingUser: true, userCreationError: null });

    const userData = {
      username: newUsername,
      email: newEmail,
    };

    apiPost(
      '/users',
      userData,
      (result) => {
        // User created successfully - refresh users list and auto-select
        if (this.props.onUsersRefresh) {
          this.props.onUsersRefresh(() => {
            // Auto-select the newly created user
            this.props.onSelectUser(result.id);
            this.setState({ 
              showUserSelector: false,
              showCreateUserForm: false,
              newUsername: '',
              newEmail: '',
              userCreationError: null,
              isCreatingUser: false,
              error: null,
            });
          });
        } else {
          // Fallback if callback not provided
          this.setState({ 
            showUserSelector: false,
            showCreateUserForm: false,
            newUsername: '',
            newEmail: '',
            userCreationError: null,
            isCreatingUser: false,
            error: null,
          });
          this.props.onSelectUser(result.id);
        }
      },
      (error) => {
        this.setState({ 
          userCreationError: typeof error === 'string' ? error : 'Failed to create user. Please try again.',
          isCreatingUser: false,
        });
      }
    );
  };

  renderCreateUserForm() {
    return (
      <div className='create-user-form'>
        <h3>Create New User</h3>
        <form onSubmit={this.handleCreateUser}>
          <input
            type='text'
            name='newUsername'
            placeholder='Username'
            value={this.state.newUsername}
            onChange={this.handleCreateUserInputChange}
            disabled={this.state.isCreatingUser}
            required
          />
          <input
            type='email'
            name='newEmail'
            placeholder='Email'
            value={this.state.newEmail}
            onChange={this.handleCreateUserInputChange}
            disabled={this.state.isCreatingUser}
            required
          />
          {this.state.userCreationError && (
            <div className='error-message'>{this.state.userCreationError}</div>
          )}
          <button 
            type='submit'
            disabled={this.state.isCreatingUser}
            className='button'
          >
            {this.state.isCreatingUser ? 'Creating...' : 'Create User'}
          </button>
          <button
            type='button'
            onClick={() => this.setState({ 
              showCreateUserForm: false,
              userCreationError: null,
              newUsername: '',
              newEmail: '',
            })}
            className='button cancel-button'
            disabled={this.state.isCreatingUser}
          >
            Cancel
          </button>
        </form>
      </div>
    );
  }

  selectCategory = ({ type, id = 0 }) => {
    // Validate user is selected before starting game
    if (!this.props.selectedUserId) {
      this.setState({ 
        error: 'Please select a user before starting a game.',
        showUserSelector: true,
      });
      return;
    }
    
    this.setState({ quizCategory: { type, id }, isLoading: true }, this.startGame);
  };

  handleChange = (event) => {
    this.setState({ [event.target.name]: event.target.value });
  };

  startGame = () => {
    const gameData = {
      user_id: this.props.selectedUserId,
      category_id: this.state.quizCategory.id,
      number_of_questions: this.state.currentScore.total_questions,
    };

    apiPost(
      '/games',
      gameData,
      (result) => {
        this.setState({
          gameSessionId: result.game_session_id,
          currentQuestionNumber: result.current_question_number,
          currentScore: result.current_score,
          currentQuestion: result.question,
          guess: '',
          showAnswer: false,
          isGameComplete: false,
          wasAnswerCorrect: null,
          correctAnswer: '',
          isLoading: false,
          error: null,
        });
      },
      (error) => {
        // Check if error is due to missing user
        const userNotFoundError = error && (error.includes('not found') || error.includes('User'));
        if (userNotFoundError) {
          this.setState({
            error: `Selected user (ID: ${this.props.selectedUserId}) not found. Please select a different user.`,
            isLoading: false,
            showUserSelector: true,
          });
        } else {
          this.setState({
            error: error || 'Unable to start game. Please try again.',
            isLoading: false,
          });
        }
      }
    );
  };

  submitGuess = (event) => {
    event.preventDefault();
    this.setState({ isLoading: true });

    const answerData = {
      user_answer: this.state.guess,
    };

    apiPost(
      `/games/${this.state.gameSessionId}/${this.state.currentQuestionNumber}`,
      answerData,
      (result) => {
        // Handle game completion
        if (result.status === 'completed') {
          this.setState({
            isGameComplete: true,
            currentScore: result.current_score,
            isLoading: false,
            error: null,
          });
        } else {
          // Game continues - show answer, then prepare for next question
          this.setState({
            wasAnswerCorrect: result.correct,
            correctAnswer: result.correct_answer,
            showAnswer: true,
            currentScore: result.current_score,
            isLoading: false,
            error: null,
          });
        }
      },
      (error) => {
        this.setState({
          error: error || 'Unable to submit answer. Please try again.',
          isLoading: false,
        });
      }
    );
  };

  getNextQuestion = () => {
    // After viewing the answer, load the next question
    this.setState({
      currentQuestionNumber: this.state.currentScore.total_answered + 1,
      currentQuestion: {},
      guess: '',
      showAnswer: false,
      wasAnswerCorrect: null,
      correctAnswer: '',
    });

    // Fetch the next question by calling GET /games/<id>
    apiGet(
      `/games/${this.state.gameSessionId}`,
      (result) => {
        if (result.status === 'completed') {
          this.setState({
            isGameComplete: true,
            currentScore: result.current_score,
          });
        } else {
          this.setState({
            currentQuestionNumber: result.current_question_number,
            currentScore: result.current_score,
            currentQuestion: result.question,
          });
        }
      },
      (error) => {
        this.setState({
          error: error || 'Unable to load next question. Please try again.',
        });
      }
    );
  };

  restartGame = () => {
    this.setState({
      showUserSelector: false,
      quizCategory: null,
      gameSessionId: null,
      currentQuestionNumber: 1,
      currentScore: {
        correct: 0,
        total_answered: 0,
        total_questions: 5,
      },
      currentQuestion: {},
      guess: '',
      showAnswer: false,
      isGameComplete: false,
      wasAnswerCorrect: null,
      correctAnswer: '',
      error: null,
    });
  };

  renderUserSelector() {
    if (this.state.showCreateUserForm) {
      return (
        <div className='quiz-play-holder'>
          {this.renderCreateUserForm()}
        </div>
      );
    }

    return (
      <div className='quiz-play-holder'>
        <div className='choose-header'>Select a User</div>
        <div className='user-selector'>
          <select onChange={this.handleUserSelect} defaultValue=''>
            <option value=''>-- Choose a User --</option>
            {this.props.users && this.props.users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.username} (ID: {user.id})
              </option>
            ))}
          </select>
          {(!this.props.users || this.props.users.length === 0) && (
            <div className='error-message'>
              No users available. Create one below to get started!
            </div>
          )}
        </div>
        <button
          className='button create-user-button'
          onClick={() => this.setState({ showCreateUserForm: true })}
        >
          + Create New User
        </button>
        <div className='back-button' onClick={() => this.setState({ showUserSelector: false })}>
          Back to Categories
        </div>
      </div>
    );
  }

  renderPrePlay() {
    // Show user selector if needed
    if (this.state.showUserSelector || !this.props.selectedUserId) {
      return this.renderUserSelector();
    }

    return (
      <div className='quiz-play-holder'>
        <div className='choose-header'>Choose Category</div>
        <div className='current-user'>
          Playing as: <strong>{this.getCurrentUsername()}</strong>
          <button 
            className='change-user-button'
            onClick={() => this.setState({ showUserSelector: true })}
          >
            Change User
          </button>
        </div>
        <div className='category-holder'>
          <div 
            className='play-category' 
            onClick={() => this.selectCategory({ type: 'ALL', id: 0 })}
          >
            ALL
          </div>
          {Object.keys(this.state.categories).map((id) => {
            return (
              <div
                key={id}
                value={id}
                className='play-category'
                onClick={() =>
                  this.selectCategory({ type: this.state.categories[id], id: parseInt(id) })
                }
              >
                {this.state.categories[id]}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  getCurrentUsername() {
    if (!this.props.selectedUserId || !this.props.users) {
      return 'Unknown';
    }
    const user = this.props.users.find(u => u.id === this.props.selectedUserId);
    return user ? user.username : 'Unknown';
  }

  renderFinalScore() {
    return (
      <div className='quiz-play-holder'>
        <div className='final-header'>
          Your Final Score is {this.state.currentScore.correct} out of{' '}
          {this.state.currentScore.total_questions}
        </div>
        <div className='play-again button' onClick={this.restartGame}>
          Play Again?
        </div>
      </div>
    );
  }

  renderCorrectAnswer() {
    return (
      <div className='quiz-play-holder'>
        <div className='quiz-question'>
          {this.state.currentQuestion.question}
        </div>
        <div className={`${this.state.wasAnswerCorrect ? 'correct' : 'wrong'}`}>
          {this.state.wasAnswerCorrect ? 'You were correct!' : 'You were incorrect'}
        </div>
        <div className='quiz-answer'>{this.state.correctAnswer}</div>
        <div className='next-question button' onClick={this.getNextQuestion}>
          {' '}
          Next Question{' '}
        </div>
      </div>
    );
  }

  renderPlay() {
    if (this.state.isLoading) {
      return (
        <div className='quiz-play-holder'>
          <div>Loading...</div>
        </div>
      );
    }

    if (this.state.error) {
      return (
        <div className='quiz-play-holder'>
          <div className='error-message'>{this.state.error}</div>
          <div className='play-again button' onClick={this.restartGame}>
            Back to Categories
          </div>
        </div>
      );
    }

    return this.state.isGameComplete
      ? this.renderFinalScore()
      : this.state.showAnswer
      ? this.renderCorrectAnswer()
      : (
        <div className='quiz-play-holder'>
          <div className='quiz-question'>
            {this.state.currentQuestion.question}
          </div>
          <form onSubmit={this.submitGuess}>
            <input type='text' name='guess' onChange={this.handleChange} />
            <input
              className='submit-guess button'
              type='submit'
              value='Submit Answer'
            />
          </form>
        </div>
      );
  }

  render() {
    return this.state.quizCategory ? this.renderPlay() : this.renderPrePlay();
  }
}

export default QuizView;
