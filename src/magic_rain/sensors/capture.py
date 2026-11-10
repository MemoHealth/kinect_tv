from threading import Event, Lock, Thread
from time import monotonic

from .base import SensorAdapter, SensorFrame, SensorHealth
from .kinect_v1 import SensorError


class LatestDepth:
    """Own one blocking adapter and transfer only the newest pending frame."""

    def __init__(self, sensor: SensorAdapter) -> None:
        self._sensor = sensor
        self._lock = Lock()
        self._stop = Event()
        self._thread = Thread(target=self._capture, daemon=True)
        self._latest: SensorFrame | None = None
        self._error: SensorHealth | None = None

    def start(self) -> None:
        self._thread.start()

    def take(self) -> tuple[SensorFrame | None, SensorHealth | None]:
        with self._lock:
            frame = self._latest
            self._latest = None
            return frame, self._error

    def stop(self) -> bool:
        self._stop.set()
        if self._thread.ident is not None:
            self._thread.join(2)
        return not self._thread.is_alive()

    def _capture(self) -> None:
        try:
            self._sensor.start()
            last_frame = monotonic()
            while not self._stop.is_set():
                frame = self._sensor.read_latest(0.15)
                now = monotonic()
                if frame is not None:
                    with self._lock:
                        self._latest = frame
                    last_frame = now
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
