from __future__ import annotations
import json
from typing import Iterator
from dataclasses import dataclass
from typing import Any, Dict, Generator, List, Optional, Tuple

from pieces import Bishop, King, Knight, Pawn, Queen, Rook, Piece

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
    """
    Board is the single source of truth for pieces placement.
    Stores Piece objects (OOP requirement).
    Provides GUI/CLI-compatible helpers so nothing crashes.
    """

    # expose helpers for Piece methods
    square_to_xy = staticmethod(square_to_xy)
    xy_to_square = staticmethod(xy_to_square)

    def __init__(self) -> None:
        # squares: "a1".."h8" -> Piece | None
        self.squares: Dict[str, Optional[Piece]] = {f"{f}{r}": None for f in FILES for r in RANKS}
        self.turn: str = "white"
        self.reset()

    # ---------------- core utils ----------------

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < 8 and 0 <= y < 8

    def reset(self) -> None:
        """Set the initial chess position."""
        for sq in self.squares:
            self.squares[sq] = None

        # pawns
        for f in FILES:
            self.squares[f"{f}2"] = Pawn("white")
            self.squares[f"{f}7"] = Pawn("black")

        # back ranks
        self.squares["a1"] = Rook("white")
        self.squares["h1"] = Rook("white")
        self.squares["b1"] = Knight("white")
        self.squares["g1"] = Knight("white")
        self.squares["c1"] = Bishop("white")
        self.squares["f1"] = Bishop("white")
        self.squares["d1"] = Queen("white")
        self.squares["e1"] = King("white")

        self.squares["a8"] = Rook("black")
        self.squares["h8"] = Rook("black")
        self.squares["b8"] = Knight("black")
        self.squares["g8"] = Knight("black")
        self.squares["c8"] = Bishop("black")
        self.squares["f8"] = Bishop("black")
        self.squares["d8"] = Queen("black")
        self.squares["e8"] = King("black")

        self.turn = "white"

    def find_piece(self, piece_type: type[Piece], color: str) -> Optional[str]:
        """Return square of first matching piece, else None."""
        for sq, p in self.squares.items():
            if p is not None and isinstance(p, piece_type) and getattr(p, "color", None) == color:
                return sq
        return None

    # ---------------- move generation helpers ----------------

    def ray_moves(self, from_sq: str, color: str, directions: List[Tuple[int, int]]) -> List[str]:
        """
        Sliding moves for rook/bishop/queen.
        Pseudo-legal: ignores check/checkmate. Never crashes.
        """
        if not is_valid_square(from_sq):
            return []

        x, y = square_to_xy(from_sq)
        out: List[str] = []

        for dx, dy in directions:
            cx, cy = x + dx, y + dy
            while self.in_bounds(cx, cy):
                to_sq = xy_to_square(cx, cy)
                target = self.squares.get(to_sq)

                if target is None:
                    out.append(to_sq)
                else:
                    if getattr(target, "color", None) != color:
                        out.append(to_sq)
                    break

                cx += dx
                cy += dy

        return out

    def get_legal_moves(self, square: str) -> List[str]:
        """
        GUI expects this name.
        For now: pseudo-legal moves only, but NEVER crash.
        """
        if not is_valid_square(square):
            return []

        piece = self.squares.get(square)
        if piece is None:
            return []

        # enforce turn (safe default for GUI)
        if getattr(piece, "color", None) != self.turn:
            return []

        try:
            moves = piece.get_moves(self, square)  # type: ignore[attr-defined]
        except Exception:
            return []

        # sanitize output
        return [m for m in moves if is_valid_square(m)]

    def move(self, from_sq: str, to_sq: str) -> bool:
        """
        Safe move executor: only allows to_sq in get_legal_moves(from_sq).
        Returns True if moved.
        """
        if not (is_valid_square(from_sq) and is_valid_square(to_sq)):
            return False

        if to_sq not in self.get_legal_moves(from_sq):
            return False

        piece = self.squares.get(from_sq)
        if piece is None:
            return False

        self.squares[to_sq] = piece
        self.squares[from_sq] = None

        self.turn = "black" if self.turn == "white" else "white"
        return True

    # ---------------- persistence (PDF-style) ----------------

    def save(self) -> Generator[dict[str, Any], None, None]:
        """Generator that yields a serializable state."""
        pieces_payload: List[dict[str, Any]] = []
        for sq, p in self.squares.items():
            if p is None:
                continue
            pieces_payload.append(
                {
                    "sq": sq,
                    "type": type(p).__name__,  # "Pawn", "King", ...
                    "color": p.color,
                }
            )

        yield {
            "turn": self.turn,
            "pieces": pieces_payload,
        }

    def load(self, state: dict[str, Any]) -> Generator[None, None, None]:
        """Generator that restores board from a state dict."""
        for sq in self.squares:
            self.squares[sq] = None

        self.turn = state.get("turn", "white")

        type_map: Dict[str, type[Piece]] = {
            "Pawn": Pawn,
            "Rook": Rook,
            "Knight": Knight,
            "Bishop": Bishop,
            "Queen": Queen,
            "King": King,
        }

        for item in state.get("pieces", []):
            sq = item.get("sq")
            tname = item.get("type")
            color = item.get("color")

            if not (is_valid_square(sq) and isinstance(tname, str) and isinstance(color, str)):
                continue

            cls = type_map.get(tname)
            if cls is None:
                continue

            self.squares[sq] = cls(color)

        yield None

    # ---------------- GUI compatibility layer ----------------
    # (This is what prevents crashes when GUI expects different names.)

    def setup_board(self) -> None:
        """GUI compatibility alias."""
        self.reset()

    def get_piece(self, square: str) -> Optional[Piece]:
        """GUI compatibility: return piece at square or None."""
        if not is_valid_square(square):
            return None
        return self.squares.get(square)

    def set_piece(self, square: str, piece: Optional[Piece]) -> None:
        """GUI compatibility: set piece (or None) to a square."""
        if not is_valid_square(square):
            return
        self.squares[square] = piece

    def remove_piece(self, square: str) -> None:
        """GUI compatibility: remove piece from square."""
        if not is_valid_square(square):
            return
        self.squares[square] = None

    def move_piece(self, from_sq: str, to_sq: str) -> bool:
        """
        Some GUIs call move_piece(). Delegate to move().
        """
        return self.move(from_sq, to_sq)

    def piece_to_key(self, piece: Any) -> Optional[str]:
        """
        GUI helper:
        - if GUI still expects 'wP' style keys, it can call this.
        - returns None if piece is not drawable.
        """
        if piece is None:
            return None
        key = getattr(piece, "image_key", None)
        return key if isinstance(key, str) else None
    
    def print_board(self) -> None:
        """
        Prints the board row-first (8 -> 1) like in the PDF example.
        :contentReference[oaicite:1]{index=1}
        """
        for r in reversed(RANKS):
            row = [self.squares[f"{f}{r}"] for f in FILES]
            print(row)

    def is_square_empty(self, square: str) -> bool:
        """PDF helper."""
        return self.get_piece(square) is None

    def kill_piece(self, square: str) -> Optional[Piece]:
        """
        Mark piece as dead if it supports die(); remove from board.
        :contentReference[oaicite:2]{index=2}
        """
        p = self.get_piece(square)
        if p is None:
            return None
        die = getattr(p, "die", None)
        if callable(die):
            die()
        self.remove_piece(square)
        return p

    def save_board(self, path: str = "board.txt") -> None:
        """
        Append one JSON line (state) to board.txt (NDJSON).
        PDF asks to save states and append.
        :contentReference[oaicite:3]{index=3}
        """
        state = next(self.save())
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(state, ensure_ascii=False) + "\n")

    @staticmethod
    def read_states(path: str = "board.txt") -> Iterator[dict]:
        """
        Generator that yields one saved state at a time (line-by-line).
        :contentReference[oaicite:4]{index=4}
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    yield json.loads(line)
        except FileNotFoundError:
            return