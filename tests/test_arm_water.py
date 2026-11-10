import numpy as np
import pytest

from magic_rain.config import DemoConfig
from magic_rain.coordinates import Viewport
from magic_rain.simulation.arm_water import ArmWater, find_basins
from magic_rain.simulation.rain import DemoRain


def cups(positions=(45,)):
    mask = np.zeros((100, 300), dtype=bool)
    for left in positions:
        mask[27:60, left - 4:left] = True
        mask[34:60, left + 36:left + 40] = True
        mask[60:66, left - 4:left + 40] = True
    return mask


def test_three_open_topped_cups_need_a_floor_and_find_lower_lip():
    mask = cups((45, 130, 220))
    basins = find_basins(mask)
    assert len(basins) == 3
    assert all(basin.top == 34 and basin.lip == 1 for basin in basins)
    assert not find_basins(mask[:60])
    mask[23:27, :] = True
    mask[27:34, :] = True
    assert not find_basins(mask)


def test_open_floor_does_not_hold_water():
    mask = cups()
    mask[60:66, 71:81] = False
    assert not find_basins(mask)


@pytest.mark.parametrize("snow, amount", [(False, 14), (True, 28)])
def test_precipitation_raises_a_horizontal_surface_inside_the_arms(snow, amount):
    field = Viewport(0, 0, 300, 100)
    water = ArmWater()
    water.update(cups(), field)
    pool = water.pools[0]
    initial = pool.basin.surface(0)[1]
    x = np.array([60.0, 100.0])
    y = np.array([58.0, 58.0])
    caught = water.collect(x, y, x, y + 4, field, snow=snow)
    assert caught.tolist() == [True, False]
    assert pool.amount == amount
    assert pool.basin.surface(pool.amount)[1] < initial
    assert not water.take_spills(8)


def test_overflow_uses_lower_arm_and_opening_releases_remaining_water():
    field = Viewport(0, 0, 300, 100)
    water = ArmWater()
    water.update(cups(), field)
    pool = water.pools[0]
    pool.amount = pool.basin.capacity - 1
    x = np.array([60.0])
    y = np.array([33.0])
    assert water.collect(x, y, x, y + 2, field, snow=False).all()
    assert pool.amount == pool.basin.capacity
    spill = water.take_spills(1)
    spill_x, spill_y, velocity = spill[0]
    assert spill_x >= 85 and velocity > 0
    assert not cups()[int(spill_y), int(spill_x)]
    opened = cups()
    opened[34:60, 81:85] = False
    water.update(opened, field)
    assert not water.pools
    assert len(water.take_spills(32)) > 0


def test_rain_captures_at_bottom_and_does_not_respawn_from_floor():
    field = Viewport(0, 0, 300, 100)
    water = ArmWater()
    mask = cups()
    water.update(mask, field)
    rain = DemoRain(DemoConfig(particle_count=2))
    rain.x[:] = (60, 220)
    rain.y[:] = (59, 707)
    rain.step(1 / 60, mask, field, water=water)
    assert water.pools[0].amount == 14
    assert (rain.y < 0).all()
