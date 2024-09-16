from src.gui.main_window import MainWindow
from src.game.board import Board


def main():
    board = Board()
    window = MainWindow(board)
    window.run()


if __name__ == "__main__":
    main()
