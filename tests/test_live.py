import numpy as np

from magic_rain.interaction.field import MotionField
from magic_rain.live import LiveInput
from magic_rain.sensors.base import SensorFrame, SensorHealth
from magic_rain.vision.background import BackgroundCalibration


def test_live_calibrates_keeps_three_regions_then_clears_on_fault(monkeypatch):
    scene = LiveInput(mirrored=False)
    scene._calibration = BackgroundCalibration(3)
    depth = np.full((240, 320), 3200, dtype=np.uint16)
    people = depth.copy()
    people[40:210, 30:76] = 1400
    people[64:210, 130:170] = 1600
    people[55:202, 230:276] = 1750

    def depth_frame(depth, timestamp):
        return SensorFrame(timestamp, depth, None, 320, 240, "kinect_v1")

    inputs = iter(
        [(depth_frame(depth, t), None) for t in (1.0, 1.1, 1.2)]
        + [(depth_frame(people, 1.3), None), (None, SensorHealth.NO_DEVICE)]
    )
    monkeypatch.setattr(scene._capture, "take", lambda: next(inputs))
    for now in (1.0, 1.1, 1.2):
        assert not scene.mask(now).any()
    assert scene.notice == ""
    assert scene.mask(1.3)[100, [50, 150, 250]].all()
    assert not scene.mask(1.4).any()
    assert "Kinect" in scene.notice


def test_local_wind_follows_movement_then_decays():
    motion = MotionField()
    start = np.zeros((240, 320), dtype=bool)
    start[40:140, 30:86] = True
    end = np.zeros_like(start)
    end[40:140, 38:94] = True
    for _ in range(120):
        motion.update(start, 1 / 60)
    motion.update(end, 1 / 60)
    assert motion.wind[8:14, :14].max() > 0
    assert not motion.wind[:, 20:].any()
    for _ in range(180):
        motion.update(end, 1 / 60)
    assert np.abs(motion.wind).max() < 0.01
    motion.update(np.zeros_like(end), 1 / 60)
    assert np.abs(motion.wind).max() < 0.01
