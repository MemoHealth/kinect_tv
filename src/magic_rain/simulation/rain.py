import numpy as np
from numpy.typing import NDArray

from ..config import SCENE_SIZE, DemoConfig
from ..coordinates import Viewport
from .arm_water import ArmWater


class DemoRain:
    def __init__(self, config: DemoConfig, *, snow: bool = False) -> None:
        width, height = SCENE_SIZE
        rng = np.random.default_rng(config.seed)
        count = config.particle_count
        self.x = rng.uniform(0, width, count)
        self.y = rng.uniform(-40, height, count)
        self.snow = snow
        low, high = (25, 105) if snow else (110, 390)
        self.speed = rng.uniform(low, high, count)
        self._start_speed = self.speed.copy()
        self.depth_band = np.digitize(self._start_speed, (190, 305))
        self.drift = rng.uniform(-9, 16, count)
        self.velocity_x = self.drift.copy()
        self.time = 0.0
        self.floor_hits = np.zeros(count, dtype=bool)
        self.floor_x = np.zeros(count)
        self._rng = rng
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

    def step(
        self,
        dt: float,
        mask: NDArray[np.bool_],
        field: Viewport,
        wind: NDArray[np.float64] | None = None,
        *,
        water: ArmWater | None = None,
    ) -> None:
        width, height = SCENE_SIZE
        self.time += dt
        acceleration, speed_margin = (7, 12) if self.snow else (36, 45)
        np.minimum(
            self.speed + acceleration * dt, self._start_speed + speed_margin,
            out=self.speed,
        )
        drift = self.drift.copy()
        if self.snow:
            drift += 21 * np.sin(self.y / 50 + self._start_speed)
        if wind is not None:
            u = (self.x - field.x) / field.width
            v = (self.y - field.y) / field.height
            inside = (0 <= u) & (u < 1) & (0 <= v) & (v < 1)
            sx = (u[inside] * wind.shape[1]).astype(int)
            sy = (v[inside] * wind.shape[0]).astype(int)
            drift[inside] += wind[sy, sx]
        self.slide *= 1 - 4 * dt
        self.shimmer *= 1 - 2.4 * dt
        velocity = drift + self.slide
        next_x = self.x + velocity * dt
        next_y = self.y + self.speed * dt
        caught = (
            water.collect(self.x, self.y, next_x, next_y, field, snow=self.snow)
            if water is not None else np.zeros(self.x.size, dtype=bool)
        )
        rows, columns = mask.shape
        directions = self._directions(mask)
        deflection = np.zeros(self.x.size, dtype=np.int8)
        # Sample the swept path so thin rows do not disappear between steps.
        for fraction in (0.25, 0.5, 0.75, 1.0):
            u = (self.x + (next_x - self.x) * fraction - field.x) / field.width
            v = (self.y + (next_y - self.y) * fraction - field.y) / field.height
            inside = (0 <= u) & (u < 1) & (0 <= v) & (v < 1)
            indices = np.flatnonzero(inside & (deflection == 0) & ~caught)
            sx = (u[indices] * columns).astype(int)
            sy = (v[indices] * rows).astype(int)
            hit = mask[sy, sx]
            deflection[indices[hit]] = directions[sy[hit], sx[hit]]
        hits = deflection != 0

        self.slide[hits] = (64.0 if self.snow else 200.0) * deflection[hits]
        velocity[hits] = drift[hits] + self.slide[hits]
        self.shimmer[hits] = 1
        next_y[hits] = self.y[hits] + 3 * dt

        next_x = self.x + velocity * dt
        floor = height - 12 if water is not None else height + 20
        self.floor_hits[:] = (next_y >= floor) & ~caught
        self.floor_x[self.floor_hits] = next_x[self.floor_hits] % width
        recycled = (next_y >= floor) | caught
        self.x[:] = next_x % width
        self.x[recycled] = self._rng.uniform(0, width, np.count_nonzero(recycled))
        self.speed[recycled] = self._start_speed[recycled]
        self.slide[recycled] = 0
        self.shimmer[recycled] = 0
        self.y[:] = (next_y + 40) % (height + 60) - 40
        self.y[recycled] = -40
        if water is not None:
            indices = np.flatnonzero(recycled)
            spills = water.take_spills(min(indices.size, 8))
            for index, (x, y, speed) in zip(indices[:len(spills)], spills, strict=True):
                self.x[index], self.y[index] = x, y
                self.slide[index] = speed
                self.shimmer[index] = 0.65
        self.velocity_x[:] = drift + self.slide
