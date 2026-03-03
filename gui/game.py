import pygame
import time
from board import Board

WIDTH = 800
PANEL = 80
HEIGHT = WIDTH + PANEL
SQUARE = WIDTH // 8

LIGHT = (240, 217, 181)
DARK = (181, 136, 99)

HOVER = (255, 255, 255, 40)    # RGBA overlay
SELECT = (255, 255, 0, 70)     # RGBA overlay

GREEN_DOT = (60, 180, 75)
RED = (220, 50, 50)


class Sawdust:
    """Small 'debris' effect for 2 seconds after capture."""
    def __init__(self, cx: int, cy: int):
        self.cx = cx
        self.cy = cy
        self.start = time.time()

    def alive(self) -> bool:
        return (time.time() - self.start) < 2.0

    def draw(self, screen):
        t = time.time() - self.start
        alpha = max(0, 220 - int(t * 110))  # fade out
        surf = pygame.Surface((SQUARE, SQUARE), pygame.SRCALPHA)

        for i in range(18):
            x = (i * 7 + int(t * 30)) % SQUARE
            y = (i * 11 + int(t * 25)) % SQUARE
            pygame.draw.circle(surf, (200, 200, 200, alpha), (x, y), 2)

        screen.blit(surf, (self.cx - SQUARE // 2, self.cy - SQUARE // 2))


class ChessGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess")

        self.board = Board()
        self.board.setup_board()

        self.turn = "WHITE"
        self.selected: str | None = None
        self.legal_moves: list[str] = []
        self.hover_sq: str | None = None

        self.images: dict[str, pygame.Surface] = {}
        self.load_images()

        self.font = pygame.font.SysFont("arial", 26)

        self.white_captures = 0
        self.black_captures = 0
        self.effects: list[Sawdust] = []

    def load_images(self):
        # expects assets: wP.png ... bK.png (case sensitive!)
        pieces = ["P", "R", "N", "B", "Q", "K"]
        for color in ("WHITE", "BLACK"):
            for p in pieces:
                filename = f"{color[0].lower()}{p.lower()}.png"  # wP.png style -> wp.png actually, we downloaded wP.png
                # Your files are named wP.png / bK.png (capital second letter). We must match that:
                filename = f"{color[0].lower()}{p}.png"  # wP.png, bK.png
                img = pygame.image.load(f"assets/{filename}")
                self.images[f"{color}_{p}"] = pygame.transform.scale(img, (SQUARE, SQUARE))

    def square_from_mouse(self, pos):
        x, y = pos
        if y >= WIDTH:
            return None
        col = x // SQUARE
        row = y // SQUARE
        file = chr(ord("a") + col)
        rank = str(8 - row)
        return file + rank

    def square_to_screen_xy(self, square: str) -> tuple[int, int]:
        col = ord(square[0]) - ord("a")
        row = 8 - int(square[1])
        return col * SQUARE, row * SQUARE

    def draw_board(self):
        for r in range(8):
            for c in range(8):
                color = LIGHT if (r + c) % 2 == 0 else DARK
                pygame.draw.rect(self.screen, color, (c * SQUARE, r * SQUARE, SQUARE, SQUARE))

        # hover highlight (square overlay)
        if self.hover_sq:
            x, y = self.square_to_screen_xy(self.hover_sq)
            surf = pygame.Surface((SQUARE, SQUARE), pygame.SRCALPHA)
            surf.fill(HOVER)
            self.screen.blit(surf, (x, y))

        # selected highlight (square overlay)
        if self.selected:
            x, y = self.square_to_screen_xy(self.selected)
            surf = pygame.Surface((SQUARE, SQUARE), pygame.SRCALPHA)
            surf.fill(SELECT)
            self.screen.blit(surf, (x, y))

    def draw_move_hints(self):
        # pulsing for capture squares
        pulse = 0.5 + 0.5 * (pygame.time.get_ticks() % 800) / 800.0  # 0..1
        thickness = 3 + int(pulse * 3)

        for sq in self.legal_moves:
            x, y = self.square_to_screen_xy(sq)
            target = self.board.get_piece(sq)

            if target is None:
                pygame.draw.circle(self.screen, GREEN_DOT, (x + SQUARE // 2, y + SQUARE // 2), 10)
            else:
                pygame.draw.rect(self.screen, RED, (x + 4, y + 4, SQUARE - 8, SQUARE - 8), thickness)

    def draw_pieces(self):
        selected_piece = None

        # draw all except selected (so selected can be drawn "lifted" last)
        for sq, piece in self.board.squares.items():
            if piece is None:
                continue
            if self.selected == sq:
                selected_piece = (sq, piece)
                continue

            x, y = self.square_to_screen_xy(sq)
            img = self.images.get(f"{piece.color}_{piece.symbol}")
            if img:
                self.screen.blit(img, (x, y))

        # draw selected lifted with shadow
        if selected_piece:
            sq, piece = selected_piece
            x, y = self.square_to_screen_xy(sq)

            # shadow
            shadow = pygame.Surface((SQUARE, SQUARE), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 90), (18, 56, 44, 14))
            self.screen.blit(shadow, (x, y))

            img = self.images.get(f"{piece.color}_{piece.symbol}")
            if img:
                self.screen.blit(img, (x, y - 10))

    def draw_panel(self):
        pygame.draw.rect(self.screen, (30, 30, 30), (0, WIDTH, WIDTH, PANEL))

        txt1 = self.font.render(f"Turn: {self.turn}", True, (255, 255, 255))
        self.screen.blit(txt1, (12, WIDTH + 10))

        txt2 = self.font.render(f"WHITE captures: {self.white_captures}", True, (255, 255, 255))
        self.screen.blit(txt2, (220, WIDTH + 10))

        txt3 = self.font.render(f"BLACK captures: {self.black_captures}", True, (255, 255, 255))
        self.screen.blit(txt3, (520, WIDTH + 10))

    def update_effects(self):
        self.effects = [e for e in self.effects if e.alive()]
        for e in self.effects:
            e.draw(self.screen)

    def on_click(self, sq: str | None):
        if sq is None:
            return

        # 1) no selection: try select own piece
        if self.selected is None:
            piece = self.board.get_piece(sq)
            if piece and piece.color == self.turn:
                self.selected = sq
                self.legal_moves = self.board.get_legal_moves(sq)
            return

        # 2) click same square -> deselect
        if sq == self.selected:
            self.selected = None
            self.legal_moves = []
            return

        # 3) attempt move if legal
        if sq in self.legal_moves:
            captured = self.board.get_piece(sq)

            try:
                self.board.move_piece(self.selected, sq)

                if captured is not None:
                    x, y = self.square_to_screen_xy(sq)
                    self.effects.append(Sawdust(x + SQUARE // 2, y + SQUARE // 2))

                    if self.turn == "WHITE":
                        self.white_captures += 1
                    else:
                        self.black_captures += 1

                # switch turn
                self.turn = "BLACK" if self.turn == "WHITE" else "WHITE"

            except Exception:
                pass

        # deselect always after second click
        self.selected = None
        self.legal_moves = []

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            clock.tick(60)

            self.hover_sq = self.square_from_mouse(pygame.mouse.get_pos())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    sq = self.square_from_mouse(pygame.mouse.get_pos())
                    self.on_click(sq)

            self.screen.fill((0, 0, 0))
            self.draw_board()

            if self.selected:
                self.draw_move_hints()

            self.draw_pieces()
            self.update_effects()
            self.draw_panel()

            pygame.display.flip()

        pygame.quit()