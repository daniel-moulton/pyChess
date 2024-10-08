import os
from PIL import Image, ImageTk
import tkinter as tk
from src.game.piece import King, Piece, Knight, Bishop, Rook, Queen
from src.game.colour import Colour
from src.game.board import Board
from src.game.piece_type import PieceType


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
promotion_colour = '#8d7281'


class BoardView:
    """
    Class representing the graphical view of the chess board.

    Attributes:
        canvas (tk.Canvas): The canvas object on which the board is drawn.
        board (Board): The board object representing the chess board.
        canvas_ids (list): A list of canvas item ids used to store the ids of the highlighted squares.
        piece_images (dict): A dictionary mapping piece names to their corresponding image objects.
        selected_piece (Piece): The piece that is currently selected.
        destination_square (tuple): The square to which the selected piece will be moved.
        promotion_pending (bool): A flag to track if a promotion is pending.
    """

    def __init__(self, canvas: tk.Canvas, board: Board) -> None:
        self.board = board
        self.canvas = canvas
        self.canvas.pack()
        self.canvas_ids = []

        self.piece_images = self.load_piece_images()
        self.selected_piece = None  # First clicked piece/square
        self.destination_square = None  # Second clicked square
        self.promotion_pending = False  # Track if promotion is pending
        self.draw_board()
        self.draw_pieces(board)
        self.canvas.bind("<Button-1>", self.on_click)

    def load_piece_images(self) -> dict[int, ImageTk.PhotoImage]:
        """
        Loads and returns a dictionary of piece images.

        Returns:
            dict[int, ImageTk.PhotoImage]: A dictionary mapping piece names to their corresponding image objects.
        """
        images = {}
        pieces_path = 'src/gui/images'
        for piece, image_name in binary_to_image.items():
            if image_name is not None:
                image_path = os.path.join(pieces_path, image_name)
                image = Image.open(image_path).convert('RGBA')
                image = image.resize((100, 100))
                images[piece] = ImageTk.PhotoImage(image)
        return images

    def draw_board(self) -> None:
        """
        Draws the chess board on the canvas.

        Returns:
            None
        """
        size = 100
        for i in range(8):
            for j in range(8):
                colour = board_colours[(i+j) % 2]
                file1, rank1 = j*size, i*size
                file2, rank2 = file1+size, rank1+size
                self.canvas.create_rectangle(file1, rank1, file2, rank2, fill=colour, outline='')

    def draw_piece(self, piece: Piece, file: int, rank: int) -> None:
        """
        Draws a piece on the board at the specified file and rank.

        Args:
            piece (Piece): The piece to draw.
            file (int): The file (column) index of the piece.
            rank (int): The rank (row) index of the piece.

        Returns:
            None
        """
        # Resize the image to the square size using PIL
        if piece is not None:
            rank = 7 - rank
            self.canvas.create_image(file*100, rank*100, image=self.piece_images[piece.encode()], anchor='nw')
        else:
            self.highlight_selected_square(file, rank, highlight=False)

    def draw_pieces(self, board: Board) -> None:
        """
        Draws the pieces on the board.

        Args:
            board (Board): The board object representing the chess board.

        Returns:
            None
        """
        # Iterate over the board and draw the pieces
        # The board is stored upside down so we need to reverse the ranks
        for rank in range(7, -1, -1):
            for file in range(8):
                piece = board.get_piece(file, rank)
                if piece is not None:
                    self.draw_piece(piece, file, rank)

    def on_click(self, event: tk.Event) -> None:
        """
        Handles the click event on the canvas.

        Only runs if the game is active.

        Args:
            event (tk.Event): The event object representing the click event.

        Returns:
            None
        """
        if not self.board.game_active:
            return

        file, rank = self.get_clicked_square(event)

        clicked_piece = self.board.get_piece(file, rank)

        if self.promotion_pending:
            self.handle_promotion_click(file, rank)
        elif self.selected_piece is None:
            self.handle_first_click(clicked_piece, file, rank)
        else:
            self.handle_second_click(file, rank)

    def get_clicked_square(self, event: tk.Event) -> tuple[int, int]:
        """
        Returns the file and rank of the square clicked on the canvas.

        Divides the x and y coordinates of the click event by 100 to get the file and rank.

        Args:
            event (tk.Event): The event object representing the click event.

        Returns:
            tuple[int, int]: A tuple containing the file and rank of the clicked square.
        """
        file = event.x // 100
        rank = 7 - (event.y // 100)
        return file, rank

    def handle_first_click(self, clicked_piece: Piece, file: int, rank: int) -> None:
        """
        Handles the first click event on the canvas.

        If a piece is clicked, highlights the selected square and the possible moves for the piece.

        Args:
            clicked_piece (Piece): The piece that was clicked.
            file (int): The file (column) index of the clicked square.
            rank (int): The rank (row) index of the clicked square.

        Returns:
            None
        """
        if clicked_piece is not None and clicked_piece.colour == self.board.active_colour:
            self.selected_piece = clicked_piece
            self.highlight_selected_square(file, rank)
            self.redraw_square(clicked_piece, file, rank)
            moves = clicked_piece.generate_moves(self.board)
            for move in moves:
                self.highlight_possible_square(move, self.board.get_piece(*move) is not None)

    def handle_second_click(self, file: int, rank: int) -> None:
        """
        Handles the second click event on the canvas.

        If a piece is selected and a square is clicked, moves the piece to the clicked square if it is a valid move.
        If an illegal square is clicked, deselects the piece.

        Args:
            file (int): The file (column) index of the clicked square.
            rank (int): The rank (row) index of the clicked square.

        Returns:
            None
        """
        # Deselect if choosing an illegal square to move to
        if (file, rank) not in self.selected_piece.moves:
            self.deselect_piece()
            return

        self.move_selected_piece(file, rank)

        # Check if the pawn has reached the end of the board
        if self.selected_piece.get_type() == PieceType.PAWN and (rank == 0 or rank == 7):
            self.promotion_pending = True
            self.draw_promotion_squares(self.destination_square)
        else:
            self.selected_piece = None
            self.destination_square = None
            self.board.update_game_state()

    def handle_promotion_click(self, file: int, rank: int) -> None:
        """
        Handles the promotion click event on the canvas.

        If a pawn is selected and a promotion square is clicked, promotes the pawn to the selected piece.
        Then clears the promotion squares and redraws the board where necessary.

        Args:
            file (int): The file (column) index of the clicked square.
            rank (int): The rank (row) index of the clicked square.

        Returns:
            None
        """
        # Get the promotion piece from the user click
        # If the rank is 0 or 7, it's a queen, 1,6 is a rook, 2,5 is a bishop, 3,4 is a knight

        if not self.promotion_pending or file != self.destination_square[0]:
            return

        # Validate the rank for promotion based on piece colour
        if self.selected_piece.colour == Colour.WHITE and rank not in (4, 5, 6, 7):
            return  # Invalid click for white
        elif self.selected_piece.colour == Colour.BLACK and rank not in (0, 1, 2, 3):
            return  # Invalid click for black

        original_file, original_rank = self.selected_piece.file, self.selected_piece.rank

        promotion_piece = None
        if rank == 0 or rank == 7:
            promotion_piece = Queen(self.selected_piece.colour)
        elif rank == 1 or rank == 6:
            promotion_piece = Rook(self.selected_piece.colour)
        elif rank == 2 or rank == 5:
            promotion_piece = Bishop(self.selected_piece.colour)
        elif rank == 3 or rank == 4:
            promotion_piece = Knight(self.selected_piece.colour)

        self.selected_piece = self.board.promote_pawn(self.selected_piece, promotion_piece, self.destination_square)
        self.draw_promotion_squares(self.destination_square, remove=True)
        self.update_board_view(original_file, original_rank, self.destination_square[0], self.destination_square[1])
        self.promotion_pending = False
        self.selected_piece = None
        self.board.update_game_state()

    def deselect_piece(self) -> None:
        """
        Deselects the currently selected piece.

        Unhighlights the selected square and the possible move squares.
        Resets the selected piece and the destination square.

        Returns:
            None
        """
        # Check if the king was in check (need to rehighlight the square)
        king = self.board.black_king if self.selected_piece.colour == Colour.BLACK else self.board.black_king
        king_in_check = self.is_king_in_check(king) and self.selected_piece == king

        self.highlight_selected_square(self.selected_piece.file, self.selected_piece.rank,
                                       highlight=False, check=king_in_check)
        self.reset_possible_moves()
        self.redraw_square(self.selected_piece, self.selected_piece.file, self.selected_piece.rank)
        self.selected_piece = None
        self.destination_square = None

    def move_selected_piece(self, file: int, rank: int) -> None:
        """
        Moves the selected piece to the specified square.

        Updates the board state, redraws the board, and checks for checkmate.

        Args:
            file (int): The file (column) index of the destination square.
            rank (int): The rank (row) index of the destination square.

        Returns:
            None
        """
        self.destination_square = (file, rank)
        original_file, original_rank = self.selected_piece.file, self.selected_piece.rank

        self.board.move_piece(self.selected_piece, self.destination_square)

        self.update_board_view(original_file, original_rank, file, rank)

    def draw_promotion_squares(self, square: tuple[int, int], remove: bool = False) -> None:
        """
        Draws the promotion squares on the canvas.

        Draws the promotion squares for the pawn at the specified square.
        Draws the pieces in the order: Queen, Rook, Bishop, Knight. (i.e. top to
        bottom for white, bottom to top for black)

        Args:
            square (tuple): The file and rank of the square to promote the pawn
            remove (bool): Whether to remove the promotion squares instead of adding them.

        Returns:
            None
        """
        file, rank = square

        start, end = (0, 4) if rank == 0 else (4, 8)  # Adjusted end values for both cases
        piece_colour = Colour.WHITE if rank == 7 else Colour.BLACK

        pieces = [Queen(piece_colour), Rook(piece_colour), Bishop(piece_colour), Knight(piece_colour)]

        # Reverse the list for white (ensures piece order)
        if rank == 7:
            pieces = pieces[::-1]

        for i in range(start, end):
            piece = pieces[i-start]
            if not remove:
                self.highlight_selected_square(file, i, promotion=True)
                self.draw_piece(piece, file, i)
            else:
                self.redraw_square(None, file, i)
                self.redraw_square(self.board.get_piece(file, i), file, i)

    def update_board_view(self, original_file: int, original_rank: int, file: int, rank: int) -> None:
        """
        Updates the board view after a move is made.

        Unhighlights the original square, empties the original square, empties the possible move squares,
        empties and redraws the destination square, and redraws the selected piece.

        Checks if the opposite king is in check, highlights the king if in check, and checks for checkmate.

        Args:
            original_file (int): The file (column) index of the original square.
            original_rank (int): The rank (row) index of the original square
            file (int): The file (column) index of the destination square.
            rank (int): The rank (row) index of the destination square.

        Returns:
            None
        """
        # Unhighlight the original square
        self.highlight_selected_square(original_file, original_rank, highlight=False)

        # Empty the original square
        self.redraw_square(None, original_file, original_rank)

        # Empty the possible move squares
        self.reset_possible_moves()

        # Empty and redraw the destination square
        self.redraw_square(None, file, rank)
        self.redraw_square(self.selected_piece, file, rank)

        opp_king = self.board.white_king if self.selected_piece.colour == Colour.BLACK else self.board.black_king
        own_king = self.board.black_king if self.selected_piece.colour == Colour.BLACK else self.board.white_king

        # Check if move has put the opposite king in check
        if self.is_king_in_check(opp_king):
            self.highlight_king_if_in_check(opp_king)

            # Check for checkmate
            if self.is_king_in_checkmate():
                print("Checkmate")
                self.board.game_active = False

        # Unhighlight own king if it is no longer in check
        self.highlight_king_if_in_check(own_king)

    def reset_possible_moves(self) -> None:
        """
        Resets the possible move squares.

        Empties the canvas ids list and deletes the highlighted squares.

        Returns:
            None
        """
        for ids in self.canvas_ids:
            self.canvas.delete(ids)

    def highlight_selected_square(self, file: int, rank: int, highlight: bool = True,
                                  check: bool = False, promotion: bool = False) -> None:
        """
        Highlights the selected square on the canvas.

        If check, highlight the square red to indicate check.
        If highlight, highlight the square with the highlight colour (indicating the selected piece).
        Else, highlight the square with the original colour.

        Args:
            file (int): The file (column) index of the square.
            rank (int): The rank (row) index of the square.
            highlight (bool): Whether to highlight the square.
            check (bool): Whether to highlight the square as a check square.
            promotion (bool): Whether to highlight the square as a promotion square.

        Returns:
            None
        """
        size = 100
        rank = 7 - rank
        file1, rank1 = file*size, rank*size
        file2, rank2 = file1+size, rank1+size
        if check:
            colour = check_colour
        elif promotion:
            colour = promotion_colour
        else:
            colour = highlight_colour if highlight else board_colours[(file+rank) % 2]
        self.canvas.create_rectangle(file1, rank1, file2, rank2, fill=colour, outline='')

    def redraw_square(self, piece: Piece, file: int, rank: int) -> None:
        """
        Redraws the square on the canvas.

        Empties the square and redraws the square with the new piece.

        Args:
            piece (Piece): The piece to draw on the square.
            file (int): The file (column) index of the square.
            rank (int): The rank (row) index of the square.

        Returns:
            None
        """
        self.draw_piece(piece, file, rank)

    def highlight_possible_square(self, move: tuple[int, int], capture: bool = False) -> None:
        """
        Highlights the possible move squares on the canvas.

        If the move is a capture, highlights the square with four triangles in the corners.
        Else, highlights the square with a circle.

        Args:
            move (tuple): The file and rank of the square to highlight.
            capture (bool): Whether the move is a capture move.

        Returns:
            None
        """
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
                file1+circle_offset, rank1+circle_offset, file2-circle_offset,
                rank2-circle_offset, fill=highlight_colour, outline='')
            self.canvas_ids.append(ids)

    def draw_highlight_triangles(self, file1: int, rank1: int, file2: int, rank2: int) -> list[int]:
        """
        Draws four triangles in the corners of the square to indicate a capture move.

        Args:
            file1 (int): The x-coordinate of the top-left corner of the square.
            rank1 (int): The y-coordinate of the top-left corner of the square.
            file2 (int): The x-coordinate of the bottom-right corner of the square.
            rank2 (int): The y-coordinate of the bottom-right corner of the square.

        Returns:
            list[int]: A list of ids of the triangles drawn on the canvas.
        """
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

    def is_king_in_check(self, king: King) -> bool:
        """
        Checks if the specified king is in check.

        Args:
            king (King): The king to check for check.

        Returns:
            bool: True if the king is in check, False otherwise.
        """
        return king.in_check(self.board)

    def highlight_king_if_in_check(self, king: King) -> None:
        """
        Highlights the king if it is in check.

        Highlights the king's square with the check colour.

        Args:
            king (King): The king to highlight.

        Returns:
            None
        """
        # Remove any highlight on the king's square
        self.highlight_selected_square(king.file, king.rank, highlight=False)

        if self.is_king_in_check(king):
            # Highlight the king if in check
            self.highlight_selected_square(king.file, king.rank, check=True)

        self.redraw_square(king, king.file, king.rank)

    def is_king_in_checkmate(self) -> bool:
        """
        Checks if the king is in checkmate.

        Returns:
            bool: True if the king is in checkmate, False otherwise.
        """
        king = self.board.white_king if self.selected_piece.colour == Colour.BLACK else self.board.black_king

        if not self.is_king_in_check(king):
            return False

        return self.board.is_king_in_checkmate(king)
