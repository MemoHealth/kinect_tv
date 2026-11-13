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
    body = mask()
    world.update(body, 0)
    world.fruits = [Fruit(x, 110, 0, 0, i) for i, x in enumerate((50, 160, 270))]
    world.update(np.roll(body, 7, axis=1), 0)
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
        assert len(world.fruits) <= 10 and len(world.halves) <= 20
    assert highest >= 3


def test_two_pixel_jitter_and_reacquisition_do_not_slice():
    world = FruitNinja(Viewport(0, 0, 320, 240), (240, 320))
    world._next_fruit = 100
    body = mask()
    world.update(body, 0)
    for shift in (-2, 2, -1, 1, 0) * 10:
        world.fruits = [Fruit(50, 110, 0, 0, 0)]
        world.update(np.roll(body, shift, axis=1), 1 / 30)
        assert not world.halves
    world.update(np.zeros_like(body), 1 / 30)
    world.fruits = [Fruit(50, 110, 0, 0, 0)]
    world.update(body, 1 / 30)
    assert len(world.fruits) == 1 and not world.halves


def test_more_fruit_arrives_from_above_as_well_as_below():
    world = FruitNinja(Viewport.fit((320, 240), SCENE_SIZE), (240, 320))
    empty = np.zeros((240, 320), dtype=bool)
    for _ in range(10):
        world._next_fruit = 0
        world.update(empty, 0)
        assert 0.32 <= world._next_fruit <= 0.56
    assert len(world.fruits) == 10
    assert sum(fruit.y < 0 and fruit.vy > 0 for fruit in world.fruits) >= 5
    assert any(fruit.y > SCENE_SIZE[1] and fruit.vy < 0 for fruit in world.fruits)


def test_intentional_sweeps_hit_at_production_viewport_scale():
    field = Viewport.fit((320, 240), SCENE_SIZE)
    world = FruitNinja(field, (240, 320))
    world._next_fruit = 100
    body = mask()
    moved = np.roll(body, 7, axis=1)
    world.update(body, 0)
    world.fruits = [
        Fruit(*field.point_at(((x + 14.5) / 320, 110.5 / 240)), 0, 0, i)
        for i, x in enumerate((50, 160, 270))
    ]
    world.update(moved, 1 / 60)
    assert not world.fruits and len(world.halves) == 6
