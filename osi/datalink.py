"""
Data Link Layer Implementation.

The Data Link Layer is responsible for node-to-node data transfer.
It handles framing, physical addressing (MAC), and error detection.
"""
from typing import Any, Dict, Optional, Tuple
import struct

from osi import OSILayer
import utils


class Frame:
    """
    A data link layer frame.
    
    Contains source and destination MAC addresses, payload data, and a checksum.
    """
    
    def __init__(self, src_mac: str, dst_mac: str, data: bytes):
        """
        Initialize a frame with source and destination MAC addresses and data.
        
        Args:
            src_mac: Source MAC address
            dst_mac: Destination MAC address
            data: Payload data
        """
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.data = data
        self.checksum = utils.calculate_checksum(data)
    
    def to_bytes(self) -> bytes:
        """Convert the frame to bytes for transmission."""
        # Format: src_mac|dst_mac|checksum_length|checksum|data_length|data
        frame_dict = {
            'src_mac': self.src_mac,
            'dst_mac': self.dst_mac,
            'checksum': self.checksum.hex(),
            'data': self.data.hex()
        }
        return utils.serialize_dict(frame_dict)
    
    @classmethod
    def from_bytes(cls, frame_bytes: bytes) -> 'Frame':
        """Create a frame from bytes received from the physical layer."""
        frame_dict = utils.deserialize_dict(frame_bytes)
        src_mac = frame_dict['src_mac']
        dst_mac = frame_dict['dst_mac']
        checksum = bytes.fromhex(frame_dict['checksum'])
        data = bytes.fromhex(frame_dict['data'])
        
        frame = cls(src_mac, dst_mac, data)
        frame.checksum = checksum
        return frame
    
    def is_valid(self) -> bool:
        """Check if the frame's checksum is valid."""
        return utils.verify_checksum(self.data, self.checksum)


class DataLinkLayer(OSILayer):
    """
    Data Link Layer implementation.
    
    This layer handles framing, MAC addressing, and error detection.
    """
    
    def __init__(self, mac_address: Optional[str] = None):
        """
        Initialize the Data Link Layer.
        
        Args:
            mac_address: The MAC address of this node. If None, a random one is generated.
        """
        super().__init__("Data Link")
        self.mac_address = mac_address or utils.generate_mac_address()
        # In a real implementation, we would have an ARP table to map IP to MAC
        self.destination_mac = None
    
    def set_destination_mac(self, mac_address: str) -> None:
        """Set the destination MAC address."""
        self.destination_mac = mac_address
    
    def send_down(self, data: bytes, **kwargs) -> None:
        """
        Process data from the Network layer and send it down to the Physical layer.
        
        Args:
            data: The data to be framed and sent
            **kwargs: Additional parameters, may include destination MAC
        """
        dst_mac = kwargs.get('dst_mac', self.destination_mac)
        if not dst_mac:
            # In a real implementation, we would use ARP to resolve the MAC
            dst_mac = utils.generate_mac_address()
            print(f"[{self.name}] No destination MAC provided, using generated: {dst_mac}")
            # Store this MAC for future use
            self.destination_mac = dst_mac
        
        print(f"[{self.name}] Creating frame: {self.mac_address} -> {dst_mac}")
        
        # Create a frame with the data
        frame = Frame(self.mac_address, dst_mac, data)
        frame_bytes = frame.to_bytes()
        
        print(f"[{self.name}] Frame created, size: {len(frame_bytes)} bytes")
        
        # Send the frame down to the Physical layer
        if self.lower_layer:
            self.lower_layer.send_down(frame_bytes)
    
    def send_up(self, data: bytes, **kwargs) -> None:
        """
        Process data from the Physical layer and send it up to the Network layer.
        
        Args:
            data: The framed data received from the Physical layer
            **kwargs: Additional parameters
        """
        print(f"[{self.name}] Received frame, size: {len(data)} bytes")
        
        # Parse the frame
        try:
            frame = Frame.from_bytes(data)
            
            print(f"[{self.name}] Frame: {frame.src_mac} -> {frame.dst_mac}")
            
            # Check if the frame is valid
            if not frame.is_valid():
                print(f"[{self.name}] Invalid frame checksum, discarding")
                return
            
            # Check if the frame is addressed to us or is a broadcast
            # For simulation purposes, we'll accept all frames to ensure communication works
            # In a real implementation, we would strictly check the MAC address
            if frame.dst_mac != self.mac_address and frame.dst_mac != "ff:ff:ff:ff:ff:ff":
                print(f"[{self.name}] Frame not addressed to us ({self.mac_address}), but accepting for simulation")
                # Store the source MAC for future responses
                if not self.destination_mac:
                    self.destination_mac = frame.src_mac
                    print(f"[{self.name}] Setting destination MAC to {self.destination_mac}")
                
                # Send the data up to the Network layer
                if self.upper_layer:
                    self.upper_layer.send_up(data=frame.data, src_mac=frame.src_mac)
                return
            
            # Store the source MAC for future responses
            if not self.destination_mac:
                self.destination_mac = frame.src_mac
                print(f"[{self.name}] Setting destination MAC to {self.destination_mac}")
            
            # Send the data up to the Network layer
            if self.upper_layer:
                self.upper_layer.send_up(data=frame.data, src_mac=frame.src_mac)
        
        except Exception as e:
            print(f"[{self.name}] Error processing frame: {e}")
            return 