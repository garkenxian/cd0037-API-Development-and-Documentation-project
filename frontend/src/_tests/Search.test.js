import React from 'react';
import { render } from '@testing-library/react';
import Search from '../components/Search';

describe('Search Component', () => {
  const mockSubmitSearch = jest.fn();

  beforeEach(() => {
    mockSubmitSearch.mockClear();
  });

  it('renders without crashing', () => {
    render(<Search submitSearch={mockSubmitSearch} />);
  });

  it('renders search input field', () => {
    const { container } = render(<Search submitSearch={mockSubmitSearch} />);
    const input = container.querySelector('input:not([type="submit"])');
    expect(input).toBeTruthy();
    expect(input.placeholder).toBe('Search questions...');
  });

  it('renders submit button', () => {
    const { container } = render(<Search submitSearch={mockSubmitSearch} />);
    const submitButton = container.querySelector('input[type="submit"]');
    expect(submitButton).toBeTruthy();
    expect(submitButton.value).toBe('Submit');
  });

  it('has form element', () => {
    const { container } = render(<Search submitSearch={mockSubmitSearch} />);
    const form = container.querySelector('form');
    expect(form).toBeTruthy();
  });

  it('has button with correct CSS class', () => {
    const { container } = render(<Search submitSearch={mockSubmitSearch} />);
    const submitButton = container.querySelector('.button');
    expect(submitButton).toBeTruthy();
  });
});
