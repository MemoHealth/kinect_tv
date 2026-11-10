import numpy as np
import pygame
from numpy.typing import NDArray

from ..coordinates import Viewport


def boundary(mask: NDArray[np.bool_]) -> NDArray[np.bool_]:
    padded = np.pad(mask, 1)
    interior = (
        padded[:-2, 1:-1] & padded[2:, 1:-1] & padded[1:-1, :-2] & padded[1:-1, 2:]
    )
    return mask & ~interior


class Outline:
    def __init__(self, field: Viewport, shape: tuple[int, int]) -> None:
        self._field = field
        self._source = pygame.Surface(shape[::-1], pygame.SRCALPHA)
        self._scaled = pygame.Surface((field.width, field.height), pygame.SRCALPHA)
        self._previous: NDArray[np.bool_] | None = None
        self._opacity = 0.0
        self._visible = False

    def draw(
        self, canvas: pygame.Surface, mask: NDArray[np.bool_], dt: float
    ) -> None:
        if mask is not self._previous:
            self._previous = mask
            self._visible = bool(mask.any())
            if self._visible:
                self._source.fill((128, 221, 231, 0))
                pixels = pygame.surfarray.pixels_alpha(self._source)
                pixels[boundary(mask).T] = 145
                del pixels
                pygame.transform.scale(
                    self._source, self._scaled.get_size(), self._scaled
                )
        delta = dt * (8 if self._visible else -5)
        self._opacity = min(1.0, max(0.0, self._opacity + delta))
        if self._opacity:
            self._scaled.set_alpha(round(self._opacity * 255))
            canvas.blit(self._scaled, (self._field.x, self._field.y))
