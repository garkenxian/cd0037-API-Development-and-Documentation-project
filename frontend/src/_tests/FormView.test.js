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

  describe('Field Handling', () => {
    it('updates question field on input change', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const questionInput = container.querySelector('input[name="question"]');
      fireEvent.change(questionInput, { target: { value: 'New question?' } });

      expect(questionInput.value).toBe('New question?');
    });

    it('updates answer field on input change', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const answerInput = container.querySelector('input[name="answer"]');
      fireEvent.change(answerInput, { target: { value: 'New answer' } });

      expect(answerInput.value).toBe('New answer');
    });

    it('updates difficulty select on change', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const difficultySelect = container.querySelector('select[name="difficulty"]');
      fireEvent.change(difficultySelect, { target: { value: '3' } });

      expect(difficultySelect.value).toBe('3');
    });

    it('updates category select on change', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const categorySelect = container.querySelector('select[name="category"]');
      fireEvent.change(categorySelect, { target: { value: '2' } });

      expect(categorySelect.value).toBe('2');
    });
  });

  describe('Type Conversion', () => {
    it('converts difficulty to integer before posting', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const questionInput = container.querySelector('input[name="question"]');
      const answerInput = container.querySelector('input[name="answer"]');
      const difficultySelect = container.querySelector('select[name="difficulty"]');

      fireEvent.change(questionInput, { target: { value: 'Q?' } });
      fireEvent.change(answerInput, { target: { value: 'A' } });
      fireEvent.change(difficultySelect, { target: { value: '4' } });

      const form = container.querySelector('form');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalledWith(
          '/questions',
          expect.objectContaining({
            difficulty: 4, // Must be integer, not string
          }),
          expect.any(Function),
          expect.any(Function)
        );
      });
    });

    it('converts category to integer before posting', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const questionInput = container.querySelector('input[name="question"]');
      const answerInput = container.querySelector('input[name="answer"]');
      const categorySelect = container.querySelector('select[name="category"]');

      fireEvent.change(questionInput, { target: { value: 'Q?' } });
      fireEvent.change(answerInput, { target: { value: 'A' } });
      fireEvent.change(categorySelect, { target: { value: '3' } });

      const form = container.querySelector('form');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalledWith(
          '/questions',
          expect.objectContaining({
            category: 3, // Must be integer, not string
          }),
          expect.any(Function),
          expect.any(Function)
        );
      });
    });
  });

  describe('Form State', () => {
    it('has correct default difficulty value', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const difficultySelect = container.querySelector('select[name="difficulty"]');
      expect(difficultySelect.value).toBe('1');
    });

    it('has correct default category value', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const categorySelect = container.querySelector('select[name="category"]');
      expect(categorySelect.value).toBe('1');
    });

    it('renders all difficulty options', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const difficultySelect = container.querySelector('select[name="difficulty"]');
      const options = difficultySelect.querySelectorAll('option');

      expect(options.length).toBe(5);
      Array.from(options).forEach((opt, index) => {
        expect(opt.value).toBe(String(index + 1));
      });
    });

    it('renders category options from API response', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(container.textContent).toContain('Science');
      });

      const categorySelect = container.querySelector('select[name="category"]');
      const options = categorySelect.querySelectorAll('option');

      expect(options.length).toBe(3);
      expect(options[0].textContent).toContain('Science');
    });
  });

  describe('Form Labels', () => {
    it('has label for question field', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const labels = container.querySelectorAll('label');
      const questionLabel = Array.from(labels).find(l => l.textContent.includes('Question'));

      expect(questionLabel).toBeTruthy();
    });

    it('has label for answer field', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const labels = container.querySelectorAll('label');
      const answerLabel = Array.from(labels).find(l => l.textContent.includes('Answer'));

      expect(answerLabel).toBeTruthy();
    });

    it('has label for difficulty field', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const labels = container.querySelectorAll('label');
      const difficultyLabel = Array.from(labels).find(l => l.textContent.includes('Difficulty'));

      expect(difficultyLabel).toBeTruthy();
    });

    it('has label for category field', async () => {
      const { container } = render(<FormView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      const labels = container.querySelectorAll('label');
      const categoryLabel = Array.from(labels).find(l => l.textContent.includes('Category'));

      expect(categoryLabel).toBeTruthy();
    });
  });
});
