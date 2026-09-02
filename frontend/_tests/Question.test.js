import React from 'react';
import ReactDOM from 'react-dom';
import Question from '../src/components/Question';

describe('Question Component', () => {
  const mockQuestion = {
    id: 1,
    question: 'What is the capital of France?',
    answer: 'Paris',
    category: 'Geography',
    difficulty: 1,
  };

  const mockAction = jest.fn();

  it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(
      <Question
        question={mockQuestion.question}
        answer={mockQuestion.answer}
        category={mockQuestion.category}
        difficulty={mockQuestion.difficulty}
        questionAction={mockAction}
      />,
      div
    );
    ReactDOM.unmountComponentAtNode(div);
  });

  it('displays the question text', () => {
    const div = document.createElement('div');
    ReactDOM.render(
      <Question
        question={mockQuestion.question}
        answer={mockQuestion.answer}
        category={mockQuestion.category}
        difficulty={mockQuestion.difficulty}
        questionAction={mockAction}
      />,
      div
    );
    expect(div.querySelector('.Question').textContent).toBe(
      mockQuestion.question
    );
    ReactDOM.unmountComponentAtNode(div);
  });

  it('displays the difficulty level', () => {
    const div = document.createElement('div');
    ReactDOM.render(
      <Question
        question={mockQuestion.question}
        answer={mockQuestion.answer}
        category={mockQuestion.category}
        difficulty={mockQuestion.difficulty}
        questionAction={mockAction}
      />,
      div
    );
    expect(div.querySelector('.difficulty').textContent).toContain(
      `Difficulty: ${mockQuestion.difficulty}`
    );
    ReactDOM.unmountComponentAtNode(div);
  });

  it('shows and hides answer on button click', () => {
    const div = document.createElement('div');
    const root = ReactDOM.render(
      <Question
        question={mockQuestion.question}
        answer={mockQuestion.answer}
        category={mockQuestion.category}
        difficulty={mockQuestion.difficulty}
        questionAction={mockAction}
      />,
      div
    );
    
    const button = div.querySelector('.show-answer');
    expect(button.textContent).toBe('Show Answer');
    
    // Initially answer should be hidden
    const answerSpan = div.querySelector('.answer-holder span');
    expect(answerSpan.style.visibility).toBe('hidden');
    
    ReactDOM.unmountComponentAtNode(div);
  });

  it('calls questionAction when delete button is clicked', () => {
    const div = document.createElement('div');
    const mockActionLocal = jest.fn();
    ReactDOM.render(
      <Question
        question={mockQuestion.question}
        answer={mockQuestion.answer}
        category={mockQuestion.category}
        difficulty={mockQuestion.difficulty}
        questionAction={mockActionLocal}
      />,
      div
    );
    
    const deleteImg = div.querySelector('.delete');
    deleteImg.click();
    
    expect(mockActionLocal).toHaveBeenCalledWith('DELETE');
    ReactDOM.unmountComponentAtNode(div);
  });

  it('renders category image with correct alt text', () => {
    const div = document.createElement('div');
    ReactDOM.render(
      <Question
        question={mockQuestion.question}
        answer={mockQuestion.answer}
        category={mockQuestion.category}
        difficulty={mockQuestion.difficulty}
        questionAction={mockAction}
      />,
      div
    );
    
    const categoryImg = div.querySelector('.category');
    expect(categoryImg).toBeTruthy();
    expect(categoryImg.alt).toBe(mockQuestion.category.toLowerCase());
    ReactDOM.unmountComponentAtNode(div);
  });
});
