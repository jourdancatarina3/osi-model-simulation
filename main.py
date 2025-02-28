#!/usr/bin/env python3
"""
OSI Model Simulation.

This script simulates the seven layers of the OSI model using Python.
It can be run in either server or client mode.
"""
import sys
import time
import argparse
from typing import List

from osi import OSILayer
from osi.physical import PhysicalLayer
from osi.datalink import DataLinkLayer
from osi.network import NetworkLayer
from osi.transport import TransportLayer
from osi.session import SessionLayer
from osi.presentation import PresentationLayer
from osi.application import ApplicationLayer, HTTPRequest, HTTPResponse, index_handler, echo_handler, time_handler


def create_osi_stack(is_server: bool = False, host: str = 'localhost', port: int = 12345) -> List[OSILayer]:
    """
    Create the OSI layer stack.
    
    Args:
        is_server: Whether this instance is a server or client
        host: The hostname or IP address to connect to or bind to
        port: The port number to use
        
    Returns:
        The list of OSI layers
    """
    # Create the layers
    physical_layer = PhysicalLayer(is_server, host, port)
    datalink_layer = DataLinkLayer()
    network_layer = NetworkLayer()
    transport_layer = TransportLayer()
    session_layer = SessionLayer()
    presentation_layer = PresentationLayer()
    application_layer = ApplicationLayer(is_server)
    
    # Connect the layers
    physical_layer.set_upper_layer(datalink_layer)
    datalink_layer.set_lower_layer(physical_layer)
    datalink_layer.set_upper_layer(network_layer)
    network_layer.set_lower_layer(datalink_layer)
    network_layer.set_upper_layer(transport_layer)
    transport_layer.set_lower_layer(network_layer)
    transport_layer.set_upper_layer(session_layer)
    session_layer.set_lower_layer(transport_layer)
    session_layer.set_upper_layer(presentation_layer)
    presentation_layer.set_lower_layer(session_layer)
    presentation_layer.set_upper_layer(application_layer)
    application_layer.set_lower_layer(presentation_layer)
    
    # Return the layers
    return [
        physical_layer,
        datalink_layer,
        network_layer,
        transport_layer,
        session_layer,
        presentation_layer,
        application_layer
    ]


def run_server(host: str = 'localhost', port: int = 12345) -> None:
    """
    Run the OSI model simulation in server mode.
    
    Args:
        host: The hostname or IP address to bind to
        port: The port number to use
    """
    print(f"Starting OSI Model Simulation Server on {host}:{port}")
    
    # Create the OSI layer stack
    layers = create_osi_stack(True, host, port)
    physical_layer = layers[0]
    application_layer = layers[-1]
    
    # Add route handlers
    application_layer.add_route('/', index_handler)
    application_layer.add_route('/echo', echo_handler)
    application_layer.add_route('/time', time_handler)
    
    # Initialize the physical layer
    physical_layer.initialize()
    
    print("Server is running. Press Ctrl+C to stop.")
    
    try:
        # Main server loop
        while True:
            # Receive data from the client
            physical_layer.send_up()
            
            # Sleep to avoid high CPU usage
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nShutting down server...")
    
    finally:
        # Close the connection
        physical_layer.close()


def run_client(host: str = 'localhost', port: int = 12345) -> None:
    """
    Run the OSI model simulation in client mode.
    
    Args:
        host: The hostname or IP address to connect to
        port: The port number to use
    """
    print(f"Starting OSI Model Simulation Client, connecting to {host}:{port}")
    
    # Create the OSI layer stack
    layers = create_osi_stack(False, host, port)
    physical_layer = layers[0]
    application_layer = layers[-1]
    
    # Initialize the physical layer
    physical_layer.initialize()
    
    # Set remote information
    application_layer.remote_ip = host
    application_layer.remote_port = port
    
    try:
        # Send a request to the index route
        print("\nSending request to /")
        request = HTTPRequest('GET', '/', {'User-Agent': 'OSI-Model-Client'})
        application_layer.send_request(request)
        
        # Wait for the response
        time.sleep(1)
        physical_layer.send_up()
        
        # Send a request to the echo route
        print("\nSending request to /echo")
        request = HTTPRequest('POST', '/echo', {'Content-Type': 'text/plain'}, 'Hello, OSI Model!')
        application_layer.send_request(request)
        
        # Wait for the response
        time.sleep(1)
        physical_layer.send_up()
        
        # Send a request to the time route
        print("\nSending request to /time")
        request = HTTPRequest('GET', '/time', {'User-Agent': 'OSI-Model-Client'})
        application_layer.send_request(request)
        
        # Wait for the response
        time.sleep(1)
        physical_layer.send_up()
        
        print("\nAll requests completed.")
    
    except KeyboardInterrupt:
        print("\nClient operation interrupted.")
    
    finally:
        # Close the connection
        physical_layer.close()


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='OSI Model Simulation')
    parser.add_argument('mode', choices=['server', 'client'], help='Run as server or client')
    parser.add_argument('--host', default='localhost', help='Host to bind to or connect to')
    parser.add_argument('--port', type=int, default=12345, help='Port to use')
    
    args = parser.parse_args()
    
    if args.mode == 'server':
        run_server(args.host, args.port)
    else:
        run_client(args.host, args.port)


if __name__ == '__main__':
    main() 