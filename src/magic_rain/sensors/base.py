from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Literal, Protocol

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class SensorFrame:
    timestamp_monotonic_s: float
    depth_mm: NDArray[np.uint16]
    rgb: NDArray[np.uint8] | None
    width: int
    height: int
    source: Literal["kinect_v1", "simulation"]
    dropped_frames_total: int | None = None
    rgb_coordinates: NDArray[np.int32] | None = None

    def __post_init__(self) -> None:
        if not isfinite(self.timestamp_monotonic_s) or self.timestamp_monotonic_s < 0:
            raise ValueError("Invalid frame timestamp")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Frame dimensions must be positive")
        shape = (self.height, self.width)
        if self.depth_mm.dtype != np.uint16 or self.depth_mm.shape != shape:
            raise ValueError("Expected H×W uint16 depth in millimetres")
        if self.rgb is not None and (
            self.rgb.dtype != np.uint8 or self.rgb.shape != (*shape, 3)
        ):
            raise ValueError("Expected H×W×3 uint8 RGB")
        if self.source not in ("simulation", "kinect_v1"):
            raise ValueError("Unknown frame source")
        if self.rgb_coordinates is not None and (
            self.rgb is None
            or self.rgb_coordinates.dtype != np.int32
            or self.rgb_coordinates.shape != (*shape, 2)
        ):
            raise ValueError("Expected H×W×2 int32 coordinates with RGB")


class SensorHealth(Enum):
    OK = "OK"
    NO_DEVICE = "NO_DEVICE"
    DRIVER_ERROR = "DRIVER_ERROR"
    NO_FRAMES = "NO_FRAMES"
    UNSTABLE_STREAM = "UNSTABLE_STREAM"


class SensorAdapter(Protocol):
    def start(self) -> None: ...
    def read_latest(self, timeout_s: float) -> SensorFrame | None: ...
    def health(self) -> SensorHealth: ...
    def stop(self) -> None: ...
