import numpy as np

from magic_rain.interaction.field import MotionField
from magic_rain.live import LiveInput
from magic_rain.sensors.base import SensorFrame, SensorHealth
from magic_rain.vision.background import BackgroundCalibration
from magic_rain.vision.foreground import ForegroundTracker


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


def test_registered_color_repairs_only_nearby_unmeasured_pixels():
    background = np.full((80, 100), 2700, dtype=np.uint16)
    depth = background.copy()
    depth[20:60, 30:50] = 1600
    depth[20:60, 50:56] = 0
    reference = np.full((80, 100, 3), 80, dtype=np.uint8)
    rgb = reference.copy()
    rgb[20:60, 55:64] = (150, 95, 110)
    y, x = np.indices(background.shape, dtype=np.int32)
    coordinates = np.stack((x + 7, y), axis=2)
    tracker = ForegroundTracker(background, color_reference=reference, mirrored=False)
    paired = SensorFrame(1.0, depth, rgb, 100, 80, "simulation",
                         rgb_coordinates=coordinates)
    mask = tracker.update(paired, 1.0).mask
    assert mask[40, 49:53].all()
    assert not mask[40, 53:].any()
    assert not mask[40, 29]  # RGB alone cannot replace measured background.
    unpaired = SensorFrame(1.1, depth, rgb, 100, 80, "simulation")
    assert not tracker.update(unpaired, 1.1).mask[40, 50]
    tracker.configure(mirrored=True, margin=0.12, far=3800)
    assert np.array_equal(tracker.update(paired, 1.0).mask, mask[:, ::-1])


def test_registered_color_does_not_blank_mask_when_depth_coverage_is_sparse():
    background = np.zeros((240, 320), dtype=np.uint16)
    background[30:80, 30:80] = 2000
    depth = background.copy()
    depth[30:80, 30:73] = 1200
    reference = np.zeros((240, 320, 3), dtype=np.uint8)
    rgb = reference.copy()
    rgb[27:83, 27:76] = 100
    y, x = np.indices(background.shape, dtype=np.int32)
    frame = SensorFrame(1, depth, rgb, 320, 240, "simulation",
                        rgb_coordinates=np.stack((x, y), axis=2))
    tracker = ForegroundTracker(background, mirrored=False, color_reference=reference)
    assert tracker.update(frame, 1).mask[40, 28:73].all()


def test_manual_calibration_waits_then_completes_in_open_menu(monkeypatch):
    live = LiveInput()
    depth = np.full((240, 320), 3200, dtype=np.uint16)
    monkeypatch.setattr(
        live._capture, "take",
        lambda: (SensorFrame(4.0, depth, None, 320, 240, "kinect_v1"), None),
    )
    live.calibrate_or_retry(1, from_menu=True)
    live._calibration = BackgroundCalibration(2)
    live.mask(3, preview=True)
    assert live.calibration_status(3) == "Töm spelzonen · 1 s"
    live.mask(4, preview=True)
    assert live.calibration_status(4) == "Kalibrerar · 50%"
    live.mask(4, preview=True)
    assert live.calibration_status(4) == "Kalibrering klar"
