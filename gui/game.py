import pygame
from board import Board

WIDTH = 800
HEIGHT = 800
ROWS = 8
COLS = 8
SQUARE = WIDTH // COLS

LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (246, 246, 105)


class ChessGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess")

        self.board = Board()
        self.board.setup_board()

        self.selected_square = None
        self.turn = "WHITE"

        self.images = {}
        self.load_images()

    def load_images(self):
        pieces = ["P", "R", "N", "B", "Q", "K"]
        colors = ["WHITE", "BLACK"]

        for color in colors:
            for piece in pieces:
                filename = f"{color[0].lower()}{piece.lower()}.png"
                path = f"assets/{filename}"
                image = pygame.image.load(path)
                image = pygame.transform.scale(image, (SQUARE, SQUARE))
                self.images[f"{color}_{piece}"] = image

    def draw_board(self):
        for row in range(ROWS):
            for col in range(COLS):
                color = LIGHT if (row + col) % 2 == 0 else DARK
                pygame.draw.rect(
                    self.screen,
                    color,
                    (col * SQUARE, row * SQUARE, SQUARE, SQUARE),
                )

        if self.selected_square:
            col = ord(self.selected_square[0]) - ord("a")
            row = 8 - int(self.selected_square[1])
            pygame.draw.rect(
                self.screen,
                HIGHLIGHT,
                (col * SQUARE, row * SQUARE, SQUARE, SQUARE),
            )

    def draw_pieces(self):
        for square, piece in self.board.squares.items():
            if piece:
                col = ord(square[0]) - ord("a")
                row = 8 - int(square[1])

                key = f"{piece.color}_{piece.symbol}"
                image = self.images.get(key)

                if image:
                    self.screen.blit(
                        image,
                        (col * SQUARE, row * SQUARE),
                    )

    def get_square_from_mouse(self, pos):
        x, y = pos
        col = x // SQUARE
        row = y // SQUARE
        file = chr(ord("a") + col)
        rank = str(8 - row)
        return file + rank

    def run(self):
        running = True

        while running:
            self.draw_board()
            self.draw_pieces()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    square = self.get_square_from_mouse(pygame.mouse.get_pos())

                    if self.selected_square is None:
                        piece = self.board.get_piece(square)
                        if piece and piece.color == self.turn:
                            self.selected_square = square
                    else:
                        try:
                            self.board.move_piece(self.selected_square, square)
                            self.turn = "BLACK" if self.turn == "WHITE" else "WHITE"
                        except Exception as e:
                            print("Illegal move:", e)

                        self.selected_square = None

        pygame.quit()