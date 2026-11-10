import numpy as np
from numpy.typing import NDArray

from .sensors.capture import LatestDepth
from .sensors.kinect_v1 import HEIGHT, WIDTH, KinectV1Sensor
from .vision.background import BackgroundCalibration
from .vision.foreground import ForegroundTracker


class LiveInput:
    def __init__(self, *, mirrored: bool = True) -> None:
        self._capture = LatestDepth(KinectV1Sensor())
        self._calibration = BackgroundCalibration()
        self._tracker: ForegroundTracker | None = None
        self._empty = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
        self._mirrored = mirrored
        self.notice = "Låt ytan framför kameran vara tom en kort stund."

    def start(self) -> None:
        self._capture.start()

    def stop(self) -> bool:
        return self._capture.stop()

    def mask(self, now: float) -> NDArray[np.bool_]:
        frame, error = self._capture.take()
        if error is not None:
            self.notice = "Kinect-kameran svarar inte. Kontrollera ström och USB."
            return self._empty
        if self._tracker is not None:
            return self._tracker.update(frame, now).mask
        if frame is not None:
            reference = self._calibration.add(frame)
            if reference is not None:
                self._tracker = ForegroundTracker(reference, mirrored=self._mirrored)
                self.notice = ""
        return self._empty
