
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
        self.moves = []
    
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
    
    def generate_moves(self, board):
        moves = []
        file, rank = self.get_position()
        direction = 1 if self.color == Color.WHITE else -1
        if board.get_piece(file, rank + direction) is None:
            moves.append((file, rank + direction))
            if (rank == 1 or rank == 6) and board.get_piece(file, rank + 2 * direction) is None:
                moves.append((file, rank + 2 * direction))
        for attack in [-1, 1]:
            target = board.get_piece(file + attack, rank + direction) if 0 <= file + attack < 8 else None
            if target is not None and target.color != self.color:
                moves.append((file + attack, rank + direction))
        self.moves = moves
        return moves


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color, PieceType.KNIGHT)
    
    def generate_moves(self, board):
        moves = []
        file, rank = self.get_position()
        for dx, dy in [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]:
            if 0 <= file + dx < 8 and 0 <= rank + dy < 8:
                target = board.get_piece(file + dx, rank + dy)
                if target is None or target.color != self.color:
                    moves.append((file + dx, rank + dy))
        self.moves = moves
        return moves

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color, PieceType.BISHOP)
    
    def generate_moves(self, board):
        moves = []
        file, rank = self.get_position()
        for dx, dy in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
            x, y = file + dx, rank + dy
            while 0 <= x < 8 and 0 <= y < 8:
                target = board.get_piece(x, y)
                if target is None:
                    moves.append((x, y))
                elif target.color != self.color:
                    moves.append((x, y))
                    break
                else:
                    break
                x += dx
                y += dy
        self.moves = moves
        return moves

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color, PieceType.ROOK)
    
    def generate_moves(self, board):
        moves = []
        file, rank = self.get_position()
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            x, y = file + dx, rank + dy
            while 0 <= x < 8 and 0 <= y < 8:
                target = board.get_piece(x, y)
                if target is None:
                    moves.append((x, y))
                elif target.color != self.color:
                    moves.append((x, y))
                    break
                else:
                    break
                x += dx
                y += dy
        self.moves = moves
        return moves

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color, PieceType.QUEEN)
    
    def generate_moves(self, board):
        # Combine the moves of a rook and a bishop
        rook_moves = Rook.generate_moves(self, board)
        bishop_moves = Bishop.generate_moves(self, board)
        self.moves = rook_moves + bishop_moves
        return self.moves

class King(Piece):
    def __init__(self, color):
        super().__init__(color, PieceType.KING)
    
    def generate_moves(self, board):
        moves = []
        file, rank = self.get_position()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                x, y = file + dx, rank + dy
                if 0 <= x < 8 and 0 <= y < 8:
                    target = board.get_piece(x, y)
                    if target is None or target.color != self.color:
                        moves.append((x, y))
        self.moves = moves
        return moves

# Map FEN characters directly to the piece classes
fen_to_class = {
    'p': Pawn,
    'n': Knight,
    'b': Bishop,
    'r': Rook,
    'q': Queen,
    'k': King
}