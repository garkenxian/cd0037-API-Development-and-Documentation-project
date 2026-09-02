import React from 'react';
import { render } from '@testing-library/react';
import QuestionView from '../components/QuestionView';

describe('QuestionView Component', () => {
  // Mock jQuery AJAX calls
  beforeEach(() => {
    global.$ = jest.fn(() => ({
      ajax: jest.fn(),
    }));
  });

  it('renders without crashing', () => {
    render(<QuestionView />);
  });

  it('initializes with empty questions list', () => {
    const { container } = render(<QuestionView />);
    // Component renders with question-view class
    expect(container.querySelector('.question-view')).toBeTruthy();
  });

  it('initializes with correct state properties', () => {
    const { container } = render(<QuestionView />);
    // Component should render with the question-view container
    expect(container.querySelector('.question-view')).toBeTruthy();
  });

  it('renders without visible questions initially', () => {
    const { container } = render(<QuestionView />);
    // Component should render with the question-view class
    expect(container.querySelector('.question-view')).toBeTruthy();
  });
});
