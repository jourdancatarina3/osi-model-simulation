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

## How to Run

1. Start the server:
   ```
   python main.py server
   ```

2. In another terminal, start the client:
   ```
   python main.py client
   ```

## Requirements

- Python 3.6+
- No external libraries required (uses only standard library) 