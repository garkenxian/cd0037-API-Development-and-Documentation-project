import React from 'react';
import ReactDOM from 'react-dom';
import App from '../src/App';

describe('App Component', () => {
  it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<App />, div);
    ReactDOM.unmountComponentAtNode(div);
  });

  it('renders the App component', () => {
    const div = document.createElement('div');
    ReactDOM.render(<App />, div);
    expect(div.innerHTML).toBeTruthy();
    ReactDOM.unmountComponentAtNode(div);
  });
});
