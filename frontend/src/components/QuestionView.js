import React, { Component } from 'react';
import '../stylesheets/App.css';
import Question from './Question';
import Search from './Search';
import { apiGet, apiDelete, apiPost } from '../utils/api';

class QuestionView extends Component {
  constructor() {
    super();
    this.state = {
      questions: [],
      page: 1,
      totalQuestions: 0,
      totalPages: 1,
      categories: {},
      currentCategory: null,
      activeSearch: null,
      newCategoryType: '',
      createCategoryError: '',
      createCategorySuccess: '',
      leaderboard: [],
      leaderboardError: '',
    };
  }

  componentDidMount() {
    this.getQuestions();
    this.getLeaderboard();
  }

  getQuestions = () => {
    // Build URL with page and optional search parameters
    let url = `/questions?page=${this.state.page}`;
    if (this.state.activeSearch) {
      url += `&search=${encodeURIComponent(this.state.activeSearch)}`;
    }

    apiGet(
      url,
      (result) => {
        this.setState({
          questions: result.questions,
          totalQuestions: result.total_questions,
          totalPages: result.total_pages,
          categories: result.categories,
          currentCategory: result.current_category,
        });
      },
      (error) => {
        alert('Unable to load questions. Please try your request again');
      }
    );
  };

  selectPage(num) {
    this.setState({ page: num }, () => this.getQuestions());
  }

  createPagination() {
    let pageNumbers = [];
    for (let i = 1; i <= this.state.totalPages; i++) {
      pageNumbers.push(
        <span
          key={i}
          className={`page-num ${i === this.state.page ? 'active' : ''}`}
          onClick={() => {
            this.selectPage(i);
          }}
        >
          {i}
        </span>
      );
    }
    return pageNumbers;
  }

  getByCategory = (id) => {
    apiGet(
      `/categories/${id}/questions`,
      (result) => {
        this.setState({
          questions: result.questions,
          totalQuestions: result.total_questions,
          totalPages: result.total_pages,
          currentCategory: result.current_category,
          activeSearch: null,
          page: 1,
        });
      },
      (error) => {
        alert('Unable to load questions. Please try your request again');
      }
    );
  };

  submitSearch = (searchTerm) => {
    // Use GET /questions?search=... instead of POST /questions
    apiGet(
      `/questions?search=${encodeURIComponent(searchTerm)}`,
      (result) => {
        this.setState({
          questions: result.questions,
          totalQuestions: result.total_questions,
          totalPages: result.total_pages,
          currentCategory: result.current_category,
          activeSearch: searchTerm,
          page: 1,
        });
      },
      (error) => {
        alert('Unable to load questions. Please try your request again');
      }
    );
  };

  questionAction = (id) => (action) => {
    if (action === 'DELETE') {
      if (window.confirm('are you sure you want to delete the question?')) {
        apiDelete(
          `/questions/${id}`,
          () => {
            // First try refreshing the current page. Only fall back if that page no longer exists.
            this.getQuestionsForPage(
              this.state.page,
              null,
              (error) => {
                const isOutOfRange =
                  typeof error === 'string' &&
                  error.toLowerCase().includes('out of range');

                if (isOutOfRange && this.state.page > 1) {
                  this.getQuestionsForPage(this.state.page - 1);
                  return;
                }

                const errorMsg =
                  typeof error === 'string'
                    ? error
                    : 'Unable to load questions. Please try your request again';
                alert(errorMsg);
              }
            );
          },
          (error) => {
            // Show backend error message if available, otherwise generic message
            const errorMsg = typeof error === 'string' ? error : 'Unable to delete question. Please try your request again';
            alert(errorMsg);
          }
        );
      }
    }
  };

