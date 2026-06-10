"""Global settings and constants for Galaxy Reborn: The Last Frontier."""
from __future__ import annotations

# --- Display ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
TITLE = "Galaxy Reborn: The Last Frontier"
FPS = 60

# --- Tiles ---
TILE_SIZE = 32

# --- Physics ---
GRAVITY = 980.0          # px/s^2
TERMINAL_VELOCITY = 900.0  # px/s

# --- Neon color palette (RGB) ---
NEON_CYAN = (0, 255, 231)
NEON_MAGENTA = (255, 0, 200)
NEON_BLUE = (40, 120, 255)
NEON_PURPLE = (160, 60, 255)
NEON_GREEN = (80, 255, 120)
NEON_RED = (255, 60, 80)
NEON_YELLOW = (255, 230, 60)

# --- Base UI colors ---
COLOR_BG = (8, 8, 20)
COLOR_BG_DARK = (4, 4, 12)
COLOR_WHITE = (240, 240, 250)
COLOR_GRAY = (120, 120, 140)
COLOR_BLACK = (0, 0, 0)

# --- Layer names (rendering order, also TMX layer names) ---
LAYER_BACKGROUND = "Background"
LAYER_MIDGROUND = "Midground"
LAYER_COLLISION = "Collision"
LAYER_FOREGROUND = "Foreground"
LAYER_OBJECTS = "Objects"

LAYER_NAMES = [
    LAYER_BACKGROUND,
    LAYER_MIDGROUND,
    LAYER_COLLISION,
    LAYER_FOREGROUND,
    LAYER_OBJECTS,
]

# Entity render layers (z-order)
ENTITY_LAYERS = ["background", "default", "enemies", "player", "projectiles", "fx", "foreground"]

# --- Paths ---
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SAVES_DIR = os.path.join(BASE_DIR, "saves")
LEVELS_DIR = os.path.join(DATA_DIR, "levels")

# --- Gameplay tuning ---
COYOTE_FRAMES = 6
JUMP_BUFFER_FRAMES = 8
SPATIAL_HASH_CELL = 128
MAX_PARTICLES = 2000
MAX_INVENTORY_SLOTS = 40
SFX_CHANNELS = 32
