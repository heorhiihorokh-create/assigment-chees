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

    def setup_board(self) -> None:
        # Pawns
        for f in FILES:
            self.set_piece(f"{f}2", Pawn("WHITE", f"{f}2"))
            self.set_piece(f"{f}7", Pawn("BLACK", f"{f}7"))
  
        # Rooks
        self.set_piece("a1", Rook("WHITE", "a1"))
        self.set_piece("h1", Rook("WHITE", "h1"))
        self.set_piece("a8", Rook("BLACK", "a8"))
        self.set_piece("h8", Rook("BLACK", "h8"))

        # Knights
        self.set_piece("b1", Knight("WHITE", "b1"))
        self.set_piece("g1", Knight("WHITE", "g1"))
        self.set_piece("b8", Knight("BLACK", "b8"))
        self.set_piece("g8", Knight("BLACK", "g8"))

        # Bishops
        self.set_piece("c1", Bishop("WHITE", "c1"))
        self.set_piece("f1", Bishop("WHITE", "f1"))
        self.set_piece("c8", Bishop("BLACK", "c8"))
        self.set_piece("f8", Bishop("BLACK", "f8"))

        # Queens
        self.set_piece("d1", Queen("WHITE", "d1"))
        self.set_piece("d8", Queen("BLACK", "d8"))

        # Kings
        self.set_piece("e1", King("WHITE", "e1"))
        self.set_piece("e8", King("BLACK", "e8"))