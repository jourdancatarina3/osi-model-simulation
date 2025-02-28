"""
Session Layer Implementation.

The Session Layer is responsible for establishing, managing, and terminating connections.
It handles session setup, coordination, and synchronization between applications.
"""
from typing import Any, Dict, Optional, Tuple, List, Set
import time
import uuid

from osi import OSILayer
import utils


class Session:
    """
    A session layer session.
    
    Represents a communication session between two applications.
    """
    
    # Session states
    CLOSED = 0
    CONNECTING = 1
    ESTABLISHED = 2
    DISCONNECTING = 3
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize a session.
        
        Args:
            session_id: The session ID. If None, a random one is generated.
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.state = self.CLOSED
        self.creation_time = time.time()
        self.last_activity_time = self.creation_time
        self.data = {}  # Session data store
    
    def is_established(self) -> bool:
        """Check if the session is established."""
        return self.state == self.ESTABLISHED
    
    def update_activity(self) -> None:
        """Update the last activity time."""
        self.last_activity_time = time.time()
    
    def get_duration(self) -> float:
        """Get the session duration in seconds."""
        return time.time() - self.creation_time
    
    def get_idle_time(self) -> float:
        """Get the idle time in seconds."""
        return time.time() - self.last_activity_time
    
    def set_data(self, key: str, value: Any) -> None:
        """Set session data."""
        self.data[key] = value
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get session data."""
        return self.data.get(key, default)


class SessionMessage:
    """
    A session layer message.
    
    Contains session control information and payload data.
    """
    
    # Message types
    CONNECT = 1
    CONNECT_ACK = 2
    DATA = 3
    DISCONNECT = 4
    DISCONNECT_ACK = 5
    KEEPALIVE = 6
    
    def __init__(self, msg_type: int, session_id: str, data: bytes = b''):
        """
        Initialize a session message.
        
        Args:
            msg_type: The message type
            session_id: The session ID
            data: The payload data
        """
        self.msg_type = msg_type
        self.session_id = session_id
        self.data = data
        self.timestamp = time.time()
    
    def to_bytes(self) -> bytes:
        """Convert the message to bytes for transmission."""
        message_dict = {
            'msg_type': self.msg_type,
            'session_id': self.session_id,
            'timestamp': self.timestamp,
            'data': self.data.hex()
        }
        return utils.serialize_dict(message_dict)
    
    @classmethod
    def from_bytes(cls, message_bytes: bytes) -> 'SessionMessage':
        """Create a message from bytes received from the Transport layer."""
        message_dict = utils.deserialize_dict(message_bytes)
        msg_type = message_dict['msg_type']
        session_id = message_dict['session_id']
        data = bytes.fromhex(message_dict['data'])
        
        message = cls(msg_type, session_id, data)
        message.timestamp = message_dict['timestamp']
        return message
    
    def is_connect(self) -> bool:
        """Check if this is a CONNECT message."""
        return self.msg_type == self.CONNECT
    
    def is_connect_ack(self) -> bool:
        """Check if this is a CONNECT_ACK message."""
        return self.msg_type == self.CONNECT_ACK
    
    def is_data(self) -> bool:
        """Check if this is a DATA message."""
        return self.msg_type == self.DATA
    
    def is_disconnect(self) -> bool:
        """Check if this is a DISCONNECT message."""
        return self.msg_type == self.DISCONNECT
    
    def is_disconnect_ack(self) -> bool:
        """Check if this is a DISCONNECT_ACK message."""
        return self.msg_type == self.DISCONNECT_ACK
    
    def is_keepalive(self) -> bool:
        """Check if this is a KEEPALIVE message."""
        return self.msg_type == self.KEEPALIVE


class SessionLayer(OSILayer):
    """
    Session Layer implementation.
    
    This layer handles session establishment, management, and termination.
    """
    
    def __init__(self):
        """Initialize the Session Layer."""
        super().__init__("Session")
        self.sessions: Dict[str, Session] = {}
        self.local_port = 80  # Default port for HTTP
        self.remote_port = None
        self.remote_ip = None
    
    def create_session(self) -> Session:
        """
        Create a new session.
        
        Returns:
            The new session
        """
        session = Session()
        self.sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.
        
        Args:
            session_id: The session ID
            
        Returns:
            The session if found, None otherwise
        """
        return self.sessions.get(session_id)
    
    def establish_session(self, remote_ip: str, remote_port: int) -> Session:
        """
        Establish a session with a remote host.
        
        Args:
            remote_ip: Remote IP address
            remote_port: Remote port number
            
        Returns:
            The established session
        """
        # Create a new session
        session = self.create_session()
        session.state = Session.CONNECTING
        
        # Store remote information
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        
        print(f"[{self.name}] Establishing session {session.session_id} with {remote_ip}:{remote_port}")
        
        # Create a CONNECT message
        connect_message = SessionMessage(
            SessionMessage.CONNECT,
            session.session_id
        )
        
        # Send the message down to the Transport layer
        if self.lower_layer:
            self.lower_layer.send_down(
                connect_message.to_bytes(),
                remote_ip=remote_ip,
                remote_port=remote_port,
                local_port=self.local_port
            )
        
        # In a real implementation, we would wait for the CONNECT_ACK response
        # For simplicity, we'll just assume the session is established
        session.state = Session.ESTABLISHED
        
        return session
    
    def accept_session(self, session_id: str, remote_ip: str, remote_port: int) -> Session:
        """
        Accept a session from a remote host.
        
        Args:
            session_id: The session ID
            remote_ip: Remote IP address
            remote_port: Remote port number
            
        Returns:
            The accepted session
        """
        # Create a new session with the provided ID
        session = Session(session_id)
        session.state = Session.ESTABLISHED
        self.sessions[session_id] = session
        
        # Store remote information
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        
        print(f"[{self.name}] Accepted session {session_id} from {remote_ip}:{remote_port}")
        
        # Create a CONNECT_ACK message
        connect_ack_message = SessionMessage(
            SessionMessage.CONNECT_ACK,
            session_id
        )
        
        # Send the message down to the Transport layer
        if self.lower_layer:
            self.lower_layer.send_down(
                connect_ack_message.to_bytes(),
                remote_ip=remote_ip,
                remote_port=remote_port,
                local_port=self.local_port
            )
        
        return session
    
    def send_data(self, session: Session, data: bytes) -> None:
        """
        Send data over a session.
        
        Args:
            session: The session to send data over
            data: The data to send
        """
        if not session.is_established():
            print(f"[{self.name}] Cannot send data, session not established")
            return
        
        print(f"[{self.name}] Sending {len(data)} bytes over session {session.session_id}")
        
        # Update session activity
        session.update_activity()
        
        # Create a DATA message
        data_message = SessionMessage(
            SessionMessage.DATA,
            session.session_id,
            data
        )
        
        # Send the message down to the Transport layer
        if self.lower_layer:
            self.lower_layer.send_down(
                data_message.to_bytes(),
                remote_ip=self.remote_ip,
                remote_port=self.remote_port,
                local_port=self.local_port
            )
    
    def close_session(self, session: Session) -> None:
        """
        Close a session.
        
        Args:
            session: The session to close
        """
        if session.state == Session.CLOSED:
            print(f"[{self.name}] Session already closed")
            return
        
        print(f"[{self.name}] Closing session {session.session_id}")
        
        # Update session state
        session.state = Session.DISCONNECTING
        
        # Create a DISCONNECT message
        disconnect_message = SessionMessage(
            SessionMessage.DISCONNECT,
            session.session_id
        )
        
        # Send the message down to the Transport layer
        if self.lower_layer:
            self.lower_layer.send_down(
                disconnect_message.to_bytes(),
                remote_ip=self.remote_ip,
                remote_port=self.remote_port,
                local_port=self.local_port
            )
        
        # In a real implementation, we would wait for the DISCONNECT_ACK response
        # For simplicity, we'll just assume the session is closed
        session.state = Session.CLOSED
        
        # Remove the session from our list
        if session.session_id in self.sessions:
            del self.sessions[session.session_id]
    
    def send_down(self, data: bytes, **kwargs) -> None:
        """
        Process data from the Presentation layer and send it down to the Transport layer.
        
        Args:
            data: The data to be sent
            **kwargs: Additional parameters, may include session information
        """
        session_id = kwargs.get('session_id')
        
        # Get or create the session
        session = None
        if session_id:
            session = self.get_session(session_id)
        
        if not session:
            # If no session exists, create one
            remote_ip = kwargs.get('remote_ip')
            remote_port = kwargs.get('remote_port')
            
            if not remote_ip or not remote_port:
                print(f"[{self.name}] No remote information provided, cannot establish session")
                return
            
            session = self.establish_session(remote_ip, remote_port)
        
        # Send the data over the session
        self.send_data(session, data)
    
    def send_up(self, data: bytes, **kwargs) -> None:
        """
        Process data from the Transport layer and send it up to the Presentation layer.
        
        Args:
            data: The data received from the Transport layer
            **kwargs: Additional parameters
        """
        local_port = kwargs.get('local_port')
        remote_port = kwargs.get('remote_port')
        remote_ip = kwargs.get('remote_ip')
        
        print(f"[{self.name}] Received message, size: {len(data)} bytes")
        
        # Parse the message
        try:
            message = SessionMessage.from_bytes(data)
            
            print(f"[{self.name}] Message: Type={message.msg_type}, Session={message.session_id}")
            
            # Store remote information if not already set
            if not self.remote_ip:
                self.remote_ip = remote_ip
            if not self.remote_port:
                self.remote_port = remote_port
            
            # Handle CONNECT message
            if message.is_connect():
                print(f"[{self.name}] Received CONNECT request")
                
                # Accept the session
                session = self.accept_session(message.session_id, remote_ip, remote_port)
                return
            
            # Handle CONNECT_ACK message
            if message.is_connect_ack():
                print(f"[{self.name}] Received CONNECT_ACK")
                
                # Get the session
                session = self.get_session(message.session_id)
                if not session:
                    print(f"[{self.name}] No session found for ID {message.session_id}")
                    return
                
                # Update session state
                session.state = Session.ESTABLISHED
                return
            
            # Handle DISCONNECT message
            if message.is_disconnect():
                print(f"[{self.name}] Received DISCONNECT request")
                
                # Get the session
                session = self.get_session(message.session_id)
                if not session:
                    print(f"[{self.name}] No session found for ID {message.session_id}")
                    return
                
                # Update session state
                session.state = Session.CLOSED
                
                # Send DISCONNECT_ACK
                disconnect_ack_message = SessionMessage(
                    SessionMessage.DISCONNECT_ACK,
                    message.session_id
                )
                
                # Send the message down to the Transport layer
                if self.lower_layer:
                    self.lower_layer.send_down(
                        disconnect_ack_message.to_bytes(),
                        remote_ip=remote_ip,
                        remote_port=remote_port,
                        local_port=local_port
                    )
                
                # Remove the session from our list
                if message.session_id in self.sessions:
                    del self.sessions[message.session_id]
                
                return
            
            # Handle DISCONNECT_ACK message
            if message.is_disconnect_ack():
                print(f"[{self.name}] Received DISCONNECT_ACK")
                
                # Remove the session from our list
                if message.session_id in self.sessions:
                    del self.sessions[message.session_id]
                
                return
            
            # Handle KEEPALIVE message
            if message.is_keepalive():
                print(f"[{self.name}] Received KEEPALIVE")
                
                # Get the session
                session = self.get_session(message.session_id)
                if not session:
                    print(f"[{self.name}] No session found for ID {message.session_id}")
                    return
                
                # Update session activity
                session.update_activity()
                return
            
            # Handle DATA message
            if message.is_data():
                # Get the session
                session = self.get_session(message.session_id)
                if not session:
                    print(f"[{self.name}] No session found for ID {message.session_id}")
                    return
                
                # Check if the session is established
                if not session.is_established():
                    print(f"[{self.name}] Session not established, discarding data")
                    return
                
                # Update session activity
                session.update_activity()
                
                print(f"[{self.name}] Received {len(message.data)} bytes of data")
                
                # Send the data up to the Presentation layer
                if self.upper_layer:
                    self.upper_layer.send_up(
                        data=message.data,
                        session_id=message.session_id
                    )
        
        except Exception as e:
            print(f"[{self.name}] Error processing message: {e}")
            return 