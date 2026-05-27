from __future__ import annotations
from typing import Tuple, TypeAlias, TYPE_CHECKING

if TYPE_CHECKING:
    from models import CharacterBody, StaticBody

HEX_COLOR = str
RGB_COLOR = Tuple[int,int,int]
ColorType: TypeAlias = "HEX_COLOR | RGB_COLOR"

Vec2 = Tuple[int,int]
Number: TypeAlias = "int | float"

Model: TypeAlias = "CharacterBody | StaticBody"
