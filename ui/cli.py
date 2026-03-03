from board import Board


class ChessCLI:
    def __init__(self):
        self.board = Board()
        self.board.setup_board()

    def run(self):
        print("=== CHESS GAME ===")
        print("Enter moves like: e2 e4")
        print("Type 'exit' to quit\n")

        while True:
            self.board.print_board()
            print(f"\nTurn: {self.board.current_turn}")

            move_input = input("Move: ").strip()

            if move_input.lower() == "exit":
                break

            parts = move_input.split()

            if len(parts) != 2:
                print("Enter move in format: e2 e4\n")
                continue

            from_sq, to_sq = parts

            try:
                self.board.move_piece(from_sq, to_sq)
            except Exception as e:
                print(f"Error: {e}\n")

        print("Game ended.")