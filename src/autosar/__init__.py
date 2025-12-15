"""
AUTOSAR ECUC Configurator

A Python toolkit for working with AUTOSAR ECU configurations,
CAN/LIN networks, and related automotive communication protocols.
"""

__version__ = "0.1.0"
__author__ = "ECUC Configurator Team"

from . import model
from . import loader
from . import generator
from . import service

__all__ = ["model", "loader", "generator", "service"]
