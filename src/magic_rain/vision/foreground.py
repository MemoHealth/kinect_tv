from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from ..sensors.base import SensorFrame

STALE_S = 0.25


@dataclass(frozen=True)
class Foreground:
    mask: NDArray[np.bool_]
    confidence: float
    timestamp_monotonic_s: float
    active: bool


class ForegroundTracker:
    def __init__(
        self, background: NDArray[np.uint16], *, mirrored: bool = True
    ) -> None:
        self._background = background.astype(np.int32)
        self._mirrored = mirrored
        self._empty = np.zeros(background.shape, dtype=np.bool_)
        self._last: Foreground | None = None
        self._margin = 0.0
        self._far = 3800

    def configure(self, *, mirrored: bool, margin: float, far: int) -> None:
        self._mirrored = mirrored
        self._margin = margin
        self._far = far
        self._last = None

    def update(self, frame: SensorFrame | None, now: float) -> Foreground:
        if frame is not None and now - frame.timestamp_monotonic_s <= STALE_S:
            self._last = self._segment(frame)
        if self._last is None or now - self._last.timestamp_monotonic_s > STALE_S:
            return Foreground(self._empty, 0.0, now, False)
        return self._last

    def _segment(self, frame: SensorFrame) -> Foreground:
        depth = frame.depth_mm
        measured = (self._background != 0) & (depth != 0)
        foreground = measured & (depth >= 850) & (depth <= self._far)
        foreground &= self._background - depth >= 120
        if margin := round(depth.shape[1] * self._margin):
            foreground[:, :margin] = False
            foreground[:, -margin:] = False

        # Keep coherent regions and bridge single-pixel holes without assigning IDs.
        padded = np.pad(foreground, 1)
        neighbours = (
            padded[:-2, 1:-1].astype(np.uint8)
            + padded[2:, 1:-1]
            + padded[1:-1, :-2]
            + padded[1:-1, 2:]
        )
        core = np.pad(foreground & (neighbours >= 3), 1)
        coherent = (
            core[1:-1, 1:-1]
            | core[:-2, 1:-1]
            | core[2:, 1:-1]
            | core[1:-1, :-2]
            | core[1:-1, 2:]
        )
        mask = (foreground & coherent) | (measured & (neighbours == 4))
        size = np.count_nonzero(mask)
        coverage = np.count_nonzero(measured)
        active = 12 <= size <= min(mask.size * 0.65, coverage * 0.90)
        if not active:
            return Foreground(self._empty, 0.0, frame.timestamp_monotonic_s, False)
        if self._mirrored:
            mask = mask[:, ::-1]
        confidence = coverage / measured.size
        return Foreground(mask, confidence, frame.timestamp_monotonic_s, True)
