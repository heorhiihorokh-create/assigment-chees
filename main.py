import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", action="store_true", help="Run CLI version")
    args = parser.parse_args()

    if args.cli:
        from ui.cli import run_cli
        run_cli()
    else:
        from gui.game import ChessGUI
        game = ChessGUI()
        game.run()


if __name__ == "__main__":
    main()