#!/usr/bin/env python3
"""
OSI Model Simulation.

This script simulates the seven layers of the OSI model using Python.
It can be run in either server or client mode.
"""
import sys
import time
import argparse
import logging
from typing import List

from osi import OSILayer
from osi.physical import PhysicalLayer
from osi.datalink import DataLinkLayer
from osi.network import NetworkLayer
from osi.transport import TransportLayer
from osi.session import SessionLayer
from osi.presentation import PresentationLayer
from osi.application import ApplicationLayer, HTTPRequest, HTTPResponse, index_handler, echo_handler, time_handler


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('osi_model')


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
    
    logger.info(f"Created OSI stack for {'server' if is_server else 'client'}")
    
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
    logger.info(f"Starting OSI Model Simulation Server on {host}:{port}")
    print(f"Starting OSI Model Simulation Server on {host}:{port}")
    
    # Create the OSI layer stack
    layers = create_osi_stack(True, host, port)
    physical_layer = layers[0]
    application_layer = layers[-1]
    
    # Add route handlers
    application_layer.add_route('/', index_handler)
    application_layer.add_route('/echo', echo_handler)
    application_layer.add_route('/time', time_handler)
    logger.info("Added route handlers: /, /echo, /time")
    
    # Initialize the physical layer
    physical_layer.initialize()
    
    print("Server is running. Press Ctrl+C to stop.")
    logger.info("Server is running. Waiting for connections...")
    
    try:
        # Main server loop
        while True:
            # Receive data from the client
            physical_layer.send_up()
            
            # Sleep to avoid high CPU usage
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        logger.info("Server shutdown initiated by user")
        print("\nShutting down server...")
    
    finally:
        # Close the connection
        physical_layer.close()
        logger.info("Server shutdown complete")


def run_client(host: str = 'localhost', port: int = 12345) -> None:
    """
    Run the OSI model simulation in client mode.
    
    Args:
        host: The hostname or IP address to connect to
        port: The port number to use
    """
    logger.info(f"Starting OSI Model Simulation Client, connecting to {host}:{port}")
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
        # Define a callback to handle responses
        def handle_response(response):
            print(f"\nReceived response: {response.status_code} {response.status_message}")
            print(f"Headers: {response.headers}")
            print(f"Body: {response.body}")
        
        # Send a request to the index route
        logger.info("Sending request to /")
        print("\nSending request to /")
        request = HTTPRequest('GET', '/', {'User-Agent': 'OSI-Model-Client'})
        application_layer.send_request(request, handle_response)
        
        # Wait for the response and process it
        time.sleep(1)
        for _ in range(5):  # Try multiple times to receive the response
            physical_layer.send_up()
            time.sleep(0.2)
        
        # Send a request to the echo route
        logger.info("Sending request to /echo")
        print("\nSending request to /echo")
        request = HTTPRequest('POST', '/echo', {'Content-Type': 'text/plain'}, 'Hello, OSI Model!')
        application_layer.send_request(request, handle_response)
        
        # Wait for the response and process it
        time.sleep(1)
        for _ in range(5):  # Try multiple times to receive the response
            physical_layer.send_up()
            time.sleep(0.2)
        
        # Send a request to the time route
        logger.info("Sending request to /time")
        print("\nSending request to /time")
        request = HTTPRequest('GET', '/time', {'User-Agent': 'OSI-Model-Client'})
        application_layer.send_request(request, handle_response)
        
        # Wait for the response and process it
        time.sleep(1)
        for _ in range(5):  # Try multiple times to receive the response
            physical_layer.send_up()
            time.sleep(0.2)
        
        logger.info("All requests completed")
        print("\nAll requests completed.")
    
    except KeyboardInterrupt:
        logger.info("Client operation interrupted by user")
        print("\nClient operation interrupted.")
    
    except Exception as e:
        logger.error(f"Error in client: {e}")
        print(f"\nError: {e}")
    
    finally:
        # Close the connection
        physical_layer.close()
        logger.info("Client shutdown complete")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='OSI Model Simulation')
    parser.add_argument('mode', choices=['server', 'client'], help='Run as server or client')
    parser.add_argument('--host', default='localhost', help='Host to bind to or connect to')
    parser.add_argument('--port', type=int, default=12345, help='Port to use')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set logging level based on debug flag
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    if args.mode == 'server':
        run_server(args.host, args.port)
    else:
        run_client(args.host, args.port)


if __name__ == '__main__':
    main() 