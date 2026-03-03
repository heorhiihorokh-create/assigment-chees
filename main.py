#main
from board import Board

def main() -> None:
    board = Board()
    board.setup_board()
    board.print_board()

if __name__ == "__main__":
    main()