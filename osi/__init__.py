"""
OSI Model Simulation Package.
This package contains implementations of all seven layers of the OSI model.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class OSILayer(ABC):
    """Base class for all OSI layers."""
    
    def __init__(self, name: str):
        """Initialize the OSI layer with a name."""
        self.name = name
        self.lower_layer = None
        self.upper_layer = None
    
    def set_lower_layer(self, layer: 'OSILayer') -> None:
        """Set the lower layer in the OSI stack."""
        self.lower_layer = layer
    
    def set_upper_layer(self, layer: 'OSILayer') -> None:
        """Set the upper layer in the OSI stack."""
        self.upper_layer = layer
    
    @abstractmethod
    def send_down(self, data: Any, **kwargs) -> None:
        """
        Process data and send it down to the lower layer.
        This method should be implemented by each specific layer.
        """
        pass
    
    @abstractmethod
    def send_up(self, data: Any, **kwargs) -> None:
        """
        Process data and send it up to the upper layer.
        This method should be implemented by each specific layer.
        """
        pass
    
    def __str__(self) -> str:
        """String representation of the layer."""
        return f"{self.name} Layer" 