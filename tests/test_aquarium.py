import numpy as np
import pygame

from magic_rain.config import SCENE_SIZE
from magic_rain.coordinates import Viewport
from magic_rain.render.aquarium import LivingAquarium


def test_three_silhouettes_attract_fish_and_displace_jellyfish():
    field = Viewport.fit((320, 240), SCENE_SIZE)
    world = LivingAquarium(field, (240, 320))
    mask = np.zeros((240, 320), dtype=bool)
    for x in (40, 140, 240):
        mask[65:195, x:x + 25] = True
        mask[100:107, x - 15:x + 40] = True
    world.update(mask, 0)
    assert len(world.targets) == 6
    hand = world.targets[0]
    world.position[0] = hand - (130, 0)
    world.position[24] = hand - (75, 0)
    world.velocity[[0, 24]] = 0
    world.update(mask, 0.1)
    assert world.velocity[0, 0] > 0  # Fish approaches the outstretched hand.
    assert world.velocity[24, 0] < 0  # Jelly avoids the same silhouette.
    for _ in range(120):
        world.update(np.zeros_like(mask), 1 / 30)
    assert not world.targets.size
    assert world.position.shape == (29, 2)
    assert np.isfinite(world.position).all()
    world.draw(pygame.Surface(SCENE_SIZE))
