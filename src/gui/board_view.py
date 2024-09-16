import tkinter as tk
import os
from PIL import Image, ImageTk
from src.game.piece import Color

# Map the binary representation of the pieces to their image names
binary_to_image = {
    0b0000: None,
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

board_colours = ['#f1d9c0', '#a97a65']
highlight_colour = '#5a7048'
check_colour = '#ff0000'


class BoardView:
    def __init__(self, master, board):
        self.master = master
        self.board = board
        self.canvas = tk.Canvas(self.master, width=800, height=800)
        self.canvas.pack()
        self.canvas_ids = []

        self.piece_images = self.load_piece_images()
        self.selected_piece = None  # First clicked piece/square
        self.destination_square = None  # Second clicked square
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
        size = 100
        for i in range(8):
            for j in range(8):
                colour = board_colours[(i+j) % 2]
                file1, rank1 = j*size, i*size
                file2, rank2 = file1+size, rank1+size
                self.canvas.create_rectangle(file1, rank1, file2, rank2, fill=colour, outline='')

    # Draw a piece on the board
    def draw_piece(self, piece, file, rank):
        # Resize the image to the square size using PIL
        if piece is not None:
            rank = 7 - rank
            self.canvas.create_image(file*100, rank*100, image=self.piece_images[piece.encode()], anchor='nw')
        else:
            self.highlight_selected_square(file, rank, highlight=False)

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
        if not self.board.game_active:
            return

        file, rank = self.get_clicked_square(event)

        clicked_piece = self.board.get_piece(file, rank)

        if self.selected_piece is None:
            self.handle_first_click(clicked_piece, file, rank)
        else:
            self.handle_second_click(file, rank)
            self.selected_piece = None
            self.destination_square = None

    # Return the file and rank of the clicked square
    def get_clicked_square(self, event):
        file = event.x // 100
        rank = 7 - (event.y // 100)
        return file, rank

    # First click must select a piece
    def handle_first_click(self, clicked_piece, file, rank):
        if clicked_piece is not None and clicked_piece.color == self.board.active_color:
            self.selected_piece = clicked_piece
            self.highlight_selected_square(file, rank)
            self.redraw_square(clicked_piece, file, rank)
            moves = clicked_piece.generate_moves(self.board)
            for move in moves:
                self.highlight_possible_square(move, self.board.get_piece(*move) is not None)

    def handle_second_click(self, file, rank):
        # Deselect if choosing an illegal square to move to
        if (file, rank) not in self.selected_piece.moves:
            self.deselect_piece()
            return

        self.move_selected_piece(file, rank)

    # Return True if the same square is clicked twice
    def is_same_square(self, file, rank):
        return self.selected_piece.get_position() == (file, rank)

    # Unhighlights and deselects the selected piece
    def deselect_piece(self):
        # Check if the king was in check (need to rehighlight the square)
        king = self.board.black_king if self.selected_piece.color == Color.BLACK else self.board.black_king
        king_in_check = self.is_king_in_check(king) and self.selected_piece == king

        self.highlight_selected_square(self.selected_piece.file, self.selected_piece.rank, highlight=False, check=king_in_check)
        self.reset_possible_moves()
        self.redraw_square(self.selected_piece, self.selected_piece.file, self.selected_piece.rank)
        self.selected_piece = None
        self.destination_square = None

    def move_selected_piece(self, file, rank):
        self.destination_square = (file, rank)
        self.update_board_view(file, rank)
        self.board.move_piece(self.selected_piece, self.destination_square)
        self.update_board_view(file, rank)
        self.board.update_game_state()

    # Update the board view after moving a piece
    def update_board_view(self, file, rank):
        # Unhighlight the original square
        self.highlight_selected_square(self.selected_piece.file, self.selected_piece.rank, False)

        # Empty the original square
        self.redraw_square(None, self.selected_piece.file, self.selected_piece.rank)

        # Empty the possible move squares
        self.reset_possible_moves()

        # Empty and redraw the destination square
        self.redraw_square(None, file, rank)
        self.redraw_square(self.selected_piece, file, rank)

        opp_king = self.board.white_king if self.selected_piece.color == Color.BLACK else self.board.black_king

        if self.is_king_in_check(opp_king):
            # Check if move has put the opposite king in check
            self.highlight_king_if_in_check()

            # Check for checkmate
            if self.is_king_in_checkmate():
                print("Checkmate")
                self.board.game_active = False

    def reset_possible_moves(self):
        for ids in self.canvas_ids:
            self.canvas.delete(ids)

    def highlight_selected_square(self, file, rank, highlight=True, check=False):
        size = 100
        rank = 7 - rank
        file1, rank1 = file*size, rank*size
        file2, rank2 = file1+size, rank1+size
        if check:
            colour = check_colour
        else:
            colour = highlight_colour if highlight else board_colours[(file+rank) % 2]
        self.canvas.create_rectangle(file1, rank1, file2, rank2, fill=colour, outline='')

    def redraw_square(self, piece, file, rank):
        self.draw_piece(piece, file, rank)

    def highlight_possible_square(self, move, capture=False):
        file, rank = move
        size = 100
        rank = 7 - rank
        file1, rank1 = file*size, rank*size
        file2, rank2 = file1+size, rank1+size
        if capture:
            ids = self.draw_highlight_triangles(file1, rank1, file2, rank2)
            for id in ids:
                self.canvas_ids.append(id)
        else:
            circle_offset = 63
            ids = self.canvas.create_oval(
                file1+circle_offset, rank1+circle_offset, file2-circle_offset, rank2-circle_offset, fill=highlight_colour, outline='')
            self.canvas_ids.append(ids)

    # Highlights the four corners of a square, indicates piece can be captured
    def draw_highlight_triangles(self, file1, rank1, file2, rank2):
        ids = []
        trainagle_size = 16
        ids.append(self.canvas.create_polygon(
            file1, rank1, file1+trainagle_size, rank1, file1, rank1+trainagle_size, fill=highlight_colour, outline=''))
        ids.append(self.canvas.create_polygon(
            file2, rank1, file2-trainagle_size, rank1, file2, rank1+trainagle_size, fill=highlight_colour, outline=''))
        ids.append(self.canvas.create_polygon(
            file1, rank2, file1+trainagle_size, rank2, file1, rank2-trainagle_size, fill=highlight_colour, outline=''))
        ids.append(self.canvas.create_polygon(
            file2, rank2, file2-trainagle_size, rank2, file2, rank2-trainagle_size, fill=highlight_colour, outline=''))
        return ids

    def is_king_in_check(self, king):
        return king.in_check(self.board)

    def highlight_king_if_in_check(self):
        king = self.board.white_king if self.selected_piece.color == Color.BLACK else self.board.black_king

        # Remove any highlight on the king's square
        self.highlight_selected_square(king.file, king.rank, highlight=False)

        if self.is_king_in_check(king):
            # Highlight the king if in check
            self.highlight_selected_square(king.file, king.rank, check=True)

        self.redraw_square(king, king.file, king.rank)

    def is_king_in_checkmate(self):
        king = self.board.white_king if self.selected_piece.color == Color.BLACK else self.board.black_king

        if not self.is_king_in_check(king):
            return False

        return self.board.is_king_in_checkmate(king)
