from dataclasses import dataclass

import numpy as np
import pygame
from numpy.typing import NDArray

from ..sensors.base import SensorFrame

STALE_S = 0.25


@dataclass(frozen=True)
class Foreground:
    mask: NDArray[np.bool_]
    confidence: float
    timestamp_monotonic_s: float
    active: bool


class ForegroundTracker:
    def __init__(
        self, background: NDArray[np.uint16], *, mirrored: bool = True,
        color_reference: NDArray[np.uint8] | None = None,
        open_background: NDArray[np.bool_] | None = None,
        foreground_margin: NDArray[np.int32] | None = None,
    ) -> None:
        self._background = background.astype(np.int32)
        self._mirrored = mirrored
        self._empty = np.zeros(background.shape, dtype=np.bool_)
        self._last: Foreground | None = None
        self._color_reference = color_reference
        self._open_background = open_background
        self._foreground_margin = (
            120 if foreground_margin is None else foreground_margin
        )
        self._surface = pygame.Surface(background.shape[::-1], pygame.SRCALPHA)
        self.color_assist = True
        self._margin = 0.0
        self._far = 3800

    def configure(self, *, mirrored: bool, margin: float, far: int) -> None:
        self._mirrored = mirrored
        self._margin = margin
        self._far = far
        self._last = None

    def update(self, frame: SensorFrame | None, now: float) -> Foreground:
        if frame is not None and now - frame.timestamp_monotonic_s <= STALE_S:
            self._last = self._segment(frame)
        if self._last is None or now - self._last.timestamp_monotonic_s > STALE_S:
            return Foreground(self._empty, 0.0, now, False)
        return self._last

    def _segment(self, frame: SensorFrame) -> Foreground:
        depth = frame.depth_mm
        measured = (self._background != 0) & (depth != 0)
        in_range = (depth >= 850) & (depth <= self._far)
        foreground = in_range & measured & (
            self._background - depth >= self._foreground_margin
        )
        revealed = None
        if self._open_background is not None:
            revealed = in_range & self._open_background
            foreground |= revealed
        if margin := round(depth.shape[1] * self._margin):
            foreground[:, :margin] = False
            foreground[:, -margin:] = False

        # Keep coherent regions and bridge single-pixel holes without assigning IDs.
        padded = np.pad(foreground, 1)
        neighbours = (
            padded[:-2, 1:-1].astype(np.uint8)
            + padded[2:, 1:-1]
            + padded[1:-1, :-2]
            + padded[1:-1, 2:]
        )
        core = np.pad(foreground & (neighbours >= 3), 1)
        coherent = (
            core[1:-1, 1:-1]
            | core[:-2, 1:-1]
            | core[2:, 1:-1]
            | core[1:-1, :-2]
            | core[1:-1, 2:]
        )
        mask = (foreground & coherent) | (measured & (neighbours == 4))
        mask = self._remove_speckles(mask)
        size = np.count_nonzero(mask)
        coverage = np.count_nonzero(measured)
        open_size = 0 if revealed is None else np.count_nonzero(mask & revealed)
        active = 12 <= size <= mask.size * 0.65 and size - open_size <= coverage * 0.90
        if not active:
            return Foreground(self._empty, 0.0, frame.timestamp_monotonic_s, False)
        if self.color_assist and frame.rgb_coordinates is not None:
            self._recover_missing(mask, measured, frame, margin)
        if self._mirrored:
            mask = mask[:, ::-1]
        usable_depth = coverage if revealed is None else coverage + revealed.sum()
        confidence = usable_depth / measured.size
        return Foreground(mask, confidence, frame.timestamp_monotonic_s, True)

    def _remove_speckles(self, mask: NDArray[np.bool_]) -> NDArray[np.bool_]:
        if not mask.any():
            return mask
        alpha = pygame.surfarray.pixels_alpha(self._surface)
        alpha[:] = mask.T * np.uint8(255)
        del alpha
        minimum = max(12, round(mask.size * 64 / (320 * 240)))
        regions = pygame.mask.from_surface(self._surface).connected_components(minimum)
        clean = pygame.Mask(mask.shape[::-1])
        for region in regions:
            clean.draw(region, (0, 0))
        clean.to_surface(
            self._surface, setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0)
        )
        return pygame.surfarray.array_alpha(self._surface).T != 0

    def _recover_missing(
        self, mask: NDArray[np.bool_], measured: NDArray[np.bool_],
        frame: SensorFrame, margin: int,
    ) -> None:
        depth, rgb, coordinates = frame.depth_mm, frame.rgb, frame.rgb_coordinates
        reference = self._color_reference
        if rgb is None or coordinates is None or reference is None or not mask.any():
            return
        # A broad change (for example, exposure settling) isn't body evidence.
        sampled_change = np.abs(
            rgb[::8, ::8].astype(np.int16) - reference[::8, ::8]
        ).max(axis=2)
        if (sampled_change >= 28).mean() > 0.35:
            return
        radius = 3
        height, width = mask.shape
        horizontal = np.pad(mask, ((0, 0), (radius, radius)))
        band = np.logical_or.reduce(
            [horizontal[:, i:i + width] for i in range(2 * radius + 1)]
        )
        vertical = np.pad(band, ((radius, radius), (0, 0)))
        band = np.logical_or.reduce(
            [vertical[i:i + height] for i in range(2 * radius + 1)]
        )
        in_range = (depth == 0) | ((depth >= 850) & (depth <= self._far))
        candidates = band & ~mask & ~measured & in_range
        if margin:
            candidates[:, :margin] = False
            candidates[:, -margin:] = False
        y, x = np.nonzero(candidates)
        u, v = coordinates[y, x].T
        inside = (u >= 0) & (u < width) & (v >= 0) & (v < height)
        u, v = u[inside], v[inside]
        delta = np.abs(rgb[v, u].astype(np.int16) - reference[v, u])
        changed = (delta.max(axis=1) >= 28) & (delta.sum(axis=1) >= 45)
        if np.count_nonzero(mask) + np.count_nonzero(changed) <= mask.size * 0.65:
            mask[y[inside][changed], x[inside][changed]] = True
