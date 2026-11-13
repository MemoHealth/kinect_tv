import numpy as np
from numpy.typing import NDArray

from ..settings import MIRROR_SCENE, OPTIONS
from .color_slots import ColorSlots

HOLD_S = 1.8


def cycle_scene(current: str, direction: int, *, mirror_allowed: bool = False) -> str:
    scenes = [name for name in OPTIONS["scene"]
              if mirror_allowed or name != MIRROR_SCENE]
    index = scenes.index(current) if current in scenes else 0
    return scenes[(index + direction) % len(scenes)]


class BodySwitch:
    """Deliberate upper-contour dwell, never anatomical hand recognition."""

    def __init__(self, shape: tuple[int, int]) -> None:
        self.centres = np.array(((0.16, 0.32), (0.84, 0.32))) * shape[::-1]
        self.radius = shape[0] * 0.075
        self._stability_radius = shape[0] * 0.045
        self._shape = shape
        self._factor = 2 if shape[0] % 2 == shape[1] % 2 == 0 else 1
        self._analysis_shape = tuple(size // self._factor for size in shape)
        self._slots = ColorSlots(self._analysis_shape)
        self._time = 0.0
        self._fresh = -1.0
        self._previous: NDArray[np.bool_] | None = None
        self._tips: list[tuple[int, NDArray]] = []
        self._present = False
        self._armed = False
        self._release = 0.0
        self._cooldown = 0.0
        self._held: tuple[int, int] | None = None
        self._anchor = np.zeros(2)
        self._dwell = 0.0
        self._lost = 0.0
        self.visible = False
        self.side = 0

    @property
    def progress(self) -> float:
        return min(1.0, self._dwell / HOLD_S)

    def _find_tips(self, mask: NDArray[np.bool_]) -> None:
        if self._factor == 2:
            mask = mask.reshape(
                self._analysis_shape[0], 2, self._analysis_shape[1], 2
            ).any(axis=(1, 3))
        labels = self._slots.update(mask, self._time)
        self._tips = []
        self._present = False
        for label in np.unique(labels[labels != 0]):
            if int(label).bit_count() != 1:
                continue
            rows, cols = np.nonzero(labels == label)
            height = rows.max() - rows.min()
            if height < self._analysis_shape[0] * 0.22 or rows.size < mask.size * 0.002:
                continue
            self._present = True
            torso = (rows > rows.min() + height * 0.45) & (
                rows < rows.min() + height * 0.78
            )
            if not torso.any():
                continue
            centre = np.median(cols[torso])
            torso_left, torso_right = cols[torso].min(), cols[torso].max()
            upper = rows < rows.min() + height * 0.6
            y, x = rows[upper], cols[upper]
            if not x.size:
                continue
            for edge in (x.min(), x.max()):
                extension = max(torso_left - edge, edge - torso_right)
                if extension < 4 / self._factor:
                    continue
                if abs(edge - centre) < max(10 / self._factor, height * 0.16):
                    continue
                tip = np.array((float(edge), float(np.median(y[abs(x - edge) <= 2]))))
                self._tips.append((int(label), (tip + 0.5) * self._factor - 0.5))

    def _clear_hold(self) -> None:
        self._held = None
        self._dwell = self._lost = 0.0

    def update(
        self, mask: NDArray[np.bool_], dt: float, *, enabled: bool = True,
    ) -> int:
        dt = min(0.05, max(0, dt))
        self._time += dt
        if mask is not self._previous:
            self._previous = mask
            self._fresh = self._time
            self._find_tips(mask)
        self.visible = enabled and self._present and self._time - self._fresh <= 0.12
        if not enabled or self._time - self._fresh > 0.12:
            self._armed = False
            self._release = 0.0
            self._clear_hold()
            return 0
        hits = [(owner, side, tip) for owner, tip in self._tips
                for side, centre in enumerate(self.centres)
                if np.linalg.norm(tip - centre) <= self.radius]
        if not hits:
            self._release += dt
            if self._release >= 0.4:
                self._armed = True
            self._lost += dt
            if self._lost > 0.1:
                self._clear_hold()
            return 0
        self._release = 0.0
        if len(hits) != 1 or not self._armed or self._time < self._cooldown:
            self._clear_hold()
            return 0
        owner, side, tip = hits[0]
        key = owner, side
        moved = np.linalg.norm(tip - self._anchor) > self._stability_radius
        if key != self._held or moved:
            self._held, self._anchor = key, tip.copy()
            self._dwell = 0.0
        else:
            self._dwell += dt
        self._lost = 0.0
        self.side = side
        if self.progress >= 1:
            self._clear_hold()
            self._armed = False
            self._cooldown = self._time + 1.2
            return -1 if side == 0 else 1
        return 0