  getQuestionsForPage = (page, onSuccess, onError) => {
    // Helper to fetch questions for a specific page without setting state
    const url = this.state.activeSearch 
      ? `/questions?page=${page}&search=${encodeURIComponent(this.state.activeSearch)}`
      : `/questions?page=${page}`;
    
    apiGet(
      url,
      (result) => {
        this.setState({
          page,
          questions: result.questions,
          totalQuestions: result.total_questions,
          totalPages: result.total_pages,
          categories: result.categories,
          currentCategory: result.current_category,
        });
        if (onSuccess) onSuccess(result);
      },
      (error) => {
        if (onError) onError(error);
      }
    );
  };

  handleCategoryInputChange = (event) => {
    this.setState({
      newCategoryType: event.target.value,
      createCategoryError: '',
      createCategorySuccess: '',
    });
  };

  submitCategory = (event) => {
    event.preventDefault();
    const categoryType = this.state.newCategoryType.trim();

    if (!categoryType) {
      this.setState({ createCategoryError: 'Category name is required' });
      return;
    }

    apiPost(
      '/categories',
      { type: categoryType },
      () => {
        this.setState(
          {
            newCategoryType: '',
            createCategoryError: '',
            createCategorySuccess: 'Category added successfully!',
          },
          () => this.getQuestions()
        );
      },
      (error) => {
        this.setState({
          createCategorySuccess: '',
          createCategoryError:
            typeof error === 'string'
              ? error
              : 'Unable to add category. Please try your request again',
        });
      }
    );
  };

  getLeaderboard = () => {
    apiGet(
      '/users/leaderboard?limit=10',
      (result) => {
        this.setState({
          leaderboard: result.leaderboard || [],
          leaderboardError: '',
        });
      },
      () => {
        this.setState({
          leaderboard: [],
          leaderboardError: 'Unable to load leaderboard',
        });
      }
    );
  };


  render() {
    return (
      <div className='question-view'>
        <div className='categories-list'>
          <h2
            onClick={() => {
              this.setState({ page: 1 }, () => this.getQuestions());
            }}
          >
            Categories
          </h2>
          <form onSubmit={this.submitCategory}>
            <input
              type='text'
              value={this.state.newCategoryType}
              onChange={this.handleCategoryInputChange}
              placeholder='Add category name'
              aria-label='Add category name'
            />
            <input type='submit' className='button' value='Add Category' />
          </form>
          {this.state.createCategoryError && (
            <div className='error-message'>{this.state.createCategoryError}</div>
          )}
          {this.state.createCategorySuccess && (
            <div className='success-message'>
              {this.state.createCategorySuccess}
            </div>
          )}
          <ul>
            {Object.keys(this.state.categories).map((id) => (
              <li
                key={id}
                onClick={() => {
                  this.getByCategory(id);
                }}
              >
                {this.state.categories[id]}
                <img
                  className='category'
                  alt={`${this.state.categories[id].toLowerCase()}`}
                  src={`${this.state.categories[id].toLowerCase()}.svg`}
                  onError={(e) => {
                    e.target.src = '/question-mark-button-svgrepo-com.svg';
                  }}
                />
              </li>
            ))}
          </ul>
          <Search submitSearch={this.submitSearch} />
          <div className='leaderboard-list'>
            <h3>Leaderboard</h3>
            {this.state.leaderboardError && (
              <div className='error-message'>{this.state.leaderboardError}</div>
            )}
            {!this.state.leaderboardError && this.state.leaderboard.length === 0 && (
              <div>No scores yet</div>
            )}
            <ol>
              {this.state.leaderboard.map((entry) => (
                <li key={entry.id}>
                  {entry.username}: {entry.total_score}
                </li>
              ))}
            </ol>
          </div>
        </div>
        <div className='questions-list'>
          <h2>Questions</h2>
          {this.state.questions.map((q, ind) => (
            <Question
              key={q.id}
              question={q.question}
              answer={q.answer}
              category={this.state.categories[q.category]}
              difficulty={q.difficulty}
              questionAction={this.questionAction(q.id)}
            />
          ))}
          <div className='pagination-menu'>{this.createPagination()}</div>
        </div>
      </div>
    );
  }
}

export default QuestionView;
