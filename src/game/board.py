from src.game.piece import fen_to_class, Piece, King
from src.game.colour import Colour
from src.game.piece_type import PieceType


class Board:
    """
    Class representing the chess board.

    Attributes:
        board (list[list[Piece]]): A 2D list representing the board.
        fen (str): The position of the board in Forsyth-Edwards Notation (FEN).
        active_colour (Colour): The colour of the player whose turn it is.
        castling_rights (str): A string representing the castling rights of both players.
        en_passant_square (str): The square where an en passant capture could be made.
        halfmove_clock (int): The number of halfmoves since the last capture or pawn move.
        fullmove_number (int): The number of fullmoves in the game.
        white_king (King): The white king piece.
        black_king (King): The black king piece.
        game_active (bool): A flag indicating whether the game is being played.
    """

    def __init__(self, fen: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1') -> None:
        """
        Initializes the board object.

        Args:
            fen (str): The position of the board in Forsyth-Edwards Notation (FEN).
                The default value is the starting position of a chess game.

        Returns:
            None
        """
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.fen = fen
        self.active_colour = None
        self.castling_rights = None
        self.en_passant_square = None
        self.halfmove_clock = None
        self.fullmove_number = None
        self.white_king = None
        self.black_king = None
        self.game_active = True

        self.parse_fen(self.fen)

    def __str__(self) -> str:
        """
        Returns a string representation of the board.

        The string representation consists of the pieces on the board arranged in a grid format.
        Each piece is represented by its string representation, padded with spaces to ensure consistent spacing.

        Returns:
            str: The string representation of the board.
        """
        board_str = ''
        for rank in range(7, -1, -1):
            for file in range(8):
                piece = self.get_piece(file, rank)
                board_str += str(piece).ljust(12)
            board_str += '\n'
        return board_str

    def get_piece(self, file: int, rank: int) -> Piece:
        """
        Retrieves the piece located at the specified file and rank on the board.

        Args:
            file (int): The file (column) index of the piece.
            rank (int): The rank (row) index of the piece.

        Returns:
            Piece: The piece located at the specified file and rank.

        """
        return self.board[rank][file]

    def set_piece(self, file: int, rank: int, piece: Piece) -> None:
        """
        Sets the piece at the specified file and rank on the board.

        Args:
            file (int): The file (column) index of the piece.
            rank (int): The rank (row) index of the piece.
            piece (Piece): The piece to set at the specified file and rank.

        Returns:
            None
        """
        self.board[rank][file] = piece

    def get_board(self) -> list[list[Piece]]:
        """
        Returns the board as a 2D list of pieces.

        Returns:
            list[list[Piece]]: The board represented as a 2D list of pieces.
        """
        return self.board

    def parse_fen(self, fen: str) -> None:
        """
        Parses the FEN string and updates the board state accordingly.

        Loads the piece positions, active colour, castling rights,
        en passant square, halfmove clock, and fullmove number.

        Args:
            fen (str): The FEN string representing the board state.

        Returns:
            None
        """
        parts = fen.split()
        self.load_fen(parts[0])
        self.active_colour = Colour.WHITE if parts[1] == 'w' else Colour.BLACK
        self.castling_rights = parts[2]
        self.en_passant_square = parts[3]
        self.halfmove_clock = int(parts[4])
        self.fullmove_number = int(parts[5])
        self.white_king = self.find_king(Colour.WHITE)
        self.black_king = self.find_king(Colour.BLACK)

    def find_king(self, colour: Colour) -> Piece:
        """
        Finds the king of the specified colour on the board.

        Args:
            colour (Colour): The colour of the king to find.

        Returns:
            Piece: The king piece of the specified colour.
        """
        for rank in range(8):
            for file in range(8):
                piece = self.get_piece(file, rank)
                if piece is not None and piece.colour == colour and piece.piece_type == PieceType.KING:
                    return piece
        return None

    def load_fen(self, fen: str) -> None:
        """
        Loads the piece positions from the FEN string.

        Args:
            fen (str): The FEN string representing the piece positions.

        Returns:
            None
        """
        file, rank = 0, 7
        for char in fen:
            if char == '/':
                file = 0
                rank -= 1
            elif char.isdigit():
                file += int(char)
            else:
                piece = self.create_piece(char, file, rank)
                self.set_piece(file, rank, piece)
                file += 1

    def create_piece(self, char: str, file: int, rank: int) -> Piece:
        """
        Creates a piece object based on the FEN character representation.

        Args:
            char (str): The FEN character representing the piece.
            file (int): The file (column) index of the piece.
            rank (int): The rank (row) index of the piece.

        Returns:
            Piece: The piece object created based on the FEN character representation.
        """
        colour = Colour.WHITE if char.isupper() else Colour.BLACK
        piece_class = fen_to_class[char.lower()]
        piece = piece_class(colour)
        piece.set_position(file, rank)
        return piece

    def move_piece(self, piece: Piece, destination: tuple[int, int]) -> Piece:
        """
        Moves a piece to the specified destination on the board.

        Args:
            piece (Piece): The piece to move.
            destination (tuple[int, int]): The destination file and rank to move the piece to.

        Returns:
            Piece: The piece that was captured during the move, if any.
        """
        file, rank = destination

        # Check if the move is a capture
        captured_piece = self.get_piece(file, rank)

        # Move the piece to the new position
        self.set_piece(file, rank, piece)

        # Remove the piece from its previous position
        self.set_piece(piece.file, piece.rank, None)
        piece.set_position(file, rank)

        return captured_piece

    def promote_pawn(self, pawn: Piece, new_piece: Piece, square: tuple[int, int]) -> Piece:
        """
        Promotes a pawn to a new piece type.

        Args:
            pawn (Piece): The pawn piece to promote.
            new_piece (Piece): The new piece type to promote the pawn to.
            square (tuple[int, int]): The square to place the new piece.

        Returns:
            Piece: The new piece that the pawn was promoted to.
        """
        file, rank = square

        # Remove the pawn from the board
        self.set_piece(pawn.file, pawn.rank, None)

        # Place the new piece on the board
        self.set_piece(file, rank, new_piece)
        new_piece.set_position(file, rank)

        return new_piece

    def undo_move(self, piece: Piece, original_position: tuple[int, int],
                  captured_piece: Piece) -> None:
        """
        Undoes a move by moving the piece back to its original position and restoring the captured piece.

        Args:
            piece (Piece): The piece to move back to its original position.
            original_position (tuple[int, int]): The original file and rank of the piece.
            captured_piece (Piece): The captured piece to restore (if any).

        Returns:
            None
        """
        original_file, original_rank = original_position
        current_file, current_rank = piece.get_position()

        # Move the piece back to its original position
        self.set_piece(original_file, original_rank, piece)
        piece.set_position(original_file, original_rank)

        # Restore the captured piece
        self.set_piece(current_file, current_rank, captured_piece)

    def update_game_state(self) -> None:
        """
        Updates the game state based on the current board position.

        Switches the active colour and increments the fullmove number.

        Returns:
            None
        """
        self.active_colour = Colour.WHITE if self.active_colour == Colour.BLACK else Colour.BLACK
        if self.active_colour == Colour.WHITE:
            self.fullmove_number += 1
        self.halfmove_clock += 1

        self.check_for_draw()

    def is_king_in_checkmate(self, king: King) -> bool:
        """
        Checks if the specified king is in checkmate.

        Args:
            king (King): The king to check for checkmate.

        Returns:
            bool: True if the king is in checkmate, False otherwise.
        """
        colour = king.colour
        # Loop through board, if piece is same colour as king, check if it can move
        for rank in range(8):
            for file in range(8):
                piece = self.get_piece(file, rank)
                if piece is not None and piece.colour == colour:
                    moves = piece.generate_moves(self)
                    if moves:
                        return False
        return True

    def check_for_draw(self) -> None:
        """
        Checks if the game is a draw based on the current board position.

        Criteria for a draw:
        - 50-move rule: If no pawn moves or captures have occurred in the last 50 moves.
        - Insufficient material: If neither player has enough material to checkmate the opponent.
        - Stalemate: If the active player has no legal moves and is not in check.

        Returns:
            None
        """
        if self.halfmove_clock >= 100:
            self.game_active = False
            print("Draw by 50-move rule")
        elif self.is_stalemate() and self.game_active:
            self.game_active = False
            print("Draw by stalemate")
        # elif self.is_insufficient_material():
        #     self.game_active = False
        #     print("Draw by insufficient material")

    def is_stalemate(self) -> bool:
        """
        Checks if the game is a stalemate.

        A stalemate occurs when the active player has no legal moves and is not in check.

        Returns:
            bool: True if the game is a stalemate, False otherwise.
        """
        # Check if active player has any legal moves
        for rank in range(8):
            for file in range(8):
                piece = self.get_piece(file, rank)
                if piece is not None and piece.colour == self.active_colour:
                    moves = piece.generate_moves(self)
                    if moves:
                        return False
        return True
