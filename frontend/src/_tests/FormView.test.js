import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import FormView from '../components/FormView';
import * as api from '../utils/api';

jest.mock('../utils/api');

describe('FormView Component', () => {
  const mockCategories = {
    1: 'Science',
    2: 'Art',
    3: 'Geography',
  };

  const mockSuccessResponse = {
    id: 25,
    question: 'What is H2O?',
    answer: 'Water',
    category: 1,
    difficulty: 2,
    rating: 0,
    success: true,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    
    api.apiGet.mockImplementation((url, onSuccess, onError) => {
      if (url.includes('/categories')) {
        onSuccess({ categories: mockCategories });
      }
    });

    api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
      if (url.includes('/questions')) {
        onSuccess(mockSuccessResponse);
      }
    });
  });

  describe('Initialization', () => {
    it('renders without crashing', () => {
      render(<FormView />);
      expect(api.apiGet).toHaveBeenCalledWith(
        '/categories',
        expect.any(Function),
        expect.any(Function)
      );
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

    it('loads categories on mount', async () => {
      render(<FormView />);
      
      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalledWith(
          '/categories',
          expect.any(Function),
          expect.any(Function)
        );
      });
    });

    it('displays category options', async () => {
      const { container } = render(<FormView />);
      
      await waitFor(() => {
        expect(container.textContent).toContain('Science');
        expect(container.textContent).toContain('Art');
        expect(container.textContent).toContain('Geography');
      });
    });
  });

  describe('Form Submission', () => {
    it('submits question with correct payload', async () => {
      const { container } = render(<FormView />);

      // Wait for categories to load
      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      // Fill form
      const questionInput = container.querySelector('input[name="question"]');
      const answerInput = container.querySelector('input[name="answer"]');
      const difficultySelect = container.querySelector('select[name="difficulty"]');
      const categorySelect = container.querySelector('select[name="category"]');

      fireEvent.change(questionInput, { target: { value: 'What is H2O?' } });
      fireEvent.change(answerInput, { target: { value: 'Water' } });
      fireEvent.change(difficultySelect, { target: { value: '2' } });
      fireEvent.change(categorySelect, { target: { value: '1' } });

      // Submit form
      const form = container.querySelector('form');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalledWith(
          '/questions',
          {
            question: 'What is H2O?',
            answer: 'Water',
            difficulty: 2,
            category: 1,
          },
          expect.any(Function),
          expect.any(Function)
        );
      });
    });

    it('displays success message after submission', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      // Fill and submit form
      const questionInput = container.querySelector('input[name="question"]');
      const answerInput = container.querySelector('input[name="answer"]');
      fireEvent.change(questionInput, { target: { value: 'What is H2O?' } });
      fireEvent.change(answerInput, { target: { value: 'Water' } });

      const form = container.querySelector('form');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(container.textContent).toContain('Question added successfully');
      });
    });

    it('resets form fields after submission', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const questionInput = container.querySelector('input[name="question"]');
      const answerInput = container.querySelector('input[name="answer"]');
      fireEvent.change(questionInput, { target: { value: 'What is H2O?' } });
      fireEvent.change(answerInput, { target: { value: 'Water' } });

      const form = container.querySelector('form');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(questionInput.value).toBe('');
        expect(answerInput.value).toBe('');
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error message when submission fails', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url.includes('/questions')) {
          onError('Category not found');
        }
      });

      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const questionInput = container.querySelector('input[name="question"]');
      const answerInput = container.querySelector('input[name="answer"]');
      fireEvent.change(questionInput, { target: { value: 'What is H2O?' } });
      fireEvent.change(answerInput, { target: { value: 'Water' } });

      const form = container.querySelector('form');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(container.textContent).toContain('Category not found');
      });
    });

    it('displays error message when categories fail to load', async () => {
      api.apiGet.mockImplementation((url, onSuccess, onError) => {
        if (url.includes('/categories')) {
          onError('Unable to load categories');
        }
      });

      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(container.textContent).toContain('Unable to load categories');
      });
    });
  });

  describe('Timer Cleanup', () => {
    it('clears success message timer on unmount', async () => {
      const { container, unmount } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      // Fill and submit form
      const questionInput = container.querySelector('input[name="question"]');
      const answerInput = container.querySelector('input[name="answer"]');
      fireEvent.change(questionInput, { target: { value: 'What is H2O?' } });
      fireEvent.change(answerInput, { target: { value: 'Water' } });

      const form = container.querySelector('form');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(container.textContent).toContain('Question added successfully');
      });

      // Unmount before timer completes - should not throw or cause errors
      expect(() => {
        unmount();
      }).not.toThrow();
    });
  });

  describe('API Contract Verification', () => {
    it('uses apiGet for categories endpoint', async () => {
      render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalledWith(
          '/categories',
          expect.any(Function),
          expect.any(Function)
        );
      });
    });

    it('uses apiPost for questions submission', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const questionInput = container.querySelector('input[name="question"]');
      const answerInput = container.querySelector('input[name="answer"]');
      fireEvent.change(questionInput, { target: { value: 'What is H2O?' } });
      fireEvent.change(answerInput, { target: { value: 'Water' } });

      const form = container.querySelector('form');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalledWith(
          '/questions',
          expect.any(Object),
          expect.any(Function),
          expect.any(Function)
        );
      });
    });
  });
});
