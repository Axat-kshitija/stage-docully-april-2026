import logging

logger = logging.getLogger(__name__)

class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the request method and headers
        logger.info(f"Request Method: {request.method}, Headers: {request.headers}")
        
        response = self.get_response(request)
        return response