"""Core game state, rules, update loop, and runtime coordination."""

from __future__ import annotations

import math
import random

import pygame
from pygame import Vector2

from .config import FPS, FRUITS, HEIGHT, WIDTH
from .entities import Bomb, Fruit, Particle, SliceHalf
from .fonts import Fonts
from .input import handle_event
from .renderer import Renderer
from .storage import load_highscore, save_highscore, user_data_file
from .utils import segment_circle_hit


class Game:
    """Coordinate pygame setup, game state, rules, input, and rendering."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Fruit Slash")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.fonts = Fonts()
        self.renderer = Renderer(self.fonts)
        self.state = "menu"
        self.highscore_path = user_data_file("highscore.txt")
        self.best = load_highscore(self.highscore_path)
        self.reset()

    @property
    def zh(self) -> bool:
        """Return whether the selected font can render Chinese UI labels."""
        return self.fonts.has_chinese

    def tr(self, chinese: str, english: str) -> str:
        """Pick localized UI text based on available font support."""
        return chinese if self.zh else english

    def save_best(self) -> None:
        """Persist the current best score."""
        save_highscore(self.highscore_path, self.best)

    def reset(self) -> None:
        """Reset all per-run gameplay state before a new match starts."""
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
        """Start a fresh run from the menu or game-over screen."""
        self.reset()
        self.state = "playing"

    def spawn_wave(self) -> None:
        """Spawn a difficulty-scaled wave of fruit and occasional bombs."""
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
        """Apply scoring, combo, particle, split, or bomb effects for a hit."""
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
                velocity = Vector2(math.cos(angle), math.sin(angle)) * speed
                self.particles.append(Particle(fruit.pos.copy(), velocity, color, random.uniform(0.4, 1), random.uniform(3, 8)))
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
            self.halves.append(
                SliceHalf(
                    fruit.pos + normal * side * 7,
                    fruit.vel * 0.55 + normal * side * 150,
                    fruit.radius,
                    fruit.skin,
                    fruit.flesh,
                    side,
                    fruit.angle,
                    fruit.spin + side * 140,
                )
            )
        for _ in range(20):
            velocity = normal * random.uniform(-230, 230) + direction * random.uniform(-60, 90)
            velocity += Vector2(random.uniform(-80, 80), random.uniform(-80, 80))
            self.particles.append(Particle(fruit.pos.copy(), velocity, fruit.flesh, random.uniform(0.35, 0.8), random.uniform(2, 6)))

    def update(self, dt: float) -> None:
        """Advance timers, particles, fruit physics, misses, and game-over state."""
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
            missed = fruit.pos.y > HEIGHT + fruit.radius * 1.5 and fruit.vel.y > 0 and not fruit.counted_miss
            if missed:
                fruit.counted_miss = True
                if fruit.kind != "bomb" and not fruit.sliced:
                    self.lives -= 1
                    self.combo = 0
                    self.message = self.tr("漏掉了！", "MISSED!")
                    self.message_timer = 0.65
        self.fruits = [f for f in self.fruits if not f.sliced and f.pos.y < HEIGHT + f.radius * 2]
        if self.lives <= 0:
            self.state = "gameover"
            self.best = max(self.best, self.score)
            self.save_best()

    def handle_slice(self, pos: Vector2) -> None:
        """Record a slash point and test the resulting segment against targets."""
        previous = self.trail[-1][0] if self.trail else pos
        self.trail.append((pos, 0.18))
        velocity = pos - previous
        if velocity.length_squared() < 20:
            return
        for fruit in self.fruits:
            if not fruit.sliced and segment_circle_hit(previous, pos, fruit.pos, fruit.radius + 4):
                self.slice_fruit(fruit, velocity)

    def draw(self) -> None:
        """Delegate all frame composition to the renderer."""
        self.renderer.draw(self.screen, self)

    def run(self) -> None:
        """Run the interactive pygame main loop until the player exits."""
        running = True
        while running:
            dt = min(self.clock.tick(FPS) / 1000, 0.035)
            for event in pygame.event.get():
                running = handle_event(self, event)
                if not running:
                    break
            self.update(dt)
            self.draw()
        pygame.quit()

