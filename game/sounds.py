import math
from array import array

import pygame


def _tone(start_hz, end_hz, seconds, volume=0.3):
    # ponytail: assumes the mixer's default signed 16-bit format.
    rate, _, channels = pygame.mixer.get_init()
    n = int(rate * seconds)
    samples = array("h")
    phase = 0.0
    for i in range(n):
        phase += 2 * math.pi * (start_hz + (end_hz - start_hz) * i / n) / rate
        fade = 1 - i / n  # fade out to avoid a click at the end
        samples.extend([int(32767 * volume * fade * math.sin(phase))] * channels)
    return pygame.mixer.Sound(buffer=samples)


def load_sounds():
    """Return name -> Sound, or {} when no audio device is available."""
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        return {
            "jump": _tone(350, 700, 0.12),
            "score": _tone(900, 1300, 0.08),
            "game_over": _tone(440, 110, 0.6),
        }
    except pygame.error:
        return {}
