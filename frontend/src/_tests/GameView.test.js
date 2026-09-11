import React from 'react';
import { render, waitFor, fireEvent } from '@testing-library/react';
import GameView from '../components/GameView';
import * as api from '../utils/api';

// Mock the api module
jest.mock('../utils/api');

describe('GameView Component', () => {
  const mockUsers = [
    { id: 1, username: 'alice' },
    { id: 2, username: 'bob' },
  ];

  const mockCategories = {
    1: 'Science',
    2: 'Art',
    3: 'Geography',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock categories endpoint
    api.apiGet.mockImplementation((url, onSuccess, onError) => {
      if (url.includes('/categories')) {
        onSuccess({ categories: mockCategories });
      } else if (url.includes('/games')) {
        onSuccess({
          game_session_id: 42,
          current_question_number: 1,
          current_score: {
            correct: 0,
            total_answered: 0,
            total_questions: 5,
          },
          question: {
            id: 7,
            question: 'What is H2O?',
            category: 1,
            difficulty: 2,
            rating: 4.5,
          },
        });
      }
    });

    // Mock POST endpoints
    api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
      if (url === '/games') {
        onSuccess({
          game_session_id: 42,
          current_question_number: 1,
          current_score: {
            correct: 0,
            total_answered: 0,
            total_questions: 5,
          },
          question: {
            id: 7,
            question: 'What is H2O?',
            category: 1,
            difficulty: 2,
            rating: 4.5,
          },
        });
      }
    });
  });

  describe('Initialization', () => {
    it('renders without crashing', () => {
      render(<GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />);
      expect(api.apiGet).toHaveBeenCalledWith(
        '/categories',
        expect.any(Function),
        expect.any(Function)
      );
    });

    it('loads categories on mount', async () => {
      render(<GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />);
      
      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalledWith(
          '/categories',
          expect.any(Function),
          expect.any(Function)
        );
      });
    });

    it('shows user selector when no user is selected', () => {
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={null} onSelectUser={jest.fn()} />
      );
      expect(container.textContent).toContain('Select a User');
    });

    it('shows category selector when user is selected', () => {
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );
      expect(container.textContent).toContain('Choose Category');
    });

    it('displays correct user in header when selected', () => {
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );
      expect(container.textContent).toContain('Playing as');
      expect(container.textContent).toContain('alice');
    });
  });

  describe('User Selection', () => {
    it('calls onSelectUser when user is selected', async () => {
      const onSelectUser = jest.fn();
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={null} onSelectUser={onSelectUser} />
      );
      
      const select = container.querySelector('select');
      if (select) {
        fireEvent.change(select, { target: { value: '1' } });
        
        await waitFor(() => {
          expect(onSelectUser).toHaveBeenCalledWith(1);
        });
      }
    });

    it('shows error when no users available', () => {
      const { container } = render(
        <GameView users={[]} selectedUserId={null} onSelectUser={jest.fn()} />
      );
      expect(container.textContent).toContain('No users available');
    });
  });

  describe('Game Flow', () => {
    it('starts game with POST /games call', async () => {
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        const categoryButtons = container.querySelectorAll('.play-category');
        if (categoryButtons.length > 0) {
          fireEvent.click(categoryButtons[0]);
        }
      });

      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalledWith(
          '/games',
          expect.objectContaining({
            user_id: 1,
            number_of_questions: 5,
          }),
          expect.any(Function),
          expect.any(Function)
        );
      });
    });

    it('starts game with user-selected number of questions', async () => {
      const { container, getByLabelText } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      fireEvent.change(getByLabelText('Number of questions'), {
        target: { value: '10' },
      });

      await waitFor(() => {
        const categoryButtons = container.querySelectorAll('.play-category');
        if (categoryButtons.length > 0) {
          fireEvent.click(categoryButtons[0]);
        }
      });

      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalledWith(
          '/games',
          expect.objectContaining({
            user_id: 1,
            number_of_questions: 10,
          }),
          expect.any(Function),
          expect.any(Function)
        );
      });
    });

    it('prevents game start without valid user', async () => {
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={null} onSelectUser={jest.fn()} />
      );

      // Should show user selector, not category selector
      expect(container.textContent).toContain('Select a User');
      expect(api.apiPost).not.toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('displays error message when game start fails', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onError('User not found');
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      // Click category to start game
      await waitFor(() => {
        const categoryButtons = container.querySelectorAll('.play-category');
        if (categoryButtons.length > 0) {
          fireEvent.click(categoryButtons[0]);
        }
      });

      await waitFor(() => {
        expect(container.textContent).toContain('not found');
      });
    });

    it('shows error message if user not found', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onError('User not found');
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      // Click category to start game
      await waitFor(() => {
        const categoryButtons = container.querySelectorAll('.play-category');
        if (categoryButtons.length > 0) {
          fireEvent.click(categoryButtons[0]);
        }
      });

      await waitFor(() => {
        expect(container.textContent).toContain('not found');
      });
    });
  });
});
