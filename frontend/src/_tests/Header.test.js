import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
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
    expect(headings[0].textContent).toBe('List Questions');
    expect(headings[1].textContent).toBe('Add Questions');
    expect(headings[2].textContent).toBe('Play A Game');
  });

  it('has correct CSS class', () => {
    const { container } = render(<Header />);
    expect(container.querySelector('.App-header')).toBeTruthy();
  });

  describe('Navigation', () => {
    beforeEach(() => {
      // Mock window.location
      delete window.location;
      window.location = { 
        href: '', 
        origin: 'http://localhost:3000' 
      };
    });

    it('navigates to home when title is clicked', () => {
      render(<Header />);
      const title = screen.getByRole('heading', { level: 1 });
      fireEvent.click(title);
      expect(window.location.href).toBe('http://localhost:3000');
    });

    it('navigates to home when List Questions is clicked', () => {
      render(<Header />);
      const headings = screen.getAllByRole('heading', { level: 2 });
      fireEvent.click(headings[0]);
      expect(window.location.href).toBe('http://localhost:3000');
    });

    it('navigates to add page when Add Questions is clicked', () => {
      render(<Header />);
      const headings = screen.getAllByRole('heading', { level: 2 });
      fireEvent.click(headings[1]);
      expect(window.location.href).toBe('http://localhost:3000/add');
    });

    it('navigates to play page when Play A Game is clicked', () => {
      render(<Header />);
      const headings = screen.getAllByRole('heading', { level: 2 });
      fireEvent.click(headings[2]);
      expect(window.location.href).toBe('http://localhost:3000/play');
    });
  });
});
