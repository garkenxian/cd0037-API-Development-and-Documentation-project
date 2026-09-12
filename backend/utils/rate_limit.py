"""
Rate limiting utilities for API security.
Implements lightweight per-IP and per-resource throttling.
"""

import os
import time
from functools import wraps
from flask import request, jsonify, current_app
from collections import defaultdict, deque


class RateLimiter:
    """
    Simple in-memory rate limiter.
    Tracks request times per (endpoint, identifier) tuple.
    Useful for lightweight abuse protection without external dependencies.
    
    LIMITATIONS (by design):
    - In-memory storage: Does not persist across process restarts
    - Per-process: Each app instance has independent limits
    - Not shared: Multiple gunicorn/uwsgi workers will have separate counters
    
    For multi-process deployments (gunicorn, uwsgi, etc.), consider:
    - Redis-based rate limiting for shared state across workers
    - Nginx rate limiting at reverse proxy level
    - Application-level tracking with external storage
    
    For single-process deployments (development, small scale), this is sufficient.
    
    Note: Rate limiting is automatically disabled during testing (TESTING=True).
    """
    
    def __init__(self):
        """Initialize the rate limiter with empty request history"""
        self.requests = defaultdict(deque)
    
    def _cleanup_old_requests(self, key, window_seconds):
        """Remove requests outside the time window"""
        now = time.time()
        while self.requests[key] and self.requests[key][0] < now - window_seconds:
            self.requests[key].popleft()
    
    def is_allowed(self, identifier, limit, window_seconds):
        """
        Check if a request should be allowed based on rate limit.
        
        Args:
            identifier: Unique identifier (e.g., IP address, user ID, or composite key)
            limit: Maximum number of requests allowed in the window
            window_seconds: Time window in seconds
            
        Returns:
            bool: True if request is allowed, False if rate limited
        """
        self._cleanup_old_requests(identifier, window_seconds)
        
        if len(self.requests[identifier]) < limit:
            self.requests[identifier].append(time.time())
            return True
        
        return False
    
    def get_retry_after(self, identifier, window_seconds):
        """
        Get approximate seconds until next request is allowed.
        
        Args:
            identifier: The rate limited identifier
            window_seconds: The time window in seconds
            
        Returns:
            int: Seconds until retry is allowed (0 if allowed now)
        """
        self._cleanup_old_requests(identifier, window_seconds)
        
        if not self.requests[identifier]:
            return 0
        
        oldest_request = self.requests[identifier][0]
        retry_after = max(0, int(window_seconds - (time.time() - oldest_request)) + 1)
        return retry_after
    
    def reset(self):
        """Reset all rate limit tracking (useful for testing)"""
        self.requests.clear()


# Global rate limiter instance
_limiter = RateLimiter()


def get_rate_limiter():
    """Get the global rate limiter instance"""
    return _limiter


def rate_limit(limit, window_seconds, key_func=None):
    """
    Rate limiting decorator for Flask route handlers.
    
    Rate limiting is ENABLED by default in production deployments.
    Disabled only when TESTING=true or RATE_LIMIT_ENABLED=false.
    This ensures production environments have protection by default,
    even when FLASK_ENV is unset.
    
    Args:
        limit: Maximum number of requests allowed per identifier
        window_seconds: Time window in seconds
        key_func: Callable that returns identifier string (default: IP address)
                 key_func receives (request, view_args) as arguments
        
    Example:
        @app.route('/games/<game_id>/<question_number>', methods=['POST'])
        @rate_limit(limit=30, window_seconds=60, key_func=lambda r, va: r.remote_addr)
        def submit_answer(game_id, question_number):
            ...
    """
    if key_func is None:
        # Default: rate limit by client IP
        key_func = lambda r, va: r.remote_addr
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if rate limiting should be enabled
            # By default, it's ENABLED (fail-secure)
            # Disable only when explicitly testing or rate limiting is turned off
            is_testing = os.environ.get('TESTING', 'false').lower() in ('true', '1', 'yes')
            rate_limit_disabled = os.environ.get('RATE_LIMIT_ENABLED', 'true').lower() in ('false', '0', 'no')
            
            # Try to check app config as well if available
            try:
                is_testing = is_testing or current_app.config.get('TESTING', False)
                rate_limit_disabled_config = not current_app.config.get('RATE_LIMIT_ENABLED', True)
                rate_limit_disabled = rate_limit_disabled or rate_limit_disabled_config
            except (RuntimeError, AttributeError):
                pass
            
            # Skip rate limiting only if explicitly testing or explicitly disabled
            if is_testing or rate_limit_disabled:
                return f(*args, **kwargs)
            
            # Get the identifier for this request
            try:
                identifier = key_func(request, kwargs)
            except Exception:
                # If we can't get identifier, allow through
                return f(*args, **kwargs)
            
            # Check rate limit
            if not _limiter.is_allowed(identifier, limit, window_seconds):
                retry_after = _limiter.get_retry_after(identifier, window_seconds)
                response = jsonify({
                    "success": False,
                    "error": 429,
                    "message": f"Too many requests. Please retry after {retry_after} seconds."
                })
                response.status_code = 429
                # Add Retry-After header for standard HTTP client compatibility
                response.headers['Retry-After'] = str(retry_after)
                return response
            
            # Request allowed, proceed
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


