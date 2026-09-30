import pygame
from .player import Player
from .obstacle import Obstacle

# Game Engine

WHITE = (255, 255, 255)
BROWN = (120, 80, 40)
DARK_GREEN = (30, 100, 30)

MAX_SPEED = 18  # px/frame; keeps late-game runs fair and reactable

# key -> (name, starting speed, frames between obstacle spawns)
DIFFICULTIES = {
    pygame.K_1: ("Easy", 5, 85),
    pygame.K_2: ("Medium", 6, 70),
    pygame.K_3: ("Hard", 8, 55),
}

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ground_y = height - 40
        self.speed_increase_per_frame = 0.003
        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.reset(pygame.K_2)

    def reset(self, difficulty_key):
        self.difficulty, self.speed, self.spawn_interval = DIFFICULTIES[difficulty_key]
        self.player = Player(80, self.ground_y)
        self._spawn_timer = 0
        self.obstacles = []
        self.distance = 0
        self.score = 0
        self.game_over = False

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.game_over:
            if event.key in DIFFICULTIES:
                self.reset(event.key)
            elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return
        if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            self.player.jump()

    def handle_input(self):
        # Reserved for continuously-held-key input; this runner only
        # needs an edge-triggered jump, handled in handle_event.
        pass

    def update(self):
        if self.game_over:
            return

        self.speed = min(self.speed + self.speed_increase_per_frame, MAX_SPEED)
        self.player.update()

        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.obstacles.append(Obstacle(self.width, self.ground_y, self.speed))

        for obstacle in self.obstacles:
            obstacle.move()
            obstacle.speed = self.speed

        for obstacle in self.obstacles:
            if obstacle.swept_rect().colliderect(self.player.rect()):
                self.game_over = True
                return

        for obstacle in self.obstacles:
            if not obstacle.scored and obstacle.x + obstacle.width < self.player.x:
                obstacle.scored = True
                self.score += 1

        self.obstacles = [o for o in self.obstacles if not o.off_screen()]

        self.distance += self.speed

    def render(self, screen):
        pygame.draw.line(screen, BROWN, (0, self.ground_y), (self.width, self.ground_y), 4)

        pygame.draw.rect(screen, WHITE, self.player.rect())
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, DARK_GREEN, obstacle.rect())

        score_text = self.font.render(f"Score: {self.score}  ({self.difficulty})", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        if self.game_over:
            self._render_game_over(screen)

    def _render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        lines = [
            (self.big_font, "GAME OVER", 90),
            (self.font, f"Final Score: {self.score}", 165),
            (self.font, "Play again:  " + "   ".join(
                f"{pygame.key.name(key)} = {name}" for key, (name, _, _) in DIFFICULTIES.items()), 235),
            (self.font, "Esc or Q to exit", 285),
        ]
        for font, text, y in lines:
            surface = font.render(text, True, WHITE)
            screen.blit(surface, surface.get_rect(center=(self.width // 2, y)))
