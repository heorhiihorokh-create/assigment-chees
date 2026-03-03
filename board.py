from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
from pieces import Pawn, Rook, Knight, Bishop, Queen, King

FILES = "abcdefgh"
RANKS = "12345678"


def is_valid_square(square: str) -> bool:
    return isinstance(square, str) and len(square) == 2 and square[0] in FILES and square[1] in RANKS


@dataclass(frozen=True)
class Move:
    from_sq: str
    to_sq: str


class Board:
    def __init__(self) -> None:
        # a1..h8 -> piece or None
        self.squares: Dict[str, Optional[object]] = {f"{f}{r}": None for r in RANKS for f in FILES}

    def get_piece(self, square: str):
        if not is_valid_square(square):
            raise ValueError(f"Invalid square: {square}")
        return self.squares[square]

    def set_piece(self, square: str, piece) -> None:
        if not is_valid_square(square):
            raise ValueError(f"Invalid square: {square}")
        self.squares[square] = piece

    def print_board(self) -> None:
        for r in reversed(RANKS):
            row = []
            for f in FILES:
                sq = f"{f}{r}"
                p = self.squares[sq]
                if p is None:
                    row.append(".")
                else:
                    sym = getattr(p, "symbol", "X")
                    color = getattr(p, "color", "WHITE")
                    row.append(sym.upper() if color == "WHITE" else sym.lower())
            print(" ".join(row), f"  {r}")
        print(" ".join(FILES))