"""All screen drawing for the Fruit Slash runtime."""

from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

import pygame

from .config import BG, HEIGHT, WIDTH
from .entities import SliceHalf
from .fonts import Fonts
from .utils import clamp, lighten

if TYPE_CHECKING:
    from .game import Game


class Renderer:
    """Draw the background, entities, HUD, menus, and screen effects."""

    def __init__(self, fonts: Fonts) -> None:
        self.fonts = fonts

    def text(
        self,
        target: pygame.Surface,
        value: str,
        size: int,
        pos: tuple[int, int],
        color: tuple[int, int, int] = (255, 255, 255),
        center: bool = False,
        bold: bool = False,
    ) -> None:
        """Render one text label to a surface."""
        image = self.fonts.get(size, bold).render(value, True, color)
        rect = image.get_rect(center=pos) if center else image.get_rect(topleft=pos)
        target.blit(image, rect)

    def draw_background(self, target: pygame.Surface) -> None:
        """Draw the static stage backdrop."""
        target.fill(BG)
        pygame.draw.circle(target, (56, 25, 62), (WIDTH // 2, HEIGHT + 160), 560)
        pygame.draw.circle(target, (34, 18, 42), (WIDTH // 2, HEIGHT + 170), 455)
        for i in range(10):
            y = 90 + i * 60
            pygame.draw.line(target, (42, 25, 47), (0, y), (WIDTH, y + 35), 2)
        pygame.draw.line(target, (105, 55, 39), (0, HEIGHT - 18), (WIDTH, HEIGHT - 18), 8)

    def draw_half(self, target: pygame.Surface, half: SliceHalf) -> None:
        """Draw a sliced fruit half as a rotated temporary surface."""
        r = half.radius
        surf = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
        c = r * 3 // 2
        pygame.draw.circle(surf, half.skin, (c, c), r)
        pygame.draw.circle(surf, half.flesh, (c, c), r - 5)
        if half.side < 0:
            pygame.draw.rect(surf, (0, 0, 0, 0), (c, c - r - 2, r + 3, r * 2 + 4))
            pygame.draw.line(surf, lighten(half.flesh, 35), (c, c - r + 5), (c, c + r - 5), 4)
        else:
            pygame.draw.rect(surf, (0, 0, 0, 0), (c - r - 2, c - r - 2, r + 3, r * 2 + 4))
            pygame.draw.line(surf, lighten(half.flesh, 35), (c, c - r + 5), (c, c + r - 5), 4)
        rotated = pygame.transform.rotate(surf, half.angle)
        rotated.set_alpha(int(255 * clamp(half.life, 0, 1)))
        target.blit(rotated, rotated.get_rect(center=half.pos))

    def draw_trail(self, target: pygame.Surface, game: Game) -> None:
        """Draw the fading slash trail from recent pointer positions."""
        if len(game.trail) < 2:
            return
        layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(1, len(game.trail)):
            a, life = game.trail[i - 1]
            b, _ = game.trail[i]
            alpha = int(220 * clamp(life / 0.18, 0, 1))
            width = max(2, int(13 * i / len(game.trail)))
            pygame.draw.line(layer, (255, 246, 199, alpha), a, b, width)
            pygame.draw.circle(layer, (255, 255, 255, alpha), b, max(2, width // 3))
        target.blit(layer, (0, 0))

    def draw_hud(self, target: pygame.Surface, game: Game) -> None:
        """Draw score, lives, and short feedback messages."""
        self.text(target, str(game.score), 46, (32, 20), (255, 232, 137), bold=True)
        self.text(target, game.tr("分数", "SCORE"), 15, (35, 69), (198, 172, 186), bold=True)
        for i in range(3):
            x = WIDTH - 42 - i * 37
            color = (236, 62, 75) if i < game.lives else (68, 52, 63)
            pygame.draw.circle(target, color, (x, 40), 12)
            pygame.draw.line(target, (67, 126, 67), (x, 29), (x + 5, 23), 3)
        if game.message_timer > 0:
            scale = 1 + 0.12 * math.sin(game.message_timer * 18)
            self.text(target, game.message, int(42 * scale), (WIDTH // 2, 105), (255, 228, 90), center=True, bold=True)

    def draw_button(self, target: pygame.Surface, label: str, center: tuple[int, int]) -> pygame.Rect:
        """Draw a clickable menu button and return its hit rectangle."""
        rect = pygame.Rect(0, 0, 250, 64)
        rect.center = center
        hover = rect.collidepoint(pygame.mouse.get_pos())
        color = (255, 184, 48) if hover else (240, 137, 39)
        pygame.draw.rect(target, (66, 31, 31), rect.move(0, 6), border_radius=18)
        pygame.draw.rect(target, color, rect, border_radius=18)
        pygame.draw.rect(target, lighten(color, 28), rect.inflate(-8, -8), 2, border_radius=14)
        self.text(target, label, 28, rect.center, (43, 25, 25), center=True, bold=True)
        return rect

    def draw_menu(self, target: pygame.Surface, game: Game) -> None:
        """Draw the start screen and update the start button hit area."""
        self.text(target, game.tr("水果快斩", "FRUIT SLASH"), 76, (WIDTH // 2, 155), (255, 224, 102), center=True, bold=True)
        self.text(target, game.tr("按住鼠标划过水果，小心炸弹！", "Hold and swipe through fruit. Avoid bombs!"), 24, (WIDTH // 2, 235), (231, 211, 221), center=True)
        game.menu_button = self.draw_button(target, game.tr("开始游戏", "PLAY"), (WIDTH // 2, 355))
        self.text(target, game.tr(f"最高分  {game.best}", f"BEST  {game.best}"), 20, (WIDTH // 2, 417), (196, 167, 181), center=True)
        self.text(target, game.tr("鼠标拖动 / 触控滑动 · ESC 退出", "Mouse / touch to slash · ESC to quit"), 16, (WIDTH // 2, HEIGHT - 42), (132, 111, 125), center=True)

    def draw_gameover(self, target: pygame.Surface, game: Game) -> None:
        """Draw the game-over overlay and update the restart hit area."""
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((12, 7, 16, 178))
        target.blit(shade, (0, 0))
        self.text(target, game.tr("游戏结束", "GAME OVER"), 65, (WIDTH // 2, 185), (255, 213, 93), center=True, bold=True)
        self.text(target, game.tr(f"本局得分  {game.score}", f"SCORE  {game.score}"), 30, (WIDTH // 2, 265), center=True, bold=True)
        self.text(target, game.tr(f"最高分  {game.best}", f"BEST  {game.best}"), 20, (WIDTH // 2, 308), (205, 178, 192), center=True)
        game.restart_button = self.draw_button(target, game.tr("再来一局", "PLAY AGAIN"), (WIDTH // 2, 405))

    def draw(self, screen: pygame.Surface, game: Game) -> None:
        """Compose one frame and present it to the display."""
        canvas = pygame.Surface((WIDTH, HEIGHT))
        self.draw_background(canvas)
        for fruit in game.fruits:
            fruit.draw(canvas)
        for half in game.halves:
            self.draw_half(canvas, half)
        for particle in game.particles:
            particle.draw(canvas)
        self.draw_trail(canvas, game)
        if game.state in ("playing", "gameover"):
            self.draw_hud(canvas, game)
        if game.state == "menu":
            self.draw_menu(canvas, game)
        elif game.state == "gameover":
            self.draw_gameover(canvas, game)
        offset = (random.randint(-7, 7), random.randint(-7, 7)) if game.shake > 0 else (0, 0)
        screen.fill(BG)
        screen.blit(canvas, offset)
        if game.flash > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 111, 45, int(160 * game.flash / 0.5)))
            screen.blit(overlay, (0, 0))
        pygame.display.flip()

