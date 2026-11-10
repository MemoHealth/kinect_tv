import numpy as np
from numpy.typing import NDArray


class Funhouse:
    def __init__(self) -> None:
        self._source: NDArray[np.bool_] | None = None
        self._warped: NDArray[np.bool_] | None = None
        self._shape: tuple[int, ...] = ()
        self._strength = 0.0
        self._indices: tuple[NDArray[np.intp], NDArray[np.intp]] | None = None

    def warp(self, mask: NDArray[np.bool_], strength: float) -> NDArray[np.bool_]:
        if strength == 0:
            return mask
        if (
            self._indices is None
            or mask.shape != self._shape
            or strength != self._strength
        ):
            self._shape = mask.shape
            self._strength = strength
            self._indices = source_indices(mask.shape, strength)
            self._source = None
        if self._warped is None or mask is not self._source:
            self._source = mask
            self._warped = mask[self._indices]
        return self._warped


def source_indices(
    shape: tuple[int, ...], strength: float
) -> tuple[NDArray[np.intp], NDArray[np.intp]]:
    height, width = shape
    y = np.linspace(-1, 1, height)[:, None]
    x = np.linspace(-1, 1, width)[None, :]
    distance = np.maximum(abs(x), abs(y))
    scale = 1 + strength * (1 - distance**2)
    rows = np.rint((y * scale + 1) * (height - 1) / 2).astype(np.intp)
    cols = np.rint((x * scale + 1) * (width - 1) / 2).astype(np.intp)
    return rows, cols
