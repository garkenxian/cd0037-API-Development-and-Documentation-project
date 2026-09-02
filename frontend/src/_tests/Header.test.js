import React from 'react';
import { render, screen } from '@testing-library/react';
import Header from '../components/Header';

describe('Header Component', () => {
  it('renders without crashing', () => {
    render(<Header />);
  });

  it('renders the header with title', () => {
    render(<Header />);
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading).toBeTruthy();
    expect(heading.textContent).toBe('Udacitrivia');
  });

  it('renders navigation links', () => {
    render(<Header />);
    const headings = screen.getAllByRole('heading', { level: 2 });
    expect(headings.length).toBe(3);
    expect(headings[0].textContent).toBe('List');
    expect(headings[1].textContent).toBe('Add');
    expect(headings[2].textContent).toBe('Play');
  });

  it('has correct CSS class', () => {
    const { container } = render(<Header />);
    expect(container.querySelector('.App-header')).toBeTruthy();
  });
});
