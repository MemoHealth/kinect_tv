import numpy as np
import pygame
from numpy.typing import NDArray

from ..coordinates import Viewport
from ..interaction.funhouse import Funhouse


class ColorMirror:
    def __init__(self, field: Viewport, shape: tuple[int, int]) -> None:
        self._field = field
        self._lens = Funhouse()
        self._image = pygame.Surface(shape[::-1], depth=32)
        self._scaled = pygame.Surface((field.width, field.height), depth=32)
        self._previous: NDArray[np.uint8] | None = None
        self._parameters: tuple[float, bool] | None = None

    def draw(
        self,
        canvas: pygame.Surface,
        image: NDArray[np.uint8],
        strength: float,
        *,
        mirrored: bool,
    ) -> None:
        parameters = strength, mirrored
        if image is not self._previous or parameters != self._parameters:
            self._previous = image
            self._parameters = parameters
            view = image[:, ::-1] if mirrored else image
            warped = self._lens.warp(view, strength)
            pygame.surfarray.blit_array(self._image, warped.swapaxes(0, 1))
            pygame.transform.smoothscale(
                self._image, self._scaled.get_size(), self._scaled
            )
        canvas.fill((9, 8, 22))
        canvas.blit(self._scaled, (self._field.x, self._field.y))
