from board import Board


def main() -> None:
    board = Board()
    board.setup_board()

    print("Initial position:")
    board.print_board()

    print("\nMove: e2 -> e4")
    board.move_piece("e2", "e4")
    board.print_board()

    print("\nTry illegal rook jump: a1 -> a3 (should fail, pawn blocks on a2)")
    try:
        board.move_piece("a1", "a3")
    except ValueError as e:
        print("ERROR:", e)

    print("\nFree the rook: a2 -> a4")
    board.move_piece("a2", "a4")
    board.print_board()

    print("\nNow rook move: a1 -> a3 (should work)")
    board.move_piece("a1", "a3")
    board.print_board()


if __name__ == "__main__":
    main()