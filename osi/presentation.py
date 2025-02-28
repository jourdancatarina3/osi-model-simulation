"""
Presentation Layer Implementation.

The Presentation Layer is responsible for data translation, encryption, and compression.
It ensures that data from the application layer is properly formatted for transmission.
"""
from typing import Any, Dict, Optional, Tuple, List
import json
import base64

from osi import OSILayer
import utils


class PresentationMessage:
    """
    A presentation layer message.
    
    Contains data format, encryption, and compression information.
    """
    
    # Data formats
    TEXT = 1
    BINARY = 2
    JSON = 3
    
    # Encryption types
    NONE = 0
    XOR = 1
    
    # Compression types
    NO_COMPRESSION = 0
    SIMPLE_COMPRESSION = 1
    
    def __init__(
        self,
        data: bytes,
        data_format: int = TEXT,
        encryption: int = NONE,
        compression: int = NO_COMPRESSION,
        encryption_key: Optional[int] = None
    ):
        """
        Initialize a presentation message.
        
        Args:
            data: The payload data
            data_format: The data format
            encryption: The encryption type
            compression: The compression type
            encryption_key: The encryption key (if applicable)
        """
        self.data = data
        self.data_format = data_format
        self.encryption = encryption
        self.compression = compression
        self.encryption_key = encryption_key
    
    def to_bytes(self) -> bytes:
        """Convert the message to bytes for transmission."""
        message_dict = {
            'data_format': self.data_format,
            'encryption': self.encryption,
            'compression': self.compression,
            'data': self.data.hex()
        }
        
        if self.encryption_key is not None:
            message_dict['encryption_key'] = self.encryption_key
        
        return utils.serialize_dict(message_dict)
    
    @classmethod
    def from_bytes(cls, message_bytes: bytes) -> 'PresentationMessage':
        """Create a message from bytes received from the Session layer."""
        message_dict = utils.deserialize_dict(message_bytes)
        data_format = message_dict['data_format']
        encryption = message_dict['encryption']
        compression = message_dict['compression']
        data = bytes.fromhex(message_dict['data'])
        encryption_key = message_dict.get('encryption_key')
        
        return cls(data, data_format, encryption, compression, encryption_key)


