import numpy as np

from magic_rain.app import STEP
from magic_rain.audio.ambient import rain_loop
from magic_rain.config import SCENE_SIZE, DemoConfig
from magic_rain.coordinates import Viewport
from magic_rain.simulation.rain import DemoRain


def test_swept_path_catches_thin_obstacle():
    rain = DemoRain(DemoConfig(particle_count=1))
    rain.x[:] = 500
    rain.y[:] = 297.5
    rain.speed[:] = 390
    field = Viewport(0, 0, *SCENE_SIZE)
    mask = np.zeros((240, 320), dtype=bool)
    mask[100, 110:130] = True
    rain.step(STEP, mask, field)
    assert rain.y[0] < 300
    assert rain.shimmer[0] > 0


def test_ambient_loop_is_reproducible_and_level_bounded():
    loop = rain_loop(22050)
    assert loop.shape == (88200,)
    assert loop.dtype == np.int16
    assert 0 < np.max(np.abs(loop)) <= 1700
    np.testing.assert_array_equal(loop, rain_loop(22050))
