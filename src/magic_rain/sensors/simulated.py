from collections.abc import Callable
from math import sin, tau
from time import monotonic

import numpy as np

from .base import SensorFrame, SensorHealth

FRAME_SIZE = (320, 240)
OBSTACLE_DEPTH_MM = 1800
BACKGROUND_DEPTH_MM = 3300


class SimulatedSensor:
    def __init__(self, clock: Callable[[], float] = monotonic) -> None:
        self._clock = clock
        self._started_at: float | None = None
        width, height = FRAME_SIZE
        self._x, self._y = np.meshgrid(np.arange(width), np.arange(height))
        self.pointer: tuple[float, float] | None = None

    def start(self) -> None:
        self._started_at = self._clock()

    def read_latest(self, timeout_s: float) -> SensorFrame | None:
        if self._started_at is None:
            return None
        now = self._clock()
        phase = (now - self._started_at) * tau / 12
        u, v = self.pointer or (0.5 + 0.25 * sin(phase), 0.55 + 0.07 * sin(2 * phase))
        width, height = FRAME_SIZE
        mask = (self._x - u * width) ** 2 + (self._y - v * height) ** 2 <= 33**2
        depth = np.full((height, width), BACKGROUND_DEPTH_MM, dtype=np.uint16)
        depth[mask] = OBSTACLE_DEPTH_MM
        return SensorFrame(now, depth, None, width, height, "simulation")

    def health(self) -> SensorHealth:
        if self._started_at is None:
            return SensorHealth.NO_FRAMES
        return SensorHealth.OK

    def stop(self) -> None:
        self._started_at = None
