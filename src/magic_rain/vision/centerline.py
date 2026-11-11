import numpy as np
from numpy.typing import NDArray


def centerline(mask: NDArray[np.bool_]) -> NDArray[np.bool_]:
    """Thin a derived display mask; never modifies the physical silhouette."""
    height, width = mask.shape
    image = mask.reshape(height // 4, 4, width // 4, 4).any(axis=(1, 3))
    for _ in range(36):
        changed = False
        for phase in (0, 1):
            padded = np.pad(image, 1)
            neighbors = (
                padded[:-2, 1:-1], padded[:-2, 2:], padded[1:-1, 2:],
                padded[2:, 2:], padded[2:, 1:-1], padded[2:, :-2],
                padded[1:-1, :-2], padded[:-2, :-2],
            )
            count = np.zeros(image.shape, dtype=np.uint8)
            turns = np.zeros_like(count)
            for first, second in zip(
                neighbors, neighbors[1:] + neighbors[:1], strict=True
            ):
                count += first
                turns += ~first & second
            north, _, east, _, south, _, west, _ = neighbors
            if phase == 0:
                preserved = (north & east & south) | (east & south & west)
            else:
                preserved = (north & east & west) | (north & south & west)
            remove = image & (count >= 2) & (count <= 6) & (turns == 1) & ~preserved
            changed |= bool(remove.any())
            image &= ~remove
        if not changed:
            break
    return image
