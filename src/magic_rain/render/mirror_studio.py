from collections import deque

import numpy as np
import pygame
from numpy.typing import NDArray

from ..coordinates import Viewport
from ..interaction.color_slots import ColorSlots
from ..settings import PALETTES
from .coverage import soften


class MirrorStudio:
    def __init__(self, field: Viewport, shape: tuple[int, int]) -> None:
        self._field = field
        self._shape = shape
        self._style = "Eko"
        self._time = 0.0
        self._next_sample = 0.0
        self._samples: deque[tuple[float, NDArray[np.uint8]]] = deque(maxlen=4)
        self._slots = ColorSlots(shape)
        self._rgb: NDArray[np.uint8] | None = None
        self._mirrored = True
        self._was_color = False
        self._small = pygame.Surface(shape[::-1], pygame.SRCALPHA)
        self._small.fill((0, 0, 0, 255))
        self._scaled = pygame.Surface((field.width, field.height), pygame.SRCALPHA)
        self._portrait = pygame.Surface(
            (field.width // 2, field.height // 2), pygame.SRCALPHA
        )
        self._aperture = pygame.Surface(self._portrait.get_size(), pygame.SRCALPHA)
        self._aperture.fill((255, 255, 255, 0))
        height, width = self._portrait.get_height(), self._portrait.get_width()
        y, x = np.indices((height, width), dtype=np.float32)
        distance = (
            abs((x + 0.5) * 2 / width - 1) ** 6
            + abs((y + 0.5) * 2 / height - 1) ** 6
        ) ** (1 / 6)
        alpha = pygame.surfarray.pixels_alpha(self._aperture)
        alpha[:] = (255 * np.clip((1 - distance.T) / 0.16, 0, 1)).astype(np.uint8)
        del alpha
        self._current = np.zeros((*shape, 3), dtype=np.uint8)
        self._last_mask: NDArray[np.bool_] | None = None
        self._last_rgb: NDArray[np.uint8] | None = None
        self._map = self._kaleidoscope_map(shape)

    @staticmethod
    def _kaleidoscope_map(shape: tuple[int, int]) -> tuple[NDArray, NDArray]:
        height, width = shape
        y, x = np.indices(shape, dtype=np.float32)
        x = (x - width / 2) / (width / 2)
        y = (y - height / 2) / (height / 2)
        radius = np.hypot(x, y)
        angle = np.arctan2(y, x)
        sector = np.pi / 3
        folded = abs((angle + sector / 2) % sector - sector / 2)
        cols = np.clip((0.5 + np.cos(folded) * radius * 0.43) * width, 0, width - 1)
        rows = np.clip((0.5 + np.sin(folded) * radius * 0.43) * height, 0, height - 1)
        return rows.astype(np.intp), cols.astype(np.intp)

    def configure(self, style: str) -> None:
        if self._style != style:
            self._style = style
            self._samples.clear()

    def set_color(self, rgb: NDArray[np.uint8] | None, *, mirrored: bool) -> None:
        if (rgb is not None) != self._was_color:
            self._samples.clear()
            self._was_color = rgb is not None
        if mirrored != self._mirrored:
            self._samples.clear()
            self._last_rgb = None
        self._rgb, self._mirrored = rgb, mirrored

    def update(self, mask: NDArray[np.bool_], dt: float) -> None:
        self._time += dt
        if self._rgb is not None:
            if self._rgb is not self._last_rgb:
                image = self._rgb[:, ::-1] if self._mirrored else self._rgb
                self._current = image.copy()
                self._last_rgb = self._rgb
        elif mask is not self._last_mask or self._last_rgb is not None:
            self._last_rgb = None
            labels = self._slots.update(mask, self._time)
            colors = np.array(PALETTES["Norrsken"])
            palette = np.zeros((8, 3), dtype=np.float32)
            for group in range(1, 8):
                selected = [bool(group & (1 << i)) for i in range(3)]
                palette[group] = colors[selected].mean(axis=0)
            self._current = np.maximum(palette[labels] * 0.92,
                                       soften(palette[labels])).astype(np.uint8)
            self._last_mask = mask
        if self._time >= self._next_sample:
            self._samples.append((self._time, self._current.copy()))
            self._next_sample = self._time + 0.14
        while self._samples and self._time - self._samples[0][0] > 0.6:
            self._samples.popleft()

    def draw(self, canvas: pygame.Surface) -> None:
        canvas.fill((7, 11, 25))
        if self._style == "Eko":
            image = self._current.copy()
            for time, sample in self._samples:
                weight = 0.62 * 2 ** (-(self._time - time) / 0.2)
                image = np.maximum(image, sample * weight)
            image = image.astype(np.uint8)
        else:
            image = self._current[self._map]
        pygame.surfarray.blit_array(self._small, image.swapaxes(0, 1))
        pygame.transform.smoothscale(self._small, self._scaled.get_size(), self._scaled)
        canvas.blit(self._scaled, (self._field.x, self._field.y))
        if self._style == "Kalejdoskop":
            pygame.surfarray.blit_array(self._small, self._current.swapaxes(0, 1))
            pygame.transform.smoothscale(
                self._small, self._portrait.get_size(), self._portrait
            )
            self._portrait.blit(
                self._aperture, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
            )
            x = self._field.x + self._field.width // 4
            y = self._field.y + self._field.height // 4
            canvas.blit(self._portrait, (x, y))
