import $ from 'jquery';
import { apiGet, apiPost, apiPut, apiDelete } from './api';

// Mock jQuery AJAX
jest.mock('jquery', () => ({
  ajax: jest.fn(),
}));

describe('API Utility Functions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('apiGet', () => {
    it('should make a GET request with correct parameters', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      apiGet('/test-endpoint', onSuccess, onError);

      expect($.ajax).toHaveBeenCalledWith(
        expect.objectContaining({
          url: '/test-endpoint',
          type: 'GET',
        })
      );
    });

    it('should call onSuccess with result when request succeeds', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const mockResponse = { id: 1, name: 'test' };

      // Setup AJAX mock to call success callback
      $.ajax.mockImplementation((config) => {
        config.success(mockResponse);
      });

      apiGet('/test', onSuccess, onError);

      expect(onSuccess).toHaveBeenCalledWith(mockResponse);
      expect(onError).not.toHaveBeenCalled();
    });

    it('should call onError with error message when request fails', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      $.ajax.mockImplementation((config) => {
        config.error({
          statusText: 'Not Found',
          responseJSON: null,
        });
      });

      apiGet('/test', onSuccess, onError);

      expect(onSuccess).not.toHaveBeenCalled();
      expect(onError).toHaveBeenCalledWith('Not Found', expect.any(Object));
    });

    it('should extract error message from responseJSON.message', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      $.ajax.mockImplementation((config) => {
        config.error({
          responseJSON: { message: 'Custom error message' },
          statusText: 'Bad Request',
        });
      });

      apiGet('/test', onSuccess, onError);

      expect(onError).toHaveBeenCalledWith(
        'Custom error message',
        expect.any(Object)
      );
    });

    it('should use default error message when no error details provided', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      $.ajax.mockImplementation((config) => {
        config.error({ statusText: null, responseJSON: null });
      });

      apiGet('/test', onSuccess, onError);

      expect(onError).toHaveBeenCalledWith(
        'An error occurred. Please try again.',
        expect.any(Object)
      );
    });
  });

  describe('apiPost', () => {
    it('should make a POST request with JSON data', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const data = { name: 'test', value: 123 };

      apiPost('/test-endpoint', data, onSuccess, onError);

      expect($.ajax).toHaveBeenCalledWith(
        expect.objectContaining({
          url: '/test-endpoint',
          type: 'POST',
          dataType: 'json',
          contentType: 'application/json',
          data: JSON.stringify(data),
          xhrFields: { withCredentials: true },
          crossDomain: true,
        })
      );
    });

    it('should call onSuccess with response', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const mockResponse = { id: 1, status: 'created' };

      $.ajax.mockImplementation((config) => {
        config.success(mockResponse);
      });

      apiPost('/test', { data: 'test' }, onSuccess, onError);

      expect(onSuccess).toHaveBeenCalledWith(mockResponse);
    });

    it('should call onError when request fails', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      $.ajax.mockImplementation((config) => {
        config.error({
          responseJSON: { message: 'Validation failed' },
          statusText: 'Bad Request',
        });
      });

      apiPost('/test', { data: 'test' }, onSuccess, onError);

      expect(onError).toHaveBeenCalledWith(
        'Validation failed',
        expect.any(Object)
      );
    });

    it('should properly serialize complex data structures', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const complexData = {
        nested: { value: 'test' },
        array: [1, 2, 3],
        boolean: true,
      };

      apiPost('/test', complexData, onSuccess, onError);

      const callConfig = $.ajax.mock.calls[0][0];
      expect(callConfig.data).toBe(JSON.stringify(complexData));
    });
  });

  describe('apiPut', () => {
    it('should make a PUT request with JSON data', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const data = { name: 'updated' };

      apiPut('/test-endpoint/1', data, onSuccess, onError);

      expect($.ajax).toHaveBeenCalledWith(
        expect.objectContaining({
          url: '/test-endpoint/1',
          type: 'PUT',
          dataType: 'json',
          contentType: 'application/json',
          data: JSON.stringify(data),
          xhrFields: { withCredentials: true },
          crossDomain: true,
        })
      );
    });

    it('should call onSuccess with updated data', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const mockResponse = { id: 1, name: 'updated' };

      $.ajax.mockImplementation((config) => {
        config.success(mockResponse);
      });

      apiPut('/test/1', { name: 'updated' }, onSuccess, onError);

      expect(onSuccess).toHaveBeenCalledWith(mockResponse);
    });

    it('should handle PUT errors', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      $.ajax.mockImplementation((config) => {
        config.error({
          responseJSON: { message: 'Not found' },
          statusText: 'Not Found',
        });
      });

      apiPut('/test/999', { data: 'test' }, onSuccess, onError);

      expect(onError).toHaveBeenCalledWith('Not found', expect.any(Object));
    });
  });

  describe('apiDelete', () => {
    it('should make a DELETE request', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      apiDelete('/test-endpoint/1', onSuccess, onError);

      expect($.ajax).toHaveBeenCalledWith(
        expect.objectContaining({
          url: '/test-endpoint/1',
          type: 'DELETE',
        })
      );
    });

    it('should call onSuccess when deletion succeeds', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const mockResponse = { message: 'Deleted' };

      $.ajax.mockImplementation((config) => {
        config.success(mockResponse);
      });

      apiDelete('/test/1', onSuccess, onError);

      expect(onSuccess).toHaveBeenCalledWith(mockResponse);
    });

    it('should call onError when deletion fails', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      $.ajax.mockImplementation((config) => {
        config.error({
          responseJSON: { message: 'Cannot delete' },
          statusText: 'Conflict',
        });
      });

      apiDelete('/test/1', onSuccess, onError);

      expect(onError).toHaveBeenCalledWith(
        'Cannot delete',
        expect.any(Object)
      );
    });

    it('should handle 404 errors gracefully', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      $.ajax.mockImplementation((config) => {
        config.error({
          statusText: 'Not Found',
          responseJSON: null,
        });
      });

      apiDelete('/test/999', onSuccess, onError);

      expect(onError).toHaveBeenCalledWith('Not Found', expect.any(Object));
    });
  });

  describe('Error Handling', () => {
    it('should prioritize responseJSON.message over statusText', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      $.ajax.mockImplementation((config) => {
        config.error({
          responseJSON: { message: 'Detailed error' },
          statusText: 'Bad Request',
        });
      });

      apiGet('/test', onSuccess, onError);

      expect(onError).toHaveBeenCalledWith('Detailed error', expect.any(Object));
    });

    it('should use statusText when responseJSON is missing', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      $.ajax.mockImplementation((config) => {
        config.error({
          responseJSON: null,
          statusText: 'Server Error',
        });
      });

      apiGet('/test', onSuccess, onError);

      expect(onError).toHaveBeenCalledWith('Server Error', expect.any(Object));
    });

    it('should call alert if no onError handler provided', () => {
      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});

      $.ajax.mockImplementation((config) => {
        config.error({
          responseJSON: { message: 'Error!' },
          statusText: 'Bad Request',
        });
      });

      apiGet('/test', () => {}, null);

      expect(alertSpy).toHaveBeenCalledWith('Error!');

      alertSpy.mockRestore();
    });

    it('should handle malformed error objects gracefully', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      $.ajax.mockImplementation((config) => {
        // Error object with no useful properties
        config.error({});
      });

      apiGet('/test', onSuccess, onError);

      expect(onError).toHaveBeenCalledWith(
        'An error occurred. Please try again.',
        expect.any(Object)
      );
    });
  });

  describe('CORS Configuration', () => {
    it('should include CORS headers in POST requests', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      apiPost('/test', {}, onSuccess, onError);

      const callConfig = $.ajax.mock.calls[0][0];
      expect(callConfig.xhrFields.withCredentials).toBe(true);
      expect(callConfig.crossDomain).toBe(true);
    });

    it('should include CORS headers in PUT requests', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      apiPut('/test', {}, onSuccess, onError);

      const callConfig = $.ajax.mock.calls[0][0];
      expect(callConfig.xhrFields.withCredentials).toBe(true);
      expect(callConfig.crossDomain).toBe(true);
    });

    it('should NOT include CORS headers in GET requests', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      apiGet('/test', onSuccess, onError);

      const callConfig = $.ajax.mock.calls[0][0];
      expect(callConfig.xhrFields).toBeUndefined();
      expect(callConfig.crossDomain).toBeUndefined();
    });

    it('should NOT include CORS headers in DELETE requests', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      apiDelete('/test', onSuccess, onError);

      const callConfig = $.ajax.mock.calls[0][0];
      expect(callConfig.xhrFields).toBeUndefined();
      expect(callConfig.crossDomain).toBeUndefined();
    });
  });

  describe('Content Type', () => {
    it('should set JSON content type for POST', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      apiPost('/test', {}, onSuccess, onError);

      const callConfig = $.ajax.mock.calls[0][0];
      expect(callConfig.contentType).toBe('application/json');
      expect(callConfig.dataType).toBe('json');
    });

    it('should set JSON content type for PUT', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      apiPut('/test', {}, onSuccess, onError);

      const callConfig = $.ajax.mock.calls[0][0];
      expect(callConfig.contentType).toBe('application/json');
      expect(callConfig.dataType).toBe('json');
    });

    it('should NOT set content type for GET', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      apiGet('/test', onSuccess, onError);

      const callConfig = $.ajax.mock.calls[0][0];
      expect(callConfig.contentType).toBeUndefined();
      expect(callConfig.dataType).toBeUndefined();
    });

    it('should NOT set content type for DELETE', () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      apiDelete('/test', onSuccess, onError);

      const callConfig = $.ajax.mock.calls[0][0];
      expect(callConfig.contentType).toBeUndefined();
      expect(callConfig.dataType).toBeUndefined();
    });
  });
});
