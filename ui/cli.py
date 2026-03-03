from board import Board


class ChessCLI:
    def __init__(self):
        self.board = Board()
        self.board.setup_board()
        self.current_turn = "WHITE"

    def switch_turn(self):
        self.current_turn = "BLACK" if self.current_turn == "WHITE" else "WHITE"

    def run(self):
        print("=== CHESS GAME ===")
        print("Enter moves like: e2 e4")
        print("Type 'exit' to quit\n")

        while True:
            self.board.print_board()
            print(f"\nTurn: {self.current_turn}")

            move_input = input("Move: ").strip()

            if move_input.lower() == "exit":
                break

            try:
                from_sq, to_sq = move_input.split()

                piece = self.board.get_piece(from_sq)
                if piece is None:
                    raise ValueError("No piece on that square")

                if piece.color != self.current_turn:
                    raise ValueError("Not your turn")

                self.board.move_piece(from_sq, to_sq)

                self.switch_turn()

            except Exception as e:
                print(f"Error: {e}")

        print("Game ended.")