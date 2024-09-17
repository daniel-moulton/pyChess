from typing import TYPE_CHECKING
from src.game.colour import Colour
from src.game.piece_type import PieceType

if TYPE_CHECKING:
    from src.game.board import Board


class Piece:
    """
    Class representing a chess piece.

    Each piece is represented by a colour and a piece type.
    This is encoded as a 5 bit number:
    - The first bit represents the colour of the piece (0 for white, 1 for black).
    - The following 4 bits represent the type of the piece (see PieceType).

    Attributes:
        piece_type (PieceType): The type of the piece.
        colour (Colour): The colour of the piece.
        rank (int): The rank of the piece on the board.
        file (int): The file of the piece on the board.
        moves (list[tuple[int, int]]): A list of possible moves for the piece.
    """

    def __init__(self, colour: Colour, piece_type: PieceType = PieceType.NONE) -> None:
        """
        Initializes a chess piece.

        Args:
            colour (Colour): The colour of the piece.
            piece_type (PieceType): The type of the piece.

        Returns:
            None
        """
        self.piece_type = piece_type
        self.colour = colour
        self.rank = None
        self.file = None
        self.moves = []

    def __str__(self) -> str:
        """
        Returns a string representation of the piece.

        Format is "<colour> <piece_type>".

        Returns:
            str: A string representation of the piece.
        """
        return f'{self.colour.name} {self.piece_type.name}'

    def encode(self):
        """
        Encodes the piece as a 5 bit number.

        The first bit is the colour of the piece (0 for white, 1 for black).
        The following 4 bits represent the type of the piece (see PieceType).

        Returns:
            int: The encoded piece.
        """
        return self.colour.value | self.piece_type.value

    def generate_moves(self, board: 'Board', file: int, rank: int) -> list[tuple[int, int]]:
        """
        Generates a list of possible moves for the piece.

        This method should be overridden by subclasses.

        Args:
            board (Board): The board object representing the chess board.
            file (int): The file (column) index of the piece.
            rank (int): The rank (row) index of the piece.

        Returns:
            list[tuple[int, int]]: A list of possible moves for the piece.

        Raises:
            NotImplementedError: This method should be overridden by subclasses.
        """
        raise NotImplementedError

    def get_position(self) -> tuple[int, int]:
        """
        Get the position of the piece on the board.

        Returns:
            tuple[int, int]: The file and rank of the piece.
        """
        return self.file, self.rank

    def set_position(self, file: int, rank: int) -> None:
        """
        Set the position of the piece on the board.

        Args:
            file (int): The file (column) index of the piece.
            rank (int): The rank (row) index of the piece.

        Returns:
            None
        """
        self.file = file
        self.rank = rank

    def filter_self_check_moves(self, board: 'Board', moves: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """
        Filter out moves that would put the friendly king in check.

        Args:
            board (Board): The board object representing the chess board.
            moves (list[tuple[int, int]]): A list of possible moves for the piece.

        Returns:
            list[tuple[int, int]]: A list of possible moves that do not put the friendly king in check.
        """
        filtered_moves = []
        for move in moves:
            original_position = self.get_position()
            captured_piece = board.move_piece(self, move)

            king = board.white_king if self.colour == Colour.WHITE else board.black_king
            if not king.in_check(board):
                filtered_moves.append(move)
            board.undo_move(self, original_position, captured_piece)
        return filtered_moves

    def filter_in_check_moves(self, board: 'Board', moves: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """
        Filter out moves that would leave the friendly king in check.

        Args:
            board (Board): The board object representing the chess board.
            moves (list[tuple[int, int]]): A list of possible moves for the piece.

        Returns:
            list[tuple[int, int]]: A list of possible moves that block the check.
        """
        king = board.white_king if self.colour == Colour.WHITE else board.black_king

        if not king.in_check(board):
            return moves

        filtered_moves = []
        for move in moves:
            original_position = self.get_position()
            captured_piece = board.move_piece(self, move)
            if not king.in_check(board):
                filtered_moves.append(move)
            board.undo_move(self, original_position, captured_piece)
        return filtered_moves

    def get_fen_char(self) -> str:
        """
        Get the FEN character representing the piece.

        Returns:
            str: The FEN character representing the piece.
        """
        return 'PNBRQK'[self.piece_type.value] if self.colour == Colour.WHITE else 'pnbrqk'[self.piece_type.value]


class Pawn(Piece):
    """
    Class representing a pawn piece.

    Inherits attributes and methods from the Piece class.
    """

    def __init__(self, colour: Colour) -> None:
        """
        Initializes a pawn piece.

        Args:
            colour (Colour): The colour of the pawn.

        Returns:
            None
        """
        super().__init__(colour, PieceType.PAWN)

    def generate_moves(self, board: 'Board') -> list[tuple[int, int]]:
        """
        Generates a list of possible moves for the pawn.

        This method takes into account the special rules for pawn moves, such as double moves and captures.
        Args:
            board (Board): The board object representing the chess board.

        Returns:
            list[tuple[int, int]]: A list of possible moves for the pawn.
        """
        moves = []
        file, rank = self.get_position()
        direction = 1 if self.colour == Colour.WHITE else -1
        if board.get_piece(file, rank + direction) is None:
            moves.append((file, rank + direction))
            if (rank == 1 or rank == 6) and board.get_piece(file, rank + 2 * direction) is None:
                moves.append((file, rank + 2 * direction))
        for attack in [-1, 1]:
            target = board.get_piece(file + attack, rank + direction) if 0 <= file + attack < 8 else None
            if target is not None and target.colour != self.colour:
                moves.append((file + attack, rank + direction))

        moves = self.filter_self_check_moves(board, moves)
        moves = self.filter_in_check_moves(board, moves)

        self.moves = moves
        return moves


class Knight(Piece):
    """
    Class representing a knight piece.

    Inherits attributes and methods from the Piece class.
    """

    def __init__(self, colour: Colour) -> None:
        """
        Initializes a knight piece.

        Args:
            colour (Colour): The colour of the knight.

        Returns:
            None
        """
        super().__init__(colour, PieceType.KNIGHT)

    def generate_moves(self, board: 'Board') -> list[tuple[int, int]]:
        """
        Generates a list of possible moves for the knight.

        Args:
            board (Board): The board object representing the chess board.

        Returns:
            list[tuple[int, int]]: A list of possible moves for the knight.
        """
        moves = []
        file, rank = self.get_position()
        for dx, dy in [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]:
            if 0 <= file + dx < 8 and 0 <= rank + dy < 8:
                target = board.get_piece(file + dx, rank + dy)
                if target is None or target.colour != self.colour:
                    moves.append((file + dx, rank + dy))

        moves = self.filter_self_check_moves(board, moves)
        moves = self.filter_in_check_moves(board, moves)

        self.moves = moves
        return moves


class Bishop(Piece):
    """
    Class representing a bishop piece.

    Inherits attributes and methods from the Piece class.
    """

    def __init__(self, colour: Colour) -> None:
        super().__init__(colour, PieceType.BISHOP)

    def generate_moves(self, board: 'Board') -> list[tuple[int, int]]:
        """
        Generates a list of possible moves for the bishop.

        Args:
            board (Board): The board object representing the chess board.

        Returns:
            list[tuple[int, int]]: A list of possible moves for the bishop.
        """
        moves = []
        file, rank = self.get_position()
        for dx, dy in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
            x, y = file + dx, rank + dy
            while 0 <= x < 8 and 0 <= y < 8:
                target = board.get_piece(x, y)
                if target is None:
                    moves.append((x, y))
                elif target.colour != self.colour:
                    moves.append((x, y))
                    break
                else:
                    break
                x += dx
                y += dy

        moves = self.filter_self_check_moves(board, moves)
        moves = self.filter_in_check_moves(board, moves)

        self.moves = moves
        return moves


class Rook(Piece):
    """
    Class representing a rook piece.

    Inherits attributes and methods from the Piece class.
    """

    def __init__(self, colour: Colour) -> None:
        """
        Initializes a rook piece.

        Args:
            colour (Colour): The colour of the rook.

        Returns:
            None
        """
        super().__init__(colour, PieceType.ROOK)

    def generate_moves(self, board: 'Board') -> list[tuple[int, int]]:
        """
        Generates a list of possible moves for the rook.

        Args:
            board (Board): The board object representing the chess board.

        Returns:
            list[tuple[int, int]]: A list of possible moves for the rook.
        """
        moves = []
        file, rank = self.get_position()
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            x, y = file + dx, rank + dy
            while 0 <= x < 8 and 0 <= y < 8:
                target = board.get_piece(x, y)
                if target is None:
                    moves.append((x, y))
                elif target.colour != self.colour:
                    moves.append((x, y))
                    break
                else:
                    break
                x += dx
                y += dy

        moves = self.filter_self_check_moves(board, moves)
        moves = self.filter_in_check_moves(board, moves)

        self.moves = moves
        return moves


class Queen(Piece):
    """
    Class representing a queen piece.

    Inherits attributes and methods from the Piece class.
    """

    def __init__(self, colour: Colour) -> None:
        """
        Initializes a queen piece.

        Args:
            colour (Colour): The colour of the queen.

        Returns:
            None
        """
        super().__init__(colour, PieceType.QUEEN)

    def generate_moves(self, board: 'Board') -> list[tuple[int, int]]:
        """
        Generates a list of possible moves for the queen.

        Combines the moves of a rook and a bishop.

        Args:
            board (Board): The board object representing the chess board.

        Returns:
            list[tuple[int, int]]: A list of possible moves for the queen.
        """
        # Combine the moves of a rook and a bishop
        rook_moves = Rook.generate_moves(self, board)
        bishop_moves = Bishop.generate_moves(self, board)
        moves = rook_moves + bishop_moves
        moves = self.filter_self_check_moves(board, moves)
        self.moves = moves
        return self.moves


class King(Piece):
    """
    Class representing a king piece.

    Inherits attributes and methods from the Piece class.
    """

    def __init__(self, colour: Colour) -> None:
        """
        Initializes a king piece.

        Args:
            colour (Colour): The colour of the king.

        Returns:
            None
        """
        super().__init__(colour, PieceType.KING)

    def generate_moves(self, board: 'Board') -> list[tuple[int, int]]:
        """
        Generates a list of possible moves for the king.

        Args:
            board (Board): The board object representing the chess board.

        Returns:
            list[tuple[int, int]]: A list of possible moves for the king.
        """
        moves = []
        file, rank = self.get_position()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                x, y = file + dx, rank + dy
                if 0 <= x < 8 and 0 <= y < 8:
                    target = board.get_piece(x, y)
                    if target is None or target.colour != self.colour:
                        moves.append((x, y))

        moves = self.filter_self_check_moves(board, moves)
        moves = self.filter_in_check_moves(board, moves)

        self.moves = moves
        return moves

    def in_check(self, board: 'Board') -> bool:
        """
        Check if the king is in check.

        Args:
            board (Board): The board object representing the chess board.

        Returns:
            bool: True if the king is in check, False otherwise.
        """
        file, rank = self.get_position()

        # Check for bishops and queens
        for dx, dy in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
            x, y = file + dx, rank + dy
            while 0 <= x < 8 and 0 <= y < 8:
                target = board.get_piece(x, y)
                if target is not None:
                    if target.colour != self.colour and (target.piece_type == PieceType.BISHOP or target.piece_type == PieceType.QUEEN):
                        return True
                    break
                x += dx
                y += dy

        # Check for rooks and queens
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            x, y = file + dx, rank + dy
            while 0 <= x < 8 and 0 <= y < 8:
                target = board.get_piece(x, y)
                if target is not None:
                    if target.colour != self.colour and (target.piece_type == PieceType.ROOK or target.piece_type == PieceType.QUEEN):
                        return True
                    break
                x += dx
                y += dy

        # Check for knights
        for dx, dy in [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]:
            if 0 <= file + dx < 8 and 0 <= rank + dy < 8:
                target = board.get_piece(file + dx, rank + dy)
                if target is not None and target.colour != self.colour and target.piece_type == PieceType.KNIGHT:
                    return True

        # Check for pawns
        direction = 1 if self.colour == Colour.WHITE else -1
        for attack in [-1, 1]:
            target = board.get_piece(file + attack, rank + direction) if 0 <= file + attack < 8 else None
            if target is not None and target.colour != self.colour and target.piece_type == PieceType.PAWN:
                return True

        return False


# Map FEN characters directly to the piece classes
fen_to_class = {
    'p': Pawn,
    'n': Knight,
    'b': Bishop,
    'r': Rook,
    'q': Queen,
    'k': King
}
