"""Command-line entry point for Fruit Slash.

The implementation lives in the fruit_slash package so the game can be edited
module by module while this file keeps the original run commands working.
"""

import sys

from fruit_slash.game import Game
from fruit_slash.smoke import run_smoke_test


if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        run_smoke_test()
    else:
        Game().run()
