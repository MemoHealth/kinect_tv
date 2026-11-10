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
        self.drift = rng.uniform(-9, 16, count)
        self.slide = np.zeros(count)
        self.shimmer = np.zeros(count)

    def step(self, dt: float, mask: NDArray[np.bool_], field: Viewport) -> None:
        width, height = SCENE_SIZE
        next_y = self.y + self.speed * dt
        rows, columns = mask.shape
        u = (self.x - field.x) / field.width
        v = (next_y - field.y) / field.height
        inside = (0 <= u) & (u < 1) & (0 <= v) & (v < 1)
        indices = np.flatnonzero(inside)
        sample_x = (u[indices] * columns).astype(int)
        sample_y = (v[indices] * rows).astype(int)
        hit_mask = mask[sample_y, sample_x]
        hits = indices[hit_mask]

        self.slide *= 1 - 4 * dt
        self.shimmer *= 1 - 2.4 * dt
        hit_rows = mask[sample_y[hit_mask]]
        left = hit_rows.argmax(axis=1)
        right = columns - 1 - hit_rows[:, ::-1].argmax(axis=1)
        direction = np.where(2 * sample_x[hit_mask] < left + right, -1, 1)
        self.slide[hits] = 200 * direction
        self.shimmer[hits] = 1
        next_y[hits] = self.y[hits] + 18 * dt

        self.x[:] = (self.x + (self.drift + self.slide) * dt) % width
        self.y[:] = (next_y + 40) % (height + 60) - 40
