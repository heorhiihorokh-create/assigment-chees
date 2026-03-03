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
        if not is_valid_square(square):
            raise ValueError("Invalid square")
        return self.squares[square]

    def set_piece(self, square: str, piece):
        if not is_valid_square(square):
            raise ValueError("Invalid square")
        self.squares[square] = piece

    def print_board(self):
        for r in reversed(RANKS):
            row = []
            for f in FILES:
                p = self.squares[f"{f}{r}"]
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

    def squares_between(self, from_sq: str, to_sq: str) -> list[str]:
        fx, fy = square_to_xy(from_sq)
        tx, ty = square_to_xy(to_sq)

        dx, dy = tx - fx, ty - fy
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

    # ---- validation that does NOT mutate the board ----
    def is_legal_move(self, from_sq: str, to_sq: str) -> bool:
        if not is_valid_square(from_sq) or not is_valid_square(to_sq):
            return False
        if from_sq == to_sq:
            return False

        piece = self.get_piece(from_sq)
        if piece is None:
            return False

        target = self.get_piece(to_sq)
        if target is not None and target.color == piece.color:
            return False

        fx, fy = square_to_xy(from_sq)
        tx, ty = square_to_xy(to_sq)
        dx, dy = tx - fx, ty - fy

        # Pawn
        if piece.symbol == "P":
            direction = 1 if piece.color == "WHITE" else -1
            start = 1 if piece.color == "WHITE" else 6

            if dx == 0:
                if dy == direction and target is None:
                    return True
                if dy == 2 * direction and fy == start:
                    mid = xy_to_square(fx, fy + direction)
                    return self.get_piece(mid) is None and target is None
                return False

            if abs(dx) == 1 and dy == direction:
                return target is not None  # capture only
            return False

        # Knight
        if piece.symbol == "N":
            return (abs(dx) == 2 and abs(dy) == 1) or (abs(dx) == 1 and abs(dy) == 2)

        # King (no castling here)
        if piece.symbol == "K":
            return max(abs(dx), abs(dy)) == 1

        # Sliding pieces need clear path
        if piece.symbol in ("R", "B", "Q"):
            if piece.symbol == "R" and not (dx == 0 or dy == 0):
                return False
            if piece.symbol == "B" and abs(dx) != abs(dy):
                return False
            if piece.symbol == "Q" and not (dx == 0 or dy == 0 or abs(dx) == abs(dy)):
                return False

            between = self.squares_between(from_sq, to_sq)
            if between == [] and not (dx == 0 or dy == 0 or abs(dx) == abs(dy)):
                return False

            for sq in between:
                if self.get_piece(sq) is not None:
                    return False
            return True

        return False

    def get_legal_moves(self, from_sq: str) -> list[str]:
        piece = self.get_piece(from_sq)
        if piece is None:
            return []

        moves: list[str] = []
        for f in FILES:
            for r in RANKS:
                to_sq = f"{f}{r}"
                if self.is_legal_move(from_sq, to_sq):
                    moves.append(to_sq)
        return moves

    # ---- actual move that mutates board ----
    def move_piece(self, from_sq: str, to_sq: str) -> Optional[object]:
        if not self.is_legal_move(from_sq, to_sq):
            raise ValueError("Illegal move")

        piece = self.get_piece(from_sq)
        target = self.get_piece(to_sq)

        if target is not None:
            target.is_alive = False

        self.set_piece(to_sq, piece)
        self.set_piece(from_sq, None)
        piece.position = to_sq

        return target  # returns captured piece or None