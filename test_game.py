import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from game.game_engine import GameEngine, MAX_SPEED
from game.obstacle import Obstacle

pygame.init()


def test_fast_obstacle_cannot_tunnel_through_player():
    engine = GameEngine(800, 400)
    engine.spawn_interval = 10**9  # no random spawns
    player = engine.player
    # Starts fully right of the player, ends fully left after one 200px step.
    obstacle = Obstacle(player.x + player.width + 10, engine.ground_y, 200)
    engine.obstacles = [obstacle]
    engine.update()
    assert obstacle.x + obstacle.width < player.x  # really jumped past
    assert engine.game_over


def test_speed_is_capped():
    engine = GameEngine(800, 400)
    engine.spawn_interval = 10**9
    for _ in range(100_000):
        engine.speed += 1
        engine.update()
    assert engine.speed == MAX_SPEED


def test_game_over_screen_renders_and_esc_quits():
    engine = GameEngine(800, 400)
    engine.game_over = True
    engine.render(pygame.Surface((800, 400)))
    pygame.event.clear()
    engine.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert pygame.event.peek(pygame.QUIT)


def test_no_jump_after_game_over():
    engine = GameEngine(800, 400)
    engine.game_over = True
    engine.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    assert engine.player.on_ground


def test_replay_with_chosen_difficulty_resets_state():
    engine = GameEngine(800, 400)
    engine.score, engine.speed, engine.game_over = 12, 17, True
    engine.obstacles = [Obstacle(100, engine.ground_y, 17)]
    engine.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_3))
    assert not engine.game_over
    assert engine.score == 0 and engine.obstacles == []
    assert (engine.difficulty, engine.speed, engine.spawn_interval) == ("Hard", 8, 55)


def test_difficulty_keys_ignored_while_playing():
    engine = GameEngine(800, 400)
    engine.score = 3
    engine.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1))
    assert engine.score == 3 and engine.difficulty == "Medium"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
