"""
Snake and Ladder Game Launcher.
Run without arguments for the Desktop GUI, or with --cli for Terminal mode.

Usage:
    python main.py          # Launch GUI Desktop version
    python main.py --cli    # Launch Terminal CLI version
"""

import sys
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Snake and Ladder Game - Python Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py          Launch interactive graphical desktop app (Tkinter)
  python main.py --cli    Launch terminal CLI game with ASCII board
        """
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run game in terminal/CLI mode instead of GUI"
    )

    args = parser.parse_args()

    if args.cli:
        from cli import run_cli_game
        run_cli_game()
    else:
        try:
            from gui import run_gui
            run_gui()
        except Exception as e:
            print(f"[!] Unable to launch GUI ({e}). Falling back to Terminal CLI mode...\n")
            from cli import run_cli_game
            run_cli_game()


if __name__ == "__main__":
    main()
