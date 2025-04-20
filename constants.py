import pygame

# Game dimensions
BOARD_SIZE = 8
TILE_SIZE = 80
SCREEN_SIZE = BOARD_SIZE * TILE_SIZE

# Colors
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
BLUE = (30, 144, 255)
GREEN = (34, 139, 34)
YELLOW = (255, 215, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)

# Game State
STATE_START = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2

# Game Mode
MODE_PVP = 0  # vs Player
MODE_PVE = 1  # vs AI

# Asset paths
ASSET_PATH = "./asset/"