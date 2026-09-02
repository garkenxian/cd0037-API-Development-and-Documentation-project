// Jest setup file - Mock window functions and jQuery to prevent errors in tests

// Mock window.alert and window.confirm
global.alert = jest.fn();
global.confirm = jest.fn(() => true);

// Suppress specific console warnings and errors
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;

console.error = (...args) => {
  // Filter out jsdom "Not implemented" errors
  if (
    args[0] &&
    typeof args[0] === 'string' &&
    args[0].includes('Not implemented: window.')
  ) {
    return;
  }
  // Filter out React deprecation warnings for ReactDOM.render
  if (
    args[0] &&
    typeof args[0] === 'string' &&
    (args[0].includes('ReactDOM.render is no longer supported') ||
      args[0].includes('unmountComponentAtNode is deprecated'))
  ) {
    return;
  }
  originalConsoleError.call(console, ...args);
};

console.warn = (...args) => {
  // Filter out similar warnings as errors
  if (
    args[0] &&
    typeof args[0] === 'string' &&
    (args[0].includes('ReactDOM.render is no longer supported') ||
      args[0].includes('unmountComponentAtNode is deprecated'))
  ) {
    return;
  }
  originalConsoleWarn.call(console, ...args);
};


