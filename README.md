# OSI Model Simulation

This project simulates the seven layers of the OSI (Open Systems Interconnection) model using Python. Each layer is implemented as a separate class, and data flows through all seven layers to simulate real-world network communication.

## Layers Implemented

1. **Physical Layer**: Simulated using Python sockets and bit-level operations
2. **Data Link Layer**: Implements MAC addressing and frame transmission
3. **Network Layer**: Simulates IP addressing and packet routing
4. **Transport Layer**: Implements TCP-like packet sequencing and error handling
5. **Session Layer**: Manages connection states and synchronization
6. **Presentation Layer**: Handles encryption, compression, and encoding
7. **Application Layer**: Implements HTTP-like request-response communication

## Project Structure

- `main.py`: Entry point to run the simulation
- `osi/`: Directory containing the implementation of each OSI layer
  - `physical.py`: Physical layer implementation
  - `datalink.py`: Data Link layer implementation
  - `network.py`: Network layer implementation
  - `transport.py`: Transport layer implementation
  - `session.py`: Session layer implementation
  - `presentation.py`: Presentation layer implementation
  - `application.py`: Application layer implementation
- `utils.py`: Utility functions used across layers

## Features

- Complete implementation of all seven OSI layers
- Simulated network communication between client and server
- HTTP-like request-response protocol at the Application layer
- MAC addressing and frame handling at the Data Link layer
- IP addressing and routing at the Network layer
- Connection management at the Transport layer
- Session management at the Session layer
- Data formatting, encryption, and compression at the Presentation layer
- Detailed logging for debugging and understanding the flow of data

## How to Run

1. Start the server:
   ```
   python main.py server
   ```

2. In another terminal, start the client:
   ```
   python main.py client
   ```

3. For debugging with more detailed logs:
   ```
   python main.py server --debug
   python main.py client --debug
   ```

4. You can also specify a different host and port:
   ```
   python main.py server --host 0.0.0.0 --port 8080
   python main.py client --host 192.168.1.100 --port 8080
   ```

## Requirements

- Python 3.6+
- No external libraries required (uses only standard library)

## Implementation Notes

- For simulation purposes, the implementation accepts all frames and packets regardless of addressing
- In a real network, strict MAC and IP address checking would be enforced
- The simulation includes simplified versions of protocols like TCP and HTTP
- Error handling and retransmission are implemented in a basic way 