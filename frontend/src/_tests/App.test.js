import React from 'react';
import { render } from '@testing-library/react';
import App from '../App';

describe('App Component', () => {
  it('renders without crashing', () => {
    render(<App />);
  });

  it('renders the App component', () => {
    const { container } = render(<App />);
    expect(container).toBeTruthy();
  });
});
