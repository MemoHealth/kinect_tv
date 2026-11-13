import numpy as np

from magic_rain.sensors.base import SensorFrame
from magic_rain.vision.background import BackgroundCalibration
from magic_rain.vision.foreground import ForegroundTracker


def frame(depth, timestamp=1.0):
    height, width = depth.shape
    return SensorFrame(timestamp, depth, None, width, height, "simulation")


def enter(tracker, depth, timestamp=1.0):
    tracker.update(frame(depth, timestamp), timestamp)
    return tracker.update(frame(depth, timestamp + 1 / 30), timestamp + 1 / 30)


def test_reference_prefers_room_surface_and_requires_coverage():
    calibration = BackgroundCalibration(sample_count=3)
    empty = np.full((30, 50), 3000, dtype=np.uint16)
    moving = empty.copy()
    moving[:, :4] = 1800
    moving[:, -4:] = 0
    assert calibration.add(frame(moving)) is None
    assert calibration.add(frame(empty)) is None
    np.testing.assert_array_equal(calibration.add(frame(empty)), empty)

    missing = np.zeros_like(empty)
    for _ in range(3):
        assert calibration.add(frame(missing)) is None


def test_three_people_and_overlap_keep_all_visible_regions_and_mirror_once():
    empty = np.full((40, 80), 3200, dtype=np.uint16)
    people = empty.copy()
    people[10:35, 5:15] = 1500
    people[8:34, 31:45] = 1750
    people[12:34, 60:71] = 2100
    tracker = ForegroundTracker(empty)
    result = enter(tracker, people)
    assert result.active
    assert result.mask[20, [70, 40, 10]].all()
    assert not result.mask[20, [20, 50]].any()
    assert result.mask[20, 74] and not result.mask[20, 5]

    people[20:24, 14:33] = 1500
    result = tracker.update(frame(people, 1.1), 1.1)
    assert result.mask[22, 79 - 22]
    assert result.mask[22, 10]


def test_empty_invalid_and_stale_frames_cannot_leave_a_frozen_silhouette():
    background = np.full((40, 80), 3000, dtype=np.uint16)
    tracker = ForegroundTracker(background, mirrored=False)
    person = background.copy()
    person[10:35, 5:15] = 1500
    assert enter(tracker, person).active
    assert tracker.update(None, 1.2).active
    assert not tracker.update(None, 1.3).mask.any()
    assert not tracker.update(frame(person), 1.4).active
    assert not tracker.update(frame(np.zeros_like(background), 2), 2).active
    assert not tracker.update(frame(np.full_like(background, 1400), 3), 3).active


def test_sparse_reference_flood_and_speckles_are_rejected():
    background = np.zeros((40, 80), dtype=np.uint16)
    background[:, :16] = 3000
    tracker = ForegroundTracker(background)
    flood = np.where(background, 1600, 0).astype(np.uint16)
    assert not tracker.update(frame(flood), 1).active

    noise = background.copy()
    noise[2:4, 2:4] = noise[10:12, 2:4] = noise[22:24, 2:4] = 1600
    assert not tracker.update(frame(noise), 1).active


def test_players_stay_whole_against_a_background_outside_depth_range():
    calibration = BackgroundCalibration(10)
    empty = np.zeros((90, 120), dtype=np.uint16)
    empty[60:] = 3000
    intermittent = empty.copy()
    intermittent[10:45, 90:105] = 2000
    for sample in [intermittent] * 2 + [empty] * 8:
        reference = calibration.add(frame(sample))
    assert reference is not None
    tracker = ForegroundTracker(
        reference, mirrored=False, open_background=calibration.open_background
    )
    assert not tracker.update(frame(empty), 1).active

    people = empty.copy()
    people[15:77, 12:29] = 1800
    people[23:69, 49:65] = 2000
    people[31:70, 75:87] = 2100
    people[10:45, 90:105] = 2000
    people[18:27, 32:43] = 3900
    result = enter(tracker, people, 1.1).mask
    assert result[16:76, 20].all()
    assert result[24:68, 54].all()
    assert result[32:69, 80].all()
    assert not result[:, 90:105].any()  # Intermittent returns are not open background.
    assert not result[18:27, 32:43].any()  # Beyond the play range.
    assert not tracker.update(frame(np.full_like(empty, 1400), 1.2), 1.2).active

    flood = empty.copy()
    flood[60:] = 1400
    flood[15:25, 12:29] = 1400
    assert not tracker.update(frame(flood, 1.3), 1.3).active


def test_variable_background_and_small_noise_do_not_dominate_three_players():
    calibration = BackgroundCalibration(16)
    room = np.full((240, 320), 3200, dtype=np.uint16)
    room[30:190, 170:300] = 2400
    nearer = room.copy()
    nearer[30:190, 170:300] = 2000
    for sample in [nearer] * 4 + [room] * 12:
        reference = calibration.add(frame(sample))
    tracker = ForegroundTracker(
        reference, mirrored=False, foreground_margin=calibration.foreground_margin
    )
    noise = room.copy()
    noise[30:190, 170:300] = 2100
    noise[12:18, 15:21] = 1400
    noise[210:214, 100:104] = 1400
    assert not tracker.update(frame(noise), 1).active
    for x in (40, 130, 250):
        noise[60:200, x:x + 18] = 1400
    noise[99:102, 58:85] = 1400
    mask = enter(tracker, noise, 1.1).mask
    assert mask[120, [48, 138, 258]].all()
    assert mask[100, 78]
    assert not mask[12:18, 15:21].any()
    assert not mask[120, 210]


