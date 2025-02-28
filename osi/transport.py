"""
Transport Layer Implementation.

The Transport Layer is responsible for end-to-end communication.
It handles segmentation, flow control, error recovery, and connection management.
"""
from typing import Any, Dict, Optional, Tuple, List, Set
import random
import time

from osi import OSILayer
import utils


class Segment:
    """
    A transport layer segment.
    
    Contains source and destination ports, sequence number, acknowledgment number,
    flags, window size, and payload data.
    """
    
    # Flag constants
    SYN = 0x02
    ACK = 0x10
    FIN = 0x01
    
    def __init__(
        self,
        src_port: int,
        dst_port: int,
        seq_num: int,
        ack_num: int,
        flags: int,
        window: int,
        data: bytes
    ):
        """
        Initialize a segment with transport layer headers and data.
        
        Args:
            src_port: Source port
            dst_port: Destination port
            seq_num: Sequence number
            ack_num: Acknowledgment number
            flags: Control flags (SYN, ACK, FIN, etc.)
            window: Window size
            data: Payload data
        """
        self.src_port = src_port
        self.dst_port = dst_port
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.flags = flags
        self.window = window
        self.data = data
    
    def to_bytes(self) -> bytes:
        """Convert the segment to bytes for transmission."""
        segment_dict = {
            'src_port': self.src_port,
            'dst_port': self.dst_port,
            'seq_num': self.seq_num,
            'ack_num': self.ack_num,
            'flags': self.flags,
            'window': self.window,
            'data': self.data.hex()
        }
        return utils.serialize_dict(segment_dict)
    
    @classmethod
    def from_bytes(cls, segment_bytes: bytes) -> 'Segment':
        """Create a segment from bytes received from the Network layer."""
        segment_dict = utils.deserialize_dict(segment_bytes)
        src_port = segment_dict['src_port']
        dst_port = segment_dict['dst_port']
        seq_num = segment_dict['seq_num']
        ack_num = segment_dict['ack_num']
        flags = segment_dict['flags']
        window = segment_dict['window']
        data = bytes.fromhex(segment_dict['data'])
        
        return cls(src_port, dst_port, seq_num, ack_num, flags, window, data)
    
    def is_syn(self) -> bool:
        """Check if the SYN flag is set."""
        return bool(self.flags & self.SYN)
    
    def is_ack(self) -> bool:
        """Check if the ACK flag is set."""
        return bool(self.flags & self.ACK)
    
    def is_fin(self) -> bool:
        """Check if the FIN flag is set."""
        return bool(self.flags & self.FIN)


class Connection:
    """
    A transport layer connection.
    
    Represents a TCP-like connection with sequence numbers, state, and buffers.
    """
    
    # Connection states
    CLOSED = 0
    LISTEN = 1
    SYN_SENT = 2
    SYN_RECEIVED = 3
    ESTABLISHED = 4
    FIN_WAIT_1 = 5
    FIN_WAIT_2 = 6
    CLOSE_WAIT = 7
    CLOSING = 8
    LAST_ACK = 9
    TIME_WAIT = 10
    
    def __init__(self, local_port: int, remote_port: Optional[int] = None, remote_ip: Optional[str] = None):
        """
        Initialize a connection.
        
        Args:
            local_port: Local port number
            remote_port: Remote port number (if known)
            remote_ip: Remote IP address (if known)
        """
        self.local_port = local_port
        self.remote_port = remote_port
        self.remote_ip = remote_ip
        self.state = self.CLOSED
        self.seq_num = random.randint(0, 0xFFFFFFFF)
        self.ack_num = 0
        self.window = 65535
        self.send_buffer = b''
        self.recv_buffer = b''
        self.expected_seq = 0
        self.segments_to_ack: Set[int] = set()
    
    def is_established(self) -> bool:
        """Check if the connection is established."""
        return self.state == self.ESTABLISHED
    
    def add_to_recv_buffer(self, data: bytes) -> None:
        """Add data to the receive buffer."""
        self.recv_buffer += data
    
    def get_from_recv_buffer(self, size: Optional[int] = None) -> bytes:
        """Get data from the receive buffer."""
        if size is None or size >= len(self.recv_buffer):
            data = self.recv_buffer
            self.recv_buffer = b''
        else:
            data = self.recv_buffer[:size]
            self.recv_buffer = self.recv_buffer[size:]
        return data
    
    def add_to_send_buffer(self, data: bytes) -> None:
        """Add data to the send buffer."""
        self.send_buffer += data
    
    def get_from_send_buffer(self, size: int) -> bytes:
        """Get data from the send buffer."""
        if size >= len(self.send_buffer):
            data = self.send_buffer
            self.send_buffer = b''
        else:
            data = self.send_buffer[:size]
            self.send_buffer = self.send_buffer[size:]
        return data


