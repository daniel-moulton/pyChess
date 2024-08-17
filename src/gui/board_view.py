import tkinter as tk
import os
from PIL import Image, ImageTk

# Map the binary representation of the pieces to their image names
binary_to_image = {
    0b0001: None,
    0b1001: 'white_pawn.png',
    0b1010: 'white_knight.png',
    0b1011: 'white_bishop.png',
    0b1100: 'white_rook.png',
    0b1101: 'white_queen.png',
    0b1110: 'white_king.png',
    0b0001: 'black_pawn.png',
    0b0010: 'black_knight.png',
    0b0011: 'black_bishop.png',
    0b0100: 'black_rook.png',
    0b0101: 'black_queen.png',
    0b0110: 'black_king.png'
}



class BoardView:
    def __init__(self, master, board):
        self.master = master
        self.board = board
        self.canvas = tk.Canvas(self.master, width=800, height=800)
        self.canvas.pack()

        self.piece_images = self.load_piece_images()
        self.selected_piece = None
        self.destination_square = None
        self.draw_board()
        self.draw_pieces(board)
        self.canvas.bind("<Button-1>", self.on_click)
    
    # Load piece images from the images directory
    def load_piece_images(self):
        images = {}
        pieces_path = 'src/gui/images'
        for piece, image_name in binary_to_image.items():
            if image_name is not None:
                image_path = os.path.join(pieces_path, image_name)
                image = Image.open(image_path).convert('RGBA')
                image = image.resize((100, 100))
                images[piece] = ImageTk.PhotoImage(image)
        return images
    
    # Draw the chess board
    def draw_board(self):
        colours = ['#f1d9c0', '#a97a65']
        size = 100
        for i in range(8):
            for j in range(8):
                colour = colours[(i+j)%2]
                file1, rank1 = j*size, i*size
                file2, rank2 = file1+size, rank1+size
                self.canvas.create_rectangle(file1, rank1, file2, rank2, fill=colour, outline='')

    # Draw a piece on the board
    def draw_piece(self, piece, file, rank):
        # Resize the image to the square size using PIL
        rank = 7 - rank
        self.canvas.create_image(file*100, rank*100, image=self.piece_images[piece.encode()], anchor='nw')
    
    # Draw all the pieces on the board from a given board state
    def draw_pieces(self, board):
        # Iterate over the board and draw the pieces
        # The board is stored upside down so we need to reverse the ranks
        for rank in range(7, -1, -1):
            for file in range(8):
                piece = board.get_piece(file, rank)
                if piece is not None:
                    self.draw_piece(piece, file, rank)


    # Handle a click event
    def on_click(self, event):
        file, rank = event.x//100, event.y//100
        rank = 7 - rank
        print(f'Clicked on square {file}, {rank}')
        clicked_piece = self.board.get_piece(file, rank)
        print(clicked_piece)
        if self.selected_piece is None:
            self.selected_piece = clicked_piece
            self.highlight_square(file, rank)
            self.redraw_square(clicked_piece, file, rank)
            print(self.selected_piece.get_position())
        else:
            self.destination_square = (file, rank)
            self.board.move_piece(self.selected_piece, self.destination_square)
            self.redraw_square(self.selected_piece, file, rank)
            self.redraw_square(None, self.selected_piece.file, self.selected_piece.rank)
            self.selected_piece = None
            self.destination_square = None
    
    def highlight_square(self, file, rank):
        size = 100
        rank = 7 - rank
        file1, rank1 = file*size, rank*size
        file2, rank2 = file1+size, rank1+size
        # Set background to red without removing the piece
        self.canvas.create_rectangle(file1, rank1, file2, rank2, fill='red', outline='')

    def redraw_square(self, piece, file, rank):
        self.draw_piece(piece, file, rank)