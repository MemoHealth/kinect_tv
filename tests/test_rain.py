import numpy as np

from magic_rain.app import STEP
from magic_rain.audio.ambient import rain_loop
from magic_rain.config import SCENE_SIZE, DemoConfig
from magic_rain.coordinates import Viewport
from magic_rain.render.scene import DROP_ANGLES, RAIN_LAYERS, Scene, _orient, _streak
from magic_rain.simulation.arm_water import ArmWater
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


def test_snow_uses_slower_particles_and_deterministic_drift():
    snow = DemoRain(DemoConfig(particle_count=32), snow=True)
    replay = DemoRain(DemoConfig(particle_count=32), snow=True)
    rain = DemoRain(DemoConfig(particle_count=32))
    assert snow.speed.max() < rain.speed.min()
    mask = np.zeros((240, 320), dtype=bool)
    field = Viewport(0, 0, *SCENE_SIZE)
    for _ in range(20):
        snow.step(STEP, mask, field)
        replay.step(STEP, mask, field)
    np.testing.assert_array_equal(snow.x, replay.x)


def test_recycled_drops_reenter_across_the_sky_without_old_shimmer():
    rain = DemoRain(DemoConfig(particle_count=8))
    rain.x[:] = 500
    rain.y[:] = SCENE_SIZE[1] + 19
    rain.shimmer[:] = 1
    rain.slide[:] = 200
    field = Viewport(0, 0, *SCENE_SIZE)
    rain.step(STEP, np.zeros((240, 320), dtype=bool), field)
    assert (rain.y < 0).all()
    assert np.ptp(rain.x) > 500
    assert not rain.shimmer.any()
    assert not rain.slide.any()


def test_rain_streaks_have_dim_tails_and_brighter_near_tips():
    far = _streak(16, *RAIN_LAYERS[0][1:])
    near = _streak(16, *RAIN_LAYERS[2][1:])
    assert sum(near.get_at((2, 16))[:3]) > sum(far.get_at((2, 16))[:3])
    assert sum(near.get_at((2, 16))[:3]) > sum(near.get_at((1, 0))[:3])

    rain = DemoRain(DemoConfig(particle_count=60))
    layers = rain.depth_band.copy()
    assert set(layers) == {0, 1, 2}
    rain.step(STEP, np.zeros((240, 320), dtype=bool), Viewport(0, 0, *SCENE_SIZE))
    np.testing.assert_array_equal(rain.depth_band, layers)


def test_rotated_raindrop_keeps_the_bright_tip_at_its_anchor():
    import pygame

    source = _streak(24, *RAIN_LAYERS[2][1:])
    for angle in DROP_ANGLES:
        sprite, anchor = _orient(source, (2, 24), angle)
        canvas = pygame.Surface((100, 100))
        canvas.blit(sprite, (round(50 - anchor[0]), round(50 - anchor[1])))
        light = pygame.surfarray.array3d(canvas).sum(axis=2)
        x, y = np.unravel_index(light.argmax(), light.shape)
        assert abs(x - 50) <= 2 and abs(y - 50) <= 2


def test_floor_ripples_are_bounded_and_do_not_follow_random_respawn_x(monkeypatch):
    import pygame

    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    pygame.display.init()
    pygame.display.set_mode((1280, 720))
    try:
        scene = Scene()
        rain = DemoRain(DemoConfig(particle_count=270))
        rain.y[:] = 710
        rain.x[:] = 400
        scene.draw(rain)
        mask = np.zeros((240, 320), dtype=bool)
        field = Viewport.fit((320, 240), SCENE_SIZE)
        rain.step(0.01, mask, field, water=ArmWater())
        scene.draw(rain)
        assert len(scene._ripples) == 24
        assert all(399 < x < 401 for x, _, _ in scene._ripples)
        scene.draw(rain)
        assert len(scene._ripples) == 24
        for _ in range(60):
            rain.step(1 / 60, mask, field, water=ArmWater())
        scene.draw(rain)
        assert not scene._ripples
    finally:
        pygame.display.quit()


def test_collected_water_does_not_emit_a_floor_impact(monkeypatch):
    rain = DemoRain(DemoConfig(particle_count=8))
    rain.y[:] = 707
    water = ArmWater()
    monkeypatch.setattr(water, "collect", lambda *args, **kw: np.ones(8, dtype=bool))
    rain.step(0.02, np.zeros((240, 320), dtype=bool),
              Viewport.fit((320, 240), SCENE_SIZE), water=water)
    assert not rain.floor_hits.any()
