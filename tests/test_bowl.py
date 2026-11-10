import numpy as np
import pytest

from magic_rain.config import SCENE_SIZE, DemoConfig
from magic_rain.coordinates import Viewport
from magic_rain.simulation.bowl import BOWL_BOTTOM, BOWL_CAPACITY, BOWL_RIM, Bowl
from magic_rain.simulation.rain import DemoRain


def test_bowl_uses_swept_rim_crossing_and_ignores_ordinary_drops():
    bowl = Bowl(BOWL_CAPACITY - 1)
    hit = bowl.catch(
        np.array([480.0, 640.0, 640.0]),
        np.array([BOWL_RIM - 2.0] * 3),
        np.array([540.0, 640.0, 640.0]),
        np.array([BOWL_RIM + 2.0] * 3),
        np.array([True, False, True]),
    )
    assert hit.tolist() == [True, False, True]
    assert bowl.level == 1


@pytest.mark.parametrize("snow", [False, True])
def test_body_contacts_fill_bowl_without_rising_particles_from_floor(snow):
    rain = DemoRain(DemoConfig(particle_count=180), snow=snow)
    bowl = Bowl()
    mask = np.zeros((240, 320), dtype=bool)
    field = Viewport.fit((320, 240), SCENE_SIZE)
    for _ in range(120):
        rain.step(1 / 60, mask, field, bowl=bowl)
    assert bowl.amount == 0
    mask[145:156, 126:184] = True
    for _ in range(480):
        rain.step(1 / 60, mask, field, bowl=bowl)
    assert bowl.amount > 0
    assert rain.y.max() < BOWL_BOTTOM