class PresentationLayer(OSILayer):
    """
    Presentation Layer implementation.
    
    This layer handles data translation, encryption, and compression.
    """
    
    def __init__(self):
        """Initialize the Presentation Layer."""
        super().__init__("Presentation")
        self.default_encryption = PresentationMessage.NONE
        self.default_compression = PresentationMessage.NO_COMPRESSION
        self.encryption_key = 42  # Default encryption key
    
    def set_encryption(self, encryption_type: int, key: Optional[int] = None) -> None:
        """
        Set the default encryption type and key.
        
        Args:
            encryption_type: The encryption type
            key: The encryption key (if applicable)
        """
        self.default_encryption = encryption_type
        if key is not None:
            self.encryption_key = key
    
    def set_compression(self, compression_type: int) -> None:
        """
        Set the default compression type.
        
        Args:
            compression_type: The compression type
        """
        self.default_compression = compression_type
    
    def encrypt(self, data: bytes, encryption_type: int, key: Optional[int] = None) -> bytes:
        """
        Encrypt data.
        
        Args:
            data: The data to encrypt
            encryption_type: The encryption type
            key: The encryption key (if applicable)
            
        Returns:
            The encrypted data
        """
        if encryption_type == PresentationMessage.NONE:
            return data
        
        if encryption_type == PresentationMessage.XOR:
            return utils.simple_encrypt(data, key or self.encryption_key)
        
        # Unsupported encryption type
        print(f"[{self.name}] Unsupported encryption type: {encryption_type}")
        return data
    
    def decrypt(self, data: bytes, encryption_type: int, key: Optional[int] = None) -> bytes:
        """
        Decrypt data.
        
        Args:
            data: The data to decrypt
            encryption_type: The encryption type
            key: The encryption key (if applicable)
            
        Returns:
            The decrypted data
        """
        if encryption_type == PresentationMessage.NONE:
            return data
        
        if encryption_type == PresentationMessage.XOR:
            return utils.simple_decrypt(data, key or self.encryption_key)
        
        # Unsupported encryption type
        print(f"[{self.name}] Unsupported encryption type: {encryption_type}")
        return data
    
    def compress(self, data: bytes, compression_type: int) -> bytes:
        """
        Compress data.
        
        Args:
            data: The data to compress
            compression_type: The compression type
            
        Returns:
            The compressed data
        """
        if compression_type == PresentationMessage.NO_COMPRESSION:
            return data
        
        if compression_type == PresentationMessage.SIMPLE_COMPRESSION:
            return utils.compress(data)
        
        # Unsupported compression type
        print(f"[{self.name}] Unsupported compression type: {compression_type}")
        return data
    
    def decompress(self, data: bytes, compression_type: int) -> bytes:
        """
        Decompress data.
        
        Args:
            data: The data to decompress
            compression_type: The compression type
            
        Returns:
            The decompressed data
        """
        if compression_type == PresentationMessage.NO_COMPRESSION:
            return data
        
        if compression_type == PresentationMessage.SIMPLE_COMPRESSION:
            return utils.decompress(data)
        
        # Unsupported compression type
        print(f"[{self.name}] Unsupported compression type: {compression_type}")
        return data
    
    def format_data(self, data: Any, data_format: int) -> bytes:
        """
        Format data for transmission.
        
        Args:
            data: The data to format
            data_format: The data format
            
        Returns:
            The formatted data as bytes
        """
        if data_format == PresentationMessage.TEXT:
            if isinstance(data, str):
                return data.encode('utf-8')
            elif isinstance(data, bytes):
                return data
            else:
                return str(data).encode('utf-8')
        
        elif data_format == PresentationMessage.BINARY:
            if isinstance(data, bytes):
                return data
            elif isinstance(data, str):
                return data.encode('utf-8')
            else:
                return str(data).encode('utf-8')
        
        elif data_format == PresentationMessage.JSON:
            if isinstance(data, (dict, list, tuple)):
                return json.dumps(data).encode('utf-8')
            else:
                return json.dumps({"data": data}).encode('utf-8')
        
        # Unsupported data format
        print(f"[{self.name}] Unsupported data format: {data_format}")
        return str(data).encode('utf-8')
    
    def parse_data(self, data: bytes, data_format: int) -> Any:
        """
        Parse data received from the network.
        
        Args:
            data: The data to parse
            data_format: The data format
            
        Returns:
            The parsed data
        """
        if data_format == PresentationMessage.TEXT:
            return data.decode('utf-8')
        
        elif data_format == PresentationMessage.BINARY:
            return data
        
        elif data_format == PresentationMessage.JSON:
            return json.loads(data.decode('utf-8'))
        
        # Unsupported data format
        print(f"[{self.name}] Unsupported data format: {data_format}")
        return data
    
    def send_down(self, data: Any, **kwargs) -> None:
        """
        Process data from the Application layer and send it down to the Session layer.
        
        Args:
            data: The data to be formatted, encrypted, compressed, and sent
            **kwargs: Additional parameters
        """
        data_format = kwargs.get('data_format', PresentationMessage.TEXT)
        encryption = kwargs.get('encryption', self.default_encryption)
        compression = kwargs.get('compression', self.default_compression)
        encryption_key = kwargs.get('encryption_key', self.encryption_key)
        session_id = kwargs.get('session_id')
        remote_ip = kwargs.get('remote_ip')
        remote_port = kwargs.get('remote_port')
        
        print(f"[{self.name}] Processing data for transmission")
        
        # Format the data
        formatted_data = self.format_data(data, data_format)
        
        # Encrypt the data
        encrypted_data = self.encrypt(formatted_data, encryption, encryption_key)
        
        # Compress the data
        compressed_data = self.compress(encrypted_data, compression)
        
        # Create a presentation message
        message = PresentationMessage(
            compressed_data,
            data_format,
            encryption,
            compression,
            encryption_key if encryption != PresentationMessage.NONE else None
        )
        
        # Send the message down to the Session layer
        if self.lower_layer:
            self.lower_layer.send_down(
                message.to_bytes(),
                session_id=session_id,
                remote_ip=remote_ip,
                remote_port=remote_port
            )
    
    def send_up(self, data: bytes, **kwargs) -> None:
        """
        Process data from the Session layer and send it up to the Application layer.
        
        Args:
            data: The data received from the Session layer
            **kwargs: Additional parameters
        """
        session_id = kwargs.get('session_id')
        
        print(f"[{self.name}] Processing received data")
        
        # Parse the message
        try:
            message = PresentationMessage.from_bytes(data)
            
            # Decompress the data
            decompressed_data = self.decompress(message.data, message.compression)
            
            # Decrypt the data
            decrypted_data = self.decrypt(
                decompressed_data,
                message.encryption,
                message.encryption_key
            )
            
            # Parse the data
            parsed_data = self.parse_data(decrypted_data, message.data_format)
            
            # Send the data up to the Application layer
            if self.upper_layer:
                self.upper_layer.send_up(
                    data=parsed_data,
                    data_format=message.data_format,
                    session_id=session_id
                )
        
        except Exception as e:
            print(f"[{self.name}] Error processing message: {e}")
            return 