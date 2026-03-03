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

    def move_piece(self, from_sq: str, to_sq: str) -> None:
        if not is_valid_square(from_sq) or not is_valid_square(to_sq):
            raise ValueError("Invalid square")

        if from_sq == to_sq:
            raise ValueError("Cannot move to same square")

        piece = self.get_piece(from_sq)
        if piece is None:
            raise ValueError("No piece on source square")

        target_piece = self.get_piece(to_sq)

        if target_piece is not None and target_piece.color == piece.color:
            raise ValueError("Cannot capture own piece")

        fx, fy = square_to_xy(from_sq)
        tx, ty = square_to_xy(to_sq)

        dx = tx - fx
        dy = ty - fy

        # =========================
        # PAWN
        # =========================
        if piece.symbol == "P":
            direction = 1 if piece.color == "WHITE" else -1
            start_rank = 1 if piece.color == "WHITE" else 6

            # forward
            if dx == 0:
                if dy == direction:
                    if target_piece is not None:
                        raise ValueError("Pawn forward square occupied")

                elif dy == 2 * direction and fy == start_rank:
                    intermediate = xy_to_square(fx, fy + direction)
                    if target_piece is not None or self.get_piece(intermediate) is not None:
                        raise ValueError("Pawn path blocked")
                else:
                    raise ValueError("Illegal pawn move")

            # diagonal capture
            elif abs(dx) == 1 and dy == direction:
                if target_piece is None:
                    raise ValueError("Pawn captures diagonally only")
            else:
                raise ValueError("Illegal pawn move")

        # =========================
        # KNIGHT
        # =========================
        elif piece.symbol == "N":
            if not ((abs(dx) == 2 and abs(dy) == 1) or (abs(dx) == 1 and abs(dy) == 2)):
                raise ValueError("Illegal knight move")

        # =========================
        # KING
        # =========================
        elif piece.symbol == "K":
            if max(abs(dx), abs(dy)) != 1:
                raise ValueError("Illegal king move")

        # =========================
        # ROOK
        # =========================
        elif piece.symbol == "R":
            if not (dx == 0 or dy == 0):
                raise ValueError("Illegal rook move")

            for sq in self.squares_between(from_sq, to_sq):
                if self.get_piece(sq) is not None:
                    raise ValueError("Path blocked")

        # =========================
        # BISHOP
        # =========================
        elif piece.symbol == "B":
            if abs(dx) != abs(dy):
                raise ValueError("Illegal bishop move")

            for sq in self.squares_between(from_sq, to_sq):
                if self.get_piece(sq) is not None:
                    raise ValueError("Path blocked")

        # =========================
        # QUEEN
        # =========================
        elif piece.symbol == "Q":
            if not (dx == 0 or dy == 0 or abs(dx) == abs(dy)):
                raise ValueError("Illegal queen move")

            for sq in self.squares_between(from_sq, to_sq):
                if self.get_piece(sq) is not None:
                    raise ValueError("Path blocked")

        else:
            raise ValueError("Unknown piece type")

        # capture
        if target_piece is not None:
            target_piece.is_alive = False

        # move
        self.set_piece(to_sq, piece)
        self.set_piece(from_sq, None)
        piece.position = to_sq