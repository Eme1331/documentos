"""Entry point for Galaxy Reborn: The Last Frontier."""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.game import Game


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