def test_brief_body_in_calibration_does_not_inflate_the_noise_margin():
    calibration = BackgroundCalibration(16)
    room = np.full((240, 320), 3200, dtype=np.uint16)
    occupied = room.copy()
    occupied[45:200, 125:180] = 1400
    for sample in [room] * 8 + [occupied] * 8:
        reference = calibration.add(frame(sample))
    tracker = ForegroundTracker(
        reference, mirrored=False, foreground_margin=calibration.foreground_margin
    )
    assert calibration.foreground_margin[100, 150] <= 360
    assert enter(tracker, occupied).mask[50:195, 130:175].all()
    assert not tracker.update(frame(room, 1.1), 1.1).active


def test_moderate_body_separation_survives_a_mixed_calibration():
    calibration = BackgroundCalibration(16)
    room = np.full((240, 320), 2400, dtype=np.uint16)
    occupied = room.copy()
    occupied[45:200, 125:180] = 2000
    for sample in [room] * 8 + [occupied] * 8:
        reference = calibration.add(frame(sample))
    tracker = ForegroundTracker(
        reference, mirrored=False, foreground_margin=calibration.foreground_margin
    )
    assert enter(tracker, occupied).mask[50:195, 130:175].all()


def test_coherent_transient_noise_and_duplicate_frames_cannot_seed_players():
    background = np.full((240, 320), 3000, dtype=np.uint16)
    background[:100, :100] = 0
    tracker = ForegroundTracker(
        background, mirrored=False, open_background=background == 0
    )
    noise = background.copy()
    noise[20:40, 20:40] = 1800  # Coherent return against unknown depth.
    first = frame(noise)
    assert not tracker.update(first, 1).active
    assert not tracker.update(first, 1.01).active
    assert not tracker.update(frame(background, 1.04), 1.04).active
    assert not tracker.update(frame(noise, 1.08), 1.08).active
    assert tracker.update(frame(noise, 1.12), 1.12).active
    assert not tracker.update(frame(background, 1.16), 1.16).active
    assert not tracker.update(frame(noise, 1.20), 1.20).active


def test_connected_fast_arms_are_immediate_and_new_islands_need_confirmation():
    background = np.full((240, 320), 3000, dtype=np.uint16)
    tracker = ForegroundTracker(background, mirrored=False)
    people = background.copy()
    for x in (40, 130, 240):
        people[60:200, x:x + 18] = 1800
    assert enter(tracker, people).active
    moved = background.copy()
    for x in (46, 136, 246):
        moved[60:200, x:x + 18] = 1800
        moved[100:103, x - 30:x] = 1800
    moved[20:35, 180:195] = 1800
    mask = tracker.update(frame(moved, 1.07), 1.07).mask
    assert mask[101, [20, 110, 220]].all()
    assert mask[140, [53, 143, 253]].all()
    assert not mask[20:35, 180:195].any()
    assert not mask[140, 42]  # No trailing copy of the old body.


def test_depth_hysteresis_limits_threshold_flicker_but_never_holds_invalid_depth():
    room = np.full((240, 320), 3000, dtype=np.uint16)
    tracker = ForegroundTracker(room, mirrored=False)
    body = room.copy()
    body[40:200, 100:150] = 2840
    assert enter(tracker, body).active
    for index, depth in enumerate((2888, 2898, 2881, 2895)):
        body[40:200, 100:150] = depth
        timestamp = 1.07 + index / 30
        result = tracker.update(frame(body.copy(), timestamp), timestamp)
        assert result.mask[100, 125]
    body[40:200, 100:150] = 0
    assert not tracker.update(frame(body, 1.22), 1.22).active
    body[40:200, 100:150] = 2895
    assert not tracker.update(frame(body, 1.25), 1.25).active


def test_gaps_configuration_and_floods_cannot_confirm_new_regions():
    room = np.full((240, 320), 3000, dtype=np.uint16)
    body = room.copy()
    body[40:200, 100:150] = 1800
    tracker = ForegroundTracker(room, mirrored=False)
    assert not tracker.update(frame(body), 1).active
    assert not tracker.update(frame(body, 1.2), 1.2).active
    assert tracker.update(frame(body, 1.24), 1.24).active
    assert not tracker.update(None, 1.6).active
    assert not tracker.update(frame(body, 1.61), 1.61).active
    tracker.configure(mirrored=False, margin=0, far=3800)
    assert not tracker.update(frame(body, 1.65), 1.65).active
    assert not tracker.update(frame(np.full_like(room, 1400), 1.69), 1.69).active
    assert not tracker.update(frame(body, 1.73), 1.73).active
