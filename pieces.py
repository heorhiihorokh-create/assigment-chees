from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Dict

class BaseChessPiece:




    Color = Literal["WHITE", "BLACK"]


    @dataclass
    class Piece:
        name: str
        symbol: str
        color: Color
        position: str
        is_alive: bool = True

        def to_dict(self) -> Dict[str, object]:
            return {
                "name": self.name,
                "symbol": self.symbol,
                "color": self.color,
                "position": self.position,
                "is_alive": self.is_alive,
            }

        def __repr__(self) -> str:
            return f"{self.symbol}({self.color},{self.position})"
        
    class Pawn(Piece):
        def __init__(self, color: Color, position: str) -> None:
            super().__init__(name="Pawn", symbol="P", color=color, position=position)

    class Rook(Piece):
        def __init__(self, color: Color, position: str) -> None:
            super().__init__(name="Rook", symbol="R", color=color, position=position)