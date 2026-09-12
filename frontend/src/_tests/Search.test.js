import React from 'react';
import { render, fireEvent } from '@testing-library/react';
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

  describe('Form Submission', () => {
    it('calls submitSearch when form is submitted', () => {
      const { container } = render(<Search submitSearch={mockSubmitSearch} />);
      const form = container.querySelector('form');
      fireEvent.submit(form);
      expect(mockSubmitSearch).toHaveBeenCalled();
    });

    it('submits empty query on initial submit', () => {
      const { container } = render(<Search submitSearch={mockSubmitSearch} />);
      const form = container.querySelector('form');
      fireEvent.submit(form);
      expect(mockSubmitSearch).toHaveBeenCalledWith('');
    });

    it('updates query state on input change', () => {
      const { container } = render(<Search submitSearch={mockSubmitSearch} />);
      const input = container.querySelector('input:not([type="submit"])');
      fireEvent.change(input, { target: { value: 'science' } });
      expect(input.value).toBe('science');
    });

    it('submits entered query when form is submitted', () => {
      const { container } = render(<Search submitSearch={mockSubmitSearch} />);
      const input = container.querySelector('input:not([type="submit"])');
      fireEvent.change(input, { target: { value: 'biology' } });
      const form = container.querySelector('form');
      fireEvent.submit(form);
      expect(mockSubmitSearch).toHaveBeenCalledWith('biology');
    });

    it('prevents default form submission', () => {
      const { container } = render(<Search submitSearch={mockSubmitSearch} />);
      const form = container.querySelector('form');
      const event = new Event('submit', { bubbles: true });
      const preventDefaultSpy = jest.spyOn(event, 'preventDefault');
      form.dispatchEvent(event);
      expect(preventDefaultSpy).toHaveBeenCalled();
    });
  });
});
