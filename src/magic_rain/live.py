import numpy as np
from numpy.typing import NDArray

from .sensors.capture import LatestDepth
from .sensors.kinect_v1 import HEIGHT, WIDTH, KinectV1Sensor
from .settings import Settings
from .vision.background import BackgroundCalibration
from .vision.foreground import ForegroundTracker


class LiveInput:
    def __init__(self, *, mirrored: bool = True) -> None:
        self._capture = LatestDepth(KinectV1Sensor())
        self._calibration = BackgroundCalibration()
        self._tracker: ForegroundTracker | None = None
        self._empty = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
        self._mirrored = mirrored
        self._margin = 0.0
        self._far = 3800
        self._retry_after: float | None = None
        self.fault = False
        self.notice = "Låt ytan framför kameran vara tom en kort stund."

    def start(self) -> None:
        self._capture.start()

    def stop(self) -> bool:
        return self._capture.stop()

    def configure(self, settings: Settings) -> None:
        self._mirrored = settings.mirror == "På"
        self._margin = 0.12 if settings.zone == "Centrerad" else 0.0
        self._far = 2500 if settings.distance == "Nära" else 3800
        self._configure_tracker()

    def _configure_tracker(self) -> None:
        if self._tracker is not None:
            self._tracker.configure(
                mirrored=self._mirrored, margin=self._margin, far=self._far
            )

    def calibrate_or_retry(self, now: float) -> None:
        if self.fault:
            self._retry_after = now + 3
            if not self._capture.stop(timeout_s=0):
                return
            self._capture = LatestDepth(KinectV1Sensor())
            self._capture.start()
        self._tracker = None
        self._calibration = BackgroundCalibration()
        if not self.fault:
            self.notice = "Låt ytan framför kameran vara tom en kort stund."

    def mask(self, now: float) -> NDArray[np.bool_]:
        frame, error = self._capture.take()
        if error is not None:
            self.fault = True
            self.notice = "Kinect svarar inte. Kontrollera USB och ström. F1 för hjälp."
            if self._retry_after is None:
                self._retry_after = now + 3
            elif now >= self._retry_after:
                self.calibrate_or_retry(now)
            return self._empty
        if self._tracker is not None:
            return self._tracker.update(frame, now).mask
        if frame is not None:
            self.fault = False
            self._retry_after = None
            self.notice = "Låt ytan framför kameran vara tom en kort stund."
            reference = self._calibration.add(frame)
            if reference is not None:
                self._tracker = ForegroundTracker(reference, mirrored=self._mirrored)
                self._configure_tracker()
                self.notice = ""
        return self._empty
