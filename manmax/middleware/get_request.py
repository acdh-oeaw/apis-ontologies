from threading import current_thread


_requests = {}

def current_request():
    return _requests.get(current_thread().ident, None)

class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        _requests[current_thread().ident] = request
        
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        _requests.pop(current_thread().ident, None)
        return response
        

    def process_exception(self, request, exception):
        # if an exception has happened, request should be flushed too
         _requests.pop(current_thread().ident, None)



    