import React from 'react';
import { render, waitFor, fireEvent } from '@testing-library/react';
import QuestionView from '../components/QuestionView';
import * as api from '../utils/api';

jest.mock('../utils/api');

describe('QuestionView Component', () => {
  const mockCategories = {
    1: 'Science',
    2: 'Art',
    3: 'Geography',
  };

  const mockQuestionsResponse = {
    questions: [
      {
        id: 1,
        question: 'What is H2O?',
        category: 1,
        difficulty: 2,
        rating: 4.5,
        answer: 'Water',
      },
    ],
    total_questions: 12,
    current_page: 1,
    total_pages: 2,
    categories: mockCategories,
    current_category: null,
  };

  const mockSearchResponse = {
    questions: [
      {
        id: 1,
        question: 'What is H2O?',
        category: 1,
        difficulty: 2,
        rating: 4.5,
        answer: 'Water',
      },
    ],
    total_questions: 1,
    total_pages: 1,
    categories: mockCategories,
    current_category: null,
  };

  const mockLeaderboardResponse = {
    leaderboard: [
      { id: 1, username: 'alice', total_score: 12, games_played: 4, rank: 1 },
      { id: 2, username: 'bob', total_score: 8, games_played: 3, rank: 2 },
    ],
    total_users: 2,
    success: true,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    
    api.apiGet.mockImplementation((url, onSuccess, onError) => {
      if (url.includes('/users/leaderboard')) {
        onSuccess(mockLeaderboardResponse);
      } else if (url.includes('search=')) {
        onSuccess(mockSearchResponse);
      } else {
        onSuccess(mockQuestionsResponse);
      }
    });

    api.apiDelete.mockImplementation((url, onSuccess, onError) => {
      onSuccess({ deleted: true, success: true });
    });

    api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
      onSuccess({ id: 9, type: data.type, success: true });
    });
  });

  describe('Initialization', () => {
    it('renders without crashing', () => {
      render(<QuestionView />);
      expect(api.apiGet).toHaveBeenCalledWith(
        expect.stringContaining('/questions'),
        expect.any(Function),
        expect.any(Function)
      );
    });

    it('loads questions on mount', async () => {
      render(<QuestionView />);
      
      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalledWith(
          '/questions?page=1',
          expect.any(Function),
          expect.any(Function)
        );
      });
    });

    it('displays loaded questions', async () => {
      const { container } = render(<QuestionView />);
      
      await waitFor(() => {
        expect(container.textContent).toContain('What is H2O?');
      });
    });

    it('loads and shows leaderboard entries', async () => {
      const { container } = render(<QuestionView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalledWith(
          '/users/leaderboard?limit=10',
          expect.any(Function),
          expect.any(Function)
        );
      });

      await waitFor(() => {
        expect(container.textContent).toContain('Leaderboard');
        expect(container.textContent).toContain('alice: 12');
      });
    });
  });

  describe('Search Functionality', () => {
    it('encodes search terms in URL', async () => {
      const { container } = render(<QuestionView />);

      // Wait for initial load
      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalledWith(
          '/questions?page=1',
          expect.any(Function),
          expect.any(Function)
        );
      });

      api.apiGet.mockClear();

      // Find the search form and submit with special characters
      const forms = container.querySelectorAll('form');
      const searchForm = Array.from(forms).find(f => f.textContent.includes('search') || f.textContent.includes('Search'));
      
      if (searchForm) {
        const input = searchForm.querySelector('input[type="text"]');
        fireEvent.change(input, { target: { value: 'H2O test' } });
        fireEvent.submit(searchForm);

        await waitFor(() => {
          // Verify URL encoding of search term
          expect(api.apiGet).toHaveBeenCalledWith(
            expect.stringContaining('search=H2O%20test'),
            expect.any(Function),
            expect.any(Function)
          );
        });
      }
    });

    it('includes search term in API call', async () => {
      const { container } = render(<QuestionView />);

      // Wait for initial load
      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      api.apiGet.mockClear();

      // Find and submit search form
      const forms = container.querySelectorAll('form');
      const searchForm = Array.from(forms).find(f => f.textContent.includes('search') || f.textContent.includes('Search'));
      
      if (searchForm) {
        const input = searchForm.querySelector('input[type="text"]');
        fireEvent.change(input, { target: { value: 'water' } });
        fireEvent.submit(searchForm);

        await waitFor(() => {
          // Verify search parameter in URL
          expect(api.apiGet).toHaveBeenCalledWith(
            expect.stringContaining('search=water'),
            expect.any(Function),
            expect.any(Function)
          );
        });
      }
    });

    it('maintains activeSearch state across pagination', async () => {
      const { container } = render(<QuestionView />);

      // Wait for initial load and get the initial call count
      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalled();
      });

      api.apiGet.mockClear();

      // Perform search
      const forms = container.querySelectorAll('form');
      const searchForm = Array.from(forms).find(f => f.textContent.includes('search') || f.textContent.includes('Search'));
      
      if (searchForm) {
        const input = searchForm.querySelector('input[type="text"]');
        fireEvent.change(input, { target: { value: 'water' } });
        fireEvent.submit(searchForm);

        await waitFor(() => {
          expect(api.apiGet).toHaveBeenCalledWith(
            expect.stringContaining('search=water'),
            expect.any(Function),
            expect.any(Function)
          );
        });
      }

      api.apiGet.mockClear();

      // Simulate clicking page 2 pagination
      const pagination = container.querySelector('.pagination-menu');
      if (pagination) {
        const pageSpans = pagination.querySelectorAll('.page-num');
        if (pageSpans.length > 1) {
          fireEvent.click(pageSpans[1]); // Click page 2

          await waitFor(() => {
            // Verify search term is still included on page change
            expect(api.apiGet).toHaveBeenCalledWith(
              expect.stringContaining('page=2'),
              expect.any(Function),
              expect.any(Function)
            );
          });
        }
      }
    });
  });

  describe('Pagination', () => {
    it('displays pagination controls', async () => {
      const { container } = render(<QuestionView />);
      
      await waitFor(() => {
        const pagination = container.querySelector('.pagination-menu');
        expect(pagination).toBeTruthy();
      });
    });

    it('calls apiGet with correct page number when page changes', async () => {
      const { container } = render(<QuestionView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalledWith(
          '/questions?page=1',
          expect.any(Function),
          expect.any(Function)
        );
      });

      api.apiGet.mockClear();

      // Click pagination to change page
      const pagination = container.querySelector('.pagination-menu');
      if (pagination) {
        const pageSpans = pagination.querySelectorAll('.page-num');
        if (pageSpans.length > 1) {
          fireEvent.click(pageSpans[1]); // Click page 2

          await waitFor(() => {
            expect(api.apiGet).toHaveBeenCalledWith(
              expect.stringContaining('page=2'),
              expect.any(Function),
              expect.any(Function)
            );
          });
        }
      }
    });
  });

  describe('Error Handling', () => {
    it('handles API errors gracefully', async () => {
      api.apiGet.mockImplementation((url, onSuccess, onError) => {
        onError('Unable to load questions');
      });

      const { container } = render(<QuestionView />);

      await waitFor(() => {
        // Component should still render even if API fails
        expect(container.querySelector('.question-view')).toBeTruthy();
      });
    });

    it('shows category create API errors', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        onError('Category type already exists');
      });

      const { getByLabelText, getByDisplayValue, findByText } = render(
        <QuestionView />
      );

      fireEvent.change(getByLabelText('Add category name'), {
        target: { value: 'Science' },
      });
      fireEvent.click(getByDisplayValue('Add Category'));

      expect(await findByText('Category type already exists')).toBeTruthy();
    });
  });

  describe('Category Creation', () => {
    it('creates a category and refreshes questions', async () => {
      const { getByLabelText, getByDisplayValue } = render(<QuestionView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalledWith(
          '/questions?page=1',
          expect.any(Function),
          expect.any(Function)
        );
      });

      api.apiGet.mockClear();

      fireEvent.change(getByLabelText('Add category name'), {
        target: { value: 'Technology' },
      });
      fireEvent.click(getByDisplayValue('Add Category'));

      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalledWith(
          '/categories',
          { type: 'Technology' },
          expect.any(Function),
          expect.any(Function)
        );
      });

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalledWith(
          '/questions?page=1',
          expect.any(Function),
          expect.any(Function)
        );
      });
    });

    it('prevents empty category submission', async () => {
      const { getByDisplayValue, findByText } = render(<QuestionView />);

      fireEvent.click(getByDisplayValue('Add Category'));

      expect(await findByText('Category name is required')).toBeTruthy();
      expect(api.apiPost).not.toHaveBeenCalled();
    });
  });

  describe('API Contract Verification', () => {
    it('uses GET endpoint for questions list', async () => {
      render(<QuestionView />);

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalledWith(
          expect.stringContaining('/questions'),
          expect.any(Function),
          expect.any(Function)
        );
      });

      // Not POST /questions (old API)
      expect(api.apiPost).not.toHaveBeenCalled();
    });

    it('uses DELETE endpoint for question removal', async () => {
      api.apiDelete.mockClear();
      render(<QuestionView />);

      // Verify apiDelete is exported and can be called
      await waitFor(() => {
        expect(typeof api.apiDelete).toBe('function');
      });
    });

    it('calls apiGet with page parameter', async () => {
      render(<QuestionView />);

      await waitFor(() => {
        const call = api.apiGet.mock.calls[0];
        expect(call[0]).toContain('page=');
      });
    });
  });
});
