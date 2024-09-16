from src.game.piece import Color, PieceType, fen_to_class


class Board:
    def __init__(self, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.active_color = None
        self.castling_rights = None
        self.en_passant_square = None
        self.halfmove_clock = None
        self.fullmove_number = None
        self.white_king = None
        self.black_king = None
        self.game_active = True

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
        self.white_king = self.find_king(Color.WHITE)
        self.black_king = self.find_king(Color.BLACK)

    def find_king(self, color):
        for rank in range(8):
            for file in range(8):
                piece = self.get_piece(file, rank)
                if piece is not None and piece.color == color and piece.piece_type == PieceType.KING:
                    return piece
        return None

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

        # Check if the move is a capture
        captured_piece = self.get_piece(file, rank)

        # Move the piece to the new position
        self.set_piece(file, rank, piece)

        # Remove the piece from its previous position
        self.set_piece(piece.file, piece.rank, None)
        piece.set_position(file, rank)

        return captured_piece

    def undo_move(self, piece, original_position, captured_piece):
        original_file, original_rank = original_position
        current_file, current_rank = piece.get_position()

        # Move the piece back to its original position
        self.set_piece(original_file, original_rank, piece)
        piece.set_position(original_file, original_rank)

        # Restore the captured piece
        self.set_piece(current_file, current_rank, captured_piece)

    def update_game_state(self):
        self.active_color = Color.WHITE if self.active_color == Color.BLACK else Color.BLACK
        if self.active_color == Color.WHITE:
            self.fullmove_number += 1
        self.halfmove_clock += 1

    def is_king_in_checkmate(self, king):
        color = king.color
        # Loop through board, if piece is same color as king, check if it can move
        for rank in range(8):
            for file in range(8):
                piece = self.get_piece(file, rank)
                if piece is not None and piece.color == color:
                    moves = piece.generate_moves(self)
                    if moves:
                        return False
        return True
