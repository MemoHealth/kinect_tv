import numpy as np
import pygame
from numpy.typing import NDArray


class Sparks:
    def __init__(self, capacity: int, seed: int) -> None:
        self._rng = np.random.default_rng(seed)
        self._cursor = 0
        self.x = np.zeros(capacity, dtype=np.float32)
        self.y = np.zeros_like(self.x)
        self._vx = np.zeros_like(self.x)
        self._vy = np.zeros_like(self.x)
        self.life = np.zeros_like(self.x)
        self._color = np.zeros(capacity, dtype=np.uint8)
        self._sprites: list[list[pygame.Surface]] = []

    def palette(self, colors: tuple[tuple[int, int, int], ...]) -> None:
        self._sprites = []
        for color in colors:
            variants = []
            for opacity in (34, 75, 125, 188):
                sprite = pygame.Surface((13, 13), pygame.SRCALPHA)
                pygame.draw.circle(sprite, (*color, opacity // 6), (6, 6), 6)
                pygame.draw.circle(sprite, (*color, opacity // 3), (6, 6), 4)
                pygame.draw.circle(sprite, (*color, opacity), (6, 6), 2)
                variants.append(sprite)
            self._sprites.append(variants)

    def emit(
        self, x: NDArray, y: NDArray, colors: NDArray, speed: float, *, life: float
    ) -> None:
        count = x.size
        slots = (self._cursor + np.arange(count)) % self.life.size
        self._cursor = (self._cursor + count) % self.life.size
        angle = self._rng.uniform(0, np.pi * 2, count)
        velocity = speed * self._rng.uniform(0.45, 1.0, count)
        self.x[slots], self.y[slots] = x, y
        self._vx[slots] = np.cos(angle) * velocity
        self._vy[slots] = np.sin(angle) * velocity
        self.life[slots] = life * self._rng.uniform(0.55, 1.0, count)
        self._color[slots] = colors

    def update(self, dt: float, *, gravity: float = 0) -> None:
        self.life -= dt
        self._vx *= max(0, 1 - dt * 1.9)
        self._vy *= max(0, 1 - dt * 1.9)
        self._vy += gravity * dt
        self.x += self._vx * dt
        self.y += self._vy * dt

    def draw(self, canvas: pygame.Surface) -> None:
        ids = np.flatnonzero(self.life > 0)
        tiers = np.minimum(3, (self.life[ids] * 5).astype(int))
        canvas.fblits([
            (
                self._sprites[self._color[i]][tier],
                (int(self.x[i]) - 6, int(self.y[i]) - 6),
            )
            for i, tier in zip(ids, tiers, strict=True)
        ])
