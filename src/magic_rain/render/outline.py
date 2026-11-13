from math import exp

import numpy as np
import pygame
from numpy.typing import NDArray

from ..coordinates import Viewport
from .coverage import soften

_COVERAGE = np.arange(256)
_EDGE_ALPHA = np.rint(
    235 * np.exp(-((_COVERAGE - 127.5) / 58) ** 2)
).astype(np.uint8)
_HALO_ALPHA = np.rint(
    42 * np.clip(1 - np.abs(_COVERAGE - 127.5) / 127.5, 0, 1)
).astype(np.uint8)
_OUTSIDE_EDGE = (_COVERAGE < 10) | (_COVERAGE > 245)
_EDGE_ALPHA[_OUTSIDE_EDGE] = 0
_HALO_ALPHA[_OUTSIDE_EDGE] = 0
_COMPOSITE_ALPHA = np.rint(
    _EDGE_ALPHA + (255 - _EDGE_ALPHA) * (_HALO_ALPHA.astype(np.float32) / 255)
).astype(np.uint8)


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
        self._source.fill((177, 235, 242, 0))
        self._scaled = pygame.Surface((field.width, field.height), pygame.SRCALPHA)
        self._edge = pygame.Surface(
            (max(1, field.width // 2), max(1, field.height // 2)), pygame.SRCALPHA
        )
        self._target: NDArray[np.float32] | None = None
        self._coverage: NDArray[np.float32] | None = None
        self._previous: NDArray[np.bool_] | None = None
        self._opacity = 0.0
        self._visible = False

    def draw(
        self, canvas: pygame.Surface, mask: NDArray[np.bool_], dt: float
    ) -> None:
        if mask is not self._previous:
            self._previous = mask
            was_visible = self._visible
            self._visible = bool(mask.any())
            if self._visible:
                self._target = soften(soften(mask))
                if not was_visible:
                    self._coverage = self._target.copy()
        if self._visible:
            difference = self._target - self._coverage
            elapsed = max(0, dt)
            blend = np.where(
                np.abs(difference) > 0.45,
                np.float32(1 - exp(-elapsed / 0.012)),
                np.float32(1 - exp(-elapsed / 0.045)),
            )
            self._coverage += difference * blend
            pixels = pygame.surfarray.pixels_alpha(self._source)
            pixels[:] = np.rint(self._coverage.T * 255).astype(np.uint8)
            del pixels
            pygame.transform.smoothscale(
                self._source, self._edge.get_size(), self._edge
            )
            coverage = pygame.surfarray.pixels_alpha(self._edge)
            coverage[:] = _COMPOSITE_ALPHA[coverage]
            del coverage
            pygame.transform.smoothscale(
                self._edge, self._scaled.get_size(), self._scaled
            )
        delta = dt * (8 if self._visible else -5)
        self._opacity = min(1.0, max(0.0, self._opacity + delta))
        if self._opacity:
            self._scaled.set_alpha(round(self._opacity * 255))
            canvas.blit(self._scaled, (self._field.x, self._field.y))
