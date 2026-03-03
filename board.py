from __future__ import annotations
from typing import Dict, Optional
from pieces import Pawn, Rook, Knight, Bishop, Queen, King

FILES = "abcdefgh"
RANKS = "12345678"


def is_valid_square(square: str) -> bool:
    return len(square) == 2 and square[0] in FILES and square[1] in RANKS


def square_to_xy(square: str) -> tuple[int, int]:
    return FILES.index(square[0]), RANKS.index(square[1])


def xy_to_square(x: int, y: int) -> str:
    return f"{FILES[x]}{RANKS[y]}"


class Board:
    def __init__(self):
        self.squares: Dict[str, Optional[object]] = {
            f"{f}{r}": None for r in RANKS for f in FILES
        }

    def get_piece(self, square: str):
        return self.squares[square]

    def set_piece(self, square: str, piece):
        self.squares[square] = piece

    def print_board(self):
        for r in reversed(RANKS):
            row = []
            for f in FILES:
                sq = f"{f}{r}"
                p = self.squares[sq]
                if p is None:
                    row.append(".")
                else:
                    row.append(p.symbol.upper() if p.color == "WHITE" else p.symbol.lower())
            print(" ".join(row), f" {r}")
        print(" ".join(FILES))

    def setup_board(self):
        for f in FILES:
            self.set_piece(f"{f}2", Pawn("WHITE", f"{f}2"))
            self.set_piece(f"{f}7", Pawn("BLACK", f"{f}7"))

        placements = [
            ("a1", Rook), ("h1", Rook),
            ("a8", Rook), ("h8", Rook),
            ("b1", Knight), ("g1", Knight),
            ("b8", Knight), ("g8", Knight),
            ("c1", Bishop), ("f1", Bishop),
            ("c8", Bishop), ("f8", Bishop),
            ("d1", Queen), ("d8", Queen),
            ("e1", King), ("e8", King),
        ]

        for square, cls in placements:
            color = "WHITE" if square[1] in "12" else "BLACK"
            self.set_piece(square, cls(color, square))

    def squares_between(self, from_sq: str, to_sq: str):
        fx, fy = square_to_xy(from_sq)
        tx, ty = square_to_xy(to_sq)

        dx = tx - fx
        dy = ty - fy

        if not (dx == 0 or dy == 0 or abs(dx) == abs(dy)):
            return []

        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

        squares = []
        x, y = fx + step_x, fy + step_y

        while (x, y) != (tx, ty):
            squares.append(xy_to_square(x, y))
            x += step_x
            y += step_y

        return squares

    def move_piece(self, from_sq: str, to_sq: str):
        if not is_valid_square(from_sq) or not is_valid_square(to_sq):
            raise ValueError("Invalid square")

        piece = self.get_piece(from_sq)
        if piece is None:
            raise ValueError("No piece on source square")

        target = self.get_piece(to_sq)

        if target and target.color == piece.color:
            raise ValueError("Cannot capture own piece")

        fx, fy = square_to_xy(from_sq)
        tx, ty = square_to_xy(to_sq)

        dx, dy = tx - fx, ty - fy

        # PAWN
        if piece.symbol == "P":
            direction = 1 if piece.color == "WHITE" else -1
            start = 1 if piece.color == "WHITE" else 6

            if dx == 0:
                if dy == direction and target is None:
                    pass
                elif dy == 2 * direction and fy == start:
                    mid = xy_to_square(fx, fy + direction)
                    if self.get_piece(mid) or target:
                        raise ValueError("Pawn path blocked")
                else:
                    raise ValueError("Illegal pawn move")
            elif abs(dx) == 1 and dy == direction and target:
                pass
            else:
                raise ValueError("Illegal pawn move")

        # KNIGHT
        elif piece.symbol == "N":
            if not ((abs(dx) == 2 and abs(dy) == 1) or (abs(dx) == 1 and abs(dy) == 2)):
                raise ValueError("Illegal knight move")

        # KING
        elif piece.symbol == "K":
            if max(abs(dx), abs(dy)) != 1:
                raise ValueError("Illegal king move")

        # ROOK
        elif piece.symbol == "R":
            if not (dx == 0 or dy == 0):
                raise ValueError("Illegal rook move")
            if any(self.get_piece(sq) for sq in self.squares_between(from_sq, to_sq)):
                raise ValueError("Path blocked")

        # BISHOP
        elif piece.symbol == "B":
            if abs(dx) != abs(dy):
                raise ValueError("Illegal bishop move")
            if any(self.get_piece(sq) for sq in self.squares_between(from_sq, to_sq)):
                raise ValueError("Path blocked")

        # QUEEN
        elif piece.symbol == "Q":
            if not (dx == 0 or dy == 0 or abs(dx) == abs(dy)):
                raise ValueError("Illegal queen move")
            if any(self.get_piece(sq) for sq in self.squares_between(from_sq, to_sq)):
                raise ValueError("Path blocked")

        if target:
            target.is_alive = False

        self.set_piece(to_sq, piece)
        self.set_piece(from_sq, None)
        piece.position = to_sq