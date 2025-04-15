import pygame
import random
from collections import deque

BOARD_SIZE = 8
TILE_SIZE = 80
SCREEN_SIZE = BOARD_SIZE * TILE_SIZE

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
BLUE = (30, 144, 255)
GREEN = (34, 139, 34)
YELLOW = (255, 215, 0)
PURPLE = (128, 0, 128)

# Game State
STATE_START = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2

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
        self.duration = 2
        
class Board:
    def __init__(self, size=BOARD_SIZE, coin_prob=0.3, obstacle_prob=0.08, magnet_prob=0.04):
        self.size = size
        self.coins = []
        self.obstacles = []
        self.magnets = []
        self.generate_elements(coin_prob, obstacle_prob, magnet_prob)

    def generate_elements(self, coin_prob, obstacle_prob, magnet_prob):
        for i in range(self.size):
            for j in range(self.size):
                if (i, j) in [(0, 0), (self.size - 1, self.size - 1)]:
                    continue
                rand_val = random.random()
                if rand_val < magnet_prob:
                    self.magnets.append(Magnet(i, j))
                elif rand_val < coin_prob + magnet_prob:
                    self.coins.append(Coin(i, j))
                elif rand_val < coin_prob + magnet_prob + obstacle_prob:
                    self.obstacles.append((i, j))

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

class Player:
    def __init__(self, symbol, x, y):
        self.symbol = symbol
        self.position = (x, y)
        self.score = 0
        self.facing = 'right'
        self.magnet_active = False
        self.magnet_moves_left = 0
        self.magnet_radius = 1

    def move(self, direction, board):
        x, y = self.position
        dx, dy = 0, 0
        if direction == 'up': dx = -1
        elif direction == 'down': dx = 1
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
            
            # Check if the player picked up a magnet
            if board.is_magnet(new_x, new_y):
                self.magnet_active = True
                self.magnet_moves_left = 2
                board.remove_magnet(new_x, new_y)
            
            # Check if the player moved onto a coin
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

        # Flip logic depends on default sprite orientation
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
            # Draw semi-transparent circle
            s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (128, 0, 128, 75), (radius, radius), radius)
            screen.blit(s, (center[0]-radius, center[1]-radius))
            
            # Draw remaining moves
            font = pygame.font.SysFont("arial", 20)
            text = font.render(str(self.magnet_moves_left), True, PURPLE)
            text_rect = text.get_rect(center=center)
            screen.blit(text, text_rect)

