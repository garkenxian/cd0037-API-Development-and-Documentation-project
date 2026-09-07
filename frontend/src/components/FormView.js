import React, { Component } from 'react';
import { apiGet, apiPost } from '../utils/api';
import '../stylesheets/FormView.css';

class FormView extends Component {
  constructor(props) {
    super(props);
    this.state = {
      question: '',
      answer: '',
      difficulty: 1,
      category: 1,
      categories: {},
      error: '',
      successMessage: '',
    };
    this.successMessageTimer = null;
  }

  componentDidMount() {
    apiGet(
      '/categories',
      (result) => {
        this.setState({ categories: result.categories });
      },
      (error) => {
        this.setState({ error: 'Unable to load categories. Please try your request again' });
      }
    );
  }

  componentWillUnmount() {
    // Clean up timer to prevent state updates after unmount
    if (this.successMessageTimer) {
      clearTimeout(this.successMessageTimer);
    }
  }

  submitQuestion = (event) => {
    event.preventDefault();
    apiPost(
      '/questions',
      {
        question: this.state.question,
        answer: this.state.answer,
        difficulty: parseInt(this.state.difficulty),
        category: parseInt(this.state.category),
      },
      (result) => {
        document.getElementById('add-question-form').reset();
        this.setState({
          question: '',
          answer: '',
          difficulty: 1,
          category: 1,
          successMessage: 'Question added successfully!',
          error: '',
        });
        // Clear success message after 3 seconds with proper cleanup
        if (this.successMessageTimer) {
          clearTimeout(this.successMessageTimer);
        }
        this.successMessageTimer = setTimeout(() => {
          this.setState({ successMessage: '' });
          this.successMessageTimer = null;
        }, 3000);
      },
      (error) => {
        this.setState({ error: error || 'Unable to add question. Please try your request again' });
      }
    );
  };

  handleChange = (event) => {
    this.setState({ [event.target.name]: event.target.value });
  };

  render() {
    return (
      <div id='add-form'>
        <h2>Add a New Trivia Question</h2>
        {this.state.error && <div className='error-message'>{this.state.error}</div>}
        {this.state.successMessage && <div className='success-message'>{this.state.successMessage}</div>}
        <form
          className='form-view'
          id='add-question-form'
          onSubmit={this.submitQuestion}
        >
          <label>
            Question
            <input type='text' name='question' onChange={this.handleChange} required />
          </label>
          <label>
            Answer
            <input type='text' name='answer' onChange={this.handleChange} required />
          </label>
          <label>
            Difficulty
            <select name='difficulty' onChange={this.handleChange}>
              <option value='1'>1</option>
              <option value='2'>2</option>
              <option value='3'>3</option>
              <option value='4'>4</option>
              <option value='5'>5</option>
            </select>
          </label>
          <label>
            Category
            <select name='category' onChange={this.handleChange}>
              {Object.keys(this.state.categories).map((id) => {
                return (
                  <option key={id} value={id}>
                    {this.state.categories[id]}
                  </option>
                );
              })}
            </select>
          </label>
          <input type='submit' className='button' value='Submit' />
        </form>
      </div>
    );
  }
}

export default FormView;
