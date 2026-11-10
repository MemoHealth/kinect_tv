import ctypes as ct

import numpy as np
import pytest

from magic_rain import diagnostics
from magic_rain.sensors import kinect_v1
from magic_rain.sensors.base import SensorFrame, SensorHealth
from magic_rain.sensors.kinect_v1 import HEIGHT, WIDTH, KinectV1Sensor, SensorError


def test_depth_decode_copies_mm_without_padding_or_invalid_codes():
    packed = np.zeros((HEIGHT, WIDTH + 3), dtype="<u2")
    packed[0, :4] = [1800 << 3 | 5, 0, 0x0FFF << 3, 0x1FFF << 3 | 7]
    packed[0, -3:] = 1000 << 3
    packed[1, 0] = 2000 << 3
    pitch = packed.strides[0]
    depth = kinect_v1._decode_depth(packed.tobytes(), pitch)
    assert depth.shape == (HEIGHT, WIDTH)
    assert depth[0, :4].tolist() == [1800, 0, 0, 0]
    assert depth[1, 0] == 2000
    assert np.count_nonzero(depth) == 2
    with pytest.raises(SensorError, match="Felaktig djupbild"):
        kinect_v1._decode_depth(packed.tobytes()[:-pitch], pitch)


class FakeRuntime:
    def __init__(self):
        self.result = 0
        self.open_result = 0
        self.frame = kinect_v1._ImageFrame()
        self.released = 0
        self.shutdowns = 0

    def NuiInitialize(self, flags):
        assert flags == kinect_v1.USES_DEPTH
        return 0

    def NuiImageStreamOpen(self, *_):
        return self.open_result

    def NuiImageStreamGetNextFrame(self, _stream, _timeout, out_frame):
        ct.cast(out_frame, ct.POINTER(ct.POINTER(kinect_v1._ImageFrame)))[0] = (
            ct.pointer(self.frame)
        )
        return self.result

    def NuiImageStreamReleaseFrame(self, _stream, _frame):
        self.released += 1
        return 0

    def NuiShutdown(self):
        self.shutdowns += 1


def test_adapter_handles_timeouts_frame_gaps_and_disconnect(monkeypatch):
    runtime = FakeRuntime()
    depth = np.full((HEIGHT, WIDTH), 1800, dtype=np.uint16)
    monkeypatch.setattr(kinect_v1, "_load_runtime", lambda: runtime)
    monkeypatch.setattr(kinect_v1, "_copy_depth", lambda _texture: depth)
    sensor = KinectV1Sensor()
    sensor.start()
    runtime.result = kinect_v1.NO_FRAME
    assert sensor.read_latest(0) is None
    assert sensor.health() is SensorHealth.NO_FRAMES
    assert runtime.released == 0

    runtime.result = 0
    first = sensor.read_latest(0)
    runtime.frame.frame_number = 3
    second = sensor.read_latest(0)
    assert second.source == "kinect_v1"
    assert second.rgb is None
    assert first.dropped_frames_total == 0
    assert second.dropped_frames_total == 2
    assert runtime.released == 2

    runtime.result = 0x83010014
    with pytest.raises(SensorError) as error:
        sensor.read_latest(0)
    assert error.value.status is sensor.health() is SensorHealth.NO_DEVICE
    sensor.stop()
    sensor.stop()
    assert runtime.shutdowns == 1

    runtime.result = 0
    sensor.start()
    assert sensor.read_latest(0).dropped_frames_total == 0
    sensor.stop()
    assert runtime.shutdowns == 2


def test_failed_open_shuts_down_sdk(monkeypatch):
    runtime = FakeRuntime()
    runtime.open_result = 0x83010003
    monkeypatch.setattr(kinect_v1, "_load_runtime", lambda: runtime)
    sensor = KinectV1Sensor()
    with pytest.raises(SensorError, match="NuiImageStreamOpen"):
        sensor.start()
    assert sensor.health() is SensorHealth.DRIVER_ERROR
    assert sensor.read_latest(0) is None
    sensor.stop()
    assert runtime.shutdowns == 1


def test_single_frame_check_rejects_missing_depth(monkeypatch, capsys):
    sensor = KinectV1Sensor()
    depth = np.zeros((HEIGHT, WIDTH), dtype=np.uint16)
    frame = SensorFrame(1.0, depth, None, WIDTH, HEIGHT, "kinect_v1")
    monkeypatch.setattr(sensor, "start", lambda: None)
    monkeypatch.setattr(sensor, "read_latest", lambda _timeout: frame)
    monkeypatch.setattr(diagnostics, "KinectV1Sensor", lambda: sensor)
    assert diagnostics.check_depth(0) == 1
    assert "NO_FRAMES" in capsys.readouterr().err
