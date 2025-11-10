from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ShapeParameter:
    key: str
    label: str
    value: float
    minimum: float = 0.0
    maximum: float = 1000.0


@dataclass
class CutShape:
    name: str
    kind: str
    parameters: List[ShapeParameter] = field(default_factory=list)


@dataclass
class CutProgram:
    title: str
    shapes: List[CutShape] = field(default_factory=list)
