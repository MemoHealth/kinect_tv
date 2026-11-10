from dataclasses import replace

import numpy as np
import pygame
import pytest

from magic_rain.__main__ import main
from magic_rain.app import STEP
from magic_rain.config import SCENE_SIZE, DemoConfig
from magic_rain.coordinates import Viewport
from magic_rain.sensors.base import SensorHealth
from magic_rain.sensors.kinect_v1 import SensorError
from magic_rain.sensors.simulated import OBSTACLE_DEPTH_MM, SimulatedSensor
from magic_rain.simulation.rain import DemoRain


def test_sensor_emits_a_moving_depth_only_obstacle():
    now = 10.0
    sensor = SimulatedSensor(clock=lambda: now)
    assert sensor.read_latest(0) is None
    sensor.start()
    first = sensor.read_latest(0)
    now += 3
    second = sensor.read_latest(0)
    assert first.source == second.source == "simulation"
    assert first.rgb is second.rgb is None
    assert first.depth_mm.dtype == np.uint16
    assert second.timestamp_monotonic_s == 13
    assert not np.array_equal(first.depth_mm, second.depth_mm)

    sensor.pointer = (0.25, 0.75)
    frame = sensor.read_latest(0)
    assert frame.depth_mm[180, 80] == OBSTACLE_DEPTH_MM
    with pytest.raises(ValueError, match="depth"):
        replace(frame, depth_mm=frame.depth_mm.astype(np.uint8))
    with pytest.raises(ValueError, match="timestamp"):
        replace(frame, timestamp_monotonic_s=float("nan"))
    sensor.stop()
    assert sensor.health() is SensorHealth.NO_FRAMES


def test_viewport_preserves_aspect_and_rejects_letterbox():
    camera = Viewport.fit((320, 240), SCENE_SIZE)
    assert camera == Viewport(160, 0, 960, 720)
    assert camera.normalized_point((100, 300)) is None
    point = (400, 540)
    assert camera.point_at(camera.normalized_point(point)) == point
    assert Viewport.fit(SCENE_SIZE, (1024, 768)) == Viewport(0, 96, 1024, 576)


def test_drops_deflect_to_each_side_and_repeat_deterministically():
    field = Viewport.fit((4, 4), SCENE_SIZE)
    obstacle = np.zeros((4, 4), dtype=bool)
    obstacle[1:3, 1:3] = True
    config = DemoConfig(particle_count=2)
    rain = DemoRain(config)
    replay = DemoRain(config)
    for model in (rain, replay):
        model.x[:] = (500, 780)
        model.y[:] = 178
        model.speed[:] = 240
        model.step(STEP, obstacle, field)
        assert model.x[0] < 500 < 780 < model.x[1]
        assert np.all(model.y < 182)
        assert np.all(model.shimmer == 1)

    for _ in range(600):
        rain.step(STEP, obstacle, field)
        replay.step(STEP, obstacle, field)
    np.testing.assert_array_equal(rain.x, replay.x)
    np.testing.assert_array_equal(rain.y, replay.y)
    assert rain.x.size == 2
    with pytest.raises(ValueError, match="particle_count"):
        DemoConfig(particle_count=0)


@pytest.mark.parametrize("args", [[], ["--doctor"]])
def test_real_modes_report_unavailable_without_simulation(args, capsys, monkeypatch):
    def no_device(sensor):
        raise SensorError(SensorHealth.NO_DEVICE, "Ingen Kinect hittades.")

    monkeypatch.setattr("magic_rain.diagnostics.KinectV1Sensor.start", no_device)
    assert main(args) == 1
    output = capsys.readouterr()
    assert "NO_DEVICE" in output.err
    assert output.out == ""


@pytest.mark.parametrize("args", [["--demo", "--windowed"], ["--demo"]])
def test_demo_draws_and_toggles_fullscreen(args, monkeypatch, capsys):
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    observed_modes = []
    flip = pygame.display.flip

    def flip_and_send_key():
        flip()
        screen = pygame.display.get_surface()
        assert screen.get_at(screen.get_rect().center)[:3] != (0, 0, 0)
        observed_modes.append(bool(screen.get_flags() & pygame.FULLSCREEN))
        key = pygame.K_F11 if len(observed_modes) == 1 else pygame.K_ESCAPE
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))

    monkeypatch.setattr(pygame.display, "flip", flip_and_send_key)
    assert main(args) == 0
    assert observed_modes == (["--windowed" not in args, "--windowed" in args])
    assert "Simulerad sensor" in capsys.readouterr().out
    assert not pygame.display.get_init()
