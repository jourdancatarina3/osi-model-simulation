"""
Network Layer Implementation.

The Network Layer is responsible for packet forwarding and routing.
It handles logical addressing (IP) and determines the path for data to travel.
"""
from typing import Any, Dict, Optional, Tuple, List
import struct

from osi import OSILayer
import utils


class Packet:
    """
    A network layer packet.
    
    Contains source and destination IP addresses, TTL, protocol, and payload data.
    """
    
    def __init__(self, src_ip: str, dst_ip: str, data: bytes, ttl: int = 64, protocol: int = 6):
        """
        Initialize a packet with source and destination IP addresses and data.
        
        Args:
            src_ip: Source IP address
            dst_ip: Destination IP address
            data: Payload data
            ttl: Time to live
            protocol: Protocol number (6 for TCP, 17 for UDP)
        """
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.ttl = ttl
        self.protocol = protocol
        self.data = data
    
    def to_bytes(self) -> bytes:
        """Convert the packet to bytes for transmission."""
        packet_dict = {
            'src_ip': self.src_ip,
            'dst_ip': self.dst_ip,
            'ttl': self.ttl,
            'protocol': self.protocol,
            'data': self.data.hex()
        }
        return utils.serialize_dict(packet_dict)
    
    @classmethod
    def from_bytes(cls, packet_bytes: bytes) -> 'Packet':
        """Create a packet from bytes received from the Data Link layer."""
        packet_dict = utils.deserialize_dict(packet_bytes)
        src_ip = packet_dict['src_ip']
        dst_ip = packet_dict['dst_ip']
        ttl = packet_dict['ttl']
        protocol = packet_dict['protocol']
        data = bytes.fromhex(packet_dict['data'])
        
        return cls(src_ip, dst_ip, data, ttl, protocol)


class RoutingTable:
    """A simple routing table for the Network layer."""
    
    def __init__(self):
        """Initialize an empty routing table."""
        self.routes = []
    
    def add_route(self, network: str, netmask: str, gateway: str, interface: str) -> None:
        """
        Add a route to the routing table.
        
        Args:
            network: Network address
            netmask: Network mask
            gateway: Gateway IP address
            interface: Network interface
        """
        self.routes.append({
            'network': network,
            'netmask': netmask,
            'gateway': gateway,
            'interface': interface
        })
    
    def get_route(self, dst_ip: str) -> Optional[Dict]:
        """
        Get the route for a destination IP address.
        
        Args:
            dst_ip: Destination IP address
            
        Returns:
            The route if found, None otherwise
        """
        # In a real implementation, we would check if the destination IP
        # matches any of our routes based on the network and netmask
        # For simplicity, we'll just return the first route
        return self.routes[0] if self.routes else None


class NetworkLayer(OSILayer):
    """
    Network Layer implementation.
    
    This layer handles packet routing and logical addressing (IP).
    """
    
    def __init__(self, ip_address: Optional[str] = None):
        """
        Initialize the Network Layer.
        
        Args:
            ip_address: The IP address of this node. If None, a random one is generated.
        """
        super().__init__("Network")
        self.ip_address = ip_address or utils.generate_ip_address()
        self.routing_table = RoutingTable()
        
        # Add a default route
        self.routing_table.add_route('0.0.0.0', '0.0.0.0', '192.168.1.1', 'eth0')
        
        # In a real implementation, we would have an ARP table to map IP to MAC
        self.destination_ip = None
    
    def set_destination_ip(self, ip_address: str) -> None:
        """Set the destination IP address."""
        self.destination_ip = ip_address
    
    def send_down(self, data: bytes, **kwargs) -> None:
        """
        Process data from the Transport layer and send it down to the Data Link layer.
        
        Args:
            data: The data to be packaged and sent
            **kwargs: Additional parameters, may include destination IP
        """
        dst_ip = kwargs.get('dst_ip', self.destination_ip)
        if not dst_ip:
            # In a real implementation, we would use DNS to resolve the hostname
            dst_ip = utils.generate_ip_address()
            print(f"[{self.name}] No destination IP provided, using generated: {dst_ip}")
        
        protocol = kwargs.get('protocol', 6)  # Default to TCP
        
        print(f"[{self.name}] Creating packet: {self.ip_address} -> {dst_ip}")
        
        # Create a packet with the data
        packet = Packet(self.ip_address, dst_ip, data, protocol=protocol)
        packet_bytes = packet.to_bytes()
        
        print(f"[{self.name}] Packet created, size: {len(packet_bytes)} bytes")
        
        # Get the route for the destination IP
        route = self.routing_table.get_route(dst_ip)
        if not route:
            print(f"[{self.name}] No route to {dst_ip}, discarding")
            return
        
        # In a real implementation, we would use ARP to resolve the MAC address
        # of the next hop (gateway or destination)
        # For simplicity, we'll just pass the packet down to the Data Link layer
        
        # Send the packet down to the Data Link layer
        if self.lower_layer:
            self.lower_layer.send_down(packet_bytes)
    
    def send_up(self, data: bytes, **kwargs) -> None:
        """
        Process data from the Data Link layer and send it up to the Transport layer.
        
        Args:
            data: The packaged data received from the Data Link layer
            **kwargs: Additional parameters
        """
        print(f"[{self.name}] Received packet, size: {len(data)} bytes")
        
        # Parse the packet
        try:
            packet = Packet.from_bytes(data)
            
            print(f"[{self.name}] Packet: {packet.src_ip} -> {packet.dst_ip} (TTL: {packet.ttl}, Protocol: {packet.protocol})")
            
            # Check if the packet is addressed to us
            if packet.dst_ip != self.ip_address:
                print(f"[{self.name}] Packet not addressed to us, would normally forward")
                # In a real implementation, we would decrement TTL and forward the packet
                # For simplicity, we'll just discard it
                return
            
            # Store the source IP for future responses
            if not self.destination_ip:
                self.destination_ip = packet.src_ip
                print(f"[{self.name}] Setting destination IP to {self.destination_ip}")
            
            # Send the data up to the Transport layer
            if self.upper_layer:
                self.upper_layer.send_up(
                    data=packet.data,
                    src_ip=packet.src_ip,
                    protocol=packet.protocol
                )
        
        except Exception as e:
            print(f"[{self.name}] Error processing packet: {e}")
            return 