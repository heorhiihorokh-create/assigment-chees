class BaseChessPiece:


    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "symbol": self.symbol,
            "identifier": self.identifier,
            "color": self.color,
            "position": self.position,
            "is_alive": self.is_alive,
        }