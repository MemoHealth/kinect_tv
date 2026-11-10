import numpy as np

from magic_rain.live import LiveInput
from magic_rain.sensors.base import SensorFrame
from magic_rain.sensors.tilt import Tilt
from magic_rain.vision.background import BackgroundCalibration


def test_tilt_limits_busy_interval_and_motor_rest():
    tilt = Tilt()
    assert tilt.request(1, 0)
    tilt.angle = 25
    assert not tilt.request(1, 0)
    assert tilt.target == 27
    assert tilt.request(-1, 1)
    tilt.finish(1, success=True)
    assert tilt.angle == 27
    assert tilt.busy(2)
    assert tilt.request(-1, 3)
    assert tilt.request(1, 4)
    for count in range(11):
        now = 5 + count * 3
        assert not tilt.request(-1 if count % 2 == 0 else 1, now)
        tilt.finish(now, success=True)
    assert tilt.request(1, 54)
    assert not tilt.request(1, 56)


def test_tilt_failure_leaves_angle_and_reports_warning():
    tilt = Tilt(angle=-5)
    assert not tilt.request(-1, 0)
    tilt.finish(1, success=False)
    assert tilt.angle == -5
    assert tilt.warning
    assert not tilt.busy(3)


def test_depth_preview_does_not_calibrate_until_menu_closes(monkeypatch):
    live = LiveInput()
    live._calibration = BackgroundCalibration(2)
    depth = np.full((240, 320), 2200, dtype=np.uint16)
    frame = SensorFrame(1.0, depth, None, 320, 240, "kinect_v1")
    monkeypatch.setattr(live._capture, "take", lambda: (frame, None))
    for _ in range(4):
        assert not live.mask(1, preview=True).any()
        assert live.preview_depth is not None
        assert live._tracker is None
    live.mask(1)
    assert live._tracker is None
    assert live.preview_depth is None
    live.mask(1)
    assert live._tracker is not None
