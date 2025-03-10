"""
Utility functions for the OSI model simulation.
"""
import json
import random
import struct
import socket
import hashlib
import uuid
from typing import Dict, List, Tuple, Any, Union


def generate_mac_address() -> str:
    """Generate a random MAC address."""
    return ':'.join([f'{random.randint(0, 255):02x}' for _ in range(6)])


def generate_ip_address() -> str:
    """Generate a random IP address."""
    return '.'.join([str(random.randint(0, 255)) for _ in range(4)])


def get_system_mac_address() -> str:
    """Get the actual MAC address of the system."""
    try:
        # Get the MAC address using uuid module
        node = uuid.getnode()
        # Check if the node value is valid (if the 8th bit is set, it's invalid)
        if (node >> 8) & 0x1:
            print(f"[DEBUG] Invalid MAC address detected from uuid.getnode(): {node}")
            # Try to get MAC from ifconfig on macOS/Linux
            import subprocess
            try:
                result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'ether' in line:
                        mac = line.strip().split('ether')[1].strip()
                        print(f"[DEBUG] MAC address from ifconfig: {mac}")
                        return mac
            except Exception as e:
                print(f"[DEBUG] Error getting MAC from ifconfig: {e}")
                pass
            
            # Default MAC address as last resort
            return "56:b3:85:ec:00:12"
        
        # Convert the node value to a MAC address
        mac = ':'.join(['{:02x}'.format((node >> ele) & 0xff) for ele in range(0, 48, 8)][::-1])
        print(f"[DEBUG] MAC address from uuid.getnode(): {mac}")
        return mac
    except Exception as e:
        print(f"[DEBUG] Error in get_system_mac_address: {e}")
        # Default MAC address in case we can't get the system's
        return "56:b3:85:ec:00:12"  # Using the first MAC from ifconfig output


def get_system_ip_address() -> str:
    """Get the actual IP address of the system."""
    try:
        # Try to get the actual IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # This doesn't actually establish a connection
        s.connect(("8.8.8.8", 80))  # Google's DNS server
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        # If that fails, try to get the hostname
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            # If that also fails, return the default
            return "172.16.18.94"  # Using the IP from ifconfig output


def calculate_checksum(data: bytes) -> bytes:
    """Calculate a simple checksum for data integrity verification."""
    return hashlib.md5(data).digest()


def verify_checksum(data: bytes, checksum: bytes) -> bool:
    """Verify the checksum of received data."""
    return hashlib.md5(data).digest() == checksum


def bytes_to_bits(data: bytes) -> str:
    """Convert bytes to a string of bits."""
    return ''.join(format(byte, '08b') for byte in data)


def bits_to_bytes(bits: str) -> bytes:
    """Convert a string of bits to bytes."""
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))


def serialize_dict(data: Dict) -> bytes:
    """Serialize a dictionary to bytes."""
    return json.dumps(data).encode('utf-8')


def deserialize_dict(data: bytes) -> Dict:
    """Deserialize bytes to a dictionary."""
    return json.loads(data.decode('utf-8'))


def simple_encrypt(data: bytes, key: int = 42) -> bytes:
    """Simple XOR encryption for demonstration purposes."""
    return bytes(b ^ key for b in data)


def simple_decrypt(data: bytes, key: int = 42) -> bytes:
    """Simple XOR decryption for demonstration purposes."""
    return bytes(b ^ key for b in data)


def compress(data: bytes) -> bytes:
    """
    Very simple "compression" for demonstration purposes.
    In a real implementation, you would use a proper compression algorithm.
    """
    # This is just a placeholder - not real compression
    return b'COMPRESSED:' + data


def decompress(data: bytes) -> bytes:
    """
    Very simple "decompression" for demonstration purposes.
    """
    # This is just a placeholder - not real decompression
    if data.startswith(b'COMPRESSED:'):
        return data[11:]
    return data 