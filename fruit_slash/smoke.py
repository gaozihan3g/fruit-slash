"""Headless smoke test used by CI and local release checks."""

from __future__ import annotations

import os

import pygame

from .config import FPS
from .game import Game


def run_smoke_test() -> None:
    """Start the packaged runtime without opening a real window, then exit."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    game = Game()
    game.start()
    for _ in range(10):
        game.update(1 / FPS)
    game.draw()
    assert game.state == "playing"
    pygame.quit()
    print("Fruit Slash smoke test passed")

