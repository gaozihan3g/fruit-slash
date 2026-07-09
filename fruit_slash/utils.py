"""Small reusable helpers for math, collision, and colors."""

from __future__ import annotations

from pygame import Vector2


def clamp(value: float, low: float, high: float) -> float:
    """Limit a numeric value so it stays inside the inclusive range."""
    return max(low, min(high, value))


def segment_circle_hit(a: Vector2, b: Vector2, center: Vector2, radius: float) -> bool:
    """Return whether a slash segment intersects a circular target."""
    ab = b - a
    if ab.length_squared() == 0:
        return center.distance_to(a) <= radius
    t = clamp((center - a).dot(ab) / ab.length_squared(), 0, 1)
    return center.distance_to(a + ab * t) <= radius


def lighten(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    """Brighten an RGB color without exceeding the valid channel range."""
    return tuple(min(255, c + amount) for c in color)

