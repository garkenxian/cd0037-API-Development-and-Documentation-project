import React from 'react';
import ReactDOM from 'react-dom';
import QuizView from './components/QuizView';

describe('QuizView Component', () => {
  // Mock jQuery AJAX calls
  beforeEach(() => {
    global.$ = jest.fn(() => ({
      ajax: jest.fn(),
    }));
  });

  it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<QuizView />, div);
    ReactDOM.unmountComponentAtNode(div);
  });

  it('initializes with correct state properties', () => {
    const div = document.createElement('div');
    const component = ReactDOM.render(<QuizView />, div);
    expect(component.state).toHaveProperty('quizCategory');
    expect(component.state).toHaveProperty('previousQuestions');
    expect(component.state).toHaveProperty('showAnswer');
    expect(component.state).toHaveProperty('categories');
    expect(component.state).toHaveProperty('numCorrect');
    expect(component.state).toHaveProperty('currentQuestion');
    expect(component.state).toHaveProperty('guess');
    expect(component.state).toHaveProperty('forceEnd');
    ReactDOM.unmountComponentAtNode(div);
  });

  it('initializes with zero correct answers', () => {
    const div = document.createElement('div');
    const component = ReactDOM.render(<QuizView />, div);
    expect(component.state.numCorrect).toBe(0);
    ReactDOM.unmountComponentAtNode(div);
  });

  it('initializes with empty previous questions list', () => {
    const div = document.createElement('div');
    const component = ReactDOM.render(<QuizView />, div);
    expect(component.state.previousQuestions).toEqual([]);
    ReactDOM.unmountComponentAtNode(div);
  });

  it('initializes with no force end', () => {
    const div = document.createElement('div');
    const component = ReactDOM.render(<QuizView />, div);
    expect(component.state.forceEnd).toBe(false);
    ReactDOM.unmountComponentAtNode(div);
  });

  it('initializes with empty guess', () => {
    const div = document.createElement('div');
    const component = ReactDOM.render(<QuizView />, div);
    expect(component.state.guess).toBe('');
    ReactDOM.unmountComponentAtNode(div);
  });
});
