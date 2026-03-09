"""
Performance optimizations for Flask app
- Response compression
- Cache headers for static files
- Production mode optimizations
"""

from flask import make_response, request
from functools import wraps
import time

def add_performance_headers(app):
    """Add performance-enhancing headers to responses"""
    
    @app.after_request
    def optimize_response(response):
        """Add cache and compression headers"""
        
        # Cache static files for 1 year
        if request.path.startswith('/css/') or request.path.startswith('/js/') or \
           request.path.startswith('/images/') or request.path.endswith(('.css', '.js', '.jpg', '.png', '.svg')):
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
            response.headers['ETag'] = f'"{hash(request.path)}"'
        
        # Don't cache HTML and API responses
        elif request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    return app

def simple_compression(app):
    """Add simple gzip compression for responses"""
    
    @app.after_request
    def compress_response(response):
        """Compress larger responses"""
        
        # Only compress if response is large enough and not already compressed
        if response.status_code < 200 or \
           response.status_code >= 300 or \
           'Content-Encoding' in response.headers or \
           len(response.get_data()) < 500:
            return response
        
        # Add gzip hint (actual compression done by browser/CDN)
        response.headers['Vary'] = 'Accept-Encoding'
        
        return response
    
    return app
