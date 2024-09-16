import tkinter as tk
from src.gui.board_view import BoardView


class MainWindow:
    def __init__(self, board):
        self.window = tk.Tk()
        self.window.title("Chess")
        self.window.geometry("800x800")
        self.canvas = tk.Canvas(self.window, width=800, height=800)
        self.canvas.pack()
        self.board_view = BoardView(self.canvas, board)

    def run(self):
        self.window.mainloop()
