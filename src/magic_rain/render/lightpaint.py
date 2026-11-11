from colorsys import hsv_to_rgb

import numpy as np
import pygame
from numpy.typing import NDArray

from ..coordinates import Viewport
from .coverage import soften
from .outline import boundary

RAINBOW = np.array([hsv_to_rgb(index / 256, 0.78, 0.75) for index in range(256)])


class LightPaint:
    def __init__(self, field: Viewport, shape: tuple[int, int]) -> None:
        self._field = field
        self._history = np.zeros((*shape, 3), dtype=np.float32)
        self._previous = np.zeros(shape, dtype=bool)
        self._phase = 0.0
        self._brush = pygame.Surface(shape[::-1], depth=32)
        self._scaled = pygame.Surface((field.width, field.height), depth=32)

    def clear(self) -> None:
        self._history.fill(0)
        self._previous = np.zeros_like(self._previous)
        self._phase = 0.0

    def update(
        self, mask: NDArray[np.bool_], dt: float, *, half_life: float = 3,
        labels: NDArray[np.uint8] | None = None,
        palette: NDArray[np.float32] | None = None,
    ) -> None:
        self._history *= 2 ** (-dt / half_life)
        self._phase = (self._phase + dt * 0.19) % 1
        if mask is self._previous:
            return
        moving_edges = boundary(mask) & ~self._previous
        rows, cols = np.nonzero(moving_edges)
        if labels is not None and palette is not None:
            colors = palette[labels[rows, cols]]
        else:
            hues = ((self._phase + 0.45 * cols / mask.shape[1]) * 256).astype(int) % 256
            colors = RAINBOW[hues]
        self._history[rows, cols] = np.maximum(self._history[rows, cols], colors)
        self._previous = mask

    def draw(self, canvas: pygame.Surface) -> None:
        smoothed = np.maximum(self._history * 0.92, soften(self._history))
        colors = (255 * smoothed).astype(np.uint8).swapaxes(0, 1)
        pygame.surfarray.blit_array(self._brush, colors)
        pygame.transform.smoothscale(self._brush, self._scaled.get_size(), self._scaled)
        canvas.blit(
            self._scaled,
            (self._field.x, self._field.y),
            special_flags=pygame.BLEND_RGB_ADD,
        )
