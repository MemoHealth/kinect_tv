import numpy as np
import pygame
import pytest

from magic_rain.coordinates import Viewport
from magic_rain.render.lightpaint import LightPaint


def test_three_movements_leave_distinct_colors_that_decay_and_clear():
    canvas = pygame.Surface((40, 16), depth=32)
    paint = LightPaint(Viewport(0, 0, 40, 16), (16, 40))
    figures = np.zeros((16, 40), dtype=bool)
    for x in (2, 15, 28):
        figures[3:12, x:x + 7] = True
    paint.update(figures, 0.1)
    paint.draw(canvas)
    colors = [canvas.get_at((x, 4))[:3] for x in (2, 15, 28)]
    assert len(set(colors)) == 3
    assert all(max(color) > 100 for color in colors)
    paint.update(np.zeros_like(figures), 3)
    canvas.fill((0, 0, 0))
    paint.draw(canvas)
    assert 0 < max(canvas.get_at((2, 4))[:3]) < max(colors[0])
    paint.clear()
    canvas.fill((0, 0, 0))
    paint.draw(canvas)
    assert canvas.get_at((2, 4))[:3] == (0, 0, 0)


@pytest.mark.parametrize("rate", (30, 60))
def test_fade_uses_elapsed_time_at_multiple_update_rates(rate):
    mask = np.zeros((16, 40), dtype=bool)
    mask[4:12, 5:25] = True
    paint = LightPaint(Viewport(0, 0, 40, 16), mask.shape)
    paint.update(mask, 0)
    initial = paint._history.sum()
    for _ in range(rate * 6):
        paint.update(mask, 1 / rate, half_life=6)
    assert paint._history.sum() == pytest.approx(initial / 2, rel=1e-4)
