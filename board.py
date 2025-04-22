import pygame
import random
from constants import BOARD_SIZE, TILE_SIZE, GRAY

class Coin:
    def __init__(self, x, y, value=1):
        self.x = x
        self.y = y
        self.value = value
        
class Magnet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 1
        self.duration = 3

class Board:
    def __init__(self, size=BOARD_SIZE, coin_prob=0.5, magnet_prob=0.1, obstacle_prob=0.85):
        self.size = size
        self.coins = []
        self.obstacles = []
        self.magnets = []
        self.generate_obstacles(obstacle_prob)
        self.generate_elements(coin_prob, magnet_prob)

    def generate_obstacles(self, obstacle_prob):
        for i in range(1, (self.size + 1) // 2, 2):
            for j in range(i, (self.size + 1) // 2):
                self.obstacles.append((i, j))
                self.obstacles.append((self.size - i - 1, self.size - j - 1))
                self.obstacles.append((i, self.size - j - 1))
                self.obstacles.append((self.size - i - 1, j))

        for i in range(1, (self.size + 1) // 2, 2):
            for j in range(i, (self.size + 1) // 2):
                self.obstacles.append((j, i))
                self.obstacles.append((self.size - j - 1, self.size - i - 1))
                self.obstacles.append((j, self.size - i - 1))
                self.obstacles.append((self.size - j - 1, i))

        removed = []
        middle_tile = (self.size + 1) // 2 if self.size % 2 == 0 else self.size // 2
        for i in self.obstacles[:]:
            if i[0] == middle_tile or i[1] == middle_tile:
                self.obstacles.remove(i)
                removed.append(i)
            else:
                rand_val = random.random()
                if rand_val < 1 - obstacle_prob:
                    self.obstacles.remove(i)

        for i in range(min(1, len(removed))):
            selected = random.choice(removed)
            self.obstacles.append(selected)
            removed.remove(selected)

        # Remove duplicates & outmost grid
        self.obstacles = list(set(self.obstacles))
        self.obstacles = [pos for pos in self.obstacles if pos[0] != 0 and pos[0] != self.size - 1 and pos[1] != 0 and pos[1] != self.size - 1]

    def generate_elements(self, coin_prob, magnet_prob):
        for i in range(self.size):
            for j in range(self.size):
                if (i, j) in self.obstacles or (i, j) in [(0, 0), (self.size - 1, self.size - 1)]:
                    continue
                rand_val = random.random()
                if rand_val < magnet_prob:
                    self.magnets.append(Magnet(i, j))
                elif rand_val < coin_prob + magnet_prob:
                    self.coins.append(Coin(i, j))

    def is_obstacle(self, x, y):
        return (x, y) in self.obstacles

    def is_coin(self, x, y):
        return any(c.x == x and c.y == y for c in self.coins)

    def is_magnet(self, x, y):
        return any(m.x == x and m.y == y for m in self.magnets)

    def remove_coin(self, x, y):
        self.coins = [c for c in self.coins if not (c.x == x and c.y == y)]

    def remove_magnet(self, x, y):
        self.magnets = [m for m in self.magnets if not (m.x == x and m.y == y)]

    def collect_coins_in_radius(self, center_x, center_y, radius):
        collected = []
        for coin in list(self.coins):
            dx = abs(coin.x - center_x)
            dy = abs(coin.y - center_y)
            if dx <= radius and dy <= radius:
                collected.append(coin)
                self.coins.remove(coin)
        return collected

    def draw(self, screen, coin_img, obstacle_img, magnet_img):
        for x in range(self.size):
            for y in range(self.size):
                rect = pygame.Rect(y * TILE_SIZE, x * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, GRAY, rect, 1)
        for (x, y) in self.obstacles:
            screen.blit(obstacle_img, (y * TILE_SIZE, x * TILE_SIZE))
        for coin in self.coins:
            screen.blit(coin_img, (coin.y * TILE_SIZE, coin.x * TILE_SIZE))
        for magnet in self.magnets:
            screen.blit(magnet_img, (magnet.y * TILE_SIZE, magnet.x * TILE_SIZE))