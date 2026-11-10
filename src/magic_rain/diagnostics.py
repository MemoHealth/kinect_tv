import sys
from time import monotonic

import numpy as np

from .sensors.base import SensorHealth
from .sensors.kinect_v1 import KinectV1Sensor, SensorError

DOCTOR_DURATION_S = 60
MINIMUM_FPS = 20
MAXIMUM_FRAME_GAP_S = 0.75


def check_depth(duration_s: int = DOCTOR_DURATION_S) -> int:
    sensor = KinectV1Sensor()
    try:
        sensor.start()
        first = sensor.read_latest(2)
        if first is None:
            raise SensorError(SensorHealth.NO_FRAMES, "Djupkameran gav ingen bild.")
        valid = np.count_nonzero(first.depth_mm)
        if duration_s:
            print(
                f"Kinect v1 · Djup {first.width} × {first.height} · "
                f"Testar i {duration_s} s",
                flush=True,
            )
            return _measure_stream(sensor, duration_s, valid, first.depth_mm.size)
        if valid == 0:
            raise SensorError(SensorHealth.NO_FRAMES, "Djupbilden saknade mätvärden.")
        print("Kinect v1 levererar djup. Spel med kamera kommer i en senare etapp.")
        return 0
    except SensorError as error:
        print(f"Kinect · {error.status.value} · {error}", file=sys.stderr)
        return 1
    finally:
        sensor.stop()


def _measure_stream(
    sensor: KinectV1Sensor, duration_s: int, first_valid: int, pixels_per_frame: int
) -> int:
    start = last_received = monotonic()
    last_device_time = sensor.device_timestamp_ms
    frame_count = 1
    valid_pixels = first_valid
    dropped = 0
    longest_gap = 0.0
    while monotonic() - start < duration_s:
        frame = sensor.read_latest(0.2)
        now = monotonic()
        gap = now - last_received
        if gap > MAXIMUM_FRAME_GAP_S:
            raise SensorError(SensorHealth.UNSTABLE_STREAM, "Djupströmmen stannade.")
        if frame is None:
            continue
        device_time = sensor.device_timestamp_ms
        if (
            device_time is None
            or last_device_time is None
            or device_time <= last_device_time
        ):
            raise SensorError(
                SensorHealth.UNSTABLE_STREAM, "Kamerans tidsstämpel gick inte framåt."
            )
        last_device_time = device_time
        last_received = now
        longest_gap = max(gap, longest_gap)
        frame_count += 1
        valid_pixels += np.count_nonzero(frame.depth_mm)
        dropped = frame.dropped_frames_total or 0
    elapsed = monotonic() - start
    fps = (frame_count - 1) / elapsed
    valid = valid_pixels / (frame_count * pixels_per_frame)
    print(
        f"{elapsed:.1f} s · {frame_count} djupbilder · {fps:.1f} FPS · "
        f"{valid:.1%} giltiga pixlar · {dropped} bildnummer saknas · "
        f"längsta bildintervall {longest_gap * 1000:.0f} ms"
    )
    if valid == 0:
        raise SensorError(SensorHealth.NO_FRAMES, "Djupbilderna saknade mätvärden.")
    if fps < MINIMUM_FPS:
        raise SensorError(SensorHealth.UNSTABLE_STREAM, "Bildtakten var under 20 FPS.")
    print("Kinect · OK")
    return 0
