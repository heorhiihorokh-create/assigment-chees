import json
from typing import Generator
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
from pieces import Pawn, Rook, Knight, Bishop, Queen, King

FILES = "abcdefgh"
RANKS = "12345678"


def is_valid_square(square: str) -> bool:
    return isinstance(square, str) and len(square) == 2 and square[0] in FILES and square[1] in RANKS


def square_to_xy(square: str) -> tuple[int, int]:
    # a1 -> (0,0), h8 -> (7,7)
    x = FILES.index(square[0])
    y = RANKS.index(square[1])
    return x, y


def xy_to_square(x: int, y: int) -> str:
    return f"{FILES[x]}{RANKS[y]}"


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

    def squares_between(self, from_sq: str, to_sq: str) -> list[str]:
        """
        Returns squares strictly between from_sq and to_sq for straight/diagonal moves.
        If not straight/diagonal, returns [].
        """
        fx, fy = square_to_xy(from_sq)
        tx, ty = square_to_xy(to_sq)

        dx = tx - fx
        dy = ty - fy

        # straight or diagonal only
        if not (dx == 0 or dy == 0 or abs(dx) == abs(dy)):
            return []

        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

        squares: list[str] = []
        x, y = fx + step_x, fy + step_y
        while (x, y) != (tx, ty):
            squares.append(xy_to_square(x, y))
            x += step_x
            y += step_y
        return squares

    def move_piece(self, from_sq: str, to_sq: str) -> None:
        if not is_valid_square(from_sq):
            raise ValueError(f"Invalid source square: {from_sq}")
        if not is_valid_square(to_sq):
            raise ValueError(f"Invalid target square: {to_sq}")
        if from_sq == to_sq:
            raise ValueError("Source and target squares are the same")

        piece = self.get_piece(from_sq)
        if piece is None:
            raise ValueError(f"No piece on {from_sq}")

        target_piece = self.get_piece(to_sq)

        # Prevent capturing own piece
        if target_piece is not None and target_piece.color == piece.color:
            raise ValueError("Cannot capture your own piece")

        # Path blocking for sliding pieces (rook/bishop/queen)
        sym = getattr(piece, "symbol", "")
        if sym in ("R", "B", "Q"):
            between = self.squares_between(from_sq, to_sq)
            if not between:
                raise ValueError("Illegal move direction for sliding piece")
            for sq in between:
                if self.get_piece(sq) is not None:
                    raise ValueError("Path is blocked")

        # Capture
        if target_piece is not None:
            target_piece.is_alive = False

        # Move
        self.set_piece(to_sq, piece)
        self.set_piece(from_sq, None)
        piece.position = to_sq






    def find_piece(self, symbol: str, identifier: int, color: str):
        """
        PDF-style find_piece using list comprehension.
        """
        matches = [
            p for p in self.squares.values()
            if p is not None
            and getattr(p, "symbol", None) == symbol
            and getattr(p, "identifier", None) == identifier
            and getattr(p, "color", None) == color
        ]
        return matches[0] if matches else None

    def save_board(self, path: str = "board.txt") -> None:
        """
        PDF-style save using json.dumps(self.squares).
        We serialize pieces via to_dict() when present.
        """
        snapshot = {}
        for sq, piece in self.squares.items():
            if piece is None:
                snapshot[sq] = None
            else:
                if hasattr(piece, "to_dict"):
                    snapshot[sq] = piece.to_dict()
                else:
                    snapshot[sq] = {
                        "symbol": getattr(piece, "symbol", "X"),
                        "color": getattr(piece, "color", "WHITE"),
                        "position": getattr(piece, "position", sq),
                        "is_alive": getattr(piece, "is_alive", True),
                    }

        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(snapshot) + "\n")

    @staticmethod
    def board_states(path: str = "board.txt") -> Generator[dict, None, None]:
        """
        PDF-style generator: yields board snapshots line by line.
        """
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)