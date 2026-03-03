#main
from board import Board

def main() -> None:
    board = Board()
    board.setup_board()

    print("Initial position:")
    board.print_board()

    print("\nMove: e2 -> e4")
    board.move_piece("e2", "e4")
    board.print_board()

if __name__ == "__main__":
    main()