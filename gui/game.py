from __future__ import annotations

import os
import math
import random
import pygame
from typing import Optional, List, Tuple

from board import Board, FILES, RANKS


Vec2 = pygame.math.Vector2


class Particle:
    def __init__(self, pos: Tuple[float, float]) -> None:
        self.pos = Vec2(pos)
        ang = random.uniform(0, math.tau)
        speed = random.uniform(140, 320)
        self.vel = Vec2(math.cos(ang), math.sin(ang)) * speed
        self.life = random.uniform(0.35, 0.7)
        self.age = 0.0
        self.size = random.randint(2, 5)

    def update(self, dt: float) -> None:
        self.age += dt
        self.vel.y += 520 * dt  # gravity
        self.pos += self.vel * dt

    @property
    def dead(self) -> bool:
        return self.age >= self.life


class Confetti:
    def __init__(self, w: int, h: int) -> None:
        self.w, self.h = w, h
        self.x = random.uniform(0, w)
        self.y = random.uniform(-h, 0)
        self.vy = random.uniform(120, 260)
        self.vx = random.uniform(-40, 40)
        self.size = random.randint(3, 7)
        self.life = random.uniform(1.2, 2.6)
        self.age = 0.0

    def update(self, dt: float) -> None:
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.y > self.h + 20:
            self.y = random.uniform(-60, -10)
            self.x = random.uniform(0, self.w)

    @property
    def dead(self) -> bool:
        return self.age >= self.life


