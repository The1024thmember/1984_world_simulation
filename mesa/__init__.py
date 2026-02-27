"""Minimal Mesa-like stubs to run this simulation without external deps."""

from .model import Model
from .agent import Agent
from .datacollector import DataCollector
from . import space
from . import time

__all__ = ["Model", "Agent", "DataCollector", "space", "time"]
