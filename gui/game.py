import pygame
from board import Board

WIDTH = 640
HEIGHT = 640
SQUARE = WIDTH // 8

WHITE = (240, 217, 181)
BROWN = (181, 136, 99)


class ChessGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess")

        self.board = Board()
        self.board.setup_board()

        self.selected = None

        self.images = {}
        self.load_images()

    def load_images(self):
        pieces = ["P", "R", "N", "B", "Q", "K"]
        colors = ["WHITE", "BLACK"]

        for color in colors:
            for p in pieces:
                name = f"{color}_{p}"
                image = pygame.image.load(f"assets/{name}.png")
                self.images[name] = pygame.transform.scale(image, (SQUARE, SQUARE))

    def draw_board(self):
        for r in range(8):
            for c in range(8):
                color = WHITE if (r + c) % 2 == 0 else BROWN
                pygame.draw.rect(self.screen, color, (c * SQUARE, r * SQUARE, SQUARE, SQUARE))

    def draw_pieces(self):
        for square, piece in self.board.squares.items():
            if piece:
                col = "WHITE" if piece.color == "WHITE" else "BLACK"
                key = f"{col}_{piece.symbol}"
                x = ord(square[0]) - ord('a')
                y = 7 - (int(square[1]) - 1)
                self.screen.blit(self.images[key], (x * SQUARE, y * SQUARE))

    def get_square_from_mouse(self, pos):
        x, y = pos
        col = x // SQUARE
        row = y // SQUARE
        file = chr(ord('a') + col)
        rank = str(8 - row)
        return file + rank

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            clock.tick(60)
            self.draw_board()
            self.draw_pieces()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    square = self.get_square_from_mouse(pygame.mouse.get_pos())

                    if self.selected is None:
                        piece = self.board.get_piece(square)
                        if piece and piece.color == self.board.current_turn:
                            self.selected = square
                    else:
                        try:
                            self.board.move_piece(self.selected, square)
                        except:
                            pass
                        self.selected = None

            pygame.display.flip()

        pygame.quit()