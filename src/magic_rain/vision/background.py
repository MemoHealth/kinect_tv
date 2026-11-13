from collections import deque

import numpy as np
from numpy.typing import NDArray

from ..sensors.base import SensorFrame


class BackgroundCalibration:
    def __init__(self, sample_count: int = 60) -> None:
        self._sample_count = sample_count
        self._samples: list[NDArray[np.uint16]] = []
        self._colors: deque[NDArray[np.uint8]] = deque(maxlen=5)
        self.color_reference: NDArray[np.uint8] | None = None
        self.open_background: NDArray[np.bool_] | None = None
        self.foreground_margin: NDArray[np.int32] | None = None

    @property
    def progress(self) -> float:
        return len(self._samples) / self._sample_count

    def add(self, frame: SensorFrame) -> NDArray[np.uint16] | None:
        self._samples.append(frame.depth_mm)
        if frame.rgb_coordinates is not None and frame.rgb is not None:
            self._colors.append(frame.rgb)
        if len(self._samples) < self._sample_count:
            return None
        samples = np.stack(self._samples)
        self._samples.clear()
        colors = list(self._colors)
        self._colors.clear()
        valid_count = np.count_nonzero(samples, axis=0)
        samples[samples == 0] = np.iinfo(np.uint16).max
        samples.sort(axis=0)
        # Prefer the farther room surface if someone briefly crosses calibration.
        indices = (valid_count * 3) // 4
        reference = np.take_along_axis(samples, indices[None, :, :], axis=0)[0]
        reference[valid_count < (self._sample_count + 1) // 2] = 0
        if np.count_nonzero(reference) < reference.size * 0.05:
            return None
        near_index = np.maximum(0, (valid_count - 1) // 4)
        near = np.take_along_axis(samples, near_index[None, :, :], axis=0)[0]
        spread = reference.astype(np.int32) - near.astype(np.int32)
        # Keep the threshold below the observed layer separation, even if a
        # person briefly enters calibration. Limit noise compensation to 360 mm.
        self.foreground_margin = np.clip(
            np.rint(spread * 0.9), 120, 360
        ).astype(np.int32)
        self.open_background = valid_count <= self._sample_count // 20
        if colors:
            self.color_reference = np.median(colors, axis=0).astype(np.uint8)
        return reference
