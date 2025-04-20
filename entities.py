import pygame
import random
from collections import deque
from constants import BOARD_SIZE, TILE_SIZE, PURPLE

class Player:
    def __init__(self, symbol, x, y):
        self.symbol = symbol
        self.position = (x, y)
        self.score = 0
        self.facing = 'right'
        self.magnet_active = False
        self.magnet_moves_left = 0
        self.magnet_radius = 1
        self.lives = 3

    def move(self, direction, board):
        x, y = self.position
        dx, dy = 0, 0
        if direction == 'up': 
            dx = -1
        elif direction == 'down': 
            dx = 1
        elif direction == 'left':
            dy = -1
            self.facing = 'left'
        elif direction == 'right':
            dy = 1
            self.facing = 'right'
        new_x, new_y = x + dx, y + dy
        
        if 0 <= new_x < board.size and 0 <= new_y < board.size:
            if board.is_obstacle(new_x, new_y):
                return False
            self.position = (new_x, new_y)
            
            # Pick up magnet
            if board.is_magnet(new_x, new_y):
                self.magnet_active = True
                self.magnet_moves_left = 3
                board.remove_magnet(new_x, new_y)
            
            # Move onto a coin
            if board.is_coin(new_x, new_y):
                self.score += 1
                board.remove_coin(new_x, new_y)
            
            if self.magnet_active:
                collected_coins = board.collect_coins_in_radius(new_x, new_y, self.magnet_radius)
                self.score += len(collected_coins)
                
                self.magnet_moves_left -= 1
                if self.magnet_moves_left <= 0:
                    self.magnet_active = False
            
            return True
        return False

    def available_moves(self, board):
        moves = []
        for direction in ['up', 'down', 'left', 'right']:
            x, y = self.position
            dx, dy = 0, 0
            if direction == 'up': dx = -1
            elif direction == 'down': dx = 1
            elif direction == 'left': dy = -1
            elif direction == 'right': dy = 1
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < board.size and 0 <= new_y < board.size:
                if not board.is_obstacle(new_x, new_y):
                    moves.append(direction)
        return moves

    def draw(self, screen, player_img):
        x, y = self.position
        img = player_img

        if self.symbol == 'A':
            if self.facing == 'left':
                img = pygame.transform.flip(player_img, True, False)
        elif self.symbol == 'B':
            if self.facing == 'right':
                img = pygame.transform.flip(player_img, True, False)

        screen.blit(img, (y * TILE_SIZE, x * TILE_SIZE))
        
        # Draw magnet effect radius when active
        if self.magnet_active:
            radius = self.magnet_radius * TILE_SIZE
            center = ((y + 0.5) * TILE_SIZE, (x + 0.5) * TILE_SIZE)

            s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (128, 0, 128, 75), (radius, radius), radius)
            screen.blit(s, (center[0]-radius, center[1]-radius))
            
            font = pygame.font.SysFont("arial", 20)
            text = font.render(str(self.magnet_moves_left), True, PURPLE)
            text_rect = text.get_rect(center=center)
            screen.blit(text, text_rect)

class HumanPlayer(Player):
    def __init__(self, symbol, x, y, control_keys=None):
        super().__init__(symbol, x, y)
        if control_keys is None and symbol == 'A':
            self.control_keys = {
                pygame.K_UP: 'up',
                pygame.K_DOWN: 'down',
                pygame.K_LEFT: 'left',
                pygame.K_RIGHT: 'right'
            }
        elif control_keys is None and symbol == 'B':
            self.control_keys = {
                pygame.K_w: 'up',
                pygame.K_s: 'down',
                pygame.K_a: 'left',
                pygame.K_d: 'right'
            }
        else:
            self.control_keys = control_keys

    def get_move(self, keys, board):
        for key, direction in self.control_keys.items():
            if keys[key]:
                return direction
        return None

class AIPlayer(Player):
    def __init__(self, symbol, x, y):
        super().__init__(symbol, x, y)
        
    def get_move(self, board):
        def bfs(start, board, target_types):
            visited = set()
            queue = deque([(start, [])])
            while queue:
                (x, y), path = queue.popleft()
                if (x, y) in visited:
                    continue
                visited.add((x, y))
                
                found = False
                if 'coin' in target_types and board.is_coin(x, y) and (x, y) != self.position:
                    found = True
                if 'magnet' in target_types and board.is_magnet(x, y) and (x, y) != self.position:
                    found = True
                
                if found:
                    return path
                
                for direction, (dx, dy) in {
                    'up': (-1, 0), 'down': (1, 0),
                    'left': (0, -1), 'right': (0, 1)
                }.items():
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < board.size and 0 <= ny < board.size and not board.is_obstacle(nx, ny):
                        queue.append(((nx, ny), path + [direction]))
            return []

        # Find Magnet
        if not self.magnet_active:
            path_to_magnet = bfs(self.position, board, ['magnet'])
            if path_to_magnet:
                next_move = path_to_magnet[0]
                if next_move in ['left', 'right']:
                    self.facing = next_move
                return next_move
        
        # Find coins
        path_to_coin = bfs(self.position, board, ['coin'])
        if path_to_coin:
            next_move = path_to_coin[0]
            if next_move in ['left', 'right']:
                self.facing = next_move
            return next_move

        # Random move
        moves = self.available_moves(board)
        if not moves:
            return None
        fallback = random.choice(moves)
        if fallback in ['left', 'right']:
            self.facing = fallback
        return fallback

class Ghost:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.target_player = 0
        self.move_delay = 2
        self.moves_counter = 0

    def move(self, players, board):
        self.moves_counter += 1
        if self.moves_counter < self.move_delay:
            return
        
        self.moves_counter = 0
        
        if random.random() < 0.3:
            self.target_player = random.randint(0, len(players) - 1)
        
        # Get player position
        target_x, target_y = players[self.target_player].position
        
        # Find direction
        directions = [
            ('up', -1, 0), ('down', 1, 0), 
            ('left', 0, -1), ('right', 0, 1)
        ]
        random.shuffle(directions)
        
        best_dir = None
        best_dist = float('inf')
        
        for dir_name, dx, dy in directions:
            new_x, new_y = self.x + dx, self.y + dy
            
            # Check if valid move
            if (0 <= new_x < board.size and 0 <= new_y < board.size and 
                not board.is_obstacle(new_x, new_y)):
                
                # Calculate distance to target
                dist = abs(new_x - target_x) + abs(new_y - target_y)
                
                if dist < best_dist:
                    best_dist = dist
                    best_dir = (dir_name, dx, dy)
        
        # Make the move
        if best_dir:
            z, dx, dy = best_dir
            self.x += dx
            self.y += dy
    
    def check_collision(self, player):
        return self.x == player.position[0] and self.y == player.position[1]
    
    def draw(self, screen, ghost_img):
        screen.blit(ghost_img, (self.y * TILE_SIZE, self.x * TILE_SIZE))