import numpy as np
import pygame

from magic_rain.coordinates import Viewport
from magic_rain.render.outline import Outline, boundary


def test_outline_keeps_three_interiors_clear_and_fades_when_people_leave():
    mask = np.zeros((14, 36), dtype=bool)
    for x in (2, 14, 26):
        mask[3:11, x:x + 7] = True
    edges = boundary(mask)
    assert edges[3, [4, 16, 28]].all()
    assert not edges[6, [4, 16, 28]].any()
    canvas = pygame.Surface((80, 35))
    outline = Outline(Viewport(4, 3, 72, 28), mask.shape)
    outline.draw(canvas, mask, 0.15)
    assert canvas.get_at((12, 9))[:3] != (0, 0, 0)
    assert canvas.get_at((12, 15))[:3] == (0, 0, 0)
    canvas.fill((0, 0, 0))
    outline.draw(canvas, np.zeros_like(mask), 0.25)
    assert canvas.get_at((12, 9))[:3] == (0, 0, 0)
