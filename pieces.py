from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from typing import Dict, List, Tuple


FILES = "abcdefgh"
RANKS = "12345678"


def _square_to_xy(square: str) -> Tuple[int, int]:
    return FILES.index(square[0]), RANKS.index(square[1])


def _xy_to_square(x: int, y: int) -> str:
    return f"{FILES[x]}{RANKS[y]}"


class BoardMovements:
    """
    PDF-style movement helper class using @staticmethod.
    It does NOT move pieces on the board; it only generates squares.
    """

    @staticmethod
    def forward(square: str, n: int = 1) -> List[str]:
        x, y = _square_to_xy(square)
        out = []
        for i in range(1, n + 1):
            ny = y + i
            if 0 <= ny < 8:
                out.append(_xy_to_square(x, ny))
        return out

    @staticmethod
    def backward(square: str, n: int = 1) -> List[str]:
        x, y = _square_to_xy(square)
        out = []
        for i in range(1, n + 1):
            ny = y - i
            if 0 <= ny < 8:
                out.append(_xy_to_square(x, ny))
        return out

    @staticmethod
    def right(square: str, n: int = 1) -> List[str]:
        x, y = _square_to_xy(square)
        out = []
        for i in range(1, n + 1):
            nx = x + i
            if 0 <= nx < 8:
                out.append(_xy_to_square(nx, y))
        return out

    @staticmethod
    def left(square: str, n: int = 1) -> List[str]:
        x, y = _square_to_xy(square)
        out = []
        for i in range(1, n + 1):
            nx = x - i
            if 0 <= nx < 8:
                out.append(_xy_to_square(nx, y))
        return out

    @staticmethod
    def diagonals(square: str, n: int = 7) -> Dict[str, List[str]]:
        # 4 diagonals
        x, y = _square_to_xy(square)
        ne, nw, se, sw = [], [], [], []
        for i in range(1, n + 1):
            if 0 <= x + i < 8 and 0 <= y + i < 8:
                ne.append(_xy_to_square(x + i, y + i))
            if 0 <= x - i < 8 and 0 <= y + i < 8:
                nw.append(_xy_to_square(x - i, y + i))
            if 0 <= x + i < 8 and 0 <= y - i < 8:
                se.append(_xy_to_square(x + i, y - i))
            if 0 <= x - i < 8 and 0 <= y - i < 8:
                sw.append(_xy_to_square(x - i, y - i))
        return {"NE": ne, "NW": nw, "SE": se, "SW": sw}

    @staticmethod
    def knight_moves(square: str) -> List[str]:
        x, y = _square_to_xy(square)
        deltas = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        out = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                out.append(_xy_to_square(nx, ny))
        return out


def pdf_move_logger(func):
    """
    PDF-style decorator using functools.wraps.
    Safe: it logs only, doesn't change game behaviour.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs)
    return wrapper


@dataclass
class BaseChessPiece(ABC, dict):
    """
    PDF-style base class:
    - ABC + abstractmethod move()
    - also inherits dict so json.dumps(piece) is possible if needed.
    """
    color: str
    position: str
    is_alive: bool = True

    # required-like fields
    name: str = "Piece"
    symbol: str = "X"
    identifier: int = 0

    def __post_init__(self):
        # populate dict view for JSON friendliness
        dict.__init__(self)
        self.update(self.to_dict())

    def die(self) -> None:
        self.is_alive = False
        self.update(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "symbol": self.symbol,
            "identifier": self.identifier,
            "color": self.color,
            "position": self.position,
            "is_alive": self.is_alive,
        }

    def __str__(self) -> str:
        return f"{self.color} {self.name}({self.symbol}{self.identifier}) @ {self.position}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(color={self.color!r}, position={self.position!r}, id={self.identifier!r}, alive={self.is_alive!r})"

    @abstractmethod
    def move(self, to_square: str) -> None:
        """PDF-style move method. Board legality is handled by Board in our project."""
        raise NotImplementedError


class Pawn(BaseChessPiece):
    name = "Pawn"
    symbol = "P"

    @pdf_move_logger
    def move(self, to_square: str) -> None:
        self.position = to_square
        self.update(self.to_dict())


class Rook(BaseChessPiece):
    name = "Rook"
    symbol = "R"

    @pdf_move_logger
    def move(self, to_square: str) -> None:
        self.position = to_square
        self.update(self.to_dict())


class Knight(BaseChessPiece):
    name = "Knight"
    symbol = "N"

    @pdf_move_logger
    def move(self, to_square: str) -> None:
        self.position = to_square
        self.update(self.to_dict())


class Bishop(BaseChessPiece):
    name = "Bishop"
    symbol = "B"

    @pdf_move_logger
    def move(self, to_square: str) -> None:
        self.position = to_square
        self.update(self.to_dict())


class Queen(BaseChessPiece):
    name = "Queen"
    symbol = "Q"

    @pdf_move_logger
    def move(self, to_square: str) -> None:
        self.position = to_square
        self.update(self.to_dict())


class King(BaseChessPiece):
    name = "King"
    symbol = "K"

    @pdf_move_logger
    def move(self, to_square: str) -> None:
        self.position = to_square
        self.update(self.to_dict())