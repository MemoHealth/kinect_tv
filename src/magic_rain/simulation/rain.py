import numpy as np
from numpy.typing import NDArray

from ..config import SCENE_SIZE, DemoConfig
from ..coordinates import Viewport


class DemoRain:
    def __init__(self, config: DemoConfig) -> None:
        width, height = SCENE_SIZE
        rng = np.random.default_rng(config.seed)
        count = config.particle_count
        self.x = rng.uniform(0, width, count)
        self.y = rng.uniform(-40, height, count)
        self.speed = rng.uniform(110, 390, count)
        self._start_speed = self.speed.copy()
        self.drift = rng.uniform(-9, 16, count)
        self.slide = np.zeros(count)
        self.shimmer = np.zeros(count)
        self._mask: NDArray[np.bool_] | None = None
        self._direction: NDArray[np.int8] | None = None

    def _directions(self, mask: NDArray[np.bool_]) -> NDArray[np.int8]:
        if self._direction is not None and np.array_equal(mask, self._mask):
            return self._direction
        columns = np.arange(mask.shape[1])
        left = np.maximum.accumulate(np.where(mask, -1, columns), axis=1)
        right = np.minimum.accumulate(
            np.where(mask, mask.shape[1], columns)[:, ::-1], axis=1
        )[:, ::-1]
        self._mask = mask.copy()
        self._direction = np.where(columns - left < right - columns, -1, 1).astype(
            np.int8
        )
        return self._direction

    def step(self, dt: float, mask: NDArray[np.bool_], field: Viewport) -> None:
        width, height = SCENE_SIZE
        np.minimum(self.speed + 36 * dt, self._start_speed + 45, out=self.speed)
        next_x = self.x + (self.drift + self.slide) * dt
        next_y = self.y + self.speed * dt
        rows, columns = mask.shape
        directions = self._directions(mask)
        deflection = np.zeros(self.x.size, dtype=np.int8)
        # Sample the swept path so thin rows do not disappear between steps.
        for fraction in (0.25, 0.5, 0.75, 1.0):
            u = (self.x + (next_x - self.x) * fraction - field.x) / field.width
            v = (self.y + (next_y - self.y) * fraction - field.y) / field.height
            inside = (0 <= u) & (u < 1) & (0 <= v) & (v < 1)
            indices = np.flatnonzero(inside & (deflection == 0))
            sx = (u[indices] * columns).astype(int)
            sy = (v[indices] * rows).astype(int)
            hit = mask[sy, sx]
            deflection[indices[hit]] = directions[sy[hit], sx[hit]]
        hits = deflection != 0

        self.slide *= 1 - 4 * dt
        self.shimmer *= 1 - 2.4 * dt
        self.slide[hits] = 200.0 * deflection[hits]
        self.shimmer[hits] = 1
        next_y[hits] = self.y[hits] + 18 * dt

        self.x[:] = (self.x + (self.drift + self.slide) * dt) % width
        self.speed[next_y >= height + 20] = self._start_speed[next_y >= height + 20]
        self.y[:] = (next_y + 40) % (height + 60) - 40
