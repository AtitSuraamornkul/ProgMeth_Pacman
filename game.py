import pygame
import random
import os
from constants import *
from board import Board
from entities import HumanPlayer, AIPlayer, Ghost
from ui import Button

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
        
        # Game state and mode
        self.state = STATE_START
        self.running = True
        self.losing_player = None
        self.game_mode = None
        
        # Initialize buttons
        button_width, button_height = 200, 60
        center_x = SCREEN_SIZE // 2
        
        # Mode selection buttons
        self.pvp_button = Button(
            center_x - button_width // 2, 
            SCREEN_SIZE // 2 + 30, 
            button_width, button_height, 
            "vs Player", BLUE, (100, 100, 200)
        )
        
        self.pve_button = Button(
            center_x - button_width // 2, 
            SCREEN_SIZE // 2 + 110, 
            button_width, button_height, 
            "vs AI", GREEN, (100, 200, 100)
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
        
        self.load_images()
        self.init_game()

    def load_images(self):
        self.coin_img = pygame.transform.smoothscale(
            pygame.image.load(os.path.join(ASSET_PATH, "coin.png")).convert_alpha(), (TILE_SIZE, TILE_SIZE)
        )
        self.obstacle_img = pygame.transform.smoothscale(
            pygame.image.load(os.path.join(ASSET_PATH, "obstacle.png")).convert_alpha(), (TILE_SIZE, TILE_SIZE)
        )
        self.magnet_img = pygame.transform.smoothscale(
            pygame.image.load(os.path.join(ASSET_PATH, "magnet.png")).convert_alpha(), (TILE_SIZE, TILE_SIZE)
        )
        self.ghost_img = pygame.transform.smoothscale(
            pygame.image.load(os.path.join(ASSET_PATH, "ghost.png")).convert_alpha(), (TILE_SIZE, TILE_SIZE)
        )

        self.player_base_imgs = {
            'A': pygame.image.load(os.path.join(ASSET_PATH, "player1.png")).convert_alpha(),
            'B': pygame.image.load(os.path.join(ASSET_PATH, "player2.png")).convert_alpha()
        }

        self.player_imgs = {
            symbol: pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE)) for symbol, img in self.player_base_imgs.items()
        }

    def init_game(self):
        self.board = Board()
        
        if self.game_mode == MODE_PVP:
            # vs Player
            player_a = HumanPlayer('A', 0, 0) 
            player_b = HumanPlayer('B', BOARD_SIZE - 1, BOARD_SIZE - 1)
        else:
            # vs AI
            player_a = HumanPlayer('A', 0, 0)
            player_b = AIPlayer('B', BOARD_SIZE - 1, BOARD_SIZE - 1)
        
        player_b.facing = 'left'
        self.players = [player_a, player_b]
        self.current_player = 0
        self.losing_player = None
        
        # Ghost
        while True:
            ghost_x = random.randint(2, BOARD_SIZE - 3)
            ghost_y = random.randint(2, BOARD_SIZE - 3)
            
            if (not self.board.is_obstacle(ghost_x, ghost_y) and
                not self.board.is_coin(ghost_x, ghost_y) and
                not self.board.is_magnet(ghost_x, ghost_y)):
                break
                
        self.ghost = Ghost(ghost_x, ghost_y)
        
        self.invulnerable_time = 0
        self.invulnerable_player = None

    def draw_start_screen(self):
        self.screen.fill(WHITE)
        
        # Draw title
        title_surf = self.title_font.render("PACMAN GAME", True, BLUE)
        title_rect = title_surf.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 4))
        self.screen.blit(title_surf, title_rect)
        
        # Draw instructions
        instructions = [
            "Use arrow keys (Player 1) or WASD (Player 2) to move",
            "Collect coins to score points",
            "Pick up magnets to attract nearby coins",
            "Avoid the ghost",
            "Select game mode:"
        ]
        
        for i, text in enumerate(instructions):
            text_surf = self.small_font.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 3 + i * 30))
            self.screen.blit(text_surf, text_rect)
        
        # Draw mode selection buttons
        mouse_pos = pygame.mouse.get_pos()
        self.pvp_button.check_hover(mouse_pos)
        self.pve_button.check_hover(mouse_pos)
        
        self.pvp_button.draw(self.screen, self.font)
        self.pve_button.draw(self.screen, self.font)
        
        # Draw player icons for visual appeal
        if hasattr(self, 'player_imgs'):
            player_a_img = self.player_imgs['A']
            player_b_img = self.player_imgs['B']
            self.screen.blit(player_a_img, (SCREEN_SIZE // 4 - TILE_SIZE // 2, SCREEN_SIZE // 2 + 100))
            self.screen.blit(pygame.transform.flip(player_b_img, True, False), 
                           (3 * SCREEN_SIZE // 4 - TILE_SIZE // 2, SCREEN_SIZE // 2 + 100))
        
    def draw_game_over_screen(self):
        self.screen.fill(WHITE)
        
        # Draw Game Over
        title_surf = self.title_font.render("GAME OVER", True, BLUE)
        title_rect = title_surf.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 6))
        self.screen.blit(title_surf, title_rect)
        
        player_a, player_b = self.players
        
        # Running out of lives
        if self.losing_player:
            if self.losing_player.symbol == 'A':
                winner_text = "Player B Wins!"
                winner_color = YELLOW
            else:
                winner_text = "Player A Wins!"
                winner_color = GREEN
        # All Coins are collected
        elif len(self.board.coins) == 0:
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
        
        if self.losing_player:
            reason = f"Player {self.losing_player.symbol} ran out of lives!"
            reason_surf = self.font.render(reason, True, RED)
            reason_rect = reason_surf.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2.3))
            self.screen.blit(reason_surf, reason_rect)
        
        # Display scores and lives
        score_texts = [
            f"Player A Score: {player_a.score} (Lives: {player_a.lives})",
            f"Player B Score: {player_b.score} (Lives: {player_b.lives})"
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
        
        self.ghost.draw(self.screen, self.ghost_img)
        
        # Draw players
        for p in self.players:
            # Make player blink when invulnerable
            if p == self.invulnerable_player:
                if (pygame.time.get_ticks() // 200) % 2 == 0:  # Blink every 200ms
                    p.draw(self.screen, self.player_imgs[p.symbol])
            else:
                p.draw(self.screen, self.player_imgs[p.symbol])
            
        player_a, player_b = self.players
        
        # Show magnet status in the score display
        magnet_a_text = f" [MAGNET: {player_a.magnet_moves_left}]" if player_a.magnet_active else ""
        magnet_b_text = f" [MAGNET: {player_b.magnet_moves_left}]" if player_b.magnet_active else ""
        
        score_a = self.small_font.render(f"Player A: {player_a.score}{magnet_a_text} Lives: {player_a.lives}", True, BLACK)
        score_b = self.small_font.render(f"Player B: {player_b.score}{magnet_b_text} Lives: {player_b.lives}", True, BLACK)
        
        self.screen.blit(score_a, (10, SCREEN_SIZE))
        self.screen.blit(score_b, (SCREEN_SIZE - score_b.get_width() - 10, SCREEN_SIZE))
        
        current = self.small_font.render(f"Player {self.players[self.current_player].symbol}'s Turn", True, BLUE)
        current_rect = current.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE + 15))
        self.screen.blit(current, current_rect)

    def check_game_end(self):
        if len(self.board.coins) == 0:
            return True
        
        # Runs out of lives
        for player in self.players:
            if player.lives <= 0:
                self.losing_player = player
                return True
                
        return False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                
                if self.state == STATE_START:
                    if self.pvp_button.is_clicked(pos):
                        self.game_mode = MODE_PVP
                        self.init_game()
                        self.state = STATE_PLAYING
                    elif self.pve_button.is_clicked(pos):  # Added this check for PVE button
                        self.game_mode = MODE_PVE
                        self.init_game()
                        self.state = STATE_PLAYING
                
                elif self.state == STATE_GAME_OVER:  # Fixed indentation
                    if self.restart_button.is_clicked(pos):
                        self.init_game()
                        self.state = STATE_PLAYING
                    elif self.quit_button.is_clicked(pos):
                        self.running = False

    def handle_ghost_collision(self):
        # Check if ghost collided with a player
        for player in self.players:
            if (self.ghost.check_collision(player) and 
                player != self.invulnerable_player):
                # Use the proper method instead of direct attribute access
                remaining_lives = player.decrease_life()
                self.invulnerable_player = player
                self.invulnerable_time = pygame.time.get_ticks()
                
                # Use property setter
                if player.symbol == 'A':
                    player.position = (0, 0)
                else:
                    player.position = (BOARD_SIZE - 1, BOARD_SIZE - 1)
                    player.facing = 'left'
                
                # Check if player lost all lives
                if remaining_lives <= 0:
                    self.losing_player = player

    def update(self):
        if self.state == STATE_PLAYING:
            if self.invulnerable_player and pygame.time.get_ticks() - self.invulnerable_time > 3000:  # 3 seconds of invulnerability
                self.invulnerable_player = None
                
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
                    # Move ghost
                    self.ghost.move(self.players, self.board)
                    self.handle_ghost_collision()
                    
                    # Switch to other player's turn
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

