import pygame
import random
from board import Board

WIDTH = 800
HEIGHT = 800
ROWS = 8
COLS = 8
SQUARE = WIDTH // COLS

LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (246, 246, 105)


class Confetti:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.randint(3, 7)
        self.color = random.choice([
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (255, 0, 255),
            (0, 255, 255),
        ])

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = random.randint(-50, 0)
            self.x = random.randint(0, WIDTH)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 4)


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

        self.winner = None
        self.confetti = [Confetti() for _ in range(150)]

        self.big_font = pygame.font.SysFont("arial", 72)
        self.small_font = pygame.font.SysFont("arial", 32)

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

    def draw_victory_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        for c in self.confetti:
            c.update()
            c.draw(self.screen)

        text = self.big_font.render("YOU WIN!", True, (255, 215, 0))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(text, rect)

        sub = self.small_font.render("Powered by Heorhii Horokh", True, (255, 255, 255))
        sub_rect = sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        self.screen.blit(sub, sub_rect)

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

            if self.winner:
                self.draw_victory_screen()

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN and not self.winner:
                    square = self.get_square_from_mouse(pygame.mouse.get_pos())

                    if self.selected_square is None:
                        piece = self.board.get_piece(square)
                        if piece and piece.color == self.turn:
                            self.selected_square = square
                    else:
                        try:
                            target = self.board.get_piece(square)
                            self.board.move_piece(self.selected_square, square)

                            # если убили короля — победа
                            if target and target.symbol == "K":
                                self.winner = self.turn

                            self.turn = "BLACK" if self.turn == "WHITE" else "WHITE"

                        except Exception as e:
                            print("Illegal move:", e)

                        self.selected_square = None

        pygame.quit()