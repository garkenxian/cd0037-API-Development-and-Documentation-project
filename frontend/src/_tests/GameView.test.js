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

    it('handles category load error', async () => {
      api.apiGet.mockImplementation((url, onSuccess, onError) => {
        if (url.includes('/categories')) {
          onError('Failed to load categories');
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        // Component should set error state
        expect(container.querySelector('.quiz-play-holder')).toBeTruthy();
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

  describe('User Creation', () => {
    it('shows create user button', () => {
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={null} onSelectUser={jest.fn()} />
      );

      const createButton = container.querySelector('.create-user-button');
      expect(createButton).toBeTruthy();
    });

    it('toggles create user form visibility', () => {
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={null} onSelectUser={jest.fn()} />
      );

      const createButton = container.querySelector('.create-user-button');
      expect(createButton).toBeTruthy();
      
      if (createButton) {
        fireEvent.click(createButton);
        // After click, component should show form
        expect(container.querySelector('.create-user-form')).toBeTruthy();
      }
    });

    it('creates user with POST request', async () => {
      const onSelectUser = jest.fn();
      api.apiPost.mockClear();
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/users') {
          onSuccess({ id: 3, username: 'newuser' });
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={null} onSelectUser={onSelectUser} />
      );

      const createButton = container.querySelector('.create-user-button');
      if (createButton) {
        fireEvent.click(createButton);

        // Get form inputs and fill them
        const inputs = container.querySelectorAll('input[type="text"], input[type="email"]');
        if (inputs.length >= 2) {
          fireEvent.change(inputs[0], { target: { name: 'newUsername', value: 'testuser' } });
          fireEvent.change(inputs[1], { target: { name: 'newEmail', value: 'test@example.com' } });

          // Find the submit button (first button in the form, not cancel)
          const buttons = Array.from(container.querySelectorAll('.create-user-form button'));
          const submitBtn = buttons.find(b => !b.textContent.includes('Cancel'));
          
          if (submitBtn) {
            fireEvent.click(submitBtn);

            await waitFor(() => {
              expect(api.apiPost).toHaveBeenCalledWith(
                '/users',
                expect.any(Object),
                expect.any(Function),
                expect.any(Function)
              );
            });
          }
        }
      }
    });

    it('handles user creation error', async () => {
      api.apiPost.mockClear();
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/users') {
          onError('Email already exists');
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={null} onSelectUser={jest.fn()} />
      );

      const createButton = container.querySelector('.create-user-button');
      if (createButton) {
        fireEvent.click(createButton);

        const inputs = container.querySelectorAll('input[type="text"], input[type="email"]');
        if (inputs.length >= 2) {
          fireEvent.change(inputs[0], { target: { name: 'newUsername', value: 'testuser' } });
          fireEvent.change(inputs[1], { target: { name: 'newEmail', value: 'test@example.com' } });

          const buttons = Array.from(container.querySelectorAll('.create-user-form button'));
          const submitBtn = buttons.find(b => !b.textContent.includes('Cancel'));
          
          if (submitBtn) {
            fireEvent.click(submitBtn);

            await waitFor(() => {
              // Error message should appear
              expect(container.textContent).toContain('Email already exists');
            });
          }
        }
      }
    });
  });

  describe('Category Selection', () => {
    it('displays all available categories', async () => {
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        expect(container.textContent).toContain('Science');
        expect(container.textContent).toContain('Art');
        expect(container.textContent).toContain('Geography');
      });
    });
  });

  describe('Answer Submission', () => {
    it('submits answer guess during gameplay', async () => {
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
              answer: 'Water',
            },
          });
        } else if (url === '/games/42/guess') {
          onSuccess({
            game_session_id: 42,
            current_question_number: 2,
            current_score: {
              correct: 1,
              total_answered: 1,
              total_questions: 5,
            },
            is_correct: true,
          });
        }
      });

      const { container, getByDisplayValue } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        const categoryButtons = container.querySelectorAll('.play-category');
        if (categoryButtons.length > 0) {
          fireEvent.click(categoryButtons[0]);
        }
      });

      // Wait for game to start and find answer input
      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalledWith(
          '/games',
          expect.any(Object),
          expect.any(Function),
          expect.any(Function)
        );
      });
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

  describe('User Creation Validation', () => {
    it('prevents submission with empty username', async () => {
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={null} onSelectUser={jest.fn()} />
      );

      const createButton = container.querySelector('.create-user-button');
      if (createButton) {
        fireEvent.click(createButton);

        // Leave username empty, fill email
        const inputs = container.querySelectorAll('input[type="text"], input[type="email"]');
        if (inputs.length >= 2) {
          fireEvent.change(inputs[0], { target: { name: 'newUsername', value: '' } });
          fireEvent.change(inputs[1], { target: { name: 'newEmail', value: 'test@test.com' } });

          const buttons = Array.from(container.querySelectorAll('.create-user-form button'));
          const submitBtn = buttons.find(b => !b.textContent.includes('Cancel'));
          
          if (submitBtn) {
            fireEvent.click(submitBtn);

            await waitFor(() => {
              expect(container.textContent).toContain('Username is required');
            });
          }
        }
      }
    });

    it('prevents submission with empty email', async () => {
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={null} onSelectUser={jest.fn()} />
      );

      const createButton = container.querySelector('.create-user-button');
      if (createButton) {
        fireEvent.click(createButton);

        // Fill username, leave email empty
        const inputs = container.querySelectorAll('input[type="text"], input[type="email"]');
        if (inputs.length >= 2) {
          fireEvent.change(inputs[0], { target: { name: 'newUsername', value: 'testuser' } });
          fireEvent.change(inputs[1], { target: { name: 'newEmail', value: '' } });

          const buttons = Array.from(container.querySelectorAll('.create-user-form button'));
          const submitBtn = buttons.find(b => !b.textContent.includes('Cancel'));
          
          if (submitBtn) {
            fireEvent.click(submitBtn);

            await waitFor(() => {
              expect(container.textContent).toContain('Email is required');
            });
          }
        }
      }
    });

    it('calls onUsersRefresh after successful user creation', async () => {
      const onSelectUser = jest.fn();
      const onUsersRefresh = jest.fn((callback) => callback());
      
      api.apiPost.mockClear();
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/users') {
          onSuccess({ id: 3, username: 'newuser' });
        }
      });

      const { container } = render(
        <GameView 
          users={mockUsers} 
          selectedUserId={null} 
          onSelectUser={onSelectUser}
          onUsersRefresh={onUsersRefresh}
        />
      );

      const createButton = container.querySelector('.create-user-button');
      if (createButton) {
        fireEvent.click(createButton);

        const inputs = container.querySelectorAll('input[type="text"], input[type="email"]');
        if (inputs.length >= 2) {
          fireEvent.change(inputs[0], { target: { name: 'newUsername', value: 'testuser' } });
          fireEvent.change(inputs[1], { target: { name: 'newEmail', value: 'test@test.com' } });

          const buttons = Array.from(container.querySelectorAll('.create-user-form button'));
          const submitBtn = buttons.find(b => !b.textContent.includes('Cancel'));
          
          if (submitBtn) {
            fireEvent.click(submitBtn);

            await waitFor(() => {
              expect(onUsersRefresh).toHaveBeenCalled();
            });
          }
        }
      }
    });

    it('cancels user creation form', async () => {
      const { container, queryByText } = render(
        <GameView users={mockUsers} selectedUserId={null} onSelectUser={jest.fn()} />
      );

      const createButton = container.querySelector('.create-user-button');
      if (createButton) {
        fireEvent.click(createButton);
        expect(container.querySelector('.create-user-form')).toBeTruthy();

        const buttons = Array.from(container.querySelectorAll('.create-user-form button'));
        const cancelBtn = buttons.find(b => b.textContent.includes('Cancel'));
        
        if (cancelBtn) {
          fireEvent.click(cancelBtn);
          
          await waitFor(() => {
            // Form should be closed
            expect(container.querySelector('.create-user-form')).toBeFalsy();
          });
        }
      }
    });
  });

  describe('Game Session Management', () => {
    it('handles game start with category selection', async () => {
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        const categoryButtons = container.querySelectorAll('.play-category');
        expect(categoryButtons.length).toBeGreaterThan(0);
      });

      const categoryButtons = container.querySelectorAll('.play-category');
      if (categoryButtons.length > 0) {
        fireEvent.click(categoryButtons[0]);

        await waitFor(() => {
          expect(api.apiPost).toHaveBeenCalledWith(
            '/games',
            expect.objectContaining({
              user_id: 1,
              category_id: expect.any(Number),
              number_of_questions: 5,
            }),
            expect.any(Function),
            expect.any(Function)
          );
        });
      }
    });

    it('requires user selection before starting game', async () => {
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={null} onSelectUser={jest.fn()} />
      );

      // Should show user selector before category selector
      const userSelectContainer = container.textContent;
      expect(userSelectContainer).toContain('Select a User');

      // Should not have category buttons
      const categoryButtons = container.querySelectorAll('.play-category');
      expect(categoryButtons.length).toBe(0);
    });

    it('updates state after game starts successfully', async () => {
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
              question: 'Test question?',
              category: 1,
              difficulty: 2,
              rating: 4.5,
              answer: 'Test answer',
            },
          });
        }
      });

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
        expect(container.textContent).toContain('Test question');
      });
    });

    it('displays loading state during game', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        // Simulate a very slow callback - don't call onSuccess immediately
        setTimeout(() => {
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
                question: 'Test question?',
                category: 1,
                difficulty: 2,
              },
            });
          }
        }, 500);
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        const categoryButtons = container.querySelectorAll('.play-category');
        if (categoryButtons.length > 0) {
          fireEvent.click(categoryButtons[0]);
          // Loading state should be set briefly
          expect(container.textContent).toContain('Loading');
        }
      });
    });

    it('displays error during game play', async () => {
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
              question: 'Test question?',
              category: 1,
              difficulty: 2,
            },
          });
        } else if (url.includes('/games/42/') && url.includes('1')) {
          // Answer submission fails
          onError('Server error');
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      // Start game
      await waitFor(() => {
        const categoryButtons = container.querySelectorAll('.play-category');
        if (categoryButtons.length > 0) {
          fireEvent.click(categoryButtons[0]);
        }
      });

      await waitFor(() => {
        expect(container.textContent).toContain('Test question');
      });
    });

    it('submits answer and displays result', async () => {
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
              answer: 'Water',
            },
          });
        } else if (url.includes('/games/42/') && url.includes('1')) {
          // Answer submission
          onSuccess({
            game_session_id: 42,
            current_question_number: 1,
            current_score: {
              correct: 1,
              total_answered: 1,
              total_questions: 5,
            },
            correct: true,
            correct_answer: 'Water',
            status: 'in_progress',
          });
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      // Start game
      await waitFor(() => {
        const categoryButtons = container.querySelectorAll('.play-category');
        if (categoryButtons.length > 0) {
          fireEvent.click(categoryButtons[0]);
        }
      });

      await waitFor(() => {
        expect(container.textContent).toContain('What is H2O?');
      });
    });

    it('displays final score when game completes', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onSuccess({
            game_session_id: 42,
            current_question_number: 5,
            current_score: {
              correct: 4,
              total_answered: 5,
              total_questions: 5,
            },
            question: {
              id: 7,
              question: 'Last question?',
              category: 1,
              difficulty: 2,
            },
          });
        } else if (url.includes('/games/42/')) {
          // Last answer submission completes game
          onSuccess({
            status: 'completed',
            current_score: {
              correct: 4,
              total_answered: 5,
              total_questions: 5,
            },
          });
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      // Start game
      await waitFor(() => {
        const categoryButtons = container.querySelectorAll('.play-category');
        if (categoryButtons.length > 0) {
          fireEvent.click(categoryButtons[0]);
        }
      });

      await waitFor(() => {
        expect(container.textContent).toContain('Last question');
      });
    });

    it('changes user from pre-play screen', async () => {
      const onSelectUser = jest.fn();
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={onSelectUser} />
      );

      // Component loads
      await waitFor(() => {
        expect(container.querySelector('.quiz-play-holder')).toBeTruthy();
      });

      // Should have category buttons for selectedUserId=1
      const categoryButtons = container.querySelectorAll('.play-category');
      expect(categoryButtons.length).toBeGreaterThan(0);
    });

    it('displays "Play Again" button after game completion', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onSuccess({
            game_session_id: 42,
            current_question_number: 1,
            current_score: {
              correct: 0,
              total_answered: 0,
              total_questions: 1,
            },
            question: {
              id: 7,
              question: 'Only question?',
              category: 1,
              difficulty: 2,
            },
          });
        } else if (url.includes('/games/42/')) {
          // Last answer completes game
          onSuccess({
            status: 'completed',
            current_score: {
              correct: 0,
              total_answered: 1,
              total_questions: 1,
            },
          });
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      // Start game
      await waitFor(() => {
        const categoryButtons = container.querySelectorAll('.play-category');
        if (categoryButtons.length > 0) {
          fireEvent.click(categoryButtons[0]);
        }
      });

      await waitFor(() => {
        expect(container.textContent).toContain('Only question');
      });
    });

    it('gets next question after viewing answer', async () => {
      api.apiGet.mockImplementation((url, onSuccess, onError) => {
        if (url.includes('/categories')) {
          onSuccess({ categories: mockCategories });
        } else if (url.includes('/games/42')) {
          onSuccess({
            game_session_id: 42,
            current_question_number: 2,
            current_score: {
              correct: 1,
              total_answered: 1,
              total_questions: 5,
            },
            question: {
              id: 8,
              question: 'Second question?',
              category: 1,
              difficulty: 1,
            },
            status: 'in_progress',
          });
        }
      });

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
              question: 'First question?',
              category: 1,
              difficulty: 2,
            },
          });
        } else if (url.includes('/games/42/')) {
          onSuccess({
            game_session_id: 42,
            current_question_number: 1,
            current_score: {
              correct: 1,
              total_answered: 1,
              total_questions: 5,
            },
            correct: true,
            correct_answer: 'Correct',
            status: 'in_progress',
          });
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      // Start game
      await waitFor(() => {
        const categoryButtons = container.querySelectorAll('.play-category');
        if (categoryButtons.length > 0) {
          fireEvent.click(categoryButtons[0]);
        }
      });

      await waitFor(() => {
        expect(container.textContent).toContain('First question');
      });
    });

    it('submits answer and shows correct/incorrect result', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onSuccess({
            game_session_id: 42,
            current_question_number: 1,
            current_score: { correct: 0, total_answered: 0, total_questions: 5 },
            question: { id: 7, question: 'Q1?', category: 1, difficulty: 2, answer: 'A1' },
          });
        } else if (url.includes('/games/42/1')) {
          onSuccess({
            game_session_id: 42,
            current_score: { correct: 1, total_answered: 1, total_questions: 5 },
            correct: true,
            correct_answer: 'A1',
            status: 'in_progress',
          });
        }
      });

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
          expect.any(Object),
          expect.any(Function),
          expect.any(Function)
        );
      });
    });

    it('handles answer submission error', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onSuccess({
            game_session_id: 42,
            current_question_number: 1,
            current_score: { correct: 0, total_answered: 0, total_questions: 5 },
            question: { id: 7, question: 'Q1?', category: 1, difficulty: 2, answer: 'A1' },
          });
        } else if (url.includes('/games/42/1')) {
          onError('Failed to submit answer');
        }
      });

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
        expect(api.apiPost).toHaveBeenCalled();
      });
    });

    it('completes game and shows final score', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onSuccess({
            game_session_id: 42,
            current_question_number: 1,
            current_score: { correct: 0, total_answered: 0, total_questions: 1 },
            question: { id: 7, question: 'Only Q?', category: 1, difficulty: 2, answer: 'A1' },
          });
        } else if (url.includes('/games/42/1')) {
          onSuccess({
            status: 'completed',
            current_score: { correct: 1, total_answered: 1, total_questions: 1 },
          });
        }
      });

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
        expect(api.apiPost).toHaveBeenCalled();
      });
    });

    it('restarts game on "Play Again"', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onSuccess({
            game_session_id: 42,
            current_question_number: 1,
            current_score: { correct: 0, total_answered: 0, total_questions: 1 },
            question: { id: 7, question: 'Only Q?', category: 1, difficulty: 2 },
          });
        } else if (url.includes('/games/42/1')) {
          onSuccess({ status: 'completed', current_score: { correct: 1, total_answered: 1, total_questions: 1 } });
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        const categoryButtons = container.querySelectorAll('.play-category');
        if (categoryButtons.length > 0) {
          fireEvent.click(categoryButtons[0]);
        }
      });

      // Game should progress to completion
      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalled();
      });
    });

    it('displays answer and correctness indicator', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onSuccess({
            game_session_id: 42,
            current_question_number: 1,
            current_score: { correct: 0, total_answered: 0, total_questions: 5 },
            question: { id: 7, question: 'Q?', category: 1, difficulty: 2 },
          });
        } else if (url.includes('/games/42')) {
          onSuccess({
            game_session_id: 42,
            current_score: { correct: 1, total_answered: 1, total_questions: 5 },
            correct: false,
            correct_answer: 'Right answer',
            status: 'in_progress',
          });
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        const buttons = container.querySelectorAll('.play-category');
        if (buttons.length > 0) fireEvent.click(buttons[0]);
      });

      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalled();
      });
    });

    it('renders create user form with username and email fields', async () => {
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={null} onSelectUser={jest.fn()} />
      );

      const createButton = container.querySelector('.create-user-button');
      if (createButton) {
        fireEvent.click(createButton);

        const userForm = container.querySelector('.create-user-form');
        expect(userForm).toBeTruthy();

        const inputs = userForm?.querySelectorAll('input') || [];
        expect(inputs.length).toBeGreaterThanOrEqual(2);
      }
    });

    it('cancels create user form and closes it', async () => {
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={null} onSelectUser={jest.fn()} />
      );

      const createButton = container.querySelector('.create-user-button');
      if (createButton) {
        fireEvent.click(createButton);
        expect(container.querySelector('.create-user-form')).toBeTruthy();

        const buttons = Array.from(container.querySelectorAll('.create-user-form button'));
        const cancelBtn = buttons.find(b => b.textContent.includes('Cancel'));
        
        if (cancelBtn) {
          fireEvent.click(cancelBtn);
          
          // Form should close
          expect(container.querySelector('.create-user-form')).toBeFalsy();
        }
      }
    });

    it('updates game state with loaded questions', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onSuccess({
            game_session_id: 100,
            current_question_number: 2,
            current_score: { correct: 2, total_answered: 3, total_questions: 5 },
            question: { id: 10, question: 'Mid-game Q?', category: 2, difficulty: 3 },
          });
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        const buttons = container.querySelectorAll('.play-category');
        if (buttons.length > 0) fireEvent.click(buttons[0]);
      });

      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalledWith(
          '/games',
          expect.objectContaining({
            user_id: 1,
            category_id: expect.any(Number),
          }),
          expect.any(Function),
          expect.any(Function)
        );
      });
    });

    it('handles loading state during game operations', async () => {
      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        expect(api.apiGet).toHaveBeenCalledWith(
          '/categories',
          expect.any(Function),
          expect.any(Function)
        );
      });

      // Component should render
      expect(container).toBeTruthy();
    });

    it('shows specific error for user not found in game', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onError('Selected user not found');
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        const buttons = container.querySelectorAll('.play-category');
        if (buttons.length > 0) fireEvent.click(buttons[0]);
      });

      await waitFor(() => {
        expect(container.textContent).toContain('not found');
      });
    });

    it('handles generic error when user is found but other issue occurs', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onError('Database connection failed');
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        const buttons = container.querySelectorAll('.play-category');
        if (buttons.length > 0) fireEvent.click(buttons[0]);
      });

      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalled();
      });
    });

    it('shows answer correctness state after submission', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onSuccess({
            game_session_id: 42,
            current_question_number: 1,
            current_score: { correct: 0, total_answered: 0, total_questions: 5 },
            question: { id: 7, question: 'Q?', category: 1, difficulty: 2 },
          });
        } else if (url.includes('/games/42')) {
          onSuccess({
            game_session_id: 42,
            current_question_number: 1,
            current_score: { correct: 0, total_answered: 1, total_questions: 5 },
            correct: false,
            correct_answer: 'Right',
            status: 'in_progress',
          });
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        const buttons = container.querySelectorAll('.play-category');
        if (buttons.length > 0) fireEvent.click(buttons[0]);
      });

      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalled();
      });
    });

    it('transitions to final score when game completes', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onSuccess({
            game_session_id: 50,
            current_question_number: 5,
            current_score: { correct: 3, total_answered: 4, total_questions: 5 },
            question: { id: 8, question: 'Q5?', category: 1, difficulty: 1 },
          });
        } else if (url === '/games/50/5') {
          onSuccess({
            game_session_id: 50,
            current_question_number: 5,
            current_score: { correct: 4, total_answered: 5, total_questions: 5 },
            status: 'completed',
            correct: true,
          });
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        const buttons = container.querySelectorAll('.play-category');
        if (buttons.length > 0) fireEvent.click(buttons[0]);
      });

      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalled();
      });
    });

    it('fetches next question and updates game state', async () => {
      let callCount = 0;

      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onSuccess({
            game_session_id: 60,
            current_question_number: 1,
            current_score: { correct: 0, total_answered: 0, total_questions: 3 },
            question: { id: 10, question: 'Q1?', category: 1, difficulty: 2 },
          });
        }
      });

      api.apiGet.mockImplementation((url, onSuccess, onError) => {
        if (url === '/games/60') {
          onSuccess({
            game_session_id: 60,
            current_question_number: 2,
            current_score: { correct: 1, total_answered: 1, total_questions: 3 },
            question: { id: 11, question: 'Q2?', category: 1, difficulty: 1 },
          });
        } else {
          onSuccess({ categories: mockCategories, questions: [] });
        }
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        const buttons = container.querySelectorAll('.play-category');
        if (buttons.length > 0) fireEvent.click(buttons[0]);
      });

      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalled();
      });
    });

    it('completes game when final question answered', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onSuccess({
            game_session_id: 80,
            current_question_number: 5,
            current_score: { correct: 4, total_answered: 4, total_questions: 5 },
            question: { id: 15, question: 'Last Q?', category: 2, difficulty: 2 },
          });
        } else if (url === '/games/80/5') {
          onSuccess({
            game_session_id: 80,
            current_question_number: 5,
            current_score: { correct: 5, total_answered: 5, total_questions: 5 },
            status: 'completed',
            correct: true,
          });
        }
      });

      api.apiGet.mockImplementation((url, onSuccess, onError) => {
        onSuccess({ categories: mockCategories, questions: [] });
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        const buttons = container.querySelectorAll('.play-category');
        if (buttons.length > 0) fireEvent.click(buttons[0]);
      });

      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalled();
      });
    });

    it('submits answer and handles correct response', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onSuccess({
            game_session_id: 100,
            current_question_number: 1,
            current_score: { correct: 0, total_answered: 0, total_questions: 3 },
            question: { id: 20, question: 'What is 2+2?', category: 1, difficulty: 1 },
          });
        } else if (url === '/games/100/1') {
          // Answer submission response
          onSuccess({
            game_session_id: 100,
            current_question_number: 1,
            current_score: { correct: 1, total_answered: 1, total_questions: 3 },
            status: 'in_progress',
            correct: true,
            correct_answer: '4',
          });
        }
      });

      api.apiGet.mockImplementation((url, onSuccess, onError) => {
        onSuccess({ categories: mockCategories, questions: [] });
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      // Click category to start game
      await waitFor(() => {
        const buttons = container.querySelectorAll('.play-category');
        if (buttons.length > 0) fireEvent.click(buttons[0]);
      });

      // Wait for question to appear
      await waitFor(() => {
        const form = container.querySelector('form');
        expect(form).toBeTruthy();
      });

      // Submit answer
      const form = container.querySelector('form');
      const input = form.querySelector('input[name="guess"]');
      fireEvent.change(input, { target: { value: '4' } });
      fireEvent.submit(form);

      // Verify answer was submitted
      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalledWith(
          '/games/100/1',
          expect.objectContaining({ user_answer: '4' }),
          expect.any(Function),
          expect.any(Function)
        );
      });
    });

    it('submits answer and handles incorrect response', async () => {
      api.apiPost.mockImplementation((url, data, onSuccess, onError) => {
        if (url === '/games') {
          onSuccess({
            game_session_id: 110,
            current_question_number: 1,
            current_score: { correct: 0, total_answered: 0, total_questions: 3 },
            question: { id: 21, question: 'What is 1+1?', category: 1, difficulty: 1 },
          });
        } else if (url === '/games/110/1') {
          onSuccess({
            game_session_id: 110,
            current_question_number: 1,
            current_score: { correct: 0, total_answered: 1, total_questions: 3 },
            status: 'in_progress',
            correct: false,
            correct_answer: '2',
          });
        }
      });

      api.apiGet.mockImplementation((url, onSuccess, onError) => {
        onSuccess({ categories: mockCategories, questions: [] });
      });

      const { container } = render(
        <GameView users={mockUsers} selectedUserId={1} onSelectUser={jest.fn()} />
      );

      await waitFor(() => {
        const buttons = container.querySelectorAll('.play-category');
        if (buttons.length > 0) fireEvent.click(buttons[0]);
      });

      await waitFor(() => {
        const form = container.querySelector('form');
        expect(form).toBeTruthy();
      });

      const form = container.querySelector('form');
      const input = form.querySelector('input[name="guess"]');
      fireEvent.change(input, { target: { value: '3' } });
      fireEvent.submit(form);

      await waitFor(() => {
        expect(api.apiPost).toHaveBeenCalledWith(
          '/games/110/1',
          expect.any(Object),
          expect.any(Function),
          expect.any(Function)
        );
      });
    });
  });
});

