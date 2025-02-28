"""
Application Layer Implementation.

The Application Layer is the top layer in the OSI model.
It provides network services directly to end-users or applications.
"""
from typing import Any, Dict, Optional, Tuple, List, Callable
import time
import json

from osi import OSILayer


class HTTPRequest:
    """
    A simple HTTP request.
    
    Contains method, path, headers, and body.
    """
    
    def __init__(self, method: str, path: str, headers: Dict[str, str] = None, body: str = ''):
        """
        Initialize an HTTP request.
        
        Args:
            method: The HTTP method (GET, POST, etc.)
            path: The request path
            headers: The HTTP headers
            body: The request body
        """
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.body = body
    
    def to_dict(self) -> Dict:
        """Convert the request to a dictionary."""
        return {
            'method': self.method,
            'path': self.path,
            'headers': self.headers,
            'body': self.body
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HTTPRequest':
        """Create a request from a dictionary."""
        return cls(
            data['method'],
            data['path'],
            data['headers'],
            data['body']
        )
    
    def __str__(self) -> str:
        """String representation of the request."""
        headers_str = '\n'.join(f"{k}: {v}" for k, v in self.headers.items())
        return f"{self.method} {self.path} HTTP/1.1\n{headers_str}\n\n{self.body}"


class HTTPResponse:
    """
    A simple HTTP response.
    
    Contains status code, status message, headers, and body.
    """
    
    def __init__(self, status_code: int, status_message: str, headers: Dict[str, str] = None, body: str = ''):
        """
        Initialize an HTTP response.
        
        Args:
            status_code: The HTTP status code
            status_message: The status message
            headers: The HTTP headers
            body: The response body
        """
        self.status_code = status_code
        self.status_message = status_message
        self.headers = headers or {}
        self.body = body
    
    def to_dict(self) -> Dict:
        """Convert the response to a dictionary."""
        return {
            'status_code': self.status_code,
            'status_message': self.status_message,
            'headers': self.headers,
            'body': self.body
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HTTPResponse':
        """Create a response from a dictionary."""
        return cls(
            data['status_code'],
            data['status_message'],
            data['headers'],
            data['body']
        )
    
    def __str__(self) -> str:
        """String representation of the response."""
        headers_str = '\n'.join(f"{k}: {v}" for k, v in self.headers.items())
        return f"HTTP/1.1 {self.status_code} {self.status_message}\n{headers_str}\n\n{self.body}"


class ApplicationLayer(OSILayer):
    """
    Application Layer implementation.
    
    This layer provides network services directly to end-users or applications.
    """
    
    def __init__(self, is_server: bool = False):
        """
        Initialize the Application Layer.
        
        Args:
            is_server: Whether this instance is a server or client
        """
        super().__init__("Application")
        self.is_server = is_server
        self.routes = {}
        self.session_id = None
        self.remote_ip = None
        self.remote_port = None
        self.response_callbacks = {}
    
    def add_route(self, path: str, handler: Callable[[HTTPRequest], HTTPResponse]) -> None:
        """
        Add a route handler.
        
        Args:
            path: The route path
            handler: The handler function
        """
        self.routes[path] = handler
    
    def handle_request(self, request: HTTPRequest) -> HTTPResponse:
        """
        Handle an HTTP request.
        
        Args:
            request: The HTTP request
            
        Returns:
            The HTTP response
        """
        # Find a handler for the path
        handler = self.routes.get(request.path)
        
        if handler:
            return handler(request)
        
        # No handler found, return 404
        return HTTPResponse(404, "Not Found", {"Content-Type": "text/plain"}, "404 Not Found")
    
    def send_request(self, request: HTTPRequest, callback: Optional[Callable[[HTTPResponse], None]] = None) -> None:
        """
        Send an HTTP request.
        
        Args:
            request: The HTTP request to send
            callback: A callback function to handle the response
        """
        if self.is_server:
            print(f"[{self.name}] Cannot send request, this is a server")
            return
        
        print(f"[{self.name}] Sending {request.method} request to {request.path}")
        
        # Store the callback
        if callback:
            self.response_callbacks[request.path] = callback
        
        # Convert the request to a dictionary
        request_dict = request.to_dict()
        
        # Send the request down to the Presentation layer
        if self.lower_layer:
            self.lower_layer.send_down(
                request_dict,
                data_format=3,  # JSON
                session_id=self.session_id,
                remote_ip=self.remote_ip,
                remote_port=self.remote_port
            )
    
    def send_response(self, response: HTTPResponse) -> None:
        """
        Send an HTTP response.
        
        Args:
            response: The HTTP response to send
        """
        if not self.is_server:
            print(f"[{self.name}] Cannot send response, this is a client")
            return
        
        print(f"[{self.name}] Sending response: {response.status_code} {response.status_message}")
        
        # Convert the response to a dictionary
        response_dict = response.to_dict()
        
        # Send the response down to the Presentation layer
        if self.lower_layer:
            self.lower_layer.send_down(
                response_dict,
                data_format=3,  # JSON
                session_id=self.session_id
            )
    
    def send_down(self, data: Any, **kwargs) -> None:
        """
        Process data from the user application and send it down to the Presentation layer.
        
        Args:
            data: The data to be sent
            **kwargs: Additional parameters
        """
        # In a real implementation, this would be called by the user application
        # For simplicity, we'll just pass the data down to the Presentation layer
        if self.lower_layer:
            self.lower_layer.send_down(data, **kwargs)
    
    def send_up(self, data: Any, **kwargs) -> None:
        """
        Process data from the Presentation layer and send it up to the user application.
        
        Args:
            data: The data received from the Presentation layer
            **kwargs: Additional parameters
        """
        data_format = kwargs.get('data_format')
        session_id = kwargs.get('session_id')
        
        # Store the session ID if not already set
        if not self.session_id:
            self.session_id = session_id
        
        # Handle HTTP messages
        if data_format == 3:  # JSON
            if isinstance(data, dict):
                # Check if this is a request or response
                if 'method' in data and 'path' in data:
                    # This is a request
                    request = HTTPRequest.from_dict(data)
                    print(f"[{self.name}] Received {request.method} request for {request.path}")
                    
                    # Handle the request
                    response = self.handle_request(request)
                    
                    # Send the response
                    self.send_response(response)
                
                elif 'status_code' in data and 'status_message' in data:
                    # This is a response
                    response = HTTPResponse.from_dict(data)
                    print(f"[{self.name}] Received response: {response.status_code} {response.status_message}")
                    
                    # Find and call the callback
                    path = kwargs.get('path', '')
                    callback = self.response_callbacks.get(path)
                    if callback:
                        callback(response)
                        del self.response_callbacks[path]
                    else:
                        # Try to find a callback for any path
                        for path, callback in list(self.response_callbacks.items()):
                            callback(response)
                            del self.response_callbacks[path]
                            break
        
        # In a real implementation, we would pass the data up to the user application
        # For simplicity, we'll just print it
        print(f"[{self.name}] Received data: {data}")


# Example route handlers
def index_handler(request: HTTPRequest) -> HTTPResponse:
    """Handle requests to the index route."""
    return HTTPResponse(
        200,
        "OK",
        {"Content-Type": "text/html"},
        "<html><body><h1>Welcome to the OSI Model Simulation</h1></body></html>"
    )


def echo_handler(request: HTTPRequest) -> HTTPResponse:
    """Echo the request body back to the client."""
    return HTTPResponse(
        200,
        "OK",
        {"Content-Type": "text/plain"},
        request.body
    )


def time_handler(request: HTTPRequest) -> HTTPResponse:
    """Return the current server time."""
    return HTTPResponse(
        200,
        "OK",
        {"Content-Type": "text/plain"},
        f"The current time is: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    ) 