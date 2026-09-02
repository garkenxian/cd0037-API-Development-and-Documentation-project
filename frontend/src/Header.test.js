import React from 'react';
import ReactDOM from 'react-dom';
import Header from './components/Header';

describe('Header Component', () => {
  it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<Header />, div);
    ReactDOM.unmountComponentAtNode(div);
  });

  it('renders the header with title', () => {
    const div = document.createElement('div');
    ReactDOM.render(<Header />, div);
    expect(div.querySelector('h1')).toBeTruthy();
    expect(div.querySelector('h1').textContent).toBe('Udacitrivia');
    ReactDOM.unmountComponentAtNode(div);
  });

  it('renders navigation links', () => {
    const div = document.createElement('div');
    ReactDOM.render(<Header />, div);
    const headings = div.querySelectorAll('h2');
    expect(headings.length).toBe(3);
    expect(headings[0].textContent).toBe('List');
    expect(headings[1].textContent).toBe('Add');
    expect(headings[2].textContent).toBe('Play');
    ReactDOM.unmountComponentAtNode(div);
  });

  it('has correct CSS class', () => {
    const div = document.createElement('div');
    ReactDOM.render(<Header />, div);
    expect(div.querySelector('.App-header')).toBeTruthy();
    ReactDOM.unmountComponentAtNode(div);
  });
});
