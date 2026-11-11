import numpy as np
import pygame

from magic_rain.config import SCENE_SIZE
from magic_rain.coordinates import Viewport
from magic_rain.render.dance import DanceMirror
from magic_rain.vision.centerline import centerline


def test_three_silhouettes_produce_a_moving_centerline_and_both_styles():
    mask = np.zeros((240, 320), dtype=bool)
    for x in (40, 140, 240):
        mask[60:190, x:x + 18] = True
        mask[90:99, x - 22:x + 36] = True
    original = mask.copy()
    skeleton = centerline(mask)
    assert np.array_equal(mask, original)
    assert 12 < skeleton.sum() < mask.sum() / 4
    for x in (40, 140, 240):
        assert skeleton[18:42, x // 4:(x + 18) // 4].any()
    world = DanceMirror(Viewport.fit((320, 240), SCENE_SIZE), mask.shape)
    world.update(mask, 1 / 30)
    assert len(world._heads) == 3
    canvas = pygame.Surface(SCENE_SIZE)
    world.draw(canvas)
    sticks = pygame.image.tobytes(canvas, "RGB")
    world.configure("Skelett")
    world.draw(canvas)
    assert pygame.image.tobytes(canvas, "RGB") != sticks
    world.update(np.zeros_like(mask), 1 / 30)
    assert not world._segments and not world._heads


def test_broad_masks_finish_thinning_and_keep_display_geometry_bounded():
    mask = np.ones((240, 320), dtype=bool)
    thin = centerline(mask)
    assert thin.sum() < 100
    world = DanceMirror(Viewport.fit((320, 240), SCENE_SIZE), mask.shape)
    world.update(mask, 1 / 30)
    assert len(world._segments) <= 1600
    assert len(world._caps) <= 600
