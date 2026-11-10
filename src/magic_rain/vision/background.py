import numpy as np
from numpy.typing import NDArray

from ..sensors.base import SensorFrame


class BackgroundCalibration:
    def __init__(self, sample_count: int = 60) -> None:
        self._sample_count = sample_count
        self._samples: list[NDArray[np.uint16]] = []

    def add(self, frame: SensorFrame) -> NDArray[np.uint16] | None:
        self._samples.append(frame.depth_mm)
        if len(self._samples) < self._sample_count:
            return None
        samples = np.stack(self._samples)
        self._samples.clear()
        valid_count = np.count_nonzero(samples, axis=0)
        samples[samples == 0] = np.iinfo(np.uint16).max
        samples.sort(axis=0)
        indices = np.maximum(0, (valid_count - 1) // 2)
        reference = np.take_along_axis(samples, indices[None, :, :], axis=0)[0]
        reference[valid_count < (self._sample_count + 1) // 2] = 0
        if np.count_nonzero(reference) < reference.size * 0.05:
            return None
        return reference
