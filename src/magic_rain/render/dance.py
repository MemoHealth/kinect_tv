import numpy as np
import pygame
from numpy.typing import NDArray

from ..coordinates import Viewport
from ..interaction.color_slots import ColorSlots
from ..settings import PALETTES
from ..vision.centerline import centerline


class DanceMirror:
    """A silhouette-derived stick figure, independent of anatomical pose tracking."""

    def __init__(self, field: Viewport, shape: tuple[int, int]) -> None:
        self._field = field
        self._shape = shape
        self._slots = ColorSlots(shape)
        self._time = 0.0
        self._previous: NDArray[np.bool_] | None = None
        self._style = "Streck"
        self._image = pygame.Surface((shape[1] * 4, shape[0] * 4), pygame.SRCALPHA)
        self._scaled = pygame.Surface((field.width, field.height), pygame.SRCALPHA)
        self._segments: list[
            tuple[tuple[float, float], tuple[float, float], tuple]
        ] = []
        self._heads: list[tuple[float, float, tuple, float]] = []
        self._ribs: list[tuple[float, float, float]] = []
        self._caps: list[tuple[tuple[int, int], tuple]] = []
        self._background = pygame.Surface((1280, 720), depth=32)
        self._background.fill((9, 19, 33))
        self._skinny = np.zeros((shape[0] // 4, shape[1] // 4), dtype=bool)
        palette = np.array(PALETTES["Norrsken"])
        self._colors = [tuple(palette[0])]
        for group in range(1, 8):
            selected = [bool(group & (1 << i)) for i in range(3)]
            self._colors.append(tuple(palette[selected].mean(axis=0).astype(int)))

    def configure(self, style: str) -> None:
        if style != self._style:
            self._style = style
            self._redraw()

    def update(self, mask: NDArray[np.bool_], dt: float) -> None:
        self._time += dt
        if mask is self._previous:
            return
        self._previous = mask
        full_labels = self._slots.update(mask, self._time)
        height, width = mask.shape
        grouped = full_labels.reshape(height // 4, 4, width // 4, 4)
        labels = np.bitwise_or.reduce(np.bitwise_or.reduce(grouped, axis=3), axis=1)
        self._skinny = centerline(mask & (full_labels != 0))
        self._segments = []
        self._heads = []
        self._ribs = []
        self._caps = []
        padded = np.pad(self._skinny, 1)
        count = np.zeros(self._skinny.shape, dtype=np.uint8)
        sum_x = np.zeros(self._skinny.shape, dtype=np.float32)
        sum_y = np.zeros_like(sum_x)
        rows, cols = np.indices(self._skinny.shape)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                neighbor = padded[1 + dy:1 + dy + rows.shape[0],
                                  1 + dx:1 + dx + rows.shape[1]]
                count += neighbor
                sum_x += (cols + dx) * neighbor
                sum_y += (rows + dy) * neighbor
        x = sum_x / np.maximum(1, count)
        y = sum_y / np.maximum(1, count)
        points = np.rint(np.stack((x, y), axis=2) * 16 + 4).astype(int)
        ys, xs = np.nonzero(self._skinny & ((count <= 2) | (count >= 4)))
        self._caps = [
            (point, self._colors[group or 1])
            for point, group in zip(
                points[ys, xs].tolist(), labels[ys, xs], strict=True
            )
        ]
        for dy, dx in ((0, 1), (1, -1), (1, 0), (1, 1)):
            ys, xs = np.nonzero(
                self._skinny & padded[1 + dy:1 + dy + rows.shape[0],
                                     1 + dx:1 + dx + rows.shape[1]]
            )
            starts = points[ys, xs].tolist()
            ends = points[ys + dy, xs + dx].tolist()
            self._segments.extend(
                (start, end, self._colors[group or 1])
                for start, end, group in zip(starts, ends, labels[ys, xs], strict=True)
            )
        self._segments = self._segments[:1600]
        self._caps = self._caps[:600]
        for label in np.unique(labels[labels > 0]):
            group = labels == label
            ys, xs = np.nonzero(group)
            height = ys.max() - ys.min()
            if height < 10:
                continue
            middle = float(np.median(xs))
            tips = self._skinny & group & (count <= 2)
            candidates_y, candidates_x = np.nonzero(
                tips & (rows < ys.min() + height * 0.6)
            )
            if candidates_y.size:
                score = abs(candidates_x - middle) + (candidates_y - ys.min()) * 0.2
                best = score.argmin()
                hx, hy = candidates_x[best] * 8 + 2, candidates_y[best] * 8 + 2
                color = self._colors[label]
                self._heads.append((hx, hy, color, min(20, max(11, height * 0.44))))
                self._ribs.append((middle * 8 + 2, hy + height * 1.8, height * 2))
        self._redraw()

    def _redraw(self) -> None:
        self._image.fill((0, 0, 0, 0))
        for start, end, color in self._segments:
            ink = (227, 225, 208) if self._style == "Skelett" else color
            pygame.draw.line(self._image, (*ink, 224), start, end, 10)
        for point, color in self._caps:
            ink = (227, 225, 208) if self._style == "Skelett" else color
            pygame.draw.circle(self._image, (*ink, 224), point, 5)
        for hx, hy, color, radius in self._heads:
            center = round(hx * 2), round(hy * 2)
            radius *= 2
            ink = (227, 225, 208) if self._style == "Skelett" else color
            pygame.draw.circle(self._image, (9, 19, 33, 255), center, round(radius))
            pygame.draw.circle(self._image, (*ink, 235), center, round(radius), 7)
            if self._style == "Skelett":
                for shift in (-10, 10):
                    pygame.draw.circle(self._image, (*ink, 205),
                                       (center[0] + shift, center[1]), 4)
        if self._style == "Skelett":
            for x, y, height in self._ribs:
                for rib in range(3):
                    width = max(14, height * (0.48 - rib * 0.06))
                    rect = pygame.Rect((x - width / 2) * 2, (y + rib * 9) * 2,
                                       width * 2, 24)
                    pygame.draw.arc(self._image, (211, 219, 211, 190), rect,
                                    np.pi, np.pi * 2, 4)
        pygame.transform.smoothscale(self._image, self._scaled.get_size(), self._scaled)

    def draw(self, canvas: pygame.Surface) -> None:
        canvas.blit(self._background, (0, 0))
        canvas.blit(self._scaled, (self._field.x, self._field.y))
