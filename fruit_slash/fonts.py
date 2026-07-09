"""Font discovery and font object creation for localized UI text."""

from __future__ import annotations

import pygame


class Fonts:
    """Find a Chinese-capable font when available and create sized fonts."""

    def __init__(self) -> None:
        candidates = ["PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", "Arial Unicode MS"]
        path = next((pygame.font.match_font(name) for name in candidates if pygame.font.match_font(name)), None)
        self.has_chinese = path is not None
        self.path = path

    def get(self, size: int, bold: bool = False) -> pygame.font.Font:
        """Create a pygame font for the requested size and weight."""
        font = pygame.font.Font(self.path, size)
        font.set_bold(bold)
        return font

