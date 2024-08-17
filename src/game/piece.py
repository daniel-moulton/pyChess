
# Class definition for the Piece class
# Pieces are stored in a 2D array in the Board class
# Each piece is represented as a 5 bit number
# The first bit is the color of the piece (0 for white, 1 for black)
# The following 4 bits represent the type of the piece (0 for none, 1 for pawn, 2 for knight, 3 for bishop, 4 for rook, 5 for queen, 6 for king)

from enum import Enum

class Color(Enum):
    WHITE = 0b1000
    BLACK = 0b0000

class PieceType(Enum):
    NONE = 0b0000
    PAWN = 0b0001
    KNIGHT = 0b0010
    BISHOP = 0b0011
    ROOK = 0b0100
    QUEEN = 0b0101
    KING = 0b0110


class Piece:
    def __init__(self, color, piece_type=PieceType.NONE):
        self.piece_type = piece_type
        self.color = color
        self.rank = None
        self.file = None
    
    def encode(self):
        return self.color.value | self.piece_type.value
    
    def generate_moves(self, board, file, rank):
        raise NotImplementedError
    
    def get_position(self):
        return self.file, self.rank
    
    def set_position(self, file, rank):
        self.file = file
        self.rank = rank
    
    def __str__(self):
        return f'{self.color.name} {self.piece_type.name}'
    

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color, PieceType.PAWN)

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color, PieceType.KNIGHT)

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color, PieceType.BISHOP)

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color, PieceType.ROOK)

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color, PieceType.QUEEN)

class King(Piece):
    def __init__(self, color):
        super().__init__(color, PieceType.KING)

# Map FEN characters directly to the piece classes
fen_to_class = {
    'p': Pawn,
    'n': Knight,
    'b': Bishop,
    'r': Rook,
    'q': Queen,
    'k': King
}