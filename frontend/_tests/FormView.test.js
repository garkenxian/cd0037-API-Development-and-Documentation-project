import React from 'react';
import ReactDOM from 'react-dom';
import FormView from '../src/components/FormView';

describe('FormView Component', () => {
  // Mock jQuery AJAX calls
  beforeEach(() => {
    global.$ = jest.fn(() => ({
      ajax: jest.fn(),
    }));
  });

  it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<FormView />, div);
    ReactDOM.unmountComponentAtNode(div);
  });

  it('has a form element', () => {
    const div = document.createElement('div');
    ReactDOM.render(<FormView />, div);
    const form = div.querySelector('form');
    expect(form).toBeTruthy();
    ReactDOM.unmountComponentAtNode(div);
  });

  it('renders form with correct ID', () => {
    const div = document.createElement('div');
    ReactDOM.render(<FormView />, div);
    const form = div.querySelector('#add-question-form');
    expect(form).toBeTruthy();
    ReactDOM.unmountComponentAtNode(div);
  });

  it('has input fields for question and answer', () => {
    const div = document.createElement('div');
    ReactDOM.render(<FormView />, div);
    const inputs = div.querySelectorAll('input, textarea');
    expect(inputs.length).toBeGreaterThan(0);
    ReactDOM.unmountComponentAtNode(div);
  });

  it('has a submit button', () => {
    const div = document.createElement('div');
    ReactDOM.render(<FormView />, div);
    const submitButton = div.querySelector('input[type="submit"]');
    expect(submitButton).toBeTruthy();
    ReactDOM.unmountComponentAtNode(div);
  });
});
