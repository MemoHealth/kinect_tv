import numpy as np
import pygame

from magic_rain.config import SCENE_SIZE
from magic_rain.coordinates import Viewport
from magic_rain.render.galaxy import GalaxyMirror


def test_three_still_galaxies_emit_local_dust_only_after_movement():
    field = Viewport.fit((320, 240), SCENE_SIZE)
    world = GalaxyMirror(field, (240, 320))
    mask = np.zeros((240, 320), dtype=bool)
    for x in (30, 135, 240):
        mask[60:200, x:x + 30] = True
    world.update(mask, 1 / 30)
    assert len(world._points) > 400
    assert not (world._dust.life > 0).any()
    moved = mask.copy()
    moved[90:110, 50:85] = True
    world.update(moved, 1 / 30)
    active = world._dust.life > 0
    assert 0 < np.count_nonzero(active) <= 28
    assert (world._dust.x[active] < field.x + field.width / 3).all()
    canvas = pygame.Surface(SCENE_SIZE)
    world.draw(canvas)
    world.update(np.zeros_like(mask), 0.05)
    assert not world._points
    for _ in range(90):
        world.update(np.zeros_like(mask), 1 / 30)
    assert not (world._dust.life > 0).any()
