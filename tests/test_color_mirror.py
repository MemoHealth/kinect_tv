import numpy as np
import pygame

from magic_rain.coordinates import Viewport
from magic_rain.live import LiveInput
from magic_rain.render.color_mirror import ColorMirror
from magic_rain.sensors.base import SensorFrame
from magic_rain.sensors.capture import LatestDepth
from magic_rain.sensors.kinect_v1 import KinectV1Sensor, _decode_color
from magic_rain.sensors.tilt import Tilt
from magic_rain.settings import (
    FUNHOUSE_STRENGTH,
    Settings,
    load_settings,
    save_settings,
)


def test_color_frame_pitch_and_channel_order():
    buffer = np.zeros((480, 642, 4), dtype=np.uint8)
    buffer[2, 4] = [16, 48, 225, 0]
    rgb = _decode_color(buffer.tobytes(), buffer.strides[0])
    assert rgb.shape == (240, 320, 3)
    assert rgb[1, 2].tolist() == [225, 48, 16]


def test_mirror_renders_the_live_colors_with_optional_horizontal_flip():
    mirror = ColorMirror(Viewport(0, 0, 40, 20), (20, 40))
    frame = np.zeros((20, 40, 3), dtype=np.uint8)
    frame[:, :20] = (200, 20, 50)
    frame[:, 20:] = (20, 100, 220)
    canvas = pygame.Surface((40, 20), depth=32)
    mirror.draw(canvas, frame, -0.37, mirrored=True)
    assert canvas.get_at((3, 10))[:3] == (20, 100, 220)
    mirror.draw(canvas, frame, 0.44, mirrored=False)
    assert canvas.get_at((3, 10))[:3] == (200, 20, 50)


def test_color_is_opt_in_each_session_and_cleared_on_scene_exit(tmp_path, monkeypatch):
    path = tmp_path / "settings.json"
    scene = next(iter(FUNHOUSE_STRENGTH))
    path.write_text(f'{{"version":1,"scene":"{scene}"}}', encoding="utf-8")
    assert load_settings(path).scene == "Regn"
    assert save_settings(path, Settings(scene=scene))
    assert scene not in path.read_text(encoding="utf-8")

    live = LiveInput()
    rgb = np.zeros((240, 320, 3), dtype=np.uint8)
    depth = np.ones((240, 320), dtype=np.uint16)
    frame = SensorFrame(1.0, depth, rgb, 320, 240, "kinect_v1")
    monkeypatch.setattr(live._capture, "take", lambda: (frame, None))
    live.mask(1.0)
    assert live.color_image is None
    live._color_enabled = True
    live.mask(1.0)
    assert live.color_image is rgb
    assert len(live._calibration._samples) == 1
    live.mask(1.3)
    assert live.color_image is None
    live.mask(1.0)
    live.set_color(False)
    assert live.color_image is None


def test_camera_mode_switch_keeps_motor_cooldown_without_pending_movement():
    limits = Tilt(angle=5, target=10, next_move=30, moves=11)
    old = LatestDepth(KinectV1Sensor(), tilt=limits)
    replacement = old.replacement(KinectV1Sensor(color=True))
    assert replacement._tilt.target is None
    replacement._tilt.angle = 5
    assert replacement.request_tilt(1, 29)
    assert not replacement.request_tilt(1, 31)
    replacement._tilt.finish(32, success=True)
    assert replacement._tilt.next_move == 52
