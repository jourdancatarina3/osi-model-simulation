"""
Physical Layer Implementation.

The Physical Layer is responsible for the transmission and reception of raw bit streams over a physical medium.
In this simulation, we use Python sockets to simulate the physical connection.
"""
import socket
import time
from typing import Any, Dict, Optional, Tuple

from osi import OSILayer
import utils


class PhysicalLayer(OSILayer):
    """
    Physical Layer implementation.
    
    This layer handles the transmission of raw bits over a simulated physical medium (sockets).
    """
    
    def __init__(self, is_server: bool = False, host: str = 'localhost', port: int = 12345):
        """
        Initialize the Physical Layer.
        
        Args:
            is_server: Whether this instance is a server or client
            host: The hostname or IP address to connect to or bind to
            port: The port number to use
        """
        super().__init__("Physical")
        self.is_server = is_server
        self.host = host
        self.port = port
        self.socket = None
        self.client_socket = None
        self.client_address = None
        
    def initialize(self) -> None:
        """Initialize the socket connection based on whether this is a server or client."""
        if self.is_server:
            self._initialize_server()
        else:
            self._initialize_client()
    
    def _initialize_server(self) -> None:
        """Initialize the server socket and wait for a connection."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        print(f"[{self.name}] Server listening on {self.host}:{self.port}")
        
        # Accept a connection
        self.client_socket, self.client_address = self.socket.accept()
        print(f"[{self.name}] Connection established with {self.client_address}")
    
    def _initialize_client(self) -> None:
        """Initialize the client socket and connect to the server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[{self.name}] Connecting to {self.host}:{self.port}")
        
        # Try to connect with retries
        max_retries = 5
        for i in range(max_retries):
            try:
                self.socket.connect((self.host, self.port))
                print(f"[{self.name}] Connected to {self.host}:{self.port}")
                break
            except ConnectionRefusedError:
                if i < max_retries - 1:
                    print(f"[{self.name}] Connection failed, retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    raise
    
    def send_down(self, data: bytes, **kwargs) -> None:
        """
        Send data down to the physical medium (socket).
        
        In a real physical layer, this would involve encoding the bits for transmission
        over a physical medium like copper wire, fiber optic, or radio waves.
        
        Args:
            data: The bit stream to transmit
            **kwargs: Additional parameters
        """
        print(f"[{self.name}] Sending {len(data)} bytes")
        
        # Convert data to a bit string for demonstration
        bit_string = utils.bytes_to_bits(data)
        print(f"[{self.name}] Bit representation (first 64 bits): {bit_string[:64]}...")
        
        # Prepare the data with a length prefix for framing
        length_prefix = len(data).to_bytes(4, byteorder='big')
        framed_data = length_prefix + data
        
        # Send the data over the socket
        if self.is_server:
            self.client_socket.sendall(framed_data)
        else:
            self.socket.sendall(framed_data)
    
    def send_up(self, **kwargs) -> None:
        """
        Receive data from the physical medium (socket) and send it up to the Data Link layer.
        
        In a real physical layer, this would involve receiving and decoding signals
        from a physical medium.
        
        Args:
            **kwargs: Additional parameters
        """
        # Determine which socket to use
        recv_socket = self.client_socket if self.is_server else self.socket
        
        # First receive the length prefix (4 bytes)
        length_bytes = recv_socket.recv(4)
        if not length_bytes:
            print(f"[{self.name}] Connection closed")
            return
        
        # Convert length prefix to integer
        data_length = int.from_bytes(length_bytes, byteorder='big')
        
        # Receive the actual data
        data = b''
        remaining = data_length
        while remaining > 0:
            chunk = recv_socket.recv(min(4096, remaining))
            if not chunk:
                break
            data += chunk
            remaining -= len(chunk)
        
        print(f"[{self.name}] Received {len(data)} bytes")
        
        # Convert data to a bit string for demonstration
        bit_string = utils.bytes_to_bits(data)
        print(f"[{self.name}] Bit representation (first 64 bits): {bit_string[:64]}...")
        
        # Send the data up to the Data Link layer
        if self.upper_layer:
            self.upper_layer.send_up(data=data)
    
    def close(self) -> None:
        """Close the socket connection."""
        if self.is_server:
            if self.client_socket:
                self.client_socket.close()
            if self.socket:
                self.socket.close()
        else:
            if self.socket:
                self.socket.close()
        print(f"[{self.name}] Connection closed") 