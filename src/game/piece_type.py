from enum import Enum


class PieceType(Enum):
    """
    Enum representing the type of a piece.

    Each piece is encoded as a 4 bit number:
    """
    NONE = 0b0000
    PAWN = 0b0001
    KNIGHT = 0b0010
    BISHOP = 0b0011
    ROOK = 0b0100
    QUEEN = 0b0101
    KING = 0b0110
