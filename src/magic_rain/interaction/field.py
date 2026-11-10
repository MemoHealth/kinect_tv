from math import exp

import numpy as np
from numpy.typing import NDArray


class MotionField:
    def __init__(self) -> None:
        self.wind = np.zeros((30, 40))
        self.strength = 0.0
        self._last_mask: NDArray[np.bool_] | None = None
        self._occupancy = self.wind.copy()
        self._target = self.wind.copy()
        self._reach = 0.0

    def update(self, mask: NDArray[np.bool_], dt: float) -> None:
        if mask is not self._last_mask:
            self._last_mask = mask
            occupancy = mask.reshape(30, 8, 40, 8).mean(axis=(1, 3))
            padded = np.pad(occupancy + self._occupancy, 1, mode="edge")
            slope = padded[1:-1, 2:] - padded[1:-1, :-2]
            change = occupancy - self._occupancy
            target = np.zeros_like(occupancy)
            if self._occupancy.any() and occupancy.any():
                target = np.clip(-change * slope * 110, -90, 90)
            padded = np.pad(target, 1, mode="edge")
            self._target = (
                4 * target
                + padded[:-2, 1:-1]
                + padded[2:, 1:-1]
                + padded[1:-1, :-2]
                + padded[1:-1, 2:]
            ) / 8
            self._occupancy = occupancy
            self._reach = min(
                1.0, 0.6 * mask.any(axis=1).mean() + 0.7 * mask.any(axis=0).mean()
            )
        self.wind += (self._target - self.wind) * (1 - exp(-dt / 0.13))
        self._target *= exp(-dt / 0.22)
        time_constant = 0.35 if self._reach >= self.strength else 0.8
        self.strength += (self._reach - self.strength) * (1 - exp(-dt / time_constant))
