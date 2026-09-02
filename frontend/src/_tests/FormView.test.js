import React from 'react';
import { render } from '@testing-library/react';
import FormView from '../components/FormView';

describe('FormView Component', () => {
  // Mock jQuery AJAX calls
  beforeEach(() => {
    global.$ = jest.fn(() => ({
      ajax: jest.fn(),
    }));
  });

  it('renders without crashing', () => {
    render(<FormView />);
  });

  it('has a form element', () => {
    const { container } = render(<FormView />);
    const form = container.querySelector('form');
    expect(form).toBeTruthy();
  });

  it('renders form with correct ID', () => {
    const { container } = render(<FormView />);
    const form = container.querySelector('#add-question-form');
    expect(form).toBeTruthy();
  });

  it('has input fields for question and answer', () => {
    const { container } = render(<FormView />);
    const inputs = container.querySelectorAll('input, textarea');
    expect(inputs.length).toBeGreaterThan(0);
  });

  it('has a submit button', () => {
    const { container } = render(<FormView />);
    const submitButton = container.querySelector('input[type="submit"]');
    expect(submitButton).toBeTruthy();
  });
});
