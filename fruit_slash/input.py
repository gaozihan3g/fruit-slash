"""Pygame event handling for menus, gameplay, and quitting."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from pygame import Vector2

if TYPE_CHECKING:
    from .game import Game


def handle_event(game: Game, event: pygame.event.Event) -> bool:
    """Apply one pygame event and return whether the main loop should continue."""
    if event.type == pygame.QUIT:
        return False
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            return False
        if event.key in (pygame.K_SPACE, pygame.K_RETURN) and game.state != "playing":
            game.start()
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        menu_button = getattr(game, "menu_button", pygame.Rect(0, 0, 0, 0))
        restart_button = getattr(game, "restart_button", pygame.Rect(0, 0, 0, 0))
        if game.state == "menu" and menu_button.collidepoint(event.pos):
            game.start()
        elif game.state == "gameover" and restart_button.collidepoint(event.pos):
            game.start()
        elif game.state == "playing":
            game.trail = [(Vector2(event.pos), 0.18)]
    elif event.type == pygame.MOUSEMOTION and game.state == "playing" and pygame.mouse.get_pressed()[0]:
        game.handle_slice(Vector2(event.pos))
    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        game.trail.clear()
    return True

