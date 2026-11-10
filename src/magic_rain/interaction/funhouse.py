import numpy as np
from numpy.typing import NDArray


class Funhouse:
    def __init__(self) -> None:
        self._source: NDArray | None = None
        self._warped: NDArray | None = None
        self._shape: tuple[int, ...] = ()
        self._strength = 0.0
        self._indices: tuple[NDArray[np.intp], NDArray[np.intp]] | None = None

    def warp(self, image: NDArray, strength: float) -> NDArray:
        if strength == 0:
            return image
        shape = image.shape[:2]
        if (
            self._indices is None
            or shape != self._shape
            or strength != self._strength
        ):
            self._shape = shape
            self._strength = strength
            self._indices = source_indices(shape, strength)
            self._source = None
        if self._warped is None or image is not self._source:
            self._source = image
            self._warped = image[self._indices]
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
