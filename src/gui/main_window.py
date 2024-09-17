import tkinter as tk
from src.gui.board_view import BoardView
from src.game.board import Board


class MainWindow:
    def __init__(self, board: Board) -> None:
        """
        Initializes the main window of the game.

        Args:
            board (Board): The board object representing the chess board.

        Returns:
            None
        """
        self.window = tk.Tk()
        self.window.title("Chess")
        self.window.geometry("800x800")
        self.canvas = tk.Canvas(self.window, width=800, height=800)
        self.canvas.pack()
        self.board_view = BoardView(self.canvas, board)

    def run(self):
        """
        Runs the main game loop.

        Returns:
            None
        """
        self.window.mainloop()
