"""
Utility functions for the OSI model simulation.
"""
import json
import random
import struct
import socket
import hashlib
from typing import Dict, List, Tuple, Any, Union


def generate_mac_address() -> str:
    """Generate a random MAC address."""
    return ':'.join([f'{random.randint(0, 255):02x}' for _ in range(6)])


def generate_ip_address() -> str:
    """Generate a random IP address."""
    return '.'.join([str(random.randint(0, 255)) for _ in range(4)])


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