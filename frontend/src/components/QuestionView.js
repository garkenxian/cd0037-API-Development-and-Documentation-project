import React, { Component } from 'react';
import '../stylesheets/App.css';
import Question from './Question';
import Search from './Search';
import { apiGet, apiDelete } from '../utils/api';

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
    };
  }

  componentDidMount() {
    this.getQuestions();
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
          (result) => {
            // After deletion, check if we need to go back a page
            // If current page > totalPages after deletion, go to previous page
            if (this.state.page > this.state.totalPages - 1) {
              this.setState({ page: Math.max(1, this.state.page - 1) }, () => {
                this.getQuestions();
              });
            } else {
              this.getQuestions();
            }
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
                />
              </li>
            ))}
          </ul>
          <Search submitSearch={this.submitSearch} />
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
