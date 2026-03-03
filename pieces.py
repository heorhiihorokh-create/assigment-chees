from __future__ import annotations
from dataclasses import dataclass
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from board import Board

FILES = "abcdefgh"
RANKS = "12345678"


@dataclass(frozen=True)
class Piece:
    color: str  # "white" | "black"

    @property
    def color_prefix(self) -> str:
        return "w" if self.color == "white" else "b"

    @property
    def symbol(self) -> str:
        raise NotImplementedError

    @property
    def image_key(self) -> str:
        # matches assets: wP.png, bK.png, ...
        return f"{self.color_prefix}{self.symbol}"

    def get_moves(self, board: "Board", from_sq: str) -> List[str]:
        """
        Pseudo-legal moves (no check/checkmate logic).
        Must NEVER crash. Return [] if not implemented yet.
        """
        return []


@dataclass(frozen=True)
class Pawn(Piece):
    @property
    def symbol(self) -> str:
        return "P"

    def get_moves(self, board: "Board", from_sq: str) -> List[str]:
        # Minimal safe pawn moves (forward + capture diagonals), no en-passant
        x, y = board.square_to_xy(from_sq)
        diry = 1 if self.color == "white" else -1
        moves: List[str] = []

        # forward 1
        nx, ny = x, y + diry
        if board.in_bounds(nx, ny):
            to_sq = board.xy_to_square(nx, ny)
            if board.squares[to_sq] is None:
                moves.append(to_sq)

                # forward 2 from starting rank
                start_rank = 1 if self.color == "white" else 6
                if y == start_rank:
                    nny = y + 2 * diry
                    if board.in_bounds(nx, nny):
                        to_sq2 = board.xy_to_square(nx, nny)
                        if board.squares[to_sq2] is None:
                            moves.append(to_sq2)

        # captures
        for dx in (-1, 1):
            nx, ny = x + dx, y + diry
            if board.in_bounds(nx, ny):
                to_sq = board.xy_to_square(nx, ny)
                p = board.squares[to_sq]
                if p is not None and getattr(p, "color", None) != self.color:
                    moves.append(to_sq)

        return moves


@dataclass(frozen=True)
class Rook(Piece):
    @property
    def symbol(self) -> str:
        return "R"

    def get_moves(self, board: "Board", from_sq: str) -> List[str]:
        return board.ray_moves(from_sq, self.color, directions=[(1,0),(-1,0),(0,1),(0,-1)])


@dataclass(frozen=True)
class Bishop(Piece):
    @property
    def symbol(self) -> str:
        return "B"

    def get_moves(self, board: "Board", from_sq: str) -> List[str]:
        return board.ray_moves(from_sq, self.color, directions=[(1,1),(1,-1),(-1,1),(-1,-1)])


@dataclass(frozen=True)
class Knight(Piece):
    @property
    def symbol(self) -> str:
        return "N"

    def get_moves(self, board: "Board", from_sq: str) -> List[str]:
        x, y = board.square_to_xy(from_sq)
        deltas = [(1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1),(-2,1),(-1,2)]
        out: List[str] = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not board.in_bounds(nx, ny):
                continue
            to_sq = board.xy_to_square(nx, ny)
            target = board.squares[to_sq]
            if target is None or getattr(target, "color", None) != self.color:
                out.append(to_sq)
        return out


@dataclass(frozen=True)
class Queen(Piece):
    @property
    def symbol(self) -> str:
        return "Q"

    def get_moves(self, board: "Board", from_sq: str) -> List[str]:
        return board.ray_moves(
            from_sq,
            self.color,
            directions=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)],
        )


@dataclass(frozen=True)
class King(Piece):
    @property
    def symbol(self) -> str:
        return "K"

    def get_moves(self, board: "Board", from_sq: str) -> List[str]:
        x, y = board.square_to_xy(from_sq)
        out: List[str] = []
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not board.in_bounds(nx, ny):
                    continue
                to_sq = board.xy_to_square(nx, ny)
                target = board.squares[to_sq]
                if target is None or getattr(target, "color", None) != self.color:
                    out.append(to_sq)
        return out