class ChessGUI:
    """
    GUI features:
    - Hover: lift piece + highlight square
    - Click select (only your turn): show legal moves
      * green dots for empty targets
      * red overlay for capture targets
    - Second click on target -> move
    - Capture -> shard particles
    - Win (king captured) -> overlay + confetti + "Powered by Hirokiory"
    - Board state appended to board.txt after every successful move
    """

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Chess")

        # layout
        self.square = 96
        self.board_px = self.square * 8
        self.footer_h = 72
        self.w = self.board_px
        self.h = self.board_px + self.footer_h

        self.screen = pygame.display.set_mode((self.w, self.h))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.small = pygame.font.SysFont("Segoe UI", 18, bold=False)

        self.board = Board()
        self.board.setup_board()  # compatibility alias

        # state
        self.running = True
        self.hover_sq: Optional[str] = None
        self.selected_sq: Optional[str] = None
        self.legal_moves: List[str] = []

        self.white_captures = 0
        self.black_captures = 0

        self.particles: List[Particle] = []
        self.confetti: List[Confetti] = []
        self.game_over = False
        self.winner: Optional[str] = None

        # assets
        self.images = self._load_images()

        # Pre-save initial state (optional but useful)
        self.board.save_board("board.txt")

    def _load_images(self) -> dict:
        img = {}
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        assets_dir = os.path.normpath(assets_dir)

        keys = ["wP","wR","wN","wB","wQ","wK","bP","bR","bN","bB","bQ","bK"]
        for k in keys:
            path = os.path.join(assets_dir, f"{k}.png")
            if os.path.exists(path):
                surf = pygame.image.load(path).convert_alpha()
                surf = pygame.transform.smoothscale(surf, (self.square, self.square))
                img[k] = surf
        return img

    # ---------- coordinate helpers ----------

    def _xy_to_square(self, mx: int, my: int) -> Optional[str]:
        if mx < 0 or my < 0 or mx >= self.board_px or my >= self.board_px:
            return None
        file_i = mx // self.square
        rank_i = my // self.square
        # top-left is rank 8
        file_c = FILES[file_i]
        rank_c = RANKS[7 - rank_i]
        return f"{file_c}{rank_c}"

    def _square_to_rect(self, sq: str) -> pygame.Rect:
        file_i = FILES.index(sq[0])
        rank_i = RANKS.index(sq[1])
        x = file_i * self.square
        y = (7 - rank_i) * self.square
        return pygame.Rect(x, y, self.square, self.square)

    # ---------- interaction ----------

    def _select_square(self, sq: str) -> None:
        p = self.board.get_piece(sq)
        if p is None:
            self.selected_sq = None
            self.legal_moves = []
            return
        if getattr(p, "color", None) != self.board.turn:
            self.selected_sq = None
            self.legal_moves = []
            return
        self.selected_sq = sq
        self.legal_moves = self.board.get_legal_moves(sq)

    def _try_move(self, to_sq: str) -> None:
        if self.selected_sq is None:
            return
        if to_sq not in self.legal_moves:
            return

        # capture detection BEFORE move
        captured = self.board.get_piece(to_sq)

        ok = self.board.move_piece(self.selected_sq, to_sq)
        if not ok:
            return

        # save after move (PDF requirement style)
        self.board.save_board("board.txt")

        # capture count + particles + win check
        if captured is not None:
            if getattr(captured, "color", None) == "white":
                self.black_captures += 1
            else:
                self.white_captures += 1

            # shards at destination center
            r = self._square_to_rect(to_sq)
            cx, cy = r.centerx, r.centery
            for _ in range(26):
                self.particles.append(Particle((cx, cy)))

            # win if king captured (simple rule)
            if type(captured).__name__ == "King":
                self.game_over = True
                self.winner = "WHITE" if self.board.turn == "black" else "BLACK"
                self._start_confetti()

        # clear selection
        self.selected_sq = None
        self.legal_moves = []

    def _start_confetti(self) -> None:
        self.confetti = [Confetti(self.w, self.h) for _ in range(140)]

    # ---------- rendering ----------

    def _draw_board(self) -> None:
        light = (240, 218, 181)
        dark = (184, 133, 92)

        for r in range(8):
            for f in range(8):
                x = f * self.square
                y = r * self.square
                col = light if (r + f) % 2 == 0 else dark
                pygame.draw.rect(self.screen, col, (x, y, self.square, self.square))

        # hover highlight
        if self.hover_sq:
            rect = self._square_to_rect(self.hover_sq)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 3)

        # selected highlight
        if self.selected_sq:
            rect = self._square_to_rect(self.selected_sq)
            pygame.draw.rect(self.screen, (70, 170, 255), rect, 4)

    def _draw_moves_overlay(self) -> None:
        if not self.selected_sq:
            return
        for sq in self.legal_moves:
            rect = self._square_to_rect(sq)
            target = self.board.get_piece(sq)
            if target is None:
                # green dot
                cx, cy = rect.center
                pygame.draw.circle(self.screen, (40, 200, 90), (cx, cy), 12)
                pygame.draw.circle(self.screen, (20, 120, 55), (cx, cy), 12, 2)
            else:
                # capture square = red overlay
                s = pygame.Surface((self.square, self.square), pygame.SRCALPHA)
                s.fill((220, 60, 60, 90))
                self.screen.blit(s, rect.topleft)
                pygame.draw.rect(self.screen, (220, 60, 60), rect, 3)

    def _draw_pieces(self) -> None:
        # draw all pieces, lift hovered one slightly
        for sq, piece in self.board.squares.items():
            if piece is None:
                continue

            key = getattr(piece, "image_key", None)
            if not isinstance(key, str):
                continue

            img = self.images.get(key)
            if img is None:
                continue

            rect = self._square_to_rect(sq)
            lift = 0
            # lift only if hovering and it’s your turn piece
            if self.hover_sq == sq and getattr(piece, "color", None) == self.board.turn and not self.game_over:
                lift = -10

            self.screen.blit(img, (rect.x, rect.y + lift))

    def _draw_footer(self) -> None:
        y0 = self.board_px
        pygame.draw.rect(self.screen, (20, 20, 20), (0, y0, self.w, self.footer_h))

        turn_txt = f"Turn: {self.board.turn.upper()}"
        wcap = f"WHITE captures: {self.white_captures}"
        bcap = f"BLACK captures: {self.black_captures}"

        t1 = self.font.render(turn_txt, True, (255, 255, 255))
        t2 = self.font.render(wcap, True, (255, 255, 255))
        t3 = self.font.render(bcap, True, (255, 255, 255))

        self.screen.blit(t1, (16, y0 + 20))
        self.screen.blit(t2, (self.w // 2 - t2.get_width() // 2, y0 + 20))
        self.screen.blit(t3, (self.w - t3.get_width() - 16, y0 + 20))

    def _draw_particles(self) -> None:
        for p in self.particles:
            # shards as small rectangles
            pygame.draw.rect(self.screen, (235, 235, 235), (p.pos.x, p.pos.y, p.size, p.size))

    def _draw_game_over(self) -> None:
        if not self.game_over:
            return

        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        title = f"{self.winner} WIN!"
        t1 = pygame.font.SysFont("Segoe UI", 56, bold=True).render(title, True, (255, 255, 255))
        t2 = pygame.font.SysFont("Segoe UI", 22, bold=True).render("Congratulations!", True, (255, 255, 255))
        t3 = pygame.font.SysFont("Segoe UI", 18, bold=False).render("Powered by Hirokiory", True, (255, 255, 255))

        self.screen.blit(t1, (self.w // 2 - t1.get_width() // 2, self.h // 2 - 90))
        self.screen.blit(t2, (self.w // 2 - t2.get_width() // 2, self.h // 2 - 25))
        self.screen.blit(t3, (self.w // 2 - t3.get_width() // 2, self.h // 2 + 15))

    # ---------- main loop ----------

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEMOTION:
                    sq = self._xy_to_square(*event.pos)
                    self.hover_sq = sq

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.game_over:
                        # allow click to exit win screen quickly
                        self.running = False
                        continue

                    sq = self._xy_to_square(*event.pos)
                    if sq is None:
                        continue

                    if self.selected_sq is None:
                        self._select_square(sq)
                    else:
                        # second phase
                        if sq == self.selected_sq:
                            self.selected_sq = None
                            self.legal_moves = []
                        elif sq in self.legal_moves:
                            self._try_move(sq)
                        else:
                            # reselect if clicking another own piece
                            self._select_square(sq)

            # update particles
            self.particles = [p for p in self.particles if not p.dead]
            for p in self.particles:
                p.update(dt)

            # update confetti
            if self.game_over:
                self.confetti = [c for c in self.confetti if not c.dead]
                for c in self.confetti:
                    c.update(dt)

            # draw
            self._draw_board()
            self._draw_moves_overlay()
            self._draw_pieces()
            self._draw_particles()

            # confetti above everything
            if self.game_over:
                for c in self.confetti:
                    pygame.draw.rect(self.screen, (255, 255, 255), (c.x, c.y, c.size, c.size))
                self._draw_game_over()

            self._draw_footer()
            pygame.display.flip()

        pygame.quit()