import React from 'react';
import ReactDOM from 'react-dom';
import QuestionView from '../components/QuestionView';

describe('QuestionView Component', () => {
  // Mock jQuery AJAX calls
  beforeEach(() => {
    global.$ = jest.fn(() => ({
      ajax: jest.fn(),
    }));
  });

  it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<QuestionView />, div);
    ReactDOM.unmountComponentAtNode(div);
  });

  it('initializes with empty questions list', () => {
    const div = document.createElement('div');
    const component = ReactDOM.render(<QuestionView />, div);
    expect(component.state.questions).toEqual([]);
    expect(component.state.page).toBe(1);
    ReactDOM.unmountComponentAtNode(div);
  });

  it('initializes with correct state properties', () => {
    const div = document.createElement('div');
    const component = ReactDOM.render(<QuestionView />, div);
    expect(component.state).toHaveProperty('questions');
    expect(component.state).toHaveProperty('page');
    expect(component.state).toHaveProperty('totalQuestions');
    expect(component.state).toHaveProperty('categories');
    expect(component.state).toHaveProperty('currentCategory');
    ReactDOM.unmountComponentAtNode(div);
  });

  it('renders without visible questions initially', () => {
    const div = document.createElement('div');
    ReactDOM.render(<QuestionView />, div);
    // Component should render with the question-view class
    expect(div.querySelector('.question-view')).toBeTruthy();
    ReactDOM.unmountComponentAtNode(div);
  });
});
