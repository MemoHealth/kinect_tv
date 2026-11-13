"""Bounded gravity-free particles and local moving-silhouette contact."""

from collections import deque
from math import ceil, exp, log

import numpy as np
from numpy.typing import NDArray

from ..config import SCENE_SIZE
from ..coordinates import Viewport

MAX_SPEED = 480.0
HALF_LIFE = 10.0
GRID = (18, 32)


class GasParticles:
    def __init__(
        self, field: Viewport, shape: tuple[int, int], *, count: int = 600,
        seed: int = 340,
    ) -> None:
        if not 1 <= count <= 1000:
            raise ValueError("Gas particle count must be between 1 and 1000")
        self.field = field
        self.shape = shape
        self._scale = np.array((field.width / shape[1], field.height / shape[0]))
        rng = np.random.default_rng(seed)
        # Stratified placement avoids an initial dense random clump.
        columns = ceil(np.sqrt(count * SCENE_SIZE[0] / SCENE_SIZE[1]))
        rows = ceil(count / columns)
        y, x = np.divmod(np.arange(count), columns)
        self.position = np.column_stack((
            (x + rng.uniform(0.2, 0.8, count)) * SCENE_SIZE[0] / columns,
            (y + rng.uniform(0.2, 0.8, count)) * SCENE_SIZE[1] / rows,
        ))
        self.velocity = np.zeros((count, 2))
        self._mask = np.zeros(shape, dtype=bool)
        self._last: NDArray[np.bool_] | None = None
        self._history: deque[tuple[float, NDArray]] = deque(maxlen=8)
        self._recent: tuple[NDArray, ...] = ()
        self._nearest_body: NDArray | None = None
        self._time = 0.0
        self._sample_time = -1.0
        self._escape = np.zeros((*shape, 2))
        self._normal = self._escape.copy()
        self._body_speed = np.zeros(shape)

    def _nearest(self, target: NDArray[np.bool_], *, exterior: bool = False) -> NDArray:
        """Nearest target on the four axes; linear work, no all-point search."""
        height, width = target.shape
        x = np.arange(width, dtype=np.int16)[None, :]
        y = np.arange(height, dtype=np.int16)[:, None]
        left = np.maximum.accumulate(np.where(target, x, -1 if exterior else -width), 1)
        right = np.minimum.accumulate(
            np.where(target, x, width if exterior else 2 * width)[:, ::-1], 1
        )[:, ::-1]
        top = np.maximum.accumulate(np.where(target, y, -1 if exterior else -height), 0)
        bottom = np.minimum.accumulate(
            np.where(target, y, height if exterior else 2 * height)[::-1], 0
        )[::-1]
        dx = np.where(x - left <= right - x, left - x, right - x)
        dy = np.where(y - top <= bottom - y, top - y, bottom - y)
        dx = dx.astype(np.float32) * np.float32(self._scale[0])
        dy = dy.astype(np.float32) * np.float32(self._scale[1])
        horizontal = np.abs(dx) <= np.abs(dy)
        return np.stack((
            np.where(horizontal, dx, 0), np.where(horizontal, 0, dy),
        ), axis=2)

    def _sample(self, mask: NDArray[np.bool_]) -> None:
        if mask is self._last:
            return
        same = self._last is not None and np.array_equal(mask, self._last)
        self._last = mask
        self._sample_time = self._time
        if not mask.any():
            self._mask = np.zeros(self.shape, dtype=bool)
            self._body_speed.fill(0)
            self._history.clear()
            self._recent = ()
            return
        if same:
            self._body_speed.fill(0)
            self._recent = ()
            self._history.append((self._time, self._nearest_body))
            return
        padded = np.pad(mask, 1)
        self._mask = (mask | padded[:-2, 1:-1] | padded[2:, 1:-1]
                      | padded[1:-1, :-2] | padded[1:-1, 2:])
        self._escape = self._nearest(~self._mask, exterior=True)
        coverage = self._mask.astype(np.float32)
        for _ in range(2):
            padded = np.pad(coverage, 1)
            horizontal = (
                padded[:, :-2] + 2 * padded[:, 1:-1] + padded[:, 2:]
            ) * 0.25
            coverage = (
                horizontal[:-2] + 2 * horizontal[1:-1] + horizontal[2:]
            ) * 0.25
        gy, gx = np.gradient(coverage)
        gx /= self._scale[0]
        gy /= self._scale[1]
        length = np.maximum(np.hypot(gx, gy), 1e-6)
        self._normal = -np.stack((gx / length, gy / length), axis=2)
        while self._history and self._time - self._history[0][0] > 0.250001:
            self._history.popleft()
        self._body_speed.fill(0)
        self._recent = tuple(item[1] for item in list(self._history)[-4:])
        if self._history:
            timestamp, toward_old = self._history[-min(4, len(self._history))]
            elapsed = self._time - timestamp
            if elapsed > 0.015:
                advance = -(toward_old[:, :, 0] * self._normal[:, :, 0]
                            + toward_old[:, :, 1] * self._normal[:, :, 1])
                speed = (advance - 2 * max(self._scale)) / elapsed
                near = np.maximum(np.abs(toward_old[:, :, 0]),
                                  np.abs(toward_old[:, :, 1])) <= (
                    24 * max(self._scale)
                )
                self._body_speed[:] = np.where(near, np.clip(speed, 0, 300), 0)
        self._nearest_body = self._nearest(self._mask).astype(np.float32)
        self._history.append((self._time, self._nearest_body))

    def _pressure(self) -> NDArray:
        """Bilinear deposit/gather gives a cheap collective short-range repulsion."""
        rows, cols = GRID
        scale = np.array((cols - 1, rows - 1)) / np.array(SCENE_SIZE)
        grid = self.position * scale
        cell = np.minimum(grid.astype(int), (cols - 2, rows - 2))
        fraction = grid - cell
        density = np.zeros(GRID)
        weights = []
        for oy, ox in ((0, 0), (0, 1), (1, 0), (1, 1)):
            weight = (fraction[:, 0] if ox else 1 - fraction[:, 0]) * (
                fraction[:, 1] if oy else 1 - fraction[:, 1]
            )
            weights.append((oy, ox, weight))
            np.add.at(density, (cell[:, 1] + oy, cell[:, 0] + ox), weight)
        padded = np.pad(density, 1, mode="edge")
        smooth = (
            4 * density + padded[:-2, 1:-1] + padded[2:, 1:-1]
            + padded[1:-1, :-2] + padded[1:-1, 2:]
        ) / 8
        gy, gx = np.gradient(smooth)
        acceleration = np.zeros_like(self.velocity)
        for oy, ox, weight in weights:
            indices = cell[:, 1] + oy, cell[:, 0] + ox
            acceleration[:, 0] -= gx[indices] * weight * 12
            acceleration[:, 1] -= gy[indices] * weight * 12
        return np.clip(acceleration, -70, 70)

    def _contact(self, points: NDArray) -> None:
        grid = (points - (self.field.x, self.field.y)) / self._scale
        columns, rows = grid[:, 0].astype(int), grid[:, 1].astype(int)
        inside = ((grid[:, 0] >= 0) & (grid[:, 0] < self.shape[1])
                  & (grid[:, 1] >= 0) & (grid[:, 1] < self.shape[0]))
        ids = np.flatnonzero(inside)
        ids = ids[self._mask[rows[ids], columns[ids]]]
        if not ids.size:
            return
        r, c = rows[ids], columns[ids]
        escape = self._escape[r, c]
        distance = np.linalg.norm(escape, axis=1, keepdims=True)
        direction = escape / np.maximum(distance, 1e-6)
        free_grid = np.column_stack((c, r)) + escape / self._scale
        edge = np.rint(free_grid - direction).astype(int)
        edge[:, 0] = np.clip(edge[:, 0], 0, self.shape[1] - 1)
        edge[:, 1] = np.clip(edge[:, 1], 0, self.shape[0] - 1)
        normal = self._normal[edge[:, 1], edge[:, 0]].copy()
        normal[(normal * direction).sum(axis=1) < 0.2] = direction[
            (normal * direction).sum(axis=1) < 0.2
        ]
        body_speed = self._body_speed[edge[:, 1], edge[:, 0]]
        if len(self._recent) == 4:
            advances = np.stack([
                -(previous[edge[:, 1], edge[:, 0]] * normal).sum(axis=1)
                for previous in self._recent
            ])
            consistent = ((np.diff(advances, axis=0) < -0.4 * min(self._scale)).all(0)
                          & (advances[-1] > 0.4 * min(self._scale)))
            body_speed = np.where(consistent, body_speed, 0)
        else:
            body_speed = np.zeros_like(body_speed)
        if self._time - self._sample_time > 0.12:
            body_speed = np.zeros_like(body_speed)
        relative = (self.velocity[ids] * normal).sum(axis=1) - body_speed
        self.velocity[ids] += -1.82 * np.minimum(relative, 0)[:, None] * normal
        speed = np.linalg.norm(self.velocity[ids], axis=1)
        self.velocity[ids] *= np.minimum(
            1, MAX_SPEED / np.maximum(speed, 1e-6)
        )[:, None]
        projected = (
            (self.field.x, self.field.y) + (free_grid + 0.5) * self._scale
            + direction * 0.5
        )
        # Preserve tangential subpixel position instead of snapping onto a row.
        horizontal = np.abs(direction[:, 0]) > 0.5
        projected[horizontal, 1] = points[ids[horizontal], 1]
        projected[~horizontal, 0] = points[ids[~horizontal], 0]
        points[ids] = projected

    def step(self, mask: NDArray[np.bool_], dt: float) -> None:
        if dt <= 0:
            return
        self._sample(mask)
        steps = max(1, ceil(min(dt, 0.05) * 60))
        elapsed = min(dt, 0.05) / steps
        for _ in range(steps):
            self.velocity += self._pressure() * elapsed
            self.velocity *= exp(-log(2) * elapsed / HALF_LIFE)
            speed = np.linalg.norm(self.velocity, axis=1)
            self.velocity *= np.minimum(1, MAX_SPEED / np.maximum(speed, 1e-6))[:, None]
            # Four swept samples: <=2 logical pixels at the speed cap / 60 Hz.
            for _ in range(4):
                points = self.position + self.velocity * elapsed / 4
                if self._mask.any():
                    self._contact(points)
                for axis, size in enumerate(SCENE_SIZE):
                    low, high = points[:, axis] < 3, points[:, axis] > size - 3
                    self.velocity[low, axis] = np.abs(self.velocity[low, axis]) * 0.84
                    self.velocity[high, axis] = (
                        -np.abs(self.velocity[high, axis]) * 0.84
                    )
                    points[:, axis] = np.clip(points[:, axis], 3, size - 3)
                self.position[:] = points
            speed = np.linalg.norm(self.velocity, axis=1)
            self.velocity *= np.minimum(1, MAX_SPEED / np.maximum(speed, 1e-6))[:, None]
            self._time += elapsed
