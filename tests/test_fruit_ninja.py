import numpy as np
import pygame

from magic_rain.config import SCENE_SIZE
from magic_rain.coordinates import Viewport
from magic_rain.render.fruit_ninja import Fruit, FruitNinja


def mask() -> np.ndarray:
    body = np.zeros((240, 320), dtype=bool)
    for x in (50, 160, 270):
        body[85:135, x - 8:x + 8] = True
    return body


def test_three_moving_regions_can_cut_three_fruits_without_scores():
    world = FruitNinja(Viewport(0, 0, 320, 240), (240, 320))
    world._next_fruit = 100
    world.fruits = [Fruit(x, 110, 0, 0, i) for i, x in enumerate((50, 160, 270))]
    world.update(mask(), 0)
    assert not world.fruits
    assert len(world.halves) == 6
    assert np.count_nonzero(world._juice.life > 0) == 36
    world.draw(pygame.Surface(SCENE_SIZE))


def test_stationary_silhouette_does_not_cut_until_it_moves():
    world = FruitNinja(Viewport(0, 0, 320, 240), (240, 320))
    body = mask()
    world.update(body, 0)
    world.update(body, 0.2)
    world._next_fruit = 100
    world.fruits = [Fruit(50, 110, 0, 0, 0)]
    world.update(body, 0.01)
    assert len(world.fruits) == 1
    world.update(np.roll(body, 5, axis=1), 0.01)
    assert not world.fruits and len(world.halves) == 2


def test_ambient_fruit_keeps_respawning_and_storage_is_bounded():
    world = FruitNinja(Viewport.fit((320, 240), SCENE_SIZE), (240, 320))
    empty = np.zeros((240, 320), dtype=bool)
    highest = 0
    for _ in range(1800):
        world.update(empty, 1 / 30)
        highest = max(highest, len(world.fruits))
        assert len(world.fruits) <= 7 and len(world.halves) <= 14
    assert highest >= 3
