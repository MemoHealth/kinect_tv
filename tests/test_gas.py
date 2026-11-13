import numpy as np
import pygame
import pytest

from magic_rain.app import make_world
from magic_rain.config import SCENE_SIZE
from magic_rain.coordinates import Viewport
from magic_rain.render.gas import StarGas
from magic_rain.settings import GAS_SCENE, Settings, load_settings, save_settings
from magic_rain.simulation.gas import MAX_SPEED, GasParticles

FIELD = Viewport.fit((320, 240), SCENE_SIZE)
SHAPE = (240, 320)


def sweep(pixels_per_frame, axis=0, sign=1):
    gas = GasParticles(FIELD, SHAPE, count=1)
    origin = np.array((FIELD.x, FIELD.y))
    scale = np.array((FIELD.width / 320, FIELD.height / 240))
    point = np.array((100.5, 100.5))
    point[axis] = 125.5 if sign > 0 else 74.5
    gas.position[0] = origin + point * scale
    peak = 0.0
    for frame in range(30):
        low = 80 + sign * pixels_per_frame * frame
        high = low + 40
        mask = np.zeros(SHAPE, dtype=bool)
        if axis == 0:
            mask[60:160, max(0, low):min(320, high)] = True
        else:
            mask[max(0, low):min(240, high), 60:160] = True
        for _ in range(2):
            gas.step(mask, 1 / 60)
            peak = max(peak, sign * gas.velocity[0, axis])
    return peak, gas


@pytest.mark.parametrize('axis,sign', [(0, 1), (0, -1), (1, 1), (1, -1)])
def test_slow_and_fast_contact_transfer_directional_speed(axis, sign):
    slow, _ = sweep(1, axis, sign)
    fast, gas = sweep(4, axis, sign)
    assert 10 < slow < fast
    assert fast > slow * 1.5
    assert np.linalg.norm(gas.velocity, axis=1).max() <= MAX_SPEED + 1e-8


@pytest.mark.parametrize('amplitude', [1, 2])
def test_first_detection_jitter_stillness_and_reentry_do_not_punch(amplitude):
    gas = GasParticles(FIELD, SHAPE, count=1)
    gas.position[0] = (FIELD.x + 120 * 3, 100 * 3)
    empty = np.zeros(SHAPE, dtype=bool)
    for frame in range(90):
        mask = empty.copy()
        if frame not in range(40, 45):
            jitter = amplitude if frame % 2 else -amplitude
            mask[50:170, 80 + jitter:120 + jitter] = True
        gas.step(mask, 1 / 30)
        assert np.linalg.norm(gas.velocity[0]) < 1e-6
    assert np.isfinite(gas.position).all()
    # A stationary obstacle reflects an incoming particle without adding energy.
    gas.position[0] = (FIELD.x + 130 * 3, 100 * 3)
    gas.velocity[0] = (-160, 0)
    for _ in range(30):
        gas.step(mask, 1 / 60)
    assert 0 < gas.velocity[0, 0] < 160


def test_three_bodies_push_locally_and_fast_particles_cannot_cross_a_thin_arm():
    gas = GasParticles(FIELD, SHAPE, count=3)
    gas.position[:] = [(FIELD.x + (x + 25.5) * 3, 110 * 3) for x in (40, 140, 240)]
    peak = np.zeros(3)
    for frame in range(7):
        mask = np.zeros(SHAPE, dtype=bool)
        for x in (40, 140, 240):
            mask[60:190, x + frame * 2:x + 20 + frame * 2] = True
        gas.step(mask, 1 / 30)
        peak = np.maximum(peak, gas.velocity[:, 0])
    assert (peak > 20).all()

    gas = GasParticles(FIELD, SHAPE, count=1)
    mask = np.zeros(SHAPE, dtype=bool)
    mask[40:200, 150] = True
    gas.position[0] = (FIELD.x + 150 * 3 - 12, 100 * 3)
    gas.velocity[0] = (MAX_SPEED, 0)
    gas.step(mask, 1 / 30)
    assert gas.velocity[0, 0] < 0
    assert gas.position[0, 0] < FIELD.x + 150 * 3