class HumanPlayer(Player):
    def __init__(self, symbol, x, y):
        super().__init__(symbol, x, y)

    def get_move(self, keys, board):
        if keys[pygame.K_UP]: return 'up'
        elif keys[pygame.K_DOWN]: return 'down'
        elif keys[pygame.K_LEFT]: return 'left'
        elif keys[pygame.K_RIGHT]: return 'right'
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
                    return path  # return path to target
                
                for direction, (dx, dy) in {
                    'up': (-1, 0), 'down': (1, 0),
                    'left': (0, -1), 'right': (0, 1)
                }.items():
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < board.size and 0 <= ny < board.size and not board.is_obstacle(nx, ny):
                        queue.append(((nx, ny), path + [direction]))
            return []

        # First priority: find magnets if not already active
        if not self.magnet_active:
            path_to_magnet = bfs(self.position, board, ['magnet'])
            if path_to_magnet:
                next_move = path_to_magnet[0]
                if next_move in ['left', 'right']:
                    self.facing = next_move
                return next_move
        
        # Second priority: find coins
        path_to_coin = bfs(self.position, board, ['coin'])
        if path_to_coin:
            next_move = path_to_coin[0]
            if next_move in ['left', 'right']:
                self.facing = next_move
            return next_move

        # fallback: random move
        moves = self.available_moves(board)
        if not moves:
            return None
        fallback = random.choice(moves)
        if fallback in ['left', 'right']:
            self.facing = fallback
        return fallback

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.hovered = False
        
    def draw(self, screen, font):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 3, border_radius=10)
        
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE+30))
        pygame.display.set_caption("PACMAN GAME")
        self.clock = pygame.time.Clock()
        
        # Initialize fonts
        self.title_font = pygame.font.SysFont("arial", 48, bold=True)
        self.font = pygame.font.SysFont("arial", 36)
        self.small_font = pygame.font.SysFont("arial", 24)
        
        # Game state
        self.state = STATE_START
        self.running = True
        
        # Initialize buttons
        button_width, button_height = 200, 60
        center_x = SCREEN_SIZE // 2
        
        self.start_button = Button(
            center_x - button_width // 2, 
            SCREEN_SIZE // 2 + 100, 
            button_width, button_height, 
            "Start Game", GREEN, (100, 200, 100)
        )
        
        self.restart_button = Button(
            center_x - button_width // 2, 
            SCREEN_SIZE // 2 + 150, 
            button_width, button_height, 
            "Play Again", BLUE, (100, 100, 200)
        )
        
        self.quit_button = Button(
            center_x - button_width // 2, 
            SCREEN_SIZE // 2 + 230, 
            button_width, button_height, 
            "Quit", (200, 50, 50), (250, 100, 100)
        )
        
        self.init_game()

        # Load images
        self.coin_img = pygame.transform.smoothscale(
            pygame.image.load("./asset/coin.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)
        )
        self.obstacle_img = pygame.transform.smoothscale(
            pygame.image.load("./asset/obstacle.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)
        )
        self.magnet_img = pygame.transform.smoothscale(
            pygame.image.load("./asset/magnet.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)
        )

        self.player_base_imgs = {
            'A': pygame.image.load("./asset/player1.png").convert_alpha(),
            'B': pygame.image.load("./asset/player2.png").convert_alpha()
        }

        self.player_imgs = {
            symbol: pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE)) for symbol, img in self.player_base_imgs.items()
        }

    def init_game(self):
        self.board = Board()
        player_a = HumanPlayer('A', 0, 0)
        player_b = AIPlayer('B', BOARD_SIZE - 1, BOARD_SIZE - 1)
        player_b.facing = 'left'
        self.players = [player_a, player_b]
        self.current_player = 0

    def draw_start_screen(self):
        self.screen.fill(WHITE)
        
        # Draw title
        title_surf = self.title_font.render("PACMAN GAME", True, BLUE)
        title_rect = title_surf.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 4))
        self.screen.blit(title_surf, title_rect)
        
        # Draw instructions
        instructions = [
            "Use arrow keys to move",
            "Collect coins to score points",
            "Pick up magnets to attract nearby coins",
            "Player with most coins wins"
        ]
        
        for i, text in enumerate(instructions):
            text_surf = self.small_font.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 3 + i * 30))
            self.screen.blit(text_surf, text_rect)
        
        # Draw start button
        mouse_pos = pygame.mouse.get_pos()
        self.start_button.check_hover(mouse_pos)
        self.start_button.draw(self.screen, self.font)
        
        # Draw player icons for visual appeal
        if hasattr(self, 'player_imgs'):
            player_a_img = self.player_imgs['A']
            player_b_img = self.player_imgs['B']
            self.screen.blit(player_a_img, (SCREEN_SIZE // 4 - TILE_SIZE // 2, SCREEN_SIZE // 2))
            self.screen.blit(pygame.transform.flip(player_b_img, True, False), (3 * SCREEN_SIZE // 4 - TILE_SIZE // 2, SCREEN_SIZE // 2))
        
    def draw_game_over_screen(self):
        self.screen.fill(WHITE)
        
        # Draw Game Over
        title_surf = self.title_font.render("GAME OVER", True, BLUE)
        title_rect = title_surf.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 6))
        self.screen.blit(title_surf, title_rect)
        
        # Determine winner
        player_a, player_b = self.players
        
        if player_a.score > player_b.score:
            winner_text = "Player A Wins!"
            winner_color = GREEN
        elif player_a.score < player_b.score:
            winner_text = "Player B Wins!"
            winner_color = YELLOW
        else:
            winner_text = "It's a Tie!"
            winner_color = BLUE
            
        # Display winner
        winner_surf = self.title_font.render(winner_text, True, winner_color)
        winner_rect = winner_surf.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 3)) 
        self.screen.blit(winner_surf, winner_rect)
        
        # Display scores
        score_texts = [
            f"Player A Score: {player_a.score}",
            f"Player B Score: {player_b.score}"
        ]
        
        for i, text in enumerate(score_texts):
            text_surf = self.font.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 + i * 50))
            self.screen.blit(text_surf, text_rect)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        self.restart_button.check_hover(mouse_pos)
        self.quit_button.check_hover(mouse_pos)
        
        self.restart_button.draw(self.screen, self.font)
        self.quit_button.draw(self.screen, self.font)
        
        # Draw player icons for visual appeal
        if hasattr(self, 'player_imgs'):
            player_a_img = self.player_imgs['A']
            player_b_img = self.player_imgs['B']
            self.screen.blit(player_a_img, (SCREEN_SIZE // 4 - TILE_SIZE // 2, SCREEN_SIZE * 0.7))
            self.screen.blit(pygame.transform.flip(player_b_img, True, False), 
                           (3 * SCREEN_SIZE // 4 - TILE_SIZE // 2, SCREEN_SIZE * 0.7))

    def draw_playing_screen(self):
        self.screen.fill(WHITE)
        self.board.draw(self.screen, self.coin_img, self.obstacle_img, self.magnet_img)
        for p in self.players:
            p.draw(self.screen, self.player_imgs[p.symbol])
            
        # Draw scores at the top
        player_a, player_b = self.players
        
        # Show magnet status in the score display
        magnet_a_text = f" [MAGNET: {player_a.magnet_moves_left}]" if player_a.magnet_active else ""
        magnet_b_text = f" [MAGNET: {player_b.magnet_moves_left}]" if player_b.magnet_active else ""
        
        score_a = self.small_font.render(f"Player A: {player_a.score}{magnet_a_text}", True, BLACK)
        score_b = self.small_font.render(f"Player B: {player_b.score}{magnet_b_text}", True, BLACK)
        
        self.screen.blit(score_a, (10, SCREEN_SIZE))
        self.screen.blit(score_b, (SCREEN_SIZE - score_b.get_width() - 10, SCREEN_SIZE))

    def check_game_end(self):
        return len(self.board.coins) == 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                
                if self.state == STATE_START:
                    if self.start_button.is_clicked(pos):
                        self.state = STATE_PLAYING
                        
                elif self.state == STATE_GAME_OVER:
                    if self.restart_button.is_clicked(pos):
                        self.init_game()
                        self.state = STATE_PLAYING
                    elif self.quit_button.is_clicked(pos):
                        self.running = False

    def update(self):
        if self.state == STATE_PLAYING:
            player = self.players[self.current_player]
            
            if isinstance(player, HumanPlayer):
                keys = pygame.key.get_pressed()
                move = player.get_move(keys, self.board)
            else:
                pygame.time.delay(300)
                move = player.get_move(self.board)

            if move:
                moved = player.move(move, self.board)
                if moved:
                    self.current_player = 1 - self.current_player

            if self.check_game_end():
                self.state = STATE_GAME_OVER

    def draw(self):
        if self.state == STATE_START:
            self.draw_start_screen()
        elif self.state == STATE_PLAYING:
            self.draw_playing_screen()
        elif self.state == STATE_GAME_OVER:
            self.draw_game_over_screen()
            
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(10)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()

if __name__ == "__main__":
    Game().run()