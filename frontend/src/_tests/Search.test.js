import React from 'react';
import ReactDOM from 'react-dom';
import Search from '../components/Search';

describe('Search Component', () => {
  const mockSubmitSearch = jest.fn();

  beforeEach(() => {
    mockSubmitSearch.mockClear();
  });

  it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<Search submitSearch={mockSubmitSearch} />, div);
    ReactDOM.unmountComponentAtNode(div);
  });

  it('renders search input field', () => {
    const div = document.createElement('div');
    ReactDOM.render(<Search submitSearch={mockSubmitSearch} />, div);
    const input = div.querySelector('input:not([type="submit"])');
    expect(input).toBeTruthy();
    expect(input.placeholder).toBe('Search questions...');
    ReactDOM.unmountComponentAtNode(div);
  });

  it('renders submit button', () => {
    const div = document.createElement('div');
    ReactDOM.render(<Search submitSearch={mockSubmitSearch} />, div);
    const submitButton = div.querySelector('input[type="submit"]');
    expect(submitButton).toBeTruthy();
    expect(submitButton.value).toBe('Submit');
    ReactDOM.unmountComponentAtNode(div);
  });

  it('has form element', () => {
    const div = document.createElement('div');
    ReactDOM.render(<Search submitSearch={mockSubmitSearch} />, div);
    const form = div.querySelector('form');
    expect(form).toBeTruthy();
    ReactDOM.unmountComponentAtNode(div);
  });

  it('has button with correct CSS class', () => {
    const div = document.createElement('div');
    ReactDOM.render(<Search submitSearch={mockSubmitSearch} />, div);
    const submitButton = div.querySelector('.button');
    expect(submitButton).toBeTruthy();
    ReactDOM.unmountComponentAtNode(div);
  });
});
