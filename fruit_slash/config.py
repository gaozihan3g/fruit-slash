"""Shared gameplay and rendering constants.

Keeping core values in one module makes tuning the game easier and avoids
threading magic numbers through the entity, renderer, and game-loop modules.
"""

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

