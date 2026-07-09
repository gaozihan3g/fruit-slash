"""Moving gameplay objects and their lightweight drawing behavior."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame
from pygame import Vector2

from .config import FRUITS, GRAVITY, HEIGHT
from .utils import lighten


@dataclass
class Particle:
    """Short-lived juice, spark, and explosion particles."""

    pos: Vector2
    vel: Vector2
    color: tuple[int, int, int]
    life: float
    size: float

    def update(self, dt: float) -> bool:
        """Advance the particle and return whether it should stay alive."""
        self.life -= dt
        self.vel.y += GRAVITY * 0.36 * dt
        self.pos += self.vel * dt
        self.size *= 0.985
        return self.life > 0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the particle as a small fading circle."""
        radius = max(1, int(self.size))
        pygame.draw.circle(screen, self.color, self.pos, radius)


@dataclass
class SliceHalf:
    """A sliced fruit half that tumbles away after a successful slash."""

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
        """Advance the tumbling half and return whether it remains visible."""
        self.life -= dt
        self.vel.y += GRAVITY * dt
        self.pos += self.vel * dt
        self.angle += self.spin * dt
        return self.life > 0 and self.pos.y < HEIGHT + self.radius * 3


class Fruit:
    """A throwable fruit target with physics, state, and procedural art."""

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
        """Apply gravity and rotation for the current frame."""
        self.vel.y += GRAVITY * dt
        self.pos += self.vel * dt
        self.angle += self.spin * dt

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the fruit with simple procedural highlights and details."""
        r = self.radius
        x, y = int(self.pos.x), int(self.pos.y)
        shadow = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0, 0, 0, 65), (r * 3 // 2 + 5, r * 3 // 2 + 7), r)
        screen.blit(shadow, (x - r * 3 // 2, y - r * 3 // 2))
        pygame.draw.circle(screen, self.skin, (x, y), r)
        pygame.draw.circle(screen, lighten(self.skin, 38), (x - r // 3, y - r // 3), max(3, r // 7))
        pygame.draw.arc(screen, (255, 255, 255, 85), (x - r + 6, y - r + 6, 2 * r - 12, 2 * r - 12), 2.0, 3.8, 3)
        stem_end = Vector2(0, -r - 10).rotate(-self.angle)
        pygame.draw.line(screen, (83, 55, 29), self.pos + stem_end * 0.7, self.pos + stem_end, 5)
        if self.kind == "watermelon":
            for offset in (-0.45, 0, 0.45):
                pygame.draw.arc(screen, (29, 116, 62), (x - r, y - r + int(offset * r), 2 * r, 2 * r), 0.25, 2.9, 3)


class Bomb(Fruit):
    """A dangerous target that immediately ends the run when sliced."""

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
        """Draw the bomb body, fuse, and animated spark."""
        x, y, r = int(self.pos.x), int(self.pos.y), self.radius
        pygame.draw.circle(screen, (8, 7, 10), (x + 5, y + 7), r + 2)
        pygame.draw.circle(screen, (47, 43, 51), (x, y), r)
        pygame.draw.circle(screen, (90, 82, 93), (x - 9, y - 10), 8)
        pygame.draw.line(screen, (126, 84, 46), (x + 17, y - 22), (x + 26, y - 39), 5)
        glow = 5 + int(3 * math.sin(pygame.time.get_ticks() * 0.02))
        pygame.draw.circle(screen, (255, 215, 70), (x + 27, y - 41), glow + 3)
        pygame.draw.circle(screen, (255, 82, 35), (x + 27, y - 41), glow)
        pygame.draw.circle(screen, (245, 238, 215), (x - 8, y - 5), 3)

