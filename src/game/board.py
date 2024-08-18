from src.game.piece import Color, Piece, PieceType, fen_to_class

class Board:
    def __init__(self, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.active_color = None
        self.castling_rights = None
        self.en_passant_square = None
        self.halfmove_clock = None
        self.fullmove_number = None

        self.parse_fen(fen)
    
    def __str__(self):
        board_str = ''
        for rank in range(7, -1, -1):
            for file in range(8):
                piece = self.get_piece(file, rank)
                board_str += str(piece).ljust(12)
            board_str += '\n'
        return board_str
    
    def get_piece(self, file, rank):
        return self.board[rank][file]
    
    def set_piece(self, file, rank, piece):
        self.board[rank][file] = piece
    
    def get_board(self):
        return self.board
    
    def parse_fen(self, fen):
        parts = fen.split()
        self.load_fen(parts[0])
        self.active_color = Color.WHITE if parts[1] == 'w' else Color.BLACK
        self.castling_rights = parts[2]
        self.en_passant_square = parts[3]
        self.halfmove_clock = int(parts[4])
        self.fullmove_number = int(parts[5])

    def load_fen(self, fen):
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

    # Creates a piece object and sets its position
    def create_piece(self, char, file, rank):
        color = Color.WHITE if char.isupper() else Color.BLACK
        piece_class = fen_to_class[char.lower()]
        piece = piece_class(color)
        piece.set_position(file, rank)
        return piece
    
    def move_piece(self, piece, destination):
        file, rank = destination
        self.set_piece(file, rank, piece)
        self.set_piece(piece.file, piece.rank, None)
        piece.set_position(file, rank)
        if piece.piece_type == PieceType.PAWN:
            self.halfmove_clock = 0
            # Check for promotion
            if rank == 0 or rank == 7:
                char = 'Q' if piece.color == Color.WHITE else 'q'
                piece = self.create_piece(char, file, rank)
                self.set_piece(file, rank, piece)
        


        self.halfmove_clock += 1
        self.active_color = Color.WHITE if self.active_color == Color.BLACK else Color.BLACK

    