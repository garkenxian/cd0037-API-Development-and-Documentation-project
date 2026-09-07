/**
 * Shared API helper utilities for reducing duplicate request logic
 * across frontend components.
 * 
 * All functions follow a consistent pattern:
 * - Accept standard jQuery AJAX params
 * - Return standardized success/error handling
 * - Normalize error responses to a common format
 */

import $ from 'jquery';

/**
 * Generic GET request wrapper
 * @param {string} url - The API endpoint URL
 * @param {function} onSuccess - Callback function for successful response
 * @param {function} onError - Callback function for error response
 */
export const apiGet = (url, onSuccess, onError) => {
  $.ajax({
    url,
    type: 'GET',
    success: (result) => {
      onSuccess(result);
    },
    error: (error) => {
      handleApiError(error, onError);
    },
  });
};

/**
 * Generic POST request wrapper
 * @param {string} url - The API endpoint URL
 * @param {object} data - The request payload
 * @param {function} onSuccess - Callback function for successful response
 * @param {function} onError - Callback function for error response
 */
export const apiPost = (url, data, onSuccess, onError) => {
  $.ajax({
    url,
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify(data),
    xhrFields: {
      withCredentials: true,
    },
    crossDomain: true,
    success: (result) => {
      onSuccess(result);
    },
    error: (error) => {
      handleApiError(error, onError);
    },
  });
};

/**
 * Generic PUT request wrapper
 * @param {string} url - The API endpoint URL
 * @param {object} data - The request payload
 * @param {function} onSuccess - Callback function for successful response
 * @param {function} onError - Callback function for error response
 */
export const apiPut = (url, data, onSuccess, onError) => {
  $.ajax({
    url,
    type: 'PUT',
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify(data),
    xhrFields: {
      withCredentials: true,
    },
    crossDomain: true,
    success: (result) => {
      onSuccess(result);
    },
    error: (error) => {
      handleApiError(error, onError);
    },
  });
};

/**
 * Generic DELETE request wrapper
 * @param {string} url - The API endpoint URL
 * @param {function} onSuccess - Callback function for successful response
 * @param {function} onError - Callback function for error response
 */
export const apiDelete = (url, onSuccess, onError) => {
  $.ajax({
    url,
    type: 'DELETE',
    success: (result) => {
      onSuccess(result);
    },
    error: (error) => {
      handleApiError(error, onError);
    },
  });
};

/**
 * Centralized error handling
 * Normalizes error responses and calls the error callback
 * @param {object} error - jQuery AJAX error object
 * @param {function} onError - Callback function to handle the error
 */
const handleApiError = (error, onError) => {
  // Try to extract error message from response
  let errorMessage = 'An error occurred. Please try again.';
  
  try {
    if (error.responseJSON && error.responseJSON.message) {
      errorMessage = error.responseJSON.message;
    } else if (error.statusText) {
      errorMessage = error.statusText;
    }
  } catch (e) {
    // If we can't parse the error, use default message
  }
  
  if (onError) {
    onError(errorMessage, error);
  } else {
    // Fallback: alert user if no error handler provided
    alert(errorMessage);
  }
};
