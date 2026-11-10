from collections import deque
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from ..coordinates import Viewport

Span = tuple[int, int]
Spill = tuple[float, float, float]


@dataclass(frozen=True)
class Basin:
    top: int
    spans: tuple[Span, ...]
    lip: int = 0

    @property
    def capacity(self) -> int:
        return sum(right - left for left, right in self.spans)

    @property
    def center(self) -> tuple[float, float]:
        left, right = self.spans[0]
        return (left + right) / 2, self.top + len(self.spans) / 2

    def surface(self, amount: float) -> tuple[int, float]:
        for index in range(len(self.spans) - 1, -1, -1):
            left, right = self.spans[index]
            width = right - left
            if amount <= width:
                return index, index + 1 - amount / width
            amount -= width
        return 0, 0.0


@dataclass
class Pool:
    basin: Basin
    amount: float = 0


def find_basins(mask: NDArray[np.bool_]) -> list[Basin]:
    if not mask.any():
        return []
    active: list[tuple[int, list[Span]]] = []
    completed = []
    for y, row in enumerate(mask):
        boundaries = np.flatnonzero(row[:-1] != row[1:]) + 1
        spans_in_row = [
            (int(left), int(right))
            for left, right in zip(boundaries[:-1], boundaries[1:], strict=True)
            if not row[left] and 2 <= right - left <= 96
        ]
        following = []
        ended = []
        for top, spans in active:
            match = max(
                spans_in_row,
                key=lambda span: _overlap(span, spans[-1]),
                default=None,
            )
            if match is not None and _overlap(match, spans[-1]) > 0:
                spans_in_row.remove(match)
                spans.append(match)
                following.append((top, spans))
            else:
                ended.append((top, spans))
        following.extend((y, [span]) for span in spans_in_row)
        for top, spans in ended:
            left, right = spans[0]
            base_left, base_right = spans[-1]
            if top < 3 or not 7 <= len(spans) <= 52 or right - left < 10:
                continue
            floor = row[base_left:base_right]
            gaps = ~floor
            if floor.mean() < 0.65 or np.any(gaps[:-2] & gaps[1:-1] & gaps[2:]):
                continue
            clear = ~mask[top - 3:top, left:right].any(axis=0)
            if clear.sum() >= 4:
                left_above = bool(mask[top - 1, left - 1])
                right_above = bool(mask[top - 1, right])
                lip = int(left_above) - int(right_above)
                completed.append(Basin(top, tuple(spans), lip))
        active = following
    return sorted(completed, key=lambda basin: basin.capacity, reverse=True)[:3]


def _overlap(first: Span, second: Span) -> int:
    return min(first[1], second[1]) - max(first[0], second[0])


class ArmWater:
    def __init__(self) -> None:
        self.pools: list[Pool] = []
        self._mask: NDArray[np.bool_] | None = None
        self._spills: deque[Spill] = deque(maxlen=96)
        self.width = 320
        self.height = 240

    def update(self, mask: NDArray[np.bool_], field: Viewport) -> None:
        if mask is self._mask or np.array_equal(mask, self._mask):
            return
        self._mask = mask
        self.height, self.width = mask.shape
        previous = self.pools.copy()
        self.pools = []
        for basin in find_basins(mask):
            match = min(
                previous, key=lambda pool: self._distance(pool, basin), default=None
            )
            pool = Pool(basin)
            if match is not None and self._distance(match, basin) <= 18:
                previous.remove(match)
                pool.amount = min(match.amount, basin.capacity)
                self._spill_amount(
                    pool, match.amount - pool.amount, field, overflow=True
                )
            self.pools.append(pool)
        for old in previous:
            self._spill_amount(old, old.amount, field, overflow=False)

    @staticmethod
    def _distance(pool: Pool, basin: Basin) -> float:
        x, y = pool.basin.center
        other_x, other_y = basin.center
        return abs(x - other_x) + abs(y - other_y)

    def collect(self, x, y, next_x, next_y, field: Viewport, *, snow: bool):
        caught = np.zeros(x.size, dtype=bool)
        for pool in self.pools:
            basin = pool.basin
            index, level = basin.surface(pool.amount)
            line = field.y + (basin.top + level) * field.height / self.height
            left, right = basin.spans[index]
            left = field.x + left * field.width / self.width
            right = field.x + right * field.width / self.width
            ids = np.flatnonzero((y < line) & (next_y >= line) & ~caught)
            fraction = (line - y[ids]) / (next_y[ids] - y[ids])
            cross = x[ids] + fraction * (next_x[ids] - x[ids])
            ids = ids[(cross >= left) & (cross < right)]
            caught[ids] = True
            received = ids.size * (28 if snow else 14)
            excess = max(0, pool.amount + received - basin.capacity)
            pool.amount = min(basin.capacity, pool.amount + received)
            self._spill_amount(pool, excess, field, overflow=True)
        return caught

    def _spill_amount(
        self, pool: Pool, amount: float, field: Viewport, *, overflow: bool
    ) -> None:
        if amount <= 0:
            return
        basin = pool.basin
        index, level = (0, 0.0) if overflow else basin.surface(pool.amount)
        left, right = basin.spans[index]
        y = field.y + (basin.top + level) * field.height / self.height + 2
        count = min(32, max(1, round(amount / 14)))
        for drop in range(count):
            drop_y = y
            if overflow:
                side = basin.lip or (-1 if drop % 2 == 0 else 1)
                x = left - 1 if side < 0 else right
                if self._mask is not None:
                    row = self._mask[basin.top]
                    while 0 <= x < self.width and row[x]:
                        x += side
                    if not 0 <= x < self.width:
                        x = left - 1 if side < 0 else right
                        drop_y = field.y + (basin.top - 1) * field.height / self.height
                speed = 75 * side
            else:
                fraction = (drop + 0.5) / count
                x = left + fraction * (right - left)
                speed = 100 * (fraction - 0.5)
            self._spills.append((field.x + x * field.width / self.width, drop_y, speed))

    def take_spills(self, limit: int) -> list[Spill]:
        return [self._spills.popleft() for _ in range(min(limit, len(self._spills)))]
