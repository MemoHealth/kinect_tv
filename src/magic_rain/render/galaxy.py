import numpy as np
import pygame
from numpy.typing import NDArray

from ..config import SCENE_SIZE
from ..coordinates import Viewport
from .outline import boundary
from .sparks import Sparks

STAR_COLORS = ((126, 221, 255), (191, 161, 255), (255, 215, 169))


class GalaxyMirror:
    def __init__(self, field: Viewport, shape: tuple[int, int]) -> None:
        self._field = field
        self._rng = np.random.default_rng(248)
        self._stars = self._rng.random(shape) < 0.043
        self._color = self._rng.integers(len(STAR_COLORS), size=shape, dtype=np.uint8)
        self._previous = np.zeros(shape, dtype=bool)
        self._points: list[tuple[pygame.Surface, tuple[int, int]]] = []
        self._dust = Sparks(360, seed=63)
        self._dust.palette(STAR_COLORS)
        self._backdrop = self._sky()
        self._small = pygame.Surface(shape[::-1], pygame.SRCALPHA)
        self._small.fill((106, 85, 209, 0))
        self._glow = pygame.Surface((field.width, field.height), pygame.SRCALPHA)
        self._sprites = []
        for color in STAR_COLORS:
            sprite = pygame.Surface((13, 13), pygame.SRCALPHA)
            pygame.draw.circle(sprite, (*color, 20), (6, 6), 6)
            pygame.draw.circle(sprite, (*color, 58), (6, 6), 4)
            pygame.draw.circle(sprite, (*color, 200), (6, 6), 2)
            self._sprites.append(sprite)

    def _sky(self) -> pygame.Surface:
        width, height = SCENE_SIZE
        surface = pygame.Surface(SCENE_SIZE, depth=32)
        for y in range(height):
            halo = np.exp(-((y / height - 0.47) / 0.36) ** 2)
            color = (round(5 + 9 * halo), round(8 + 6 * halo), round(21 + 23 * halo))
            pygame.draw.line(surface, color, (0, y), (width, y))
        for x, y in self._rng.integers((0, 0), SCENE_SIZE, size=(165, 2)):
            light = int(self._rng.integers(20, 62))
            radius = 2 if light > 55 else 1
            pygame.draw.circle(surface, (light, light + 5, light + 17), (x, y), radius)
        return surface

    def _points_at(self, rows: NDArray, cols: NDArray) -> tuple[NDArray, NDArray]:
        height, width = self._stars.shape
        return (
            self._field.x + (cols + 0.5) * self._field.width / width,
            self._field.y + (rows + 0.5) * self._field.height / height,
        )

    def update(self, mask: NDArray[np.bool_], dt: float) -> None:
        if mask is not self._previous:
            rows, cols = np.nonzero(mask & self._stars)
            x, y = self._points_at(rows, cols)
            self._points = [
                (self._sprites[color], (int(px) - 6, int(py) - 6))
                for px, py, color in zip(x, y, self._color[rows, cols], strict=True)
            ]
            pixels = pygame.surfarray.pixels_alpha(self._small)
            pixels[:] = mask.T * np.uint8(89)
            del pixels
            pygame.transform.smoothscale(self._small, self._glow.get_size(), self._glow)
            if self._previous.any():
                rows, cols = np.nonzero(boundary(mask) & ~self._previous)
                count = min(28, rows.size // 4)
                if count:
                    ids = self._rng.choice(rows.size, count, replace=False)
                    rows, cols = rows[ids], cols[ids]
                    x, y = self._points_at(rows, cols)
                    self._dust.emit(
                        x, y, self._color[rows, cols], 56 + count * 4, life=1.1
                    )
            self._previous = mask
        self._dust.update(dt)

    def draw(self, canvas: pygame.Surface) -> None:
        canvas.blit(self._backdrop, (0, 0))
        canvas.blit(self._glow, (self._field.x, self._field.y))
        canvas.fblits(self._points)
        self._dust.draw(canvas)
