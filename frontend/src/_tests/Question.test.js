import React from 'react';
import { render } from '@testing-library/react';
import Question from '../components/Question';

describe('Question Component', () => {
  const mockQuestion = {
    id: 1,
    question: 'What is the capital of France?',
    answer: 'Paris',
    category: 'Geography',
    difficulty: 1,
  };

  const mockAction = jest.fn();

  beforeEach(() => {
    mockAction.mockClear();
  });

  it('renders without crashing', () => {
    render(
      <Question
        question={mockQuestion.question}
        answer={mockQuestion.answer}
        category={mockQuestion.category}
        difficulty={mockQuestion.difficulty}
        questionAction={mockAction}
      />
    );
  });

  it('displays the question text', () => {
    const { container } = render(
      <Question
        question={mockQuestion.question}
        answer={mockQuestion.answer}
        category={mockQuestion.category}
        difficulty={mockQuestion.difficulty}
        questionAction={mockAction}
      />
    );
    expect(container.querySelector('.Question').textContent).toBe(
      mockQuestion.question
    );
  });

  it('displays the difficulty level', () => {
    const { container } = render(
      <Question
        question={mockQuestion.question}
        answer={mockQuestion.answer}
        category={mockQuestion.category}
        difficulty={mockQuestion.difficulty}
        questionAction={mockAction}
      />
    );
    expect(container.querySelector('.difficulty').textContent).toContain(
      `Difficulty: ${mockQuestion.difficulty}`
    );
  });

  it('shows and hides answer on button click', () => {
    const { container } = render(
      <Question
        question={mockQuestion.question}
        answer={mockQuestion.answer}
        category={mockQuestion.category}
        difficulty={mockQuestion.difficulty}
        questionAction={mockAction}
      />
    );
    
    const button = container.querySelector('.show-answer');
    expect(button.textContent).toBe('Show Answer');
    
    // Initially answer should be hidden
    const answerSpan = container.querySelector('.answer-holder span');
    expect(answerSpan.style.visibility).toBe('hidden');
  });

  it('calls questionAction when delete button is clicked', () => {
    const { container } = render(
      <Question
        question={mockQuestion.question}
        answer={mockQuestion.answer}
        category={mockQuestion.category}
        difficulty={mockQuestion.difficulty}
        questionAction={mockAction}
      />
    );
    
    const deleteImg = container.querySelector('.delete');
    deleteImg.click();
    
    expect(mockAction).toHaveBeenCalledWith('DELETE');
  });

  it('renders category image with correct alt text', () => {
    const { container } = render(
      <Question
        question={mockQuestion.question}
        answer={mockQuestion.answer}
        category={mockQuestion.category}
        difficulty={mockQuestion.difficulty}
        questionAction={mockAction}
      />
    );
    
    const categoryImg = container.querySelector('.category');
    expect(categoryImg).toBeTruthy();
    expect(categoryImg.alt).toBe(mockQuestion.category.toLowerCase());
  });
});
