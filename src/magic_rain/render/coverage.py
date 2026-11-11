import numpy as np
from numpy.typing import NDArray


def soften(image: NDArray) -> NDArray[np.float32]:
    """A small display-only coverage filter with a one-pixel support radius."""
    padding = ((1, 1), (1, 1)) + ((0, 0),) * (image.ndim - 2)
    padded = np.pad(image.astype(np.float32), padding)
    horizontal = (
        padded[:, :-2] + 2 * padded[:, 1:-1] + padded[:, 2:]
    ) * 0.25
    return (horizontal[:-2] + 2 * horizontal[1:-1] + horizontal[2:]) * 0.25
