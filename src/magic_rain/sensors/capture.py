from threading import Event, Lock, Thread
from time import monotonic

from .base import SensorFrame, SensorHealth
from .kinect_v1 import KinectV1Sensor, SensorError
from .tilt import TILT_SETTLE_S, Tilt


class LatestDepth:
    """Own one blocking adapter and transfer only the newest pending frame."""

    def __init__(self, sensor: KinectV1Sensor) -> None:
        self._sensor = sensor
        self._lock = Lock()
        self._stop = Event()
        self._thread = Thread(target=self._capture, daemon=True)
        self._latest: SensorFrame | None = None
        self._error: SensorHealth | None = None
        self._tilt = Tilt()

    def start(self) -> None:
        self._thread.start()

    def take(self) -> tuple[SensorFrame | None, SensorHealth | None]:
        with self._lock:
            frame = self._latest
            self._latest = None
            return frame, self._error

    def stop(self, timeout_s: float = 2) -> bool:
        self._stop.set()
        if self._thread.ident is not None:
            self._thread.join(timeout_s)
        return not self._thread.is_alive()

    def request_tilt(self, direction: int, now: float) -> str:
        with self._lock:
            if self._error is not None:
                return "Anslut Kinect innan du ändrar vinkeln."
            return self._tilt.request(direction, now)

    def tilt_status(self, now: float) -> tuple[int | None, bool, str]:
        with self._lock:
            return self._tilt.angle, self._tilt.busy(now), self._tilt.warning

    def _move_camera(self) -> bool:
        with self._lock:
            angle = self._tilt.target
            if angle is not None:
                self._latest = None
        if angle is None:
            return False
        success = False
        try:
            self._sensor.tilt_to(angle)
            success = True
        except (SensorError, OSError):
            pass
        finally:
            with self._lock:
                self._tilt.finish(monotonic(), success=success)
        return True

    def _capture(self) -> None:
        try:
            self._sensor.start()
            last_frame = monotonic()
            read_angle = False
            while not self._stop.is_set():
                if self._move_camera():
                    last_frame = monotonic() + TILT_SETTLE_S
                    read_angle = False
                frame = self._sensor.read_latest(0.15)
                now = monotonic()
                if frame is not None:
                    if not read_angle and now >= last_frame:
                        read_angle = True
                        try:
                            angle = self._sensor.tilt_angle()
                        except (SensorError, OSError):
                            angle = None
                        if angle is not None:
                            with self._lock:
                                self._tilt.angle = angle
                    with self._lock:
                        self._latest = frame
                    last_frame = max(last_frame, now)
                elif now - last_frame >= 0.9:
                    raise SensorError(SensorHealth.NO_FRAMES, "No Kinect depth frames")
        except SensorError as error:
            with self._lock:
                self._latest = None
                self._error = error.status
        except (OSError, ValueError):
            with self._lock:
                self._latest = None
                self._error = SensorHealth.DRIVER_ERROR
        finally:
            self._sensor.stop()
