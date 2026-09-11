import React from 'react';
import { render } from '@testing-library/react';
import App from '../App';
import * as api from '../utils/api';

jest.mock('../utils/api');

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    api.apiGet.mockImplementation((url, onSuccess, onError) => {
      onSuccess({ users: [], questions: [], categories: {} });
    });
  });

  it('renders without crashing', () => {
    render(<App />);
    expect(api.apiGet).toHaveBeenCalledWith(
      '/users',
      expect.any(Function),
      expect.any(Function)
    );
  });

  it('loads users on mount', () => {
    render(<App />);
    expect(api.apiGet).toHaveBeenCalledWith(
      '/users',
      expect.any(Function),
      expect.any(Function)
    );
  });

  it('renders main container', () => {
    const { container } = render(<App />);
    expect(container.querySelector('.App')).toBeTruthy();
  });

  it('calls apiGet for users endpoint', () => {
    render(<App />);
    expect(api.apiGet).toHaveBeenCalled();
  });
});
