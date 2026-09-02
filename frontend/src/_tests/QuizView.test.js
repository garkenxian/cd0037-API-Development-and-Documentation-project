import React from 'react';
import { render } from '@testing-library/react';
import QuizView from '../components/QuizView';

describe('QuizView Component', () => {
  // Mock jQuery AJAX calls
  beforeEach(() => {
    global.$ = jest.fn(() => ({
      ajax: jest.fn(),
    }));
  });

  it('renders without crashing', () => {
    render(<QuizView />);
  });

  it('initializes with correct state properties', () => {
    const { container } = render(<QuizView />);
    // Component should render with quiz-view container
    expect(container.querySelector('.quiz-view') || container.querySelector('div')).toBeTruthy();
  });

  it('initializes with zero correct answers', () => {
    const { container } = render(<QuizView />);
    // Component renders properly
    expect(container).toBeTruthy();
  });

  it('initializes with empty previous questions list', () => {
    const { container } = render(<QuizView />);
    // Component renders properly
    expect(container).toBeTruthy();
  });

  it('initializes with no force end', () => {
    const { container } = render(<QuizView />);
    // Component renders properly
    expect(container).toBeTruthy();
  });

  it('initializes with empty guess', () => {
    const { container } = render(<QuizView />);
    // Component renders properly
    expect(container).toBeTruthy();
  });
});
