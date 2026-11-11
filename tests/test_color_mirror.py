import numpy as np
import pygame

from magic_rain.coordinates import Viewport
from magic_rain.live import LiveInput
from magic_rain.render.mirror_studio import MirrorStudio
from magic_rain.sensors.base import SensorFrame
from magic_rain.sensors.capture import LatestDepth
from magic_rain.sensors.kinect_v1 import KinectV1Sensor, _decode_color
from magic_rain.sensors.tilt import Tilt
from magic_rain.settings import (
    MIRROR_SCENE,
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
    mirror = MirrorStudio(Viewport(0, 0, 40, 20), (20, 40))
    frame = np.zeros((20, 40, 3), dtype=np.uint8)
    frame[:, :20] = (200, 20, 50)
    frame[:, 20:] = (20, 100, 220)
    canvas = pygame.Surface((40, 20), depth=32)
    mask = np.ones((20, 40), dtype=bool)
    mirror.set_color(frame, mirrored=True)
    mirror.update(mask, 0.1)
    mirror.draw(canvas)
    assert canvas.get_at((3, 10))[:3] == (20, 100, 220)
    mirror.set_color(frame, mirrored=False)
    mirror.update(mask, 0.1)
    mirror.draw(canvas)
    assert canvas.get_at((3, 10))[:3] == (200, 20, 50)


def test_color_mirror_selection_is_session_only_and_color_can_calibrate(
    tmp_path, monkeypatch
):
    path = tmp_path / "settings.json"
    scene = MIRROR_SCENE
    path.write_text(f'{{"version":1,"scene":"{scene}"}}', encoding="utf-8")
    assert load_settings(path).scene == "Regn"
    assert save_settings(path, Settings(scene=scene))
    assert scene not in path.read_text(encoding="utf-8")
    path.write_text('{"version":1,"scene":"Lustiga huset · Konvex"}', encoding="utf-8")
    assert load_settings(path).scene == "Regn"

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
    assert len(live._calibration._samples) == 2
    live.mask(1.3)
    assert live.color_image is None
    live.mask(1.0)
    live.set_color(False)
    assert live.color_image is None


def test_mirror_styles_and_loss_of_color_clear_live_reflections():
    studio = MirrorStudio(Viewport(0, 0, 64, 48), (48, 64))
    frame = np.zeros((48, 64, 3), dtype=np.uint8)
    frame[8:35, 12:26] = (150, 90, 220)
    mask = frame[:, :, 0] > 0
    studio.set_color(frame, mirrored=False)
    studio.update(mask, 0.1)
    canvas = pygame.Surface((64, 48))
    studio.draw(canvas)
    echo = pygame.image.tobytes(canvas, "RGB")
    studio.configure("Kalejdoskop")
    studio.draw(canvas)
    assert pygame.image.tobytes(canvas, "RGB") != echo
    studio.configure("Eko")
    studio.set_color(np.zeros_like(frame), mirrored=False)
    for _ in range(45):
        studio.update(np.zeros_like(mask), 1 / 60)
    studio.draw(canvas)
    assert not pygame.surfarray.array3d(canvas).any()
    studio.set_color(None, mirrored=False)
    studio.update(np.zeros_like(mask), 0.1)
    studio.draw(canvas)
    assert not pygame.surfarray.array3d(canvas).any()
    assert len(studio._samples) <= 4


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
