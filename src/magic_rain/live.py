import numpy as np
from numpy.typing import NDArray

from .sensors.capture import LatestDepth
from .sensors.kinect_v1 import HEIGHT, WIDTH, KinectV1Sensor
from .settings import FUNHOUSE_STRENGTH, Settings
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
        self._calibrate_at: float | None = None
        self.fault = False
        self.preview_depth: NDArray[np.uint16] | None = None
        self._preview_time = 0.0
        self.color_image: NDArray[np.uint8] | None = None
        self._color_time = 0.0
        self._registration_time: float | None = None
        self._color_enabled = False
        self._color_assist = True
        self._restart_for_color = False
        self.notice = "Låt ytan framför kameran vara tom en kort stund."

    def start(self) -> None:
        if self._restart_for_color:
            self._replace_capture()
        self._capture.start()

    def stop(self) -> bool:
        return self._capture.stop()

    def set_color(self, enabled: bool) -> None:
        if self._color_enabled != enabled:
            self._color_enabled = enabled
            self.color_image = None
            self._registration_time = None
            self._restart_for_color = True
            self._capture.stop(timeout_s=0)

    def _replace_capture(self) -> None:
        self._capture = self._capture.replacement(
            KinectV1Sensor(color=self._color_enabled)
        )
        self._restart_for_color = False

    def configure(self, settings: Settings) -> None:
        self._mirrored = settings.mirror == "På"
        self._margin = 0.12 if settings.zone == "Centrerad" else 0.0
        self._far = 2500 if settings.distance == "Nära" else 3800
        self._color_assist = settings.color_assist == "På"
        self.set_color(self._color_assist or settings.scene in FUNHOUSE_STRENGTH)
        if self._tracker is not None:
            self._tracker.color_assist = self._color_assist
        self._configure_tracker()

    def _configure_tracker(self) -> None:
        if self._tracker is not None:
            self._tracker.configure(
                mirrored=self._mirrored, margin=self._margin, far=self._far
            )

    def calibrate_or_retry(self, now: float, *, from_menu: bool = False) -> None:
        if self.fault:
            self._retry_after = now + 3
            if not self._capture.stop(timeout_s=0):
                return
            self._replace_capture()
            self._capture.start()
        self._tracker = None
        self._calibration = BackgroundCalibration()
        self._calibrate_at = now + 3 if from_menu else None
        if not self.fault:
            self.notice = "Låt ytan framför kameran vara tom en kort stund."

    def tilt(self, direction: int, now: float) -> str:
        warning = self._capture.request_tilt(direction, now)
        if not warning:
            self.calibrate_or_retry(now)
        return warning

    def tilt_status(self, now: float) -> tuple[int | None, bool, str]:
        return self._capture.tilt_status(now)

    def calibration_status(self, now: float) -> str:
        if self.fault:
            return "Ingen djupbild"
        if self._calibrate_at is not None and now < self._calibrate_at:
            seconds = max(1, int(self._calibrate_at - now + 0.999))
            return f"Töm spelzonen · {seconds} s"
        if self._tracker is not None:
            return "Kalibrering klar"
        if self._calibration.progress:
            return f"Kalibrerar · {self._calibration.progress:.0%}"
        return "Klar att kalibrera"

    def color_status(self, now: float) -> str:
        if not self._color_assist:
            return "Färgstöd av"
        if self._registration_time is None or now - self._registration_time > 0.5:
            return "Bara djup just nu"
        if self._calibration.color_reference is None:
            return "Kalibrera för färgstöd"
        return "Djup + färgstöd"

    def mask(self, now: float, *, preview: bool = False) -> NDArray[np.bool_]:
        if self._restart_for_color:
            if not self._capture.stop(timeout_s=0):
                return self._empty
            self._replace_capture()
            self._capture.start()
        frame, error = self._capture.take()
        if error is not None:
            self.preview_depth = None
            self.color_image = None
            self.fault = True
            self.notice = "Kinect svarar inte. Kontrollera USB och ström. F1 för hjälp."
            if self._retry_after is None:
                self._retry_after = now + 3
            elif now >= self._retry_after:
                self.calibrate_or_retry(now)
            return self._empty
        if self._capture.tilt_status(now)[1]:
            self.preview_depth = None
            self.color_image = None
            self.notice = "Kameran justeras."
            return self._empty
        if preview and frame is not None:
            depth = frame.depth_mm
            self.preview_depth = depth[:, ::-1] if self._mirrored else depth
            self._preview_time = frame.timestamp_monotonic_s
        elif not preview or now - self._preview_time > 0.25:
            self.preview_depth = None
        if self._color_enabled and frame is not None and frame.rgb is not None:
            self.color_image = frame.rgb
            self._color_time = frame.timestamp_monotonic_s
            if frame.rgb_coordinates is not None:
                self._registration_time = frame.timestamp_monotonic_s
        if now - self._color_time > 0.25:
            self.color_image = None
        if frame is not None and self.fault:
            self.fault = False
            self._retry_after = None
            if self._tracker is not None:
                self.notice = ""
        if self._tracker is not None:
            return self._tracker.update(frame, now).mask
        if frame is not None:
            self.fault = False
            self._retry_after = None
            self.notice = "Låt ytan framför kameran vara tom en kort stund."
            if self._calibrate_at is not None:
                if now < self._calibrate_at:
                    return self._empty
            elif preview:
                if self._calibration.progress:
                    self._calibration = BackgroundCalibration()
                return self._empty
            reference = self._calibration.add(frame)
            if reference is not None:
                self._tracker = ForegroundTracker(
                    reference, mirrored=self._mirrored,
                    color_reference=self._calibration.color_reference,
                    open_background=self._calibration.open_background,
                )
                self._tracker.color_assist = self._color_assist
                self._calibrate_at = None
                self._configure_tracker()
                self.notice = ""
        return self._empty
