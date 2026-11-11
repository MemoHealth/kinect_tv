from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

import numpy as np
import pygame
from numpy.typing import NDArray

from ..config import SCENE_SIZE
from ..coordinates import Viewport
from ..interaction.color_slots import ColorSlots
from ..settings import HALF_LIVES, PALETTES
from .lightpaint import LightPaint
from .outline import boundary
from .sparks import Sparks


class PaintExplosion:
    def __init__(self, field: Viewport, shape: tuple[int, int]) -> None:
        self._field = field
        self._trail = LightPaint(field, shape)
        self._slots = ColorSlots(shape)
        self._sparks = Sparks(240, seed=73)
        self._art = pygame.Surface(SCENE_SIZE, depth=32)
        self._previous = np.zeros(shape, dtype=bool)
        self._time = 0.0
        self._half_life = 3.0
        self._palette_name = ""
        self.configure("Normal", "Norrsken")

    def configure(self, fade: str, palette: str) -> None:
        self._half_life = HALF_LIVES[fade]
        if palette == self._palette_name:
            return
        self._palette_name = palette
        colors = np.array(PALETTES[palette], dtype=np.float32)
        mixes = [colors[0]]
        for bits in range(1, 8):
            group = [bool(bits & (1 << index)) for index in range(3)]
            mixes.append(colors[group].mean(0))
        self._colors = np.array(mixes, dtype=np.float32) / 255
        self._sparks.palette(tuple(tuple(map(int, color)) for color in mixes))

    def update(self, mask: NDArray[np.bool_], dt: float) -> None:
        self._time += dt
        labels = self._slots.update(mask, self._time)
        self._trail.update(
            mask, dt, half_life=self._half_life, labels=labels, palette=self._colors
        )
        if mask is not self._previous:
            if self._previous.any():
                rows, cols = np.nonzero(boundary(mask) & ~self._previous)
                count = min(22, rows.size // 6)
                if count:
                    sample = np.linspace(0, rows.size - 1, count, dtype=int)
                    x, y = cols[sample], rows[sample]
                    self._sparks.emit(
                        self._field.x + (x + 0.5) * self._field.width / mask.shape[1],
                        self._field.y + (y + 0.5) * self._field.height / mask.shape[0],
                        labels[y, x],
                        24 + count * 3.5,
                        life=0.8,
                    )
            self._previous = mask
        self._sparks.update(dt, gravity=22)

    def draw(self, canvas: pygame.Surface) -> None:
        self._render()
        canvas.blit(self._art, (0, 0))

    def _render(self) -> None:
        self._art.fill((10, 8, 23))
        self._trail.draw(self._art)
        self._sparks.draw(self._art)

    def save(self, folder: Path) -> Path:
        self._render()
        folder.mkdir(parents=True, exist_ok=True)
        prefix = f"Paint-{datetime.now():%Y-%m-%d}-"
        with NamedTemporaryFile(
            dir=folder, prefix=prefix, suffix=".png", delete=False
        ) as file:
            path = Path(file.name)
        try:
            pygame.image.save(self._art, path)
        except (OSError, pygame.error):
            path.unlink(missing_ok=True)
            raise
        return path