class TransportLayer(OSILayer):
    """
    Transport Layer implementation.
    
    This layer handles end-to-end communication, segmentation, and connection management.
    """
    
    def __init__(self):
        """Initialize the Transport Layer."""
        super().__init__("Transport")
        self.connections: Dict[int, Connection] = {}
        self.next_port = 49152  # Start with ephemeral ports
    
    def create_connection(self, remote_port: int, remote_ip: str) -> Connection:
        """
        Create a new connection to a remote host.
        
        Args:
            remote_port: Remote port number
            remote_ip: Remote IP address
            
        Returns:
            The new connection
        """
        local_port = self.next_port
        self.next_port += 1
        
        connection = Connection(local_port, remote_port, remote_ip)
        self.connections[local_port] = connection
        
        return connection
    
    def get_connection(self, local_port: int) -> Optional[Connection]:
        """
        Get a connection by local port.
        
        Args:
            local_port: Local port number
            
        Returns:
            The connection if found, None otherwise
        """
        return self.connections.get(local_port)
    
    def find_connection_by_remote(self, remote_port: int, remote_ip: str) -> Optional[Connection]:
        """
        Find a connection by remote port and IP.
        
        Args:
            remote_port: Remote port number
            remote_ip: Remote IP address
            
        Returns:
            The connection if found, None otherwise
        """
        for conn in self.connections.values():
            if conn.remote_port == remote_port and conn.remote_ip == remote_ip:
                return conn
        return None
    
    def connect(self, remote_port: int, remote_ip: str) -> Connection:
        """
        Establish a connection to a remote host.
        
        Args:
            remote_port: Remote port number
            remote_ip: Remote IP address
            
        Returns:
            The established connection
        """
        # Create a new connection
        connection = self.create_connection(remote_port, remote_ip)
        connection.state = Connection.SYN_SENT
        
        print(f"[{self.name}] Initiating connection to {remote_ip}:{remote_port}")
        
        # Send SYN segment
        syn_segment = Segment(
            connection.local_port,
            remote_port,
            connection.seq_num,
            0,
            Segment.SYN,
            connection.window,
            b''
        )
        
        # Increment sequence number
        connection.seq_num += 1
        
        # Send the segment down to the Network layer
        if self.lower_layer:
            self.lower_layer.send_down(
                syn_segment.to_bytes(),
                dst_ip=remote_ip,
                protocol=6  # TCP
            )
        
        # In a real implementation, we would wait for the SYN-ACK response
        # For simplicity, we'll just assume the connection is established
        connection.state = Connection.ESTABLISHED
        
        return connection
    
    def accept(self, local_port: int) -> Connection:
        """
        Accept a connection on a local port.
        
        Args:
            local_port: Local port number
            
        Returns:
            The accepted connection
        """
        # Create a new connection in LISTEN state
        connection = Connection(local_port)
        connection.state = Connection.LISTEN
        self.connections[local_port] = connection
        
        print(f"[{self.name}] Listening on port {local_port}")
        
        return connection
    
    def send(self, connection: Connection, data: bytes) -> None:
        """
        Send data over a connection.
        
        Args:
            connection: The connection to send data over
            data: The data to send
        """
        if not connection.is_established():
            print(f"[{self.name}] Cannot send data, connection not established")
            return
        
        print(f"[{self.name}] Sending {len(data)} bytes over connection {connection.local_port} -> {connection.remote_ip}:{connection.remote_port}")
        
        # Add data to the send buffer
        connection.add_to_send_buffer(data)
        
        # Create a segment with the data
        segment = Segment(
            connection.local_port,
            connection.remote_port,
            connection.seq_num,
            connection.ack_num,
            Segment.ACK,
            connection.window,
            connection.get_from_send_buffer(1024)  # Maximum segment size
        )
        
        # Increment sequence number
        connection.seq_num += len(segment.data)
        
        # Send the segment down to the Network layer
        if self.lower_layer:
            self.lower_layer.send_down(
                segment.to_bytes(),
                dst_ip=connection.remote_ip,
                protocol=6  # TCP
            )
    
    def close(self, connection: Connection) -> None:
        """
        Close a connection.
        
        Args:
            connection: The connection to close
        """
        if connection.state == Connection.CLOSED:
            print(f"[{self.name}] Connection already closed")
            return
        
        print(f"[{self.name}] Closing connection {connection.local_port} -> {connection.remote_ip}:{connection.remote_port}")
        
        # Send FIN segment
        fin_segment = Segment(
            connection.local_port,
            connection.remote_port,
            connection.seq_num,
            connection.ack_num,
            Segment.FIN | Segment.ACK,
            connection.window,
            b''
        )
        
        # Increment sequence number
        connection.seq_num += 1
        
        # Update connection state
        connection.state = Connection.FIN_WAIT_1
        
        # Send the segment down to the Network layer
        if self.lower_layer:
            self.lower_layer.send_down(
                fin_segment.to_bytes(),
                dst_ip=connection.remote_ip,
                protocol=6  # TCP
            )
        
        # In a real implementation, we would wait for the FIN-ACK response
        # For simplicity, we'll just assume the connection is closed
        connection.state = Connection.CLOSED
        
        # Remove the connection from our list
        if connection.local_port in self.connections:
            del self.connections[connection.local_port]
    
    def send_down(self, data: bytes, **kwargs) -> None:
        """
        Process data from the Session layer and send it down to the Network layer.
        
        Args:
            data: The data to be segmented and sent
            **kwargs: Additional parameters, may include connection information
        """
        local_port = kwargs.get('local_port')
        remote_port = kwargs.get('remote_port')
        remote_ip = kwargs.get('remote_ip')
        
        # Get or create the connection
        connection = None
        if local_port:
            connection = self.get_connection(local_port)
        
        if not connection and remote_port and remote_ip:
            connection = self.find_connection_by_remote(remote_port, remote_ip)
            if not connection:
                connection = self.connect(remote_port, remote_ip)
        
        if not connection:
            print(f"[{self.name}] No connection available, cannot send data")
            return
        
        # Send the data over the connection
        self.send(connection, data)
    
    def send_up(self, data: bytes, **kwargs) -> None:
        """
        Process data from the Network layer and send it up to the Session layer.
        
        Args:
            data: The segmented data received from the Network layer
            **kwargs: Additional parameters
        """
        src_ip = kwargs.get('src_ip')
        protocol = kwargs.get('protocol')
        
        # Check if this is a TCP segment
        if protocol != 6:
            print(f"[{self.name}] Not a TCP segment (protocol: {protocol}), discarding")
            return
        
        print(f"[{self.name}] Received segment, size: {len(data)} bytes")
        
        # Parse the segment
        try:
            segment = Segment.from_bytes(data)
            
            print(f"[{self.name}] Segment: {segment.src_port} -> {segment.dst_port} (SEQ: {segment.seq_num}, ACK: {segment.ack_num}, Flags: {segment.flags:02x})")
            
            # Find the connection
            connection = self.get_connection(segment.dst_port)
            
            # If no connection exists and this is a SYN segment, create one
            if not connection and segment.is_syn():
                connection = Connection(segment.dst_port, segment.src_port, src_ip)
                connection.state = Connection.SYN_RECEIVED
                connection.ack_num = segment.seq_num + 1
                self.connections[segment.dst_port] = connection
                
                # Send SYN-ACK segment
                syn_ack_segment = Segment(
                    connection.local_port,
                    connection.remote_port,
                    connection.seq_num,
                    connection.ack_num,
                    Segment.SYN | Segment.ACK,
                    connection.window,
                    b''
                )
                
                # Increment sequence number
                connection.seq_num += 1
                
                # Send the segment down to the Network layer
                if self.lower_layer:
                    self.lower_layer.send_down(
                        syn_ack_segment.to_bytes(),
                        dst_ip=connection.remote_ip,
                        protocol=6  # TCP
                    )
                
                # Update connection state
                connection.state = Connection.ESTABLISHED
                
                print(f"[{self.name}] Connection established: {connection.local_port} <- {connection.remote_ip}:{connection.remote_port}")
            
            # If no connection exists and this is not a SYN segment, discard
            if not connection:
                print(f"[{self.name}] No connection for port {segment.dst_port}, discarding")
                return
            
            # Handle FIN segment
            if segment.is_fin():
                print(f"[{self.name}] Received FIN, closing connection")
                
                # Send FIN-ACK segment
                fin_ack_segment = Segment(
                    connection.local_port,
                    connection.remote_port,
                    connection.seq_num,
                    segment.seq_num + 1,
                    Segment.FIN | Segment.ACK,
                    connection.window,
                    b''
                )
                
                # Increment sequence number
                connection.seq_num += 1
                
                # Send the segment down to the Network layer
                if self.lower_layer:
                    self.lower_layer.send_down(
                        fin_ack_segment.to_bytes(),
                        dst_ip=connection.remote_ip,
                        protocol=6  # TCP
                    )
                
                # Update connection state
                connection.state = Connection.CLOSED
                
                # Remove the connection from our list
                if connection.local_port in self.connections:
                    del self.connections[connection.local_port]
                
                return
            
            # Handle data segment
            if segment.data:
                # Check if the sequence number is what we expect
                if segment.seq_num == connection.expected_seq:
                    # Add the data to the receive buffer
                    connection.add_to_recv_buffer(segment.data)
                    
                    # Update the expected sequence number
                    connection.expected_seq = segment.seq_num + len(segment.data)
                    
                    # Send ACK segment
                    ack_segment = Segment(
                        connection.local_port,
                        connection.remote_port,
                        connection.seq_num,
                        connection.expected_seq,
                        Segment.ACK,
                        connection.window,
                        b''
                    )
                    
                    # Send the segment down to the Network layer
                    if self.lower_layer:
                        self.lower_layer.send_down(
                            ack_segment.to_bytes(),
                            dst_ip=connection.remote_ip,
                            protocol=6  # TCP
                        )
                    
                    # Send the data up to the Session layer
                    if self.upper_layer:
                        self.upper_layer.send_up(
                            data=connection.get_from_recv_buffer(),
                            local_port=connection.local_port,
                            remote_port=connection.remote_port,
                            remote_ip=connection.remote_ip
                        )
                else:
                    print(f"[{self.name}] Out-of-order segment, expected SEQ {connection.expected_seq}, got {segment.seq_num}")
                    
                    # Add to segments to acknowledge
                    connection.segments_to_ack.add(segment.seq_num)
                    
                    # Send duplicate ACK
                    dup_ack_segment = Segment(
                        connection.local_port,
                        connection.remote_port,
                        connection.seq_num,
                        connection.expected_seq,
                        Segment.ACK,
                        connection.window,
                        b''
                    )
                    
                    # Send the segment down to the Network layer
                    if self.lower_layer:
                        self.lower_layer.send_down(
                            dup_ack_segment.to_bytes(),
                            dst_ip=connection.remote_ip,
                            protocol=6  # TCP
                        )
        
        except Exception as e:
            print(f"[{self.name}] Error processing segment: {e}")
            return 