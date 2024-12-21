from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Macro:
  height: int
  width: int
  elements: List[int]

@dataclass(frozen=True, order=True, eq=True)
class Position:
  x: int
  y: int

@dataclass
class Entity:
  name: str
  position: Position
  direction: Optional[int]

@dataclass
class Blueprint:
  label: str
  entities: List[Entity]
  description: Optional[str]
