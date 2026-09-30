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


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
