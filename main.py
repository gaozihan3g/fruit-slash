"""Fruit Slash - a small Fruit Ninja inspired pygame game."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path

import pygame
from pygame import Vector2


WIDTH, HEIGHT = 960, 640
FPS = 60
GRAVITY = 720
BG = (20, 13, 25)


FRUITS = {
    "watermelon": ((55, 183, 96), (239, 73, 92), 44),
    "orange": ((247, 147, 30), (255, 202, 66), 34),
    "apple": ((224, 54, 63), (255, 235, 188), 36),
    "kiwi": ((126, 166, 63), (206, 225, 132), 33),
    "blueberry": ((74, 76, 181), (161, 157, 232), 28),
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def segment_circle_hit(a: Vector2, b: Vector2, center: Vector2, radius: float) -> bool:
    ab = b - a
    if ab.length_squared() == 0:
        return center.distance_to(a) <= radius
    t = clamp((center - a).dot(ab) / ab.length_squared(), 0, 1)
    return center.distance_to(a + ab * t) <= radius


def lighten(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    return tuple(min(255, c + amount) for c in color)


class Fonts:
    def __init__(self) -> None:
        candidates = ["PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", "Arial Unicode MS"]
        path = next((pygame.font.match_font(name) for name in candidates if pygame.font.match_font(name)), None)
        self.has_chinese = path is not None
        self.path = path

    def get(self, size: int, bold: bool = False) -> pygame.font.Font:
        font = pygame.font.Font(self.path, size)
        font.set_bold(bold)
        return font


@dataclass
class Particle:
    pos: Vector2
    vel: Vector2
    color: tuple[int, int, int]
    life: float
    size: float

    def update(self, dt: float) -> bool:
        self.life -= dt
        self.vel.y += GRAVITY * 0.36 * dt
        self.pos += self.vel * dt
        self.size *= 0.985
        return self.life > 0

    def draw(self, screen: pygame.Surface) -> None:
        radius = max(1, int(self.size))
        pygame.draw.circle(screen, self.color, self.pos, radius)


@dataclass
class SliceHalf:
    pos: Vector2
    vel: Vector2
    radius: int
    skin: tuple[int, int, int]
    flesh: tuple[int, int, int]
    side: int
    angle: float
    spin: float
    life: float = 1.5

    def update(self, dt: float) -> bool:
        self.life -= dt
        self.vel.y += GRAVITY * dt
        self.pos += self.vel * dt
        self.angle += self.spin * dt
        return self.life > 0 and self.pos.y < HEIGHT + self.radius * 3


class Fruit:
    def __init__(self, x: float, kind: str, difficulty: float) -> None:
        self.kind = kind
        self.skin, self.flesh, self.radius = FRUITS[kind]
        self.pos = Vector2(x, HEIGHT + self.radius)
        self.vel = Vector2(random.uniform(-105, 105), random.uniform(-820, -680) - difficulty * 18)
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-190, 190)
        self.sliced = False
        self.counted_miss = False

    def update(self, dt: float) -> None:
        self.vel.y += GRAVITY * dt
        self.pos += self.vel * dt
        self.angle += self.spin * dt

    def draw(self, screen: pygame.Surface) -> None:
        r = self.radius
        x, y = int(self.pos.x), int(self.pos.y)
        shadow = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0, 0, 0, 65), (r * 3 // 2 + 5, r * 3 // 2 + 7), r)
        screen.blit(shadow, (x - r * 3 // 2, y - r * 3 // 2))
        pygame.draw.circle(screen, self.skin, (x, y), r)
        pygame.draw.circle(screen, lighten(self.skin, 38), (x - r // 3, y - r // 3), max(3, r // 7))
        pygame.draw.arc(screen, (255, 255, 255, 85), (x-r+6, y-r+6, 2*r-12, 2*r-12), 2.0, 3.8, 3)
        stem_end = Vector2(0, -r - 10).rotate(-self.angle)
        pygame.draw.line(screen, (83, 55, 29), self.pos + stem_end * 0.7, self.pos + stem_end, 5)
        if self.kind == "watermelon":
            for offset in (-0.45, 0, 0.45):
                pygame.draw.arc(screen, (29, 116, 62), (x-r, y-r + int(offset*r), 2*r, 2*r), 0.25, 2.9, 3)


class Bomb(Fruit):
    def __init__(self, x: float, difficulty: float) -> None:
        self.kind = "bomb"
        self.radius = 32
        self.pos = Vector2(x, HEIGHT + self.radius)
        self.vel = Vector2(random.uniform(-90, 90), random.uniform(-790, -680) - difficulty * 12)
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-160, 160)
        self.sliced = False
        self.counted_miss = False

    def draw(self, screen: pygame.Surface) -> None:
        x, y, r = int(self.pos.x), int(self.pos.y), self.radius
        pygame.draw.circle(screen, (8, 7, 10), (x + 5, y + 7), r + 2)
        pygame.draw.circle(screen, (47, 43, 51), (x, y), r)
        pygame.draw.circle(screen, (90, 82, 93), (x - 9, y - 10), 8)
        pygame.draw.line(screen, (126, 84, 46), (x + 17, y - 22), (x + 26, y - 39), 5)
        glow = 5 + int(3 * math.sin(pygame.time.get_ticks() * 0.02))
        pygame.draw.circle(screen, (255, 215, 70), (x + 27, y - 41), glow + 3)
        pygame.draw.circle(screen, (255, 82, 35), (x + 27, y - 41), glow)
        pygame.draw.circle(screen, (245, 238, 215), (x - 8, y - 5), 3)


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Fruit Slash")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.fonts = Fonts()
        self.state = "menu"
        self.best = self.load_best()
        self.reset()

    @property
    def zh(self) -> bool:
        return self.fonts.has_chinese

    def tr(self, chinese: str, english: str) -> str:
        return chinese if self.zh else english

    def load_best(self) -> int:
        path = Path(__file__).with_name("highscore.txt")
        try:
            return int(path.read_text().strip())
        except (OSError, ValueError):
            return 0

    def save_best(self) -> None:
        try:
            Path(__file__).with_name("highscore.txt").write_text(str(self.best))
        except OSError:
            pass

    def reset(self) -> None:
        self.score = 0
        self.lives = 3
        self.elapsed = 0.0
        self.spawn_timer = 0.45
        self.fruits: list[Fruit] = []
        self.particles: list[Particle] = []
        self.halves: list[SliceHalf] = []
        self.trail: list[tuple[Vector2, float]] = []
        self.combo = 0
        self.combo_timer = 0.0
        self.flash = 0.0
        self.shake = 0.0
        self.message = ""
        self.message_timer = 0.0

    def start(self) -> None:
        self.reset()
        self.state = "playing"

    def spawn_wave(self) -> None:
        difficulty = min(8.0, self.elapsed / 16)
        count = random.choices([1, 2, 3], weights=[55, 34, 11 + difficulty * 2])[0]
        positions = random.sample(range(90, WIDTH - 90), count)
        for x in positions:
            kind = random.choice(list(FRUITS))
            self.fruits.append(Fruit(x, kind, difficulty))
        bomb_chance = min(0.32, 0.09 + self.elapsed / 260)
        if self.elapsed > 5 and random.random() < bomb_chance:
            self.fruits.append(Bomb(random.randint(100, WIDTH - 100), difficulty))
        self.spawn_timer = max(0.42, 0.92 - difficulty * 0.045) * random.uniform(0.82, 1.16)

    def slice_fruit(self, fruit: Fruit, slash_velocity: Vector2) -> None:
        fruit.sliced = True
        if fruit.kind == "bomb":
            self.lives = 0
            self.flash = 0.5
            self.shake = 0.8
            self.message = self.tr("炸弹！", "BOOM!")
            self.message_timer = 1.0
            for _ in range(55):
                angle = random.uniform(0, math.tau)
                speed = random.uniform(90, 470)
                color = random.choice([(255, 184, 48), (244, 68, 36), (72, 65, 70)])
                self.particles.append(Particle(fruit.pos.copy(), Vector2(math.cos(angle), math.sin(angle))*speed, color, random.uniform(.4, 1), random.uniform(3, 8)))
            return

        self.combo = self.combo + 1 if self.combo_timer > 0 else 1
        self.combo_timer = 0.48
        gained = 10 + max(0, self.combo - 1) * 2
        self.score += gained
        if self.combo >= 3:
            self.message = self.tr(f"{self.combo} 连击!", f"{self.combo} COMBO!")
            self.message_timer = 0.7
        direction = slash_velocity.normalize() if slash_velocity.length_squared() else Vector2(1, 0)
        normal = Vector2(-direction.y, direction.x)
        for side in (-1, 1):
            self.halves.append(SliceHalf(fruit.pos + normal * side * 7, fruit.vel * .55 + normal * side * 150, fruit.radius, fruit.skin, fruit.flesh, side, fruit.angle, fruit.spin + side * 140))
        for _ in range(20):
            vel = normal * random.uniform(-230, 230) + direction * random.uniform(-60, 90)
            vel += Vector2(random.uniform(-80, 80), random.uniform(-80, 80))
            self.particles.append(Particle(fruit.pos.copy(), vel, fruit.flesh, random.uniform(.35, .8), random.uniform(2, 6)))

    def update(self, dt: float) -> None:
        self.flash = max(0, self.flash - dt)
        self.shake = max(0, self.shake - dt)
        self.message_timer = max(0, self.message_timer - dt)
        self.trail = [(p, life - dt) for p, life in self.trail if life - dt > 0]
        self.particles = [p for p in self.particles if p.update(dt)]
        self.halves = [h for h in self.halves if h.update(dt)]
        if self.state != "playing":
            return
        self.elapsed += dt
        self.combo_timer = max(0, self.combo_timer - dt)
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_wave()
        for fruit in self.fruits:
            fruit.update(dt)
            if fruit.pos.y > HEIGHT + fruit.radius * 1.5 and fruit.vel.y > 0 and not fruit.counted_miss:
                fruit.counted_miss = True
                if fruit.kind != "bomb" and not fruit.sliced:
                    self.lives -= 1
                    self.combo = 0
                    self.message = self.tr("漏掉了！", "MISSED!")
                    self.message_timer = .65
        self.fruits = [f for f in self.fruits if not f.sliced and f.pos.y < HEIGHT + f.radius * 2]
        if self.lives <= 0:
            self.state = "gameover"
            self.best = max(self.best, self.score)
            self.save_best()

    def handle_slice(self, pos: Vector2) -> None:
        previous = self.trail[-1][0] if self.trail else pos
        self.trail.append((pos, .18))
        velocity = pos - previous
        if velocity.length_squared() < 20:
            return
        for fruit in self.fruits:
            if not fruit.sliced and segment_circle_hit(previous, pos, fruit.pos, fruit.radius + 4):
                self.slice_fruit(fruit, velocity)

    def draw_background(self, target: pygame.Surface) -> None:
        target.fill(BG)
        pygame.draw.circle(target, (56, 25, 62), (WIDTH // 2, HEIGHT + 160), 560)
        pygame.draw.circle(target, (34, 18, 42), (WIDTH // 2, HEIGHT + 170), 455)
        for i in range(10):
            y = 90 + i * 60
            pygame.draw.line(target, (42, 25, 47), (0, y), (WIDTH, y + 35), 2)
        pygame.draw.line(target, (105, 55, 39), (0, HEIGHT - 18), (WIDTH, HEIGHT - 18), 8)

    def draw_half(self, target: pygame.Surface, half: SliceHalf) -> None:
        r = half.radius
        surf = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
        c = r * 3 // 2
        rect = pygame.Rect(c-r, c-r, r*2, r*2)
        pygame.draw.circle(surf, half.skin, (c, c), r)
        pygame.draw.circle(surf, half.flesh, (c, c), r-5)
        if half.side < 0:
            pygame.draw.rect(surf, (0, 0, 0, 0), (c, c-r-2, r+3, r*2+4))
            pygame.draw.line(surf, lighten(half.flesh, 35), (c, c-r+5), (c, c+r-5), 4)
        else:
            pygame.draw.rect(surf, (0, 0, 0, 0), (c-r-2, c-r-2, r+3, r*2+4))
            pygame.draw.line(surf, lighten(half.flesh, 35), (c, c-r+5), (c, c+r-5), 4)
        rotated = pygame.transform.rotate(surf, half.angle)
        rotated.set_alpha(int(255 * clamp(half.life, 0, 1)))
        target.blit(rotated, rotated.get_rect(center=half.pos))

    def text(self, target: pygame.Surface, value: str, size: int, pos: tuple[int, int], color=(255,255,255), center=False, bold=False) -> None:
        image = self.fonts.get(size, bold).render(value, True, color)
        rect = image.get_rect(center=pos) if center else image.get_rect(topleft=pos)
        target.blit(image, rect)

    def draw_trail(self, target: pygame.Surface) -> None:
        if len(self.trail) < 2:
            return
        layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(1, len(self.trail)):
            a, life = self.trail[i-1]
            b, _ = self.trail[i]
            alpha = int(220 * clamp(life / .18, 0, 1))
            width = max(2, int(13 * i / len(self.trail)))
            pygame.draw.line(layer, (255, 246, 199, alpha), a, b, width)
            pygame.draw.circle(layer, (255, 255, 255, alpha), b, max(2, width//3))
        target.blit(layer, (0, 0))

    def draw_hud(self, target: pygame.Surface) -> None:
        self.text(target, str(self.score), 46, (32, 20), (255, 232, 137), bold=True)
        self.text(target, self.tr("分数", "SCORE"), 15, (35, 69), (198, 172, 186), bold=True)
        for i in range(3):
            x = WIDTH - 42 - i * 37
            color = (236, 62, 75) if i < self.lives else (68, 52, 63)
            pygame.draw.circle(target, color, (x, 40), 12)
            pygame.draw.line(target, (67, 126, 67), (x, 29), (x+5, 23), 3)
        if self.message_timer > 0:
            scale = 1 + .12 * math.sin(self.message_timer * 18)
            self.text(target, self.message, int(42*scale), (WIDTH//2, 105), (255, 228, 90), center=True, bold=True)

    def draw(self) -> None:
        canvas = pygame.Surface((WIDTH, HEIGHT))
        self.draw_background(canvas)
        for fruit in self.fruits:
            fruit.draw(canvas)
        for half in self.halves:
            self.draw_half(canvas, half)
        for particle in self.particles:
            particle.draw(canvas)
        self.draw_trail(canvas)
        if self.state in ("playing", "gameover"):
            self.draw_hud(canvas)
        if self.state == "menu":
            self.draw_menu(canvas)
        elif self.state == "gameover":
            self.draw_gameover(canvas)
        offset = (random.randint(-7, 7), random.randint(-7, 7)) if self.shake > 0 else (0, 0)
        self.screen.fill(BG)
        self.screen.blit(canvas, offset)
        if self.flash > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 111, 45, int(160 * self.flash / .5)))
            self.screen.blit(overlay, (0, 0))
        pygame.display.flip()

    def draw_button(self, target: pygame.Surface, label: str, center: tuple[int, int]) -> pygame.Rect:
        rect = pygame.Rect(0, 0, 250, 64)
        rect.center = center
        hover = rect.collidepoint(pygame.mouse.get_pos())
        color = (255, 184, 48) if hover else (240, 137, 39)
        pygame.draw.rect(target, (66, 31, 31), rect.move(0, 6), border_radius=18)
        pygame.draw.rect(target, color, rect, border_radius=18)
        pygame.draw.rect(target, lighten(color, 28), rect.inflate(-8, -8), 2, border_radius=14)
        self.text(target, label, 28, rect.center, (43, 25, 25), center=True, bold=True)
        return rect

    def draw_menu(self, target: pygame.Surface) -> None:
        self.text(target, self.tr("水果快斩", "FRUIT SLASH"), 76, (WIDTH//2, 155), (255, 224, 102), center=True, bold=True)
        self.text(target, self.tr("按住鼠标划过水果，小心炸弹！", "Hold and swipe through fruit. Avoid bombs!"), 24, (WIDTH//2, 235), (231, 211, 221), center=True)
        self.menu_button = self.draw_button(target, self.tr("开始游戏", "PLAY"), (WIDTH//2, 355))
        self.text(target, self.tr(f"最高分  {self.best}", f"BEST  {self.best}"), 20, (WIDTH//2, 417), (196, 167, 181), center=True)
        self.text(target, self.tr("鼠标拖动 / 触控滑动 · ESC 退出", "Mouse / touch to slash · ESC to quit"), 16, (WIDTH//2, HEIGHT-42), (132, 111, 125), center=True)

    def draw_gameover(self, target: pygame.Surface) -> None:
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((12, 7, 16, 178))
        target.blit(shade, (0, 0))
        self.text(target, self.tr("游戏结束", "GAME OVER"), 65, (WIDTH//2, 185), (255, 213, 93), center=True, bold=True)
        self.text(target, self.tr(f"本局得分  {self.score}", f"SCORE  {self.score}"), 30, (WIDTH//2, 265), center=True, bold=True)
        self.text(target, self.tr(f"最高分  {self.best}", f"BEST  {self.best}"), 20, (WIDTH//2, 308), (205, 178, 192), center=True)
        self.restart_button = self.draw_button(target, self.tr("再来一局", "PLAY AGAIN"), (WIDTH//2, 405))

    def run(self) -> None:
        running = True
        while running:
            dt = min(self.clock.tick(FPS) / 1000, .035)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if self.state != "playing":
                            self.start()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "menu" and getattr(self, "menu_button", pygame.Rect(0,0,0,0)).collidepoint(event.pos):
                        self.start()
                    elif self.state == "gameover" and getattr(self, "restart_button", pygame.Rect(0,0,0,0)).collidepoint(event.pos):
                        self.start()
                    elif self.state == "playing":
                        self.trail = [(Vector2(event.pos), .18)]
                elif event.type == pygame.MOUSEMOTION and self.state == "playing" and pygame.mouse.get_pressed()[0]:
                    self.handle_slice(Vector2(event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.trail.clear()
            self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
