from dataclasses import dataclass

import numpy as np
import pygame
from numpy.typing import NDArray


@dataclass
class Slot:
    center: tuple[int, int]
    seen: float


class ColorSlots:
    """Transient positions for three colors on visible, connected silhouettes."""

    def __init__(self, shape: tuple[int, int]) -> None:
        self._surface = pygame.Surface(shape[::-1], pygame.SRCALPHA)
        self._slots: dict[int, Slot] = {}
        self._labels = np.zeros(shape, dtype=np.uint8)
        self._previous: NDArray[np.bool_] | None = None

    def update(self, mask: NDArray[np.bool_], time: float) -> NDArray[np.uint8]:
        if mask is self._previous:
            return self._labels
        self._previous = mask
        self._slots = {
            index: slot for index, slot in self._slots.items()
            if time - slot.seen <= 0.55
        }
        self._labels.fill(0)
        alpha = pygame.surfarray.pixels_alpha(self._surface)
        alpha[:] = mask.T * np.uint8(255)
        del alpha
        components = pygame.mask.from_surface(self._surface).connected_components(24)
        components.sort(key=lambda component: component.count(), reverse=True)
        bodies: list[tuple[tuple[int, int], pygame.Mask, pygame.Rect]] = []
        fragments: list[tuple[pygame.Mask, pygame.Mask]] = []
        for component in components[:9]:
            center = component.centroid()
            rect = component.get_bounding_rects()[0]
            owner = next(
                (body for _, body, bounds in bodies
                 if rect.height * 2 < bounds.height
                 and bounds.left <= center[0] < bounds.right
                 and bounds.inflate(0, 20).colliderect(rect)),
                None,
            )
            if owner is not None:
                fragments.append((owner, component))
            elif len(bodies) < 3:
                bodies.append((center, component, rect))
        regions = sorted(
            ((center, body) for center, body, _ in bodies),
            key=lambda region: region[0][0],
        )

        groups: dict[int, list[int]] = {}
        reserved: set[int] = set()
        for region, (_, component) in enumerate(regions):
            inside = [
                index for index, slot in self._slots.items()
                if index not in reserved and component.get_at(slot.center)
            ]
            if len(inside) > 1:
                groups[region] = inside
                reserved.update(inside)
                for index in inside:
                    self._slots[index].seen = time

        distances = sorted(
            (abs(x - slot.center[0]) + abs(y - slot.center[1]), region, index)
            for region, ((x, y), _) in enumerate(regions) if region not in groups
            for index, slot in self._slots.items() if index not in reserved
        )
        for distance, region, index in distances:
            if distance <= mask.shape[1] * 0.22 and region not in groups:
                if index not in reserved:
                    groups[region] = [index]
                    reserved.add(index)
        for region, (center, component) in enumerate(regions):
            if region not in groups:
                free = set(range(3)) - reserved
                if not free:
                    continue
                index = min(free, key=lambda key: (key in self._slots, key))
                groups[region] = [index]
                reserved.add(index)
            indices = groups[region]
            if len(indices) == 1:
                self._slots[indices[0]] = Slot(center, time)
            color_mask = component.copy()
            for owner, fragment in fragments:
                if owner is component:
                    color_mask.draw(fragment, (0, 0))
            color_mask.to_surface(
                self._surface, setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0)
            )
            alpha = pygame.surfarray.pixels_alpha(self._surface)
            self._labels[alpha.T != 0] = sum(1 << index for index in indices)
            del alpha
        return self._labels