def test_walls_dissipate_energy_without_gravity():
    gas = GasParticles(FIELD, SHAPE, count=1)
    gas.position[0] = (SCENE_SIZE[0] - 4, 350)
    gas.velocity[0] = (100, 0)
    empty = np.zeros(SHAPE, dtype=bool)
    for _ in range(10):
        gas.step(empty, 1 / 60)
    assert -100 < gas.velocity[0, 0] < 0
    assert abs(gas.velocity[0, 1]) < 1e-6
    assert abs(gas.position[0, 1] - 350) < 1e-6


def test_minute_relaxation_reduces_energy_and_spreads_compressed_cloud():
    gas = GasParticles(FIELD, SHAPE, count=160)
    gas.position[:, 0] *= 0.45
    rng = np.random.default_rng(7)
    gas.velocity[:] = rng.uniform(-200, 200, gas.velocity.shape)
    empty = np.zeros(SHAPE, dtype=bool)

    def unevenness():
        density, _, _ = np.histogram2d(
            gas.position[:, 0], gas.position[:, 1], bins=(8, 4),
            range=((0, 1280), (0, 720)),
        )
        return density.std()

    before = unevenness()
    peak = np.sqrt(np.mean(gas.velocity ** 2))
    for _ in range(1800):
        gas.step(empty, 1 / 30)
    assert np.sqrt(np.mean(gas.velocity ** 2)) < peak * 0.1
    assert unevenness() < before * 0.65
    assert np.isfinite(gas.position).all()
    assert gas.position.shape == gas.velocity.shape == (160, 2)


def test_fixed_step_is_render_rate_independent_and_mode_is_persistent(tmp_path):
    states = []
    for fps in (30, 60):
        gas = GasParticles(FIELD, SHAPE, count=40)
        gas.velocity[:] = (80, -25)
        empty = np.zeros(SHAPE, dtype=bool)
        for _ in range(fps):
            gas.step(empty, 1 / fps)
        states.append(gas.position.copy())
    np.testing.assert_allclose(states[0], states[1], atol=1e-7)
    settings = Settings(scene=GAS_SCENE)
    path = tmp_path / 'settings.json'
    assert save_settings(path, settings)
    assert load_settings(path).scene == GAS_SCENE
    world = make_world(settings, FIELD, SHAPE)
    assert isinstance(world, StarGas)
    world.update(np.zeros(SHAPE, dtype=bool), 1 / 60)
    canvas = pygame.Surface(SCENE_SIZE)
    world.draw(canvas)
    assert world.particles.position.shape == (600, 2)
    assert pygame.surfarray.array3d(canvas).max() > 100
    world.configure("Milt")
    assert world._visible == 300 and world._tail_limit < 120
    assert world.particles.position.shape == (600, 2)


def test_mutual_repulsion_separates_neighbours_without_a_directional_bias():
    gas = GasParticles(FIELD, SHAPE, count=2)
    gas.position[:] = ((600, 360), (610, 360))
    empty = np.zeros(SHAPE, dtype=bool)
    centre = gas.position.mean(axis=0)
    for _ in range(360):
        gas.step(empty, 1 / 60)
    assert gas.position[1, 0] - gas.position[0, 0] > 11
    np.testing.assert_allclose(gas.position.mean(axis=0), centre, atol=1e-6)


def test_moving_contacts_match_at_30_and_60_render_fps():
    states = []
    for fps in (30, 60):
        gas = GasParticles(FIELD, SHAPE, count=1)
        gas.position[0] = (FIELD.x + 125.5 * 3, 100.5 * 3)
        for frame in range(fps):
            if frame % (fps // 30) == 0:
                column = 80 + (frame * 30 // fps) * 2
                mask = np.zeros(SHAPE, dtype=bool)
                mask[60:160, column:column + 40] = True
            gas.step(mask, 1 / fps)
        states.append((gas.position.copy(), gas.velocity.copy()))
    np.testing.assert_allclose(states[0], states[1], atol=1e-6)


def test_slow_contact_remains_responsive_at_20_hz_sensor_delivery():
    gas = GasParticles(FIELD, SHAPE, count=1)
    gas.position[0] = (FIELD.x + 125.5 * 3, 100.5 * 3)
    peak = 0
    for frame in range(30):
        mask = np.zeros(SHAPE, dtype=bool)
        mask[60:160, 80 + frame:120 + frame] = True
        for _ in range(3):
            gas.step(mask, 1 / 60)
            peak = max(peak, gas.velocity[0, 0])
    assert peak > 10
