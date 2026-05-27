from pgui.utils.utils_typing import ColorType, RGB_COLOR, Number
from numpy.typing import NDArray
from typing import Tuple

import numpy

def hex_to_rbg(color: ColorType) -> RGB_COLOR:
    """Convert HEX / RGB -> RGB"""
    if isinstance(color, Tuple): return color

    color = color.strip()

    if color.startswith("#"): color = color[1:]

    if len(color) == 6:
        return (
            int(color[0:2], 16),
            int(color[2:4], 16),
            int(color[4:6], 16)
        )
    
    raise ValueError("Invalid color format, the color must be ColorType")

def to_array(value: Tuple[Number]) -> NDArray:
    """Convert Tuple[int] -> NDArray"""
    return numpy.array(value, dtype=numpy.int32)


