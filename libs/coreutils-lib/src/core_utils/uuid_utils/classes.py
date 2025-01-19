from __future__ import annotations

from dataclasses import dataclass

@dataclass
class UUIDLength:
    """Simple dataclass to store UUID string lengths.

    When setting the length of a string, you can use something like UUID().standard to pass these pre-defined values.

    Args:
        standard (int): The number of characters expected in a standard UUID string
        hex (int): The number of characters expeceted in a UUID hex string

    """

    standard: int = 36
    hex: int = 32