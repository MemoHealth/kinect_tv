import numpy as np
import pygame
from numpy.typing import NDArray

from ..config import SCENE_SIZE
from ..coordinates import Viewport
from ..interaction.color_slots import ColorSlots
from ..interaction.scene_switch import PORTAL_POSITIONS, PORTAL_RADIUS
from ..simulation.coral_garden import CoralGarden
from .corals import CoralArt
from .outline import boundary


class LivingAquarium:
    def __init__(self, field: Viewport, shape: tuple[int, int]) -> None:
        self._field, self._shape = field, shape
        self._rng = np.random.default_rng(409)
        self._time = 0.0
        self._previous: NDArray[np.bool_] | None = None
        self._slot_shape = (shape[0] // 2, shape[1] // 2)
        self._slots = ColorSlots(self._slot_shape)
        self.targets = np.empty((0, 2))
        self._target_owners = np.empty(0, dtype=np.uint8)
        self.garden = CoralGarden()
        self._coral_art = CoralArt()
        self._food: list[tuple[int, tuple[float, float]]] = []
        self._edges = np.empty((0, 2))
        self.position = self._rng.uniform((35, 90), (1245, 570), (29, 2))
        self.velocity = self._rng.uniform((-24, -9), (24, 9), (29, 2))
        self._home = self.position.copy()
        self._background = self._seabed()
        self._fish = self._fish_sprites()
        self._jellies = self._jelly_sprites()
        self._bubbles = self._rng.uniform((0, 0), SCENE_SIZE, (31, 2))
        self.configure("Normalt")

    def configure(self, intensity: str) -> None:
        self._motion, self._pearl_limit, self._bubble_count = {
            "Milt": (0.7, 18, 16), "Normalt": (1.0, 30, 24),
            "Livligt": (1.1, 36, 31),
        }[intensity]

    def _seabed(self) -> pygame.Surface:
        width, height = SCENE_SIZE
        canvas = pygame.Surface(SCENE_SIZE, depth=32)
        for y in range(height):
            fraction = y / height
            color = (round(8 - 4 * fraction), round(39 - 21 * fraction),
                     round(60 - 26 * fraction))
            pygame.draw.line(canvas, color, (0, y), (width, y))
        rays = pygame.Surface(SCENE_SIZE, pygame.SRCALPHA)
        for x in (180, 560, 980):
            pygame.draw.polygon(
                rays, (69, 144, 161, 12), ((x, 0), (x + 50, 0), (x + 330, height),
                                         (x + 130, height))
            )
        canvas.blit(rays, (0, 0))
        for x in range(18, width, 44):
            sway = int(self._rng.integers(-10, 20))
            high = int(self._rng.integers(20, 78))
            points = [(x, height), (x + sway, height - high // 2),
                      (x + sway // 2, height - high)]
            pygame.draw.lines(canvas, (14, 66, 73), False, points, 3)
            pygame.draw.aalines(canvas, (26, 87, 88), False, points)
        return canvas

    @staticmethod
    def _fish_sprites() -> list[tuple[pygame.Surface, pygame.Surface]]:
        sprites = []
        for color in ((242, 173, 112), (92, 202, 210), (169, 159, 236)):
            fish = pygame.Surface((96, 50), pygame.SRCALPHA)
            pygame.draw.polygon(fish, (*color, 195), ((4, 8), (30, 24), (4, 42)))
            pygame.draw.ellipse(fish, (*color, 235), (18, 8, 68, 36))
            pygame.draw.polygon(fish, (*color, 155), ((40, 12), (52, 2), (61, 14)))
            pygame.draw.aalines(fish, (230, 235, 218, 130), False,
                               ((32, 16), (50, 10), (70, 14)))
            pygame.draw.circle(fish, (15, 38, 53), (70, 22), 4)
            pygame.draw.circle(fish, (231, 243, 241), (72, 20), 2)
            fish = pygame.transform.smoothscale(fish, (48, 25))
            sprites.append((pygame.transform.flip(fish, True, False), fish))
        return sprites

    @staticmethod
    def _jelly_sprites() -> list[pygame.Surface]:
        sprites = []
        for phase in np.linspace(0, np.pi * 2, 12, endpoint=False):
            image = pygame.Surface((66, 87), pygame.SRCALPHA)
            pygame.draw.ellipse(image, (167, 151, 235, 35), (2, 0, 62, 52))
            pygame.draw.ellipse(image, (177, 177, 240, 85), (7, 4, 52, 40))
            pygame.draw.arc(image, (202, 210, 255, 180), (7, 4, 52, 43), 0, np.pi, 2)
            for i, x in enumerate((16, 24, 33, 42, 50)):
                points = [(x + int(4 * np.sin(phase + y / 15 + i)), y)
                          for y in range(36, 81, 5)]
                pygame.draw.aalines(image, (175, 191, 234, 130), False, points)
            sprites.append(image)
        return sprites

    def _screen_points(self, rows: NDArray, cols: NDArray) -> NDArray:
        return np.column_stack((
            self._field.x + (cols + 0.5) * self._field.width / self._shape[1],
            self._field.y + (rows + 0.5) * self._field.height / self._shape[0],
        ))

    def _find_targets(self, mask: NDArray[np.bool_]) -> None:
        pooled = mask.reshape(
            self._slot_shape[0], 2, self._slot_shape[1], 2
        ).any((1, 3))
        labels = self._slots.update(pooled, self._time)
        targets = []
        owners = []
        for label in np.unique(labels[labels != 0]):
            rows, cols = np.nonzero(labels == label)
            top = rows.min()
            upper = rows < top + (rows.max() - top) * 0.63
            upper_rows, upper_cols = rows[upper], cols[upper]
            if not upper_cols.size:
                continue
            for edge in (upper_cols.min(), upper_cols.max()):
                tip = abs(upper_cols - edge) <= 1
                targets.append((float(np.median(upper_rows[tip])) * 2 + 0.5,
                                float(edge) * 2 + 0.5))
                owners.append(label)
        if targets:
            rows, cols = np.array(targets).T
            self.targets = self._screen_points(rows, cols)
            self._target_owners = np.array(owners, dtype=np.uint8)
        else:
            self.targets = np.empty((0, 2))
            self._target_owners = np.empty(0, dtype=np.uint8)
        rows, cols = np.nonzero(boundary(mask))
        if rows.size:
            ids = np.linspace(0, rows.size - 1, min(180, rows.size), dtype=int)
            self._edges = self._screen_points(rows[ids], cols[ids])
        else:
            self._edges = np.empty((0, 2))

    def update(self, mask: NDArray[np.bool_], dt: float) -> None:
        dt = min(0.05, max(0, dt))
        self._time += dt
        if mask is not self._previous:
            self._find_targets(mask)
            self._previous = mask
        portals = np.array(PORTAL_POSITIONS) * (self._field.width, self._field.height)
        portals += (self._field.x, self._field.y)
        distance = np.linalg.norm(
            self.targets[:, None, :] - portals[None, :, :], axis=2
        )
        usable = (distance > self._field.height * PORTAL_RADIUS).all(axis=1)
        self.garden.update(self.position[:24], self.targets[usable],
                           self._target_owners[usable], dt)
        phase = self._time * 0.45 + np.arange(29)
        desired = np.column_stack((np.cos(phase) * 19, np.sin(phase * 0.7) * 10))
        desired += (self._home - self.position) * 0.025
        for school in range(3):
            if self.garden.active[school]:
                ids = np.arange(school * 8, school * 8 + 8)
                vector = self.garden.lures[school] - self.position[ids]
                distance = np.linalg.norm(vector, axis=1)
                reach = np.clip((400 - distance) / 160, 0, 1)
                desired[ids] += vector * reach[:, None] * 0.30
        couriers = np.flatnonzero(self.garden.destination >= 0)
        desired[couriers] = (self.garden.corals[self.garden.destination[couriers]]
                             - self.position[couriers]) * 1.2
        # Keep a school readable instead of stacking all fish on the same lure.
        separation = self.position[:24, None, :] - self.position[None, :24, :]
        distances = np.linalg.norm(separation, axis=2)
        np.fill_diagonal(distances, np.inf)
        weight = np.clip(1 - distances / 42, 0, 1)
        force = (separation / np.maximum(distances[:, :, None], 1)
                 * weight[:, :, None]).sum(axis=1) * 45
        strength = np.linalg.norm(force, axis=1)
        force *= np.minimum(1, 60 / np.maximum(strength, 1))[:, None]
        desired[:24] += force
        if self._edges.size:
            delta = self.position[:, None, :] - self._edges[None, :, :]
            distances = np.linalg.norm(delta, axis=2)
            nearest = distances.argmin(axis=1)
            vector = delta[np.arange(29), nearest]
            distance = distances[np.arange(29), nearest]
            radius = np.r_[np.full(24, 37), np.full(5, 135)]
            force = np.clip(radius - distance, 0, None) * 1.8
            rows = ((self.position[:, 1] - self._field.y)
                    * self._shape[0] / self._field.height).astype(int)
            cols = ((self.position[:, 0] - self._field.x)
                    * self._shape[1] / self._field.width).astype(int)
            inside = mask[np.clip(rows, 0, self._shape[0] - 1),
                          np.clip(cols, 0, self._shape[1] - 1)]
            inside &= (rows >= 0) & (rows < self._shape[0])
            inside &= (cols >= 0) & (cols < self._shape[1])
            vector[inside] *= -1
            desired += vector / np.maximum(1, distance[:, None]) * force[:, None]
        speed = np.linalg.norm(desired, axis=1)
        limits = np.r_[np.full(24, 65), np.full(5, 32)]
        limits[couriers] = 95
        desired *= np.minimum(1, limits / np.maximum(speed, 1))[:, None]
        desired *= self._motion
        self.velocity += (desired - self.velocity) * (1 - np.exp(-dt / 0.7))
        self.position += self.velocity * dt
        for axis, (low, high) in enumerate(((24, 1256), (50, 645))):
            hit = (self.position[:, axis] < low) | (self.position[:, axis] > high)
            self.velocity[hit, axis] *= -0.7
            self.position[:, axis] = np.clip(self.position[:, axis], low, high)
        self._bubbles[:, 1] = (self._bubbles[:, 1] - dt * 13) % SCENE_SIZE[1]
        self.garden.arrive(self.position[:24])
        self._food = []
        for school in range(3):
            if self.garden.active[school] and self.garden.gather[school] > 0:
                for pearl in range(4):
                    angle = self._time * 0.8 + pearl * np.pi / 2
                    point = self.garden.lures[school] + (np.cos(angle) * 17,
                                                         np.sin(angle) * 12)
                    self._food.append((school, tuple(point)))
            ids = np.arange(school * 8, school * 8 + 8)
            for coral in np.unique(self.garden.destination[ids]):
                if coral < 0:
                    continue
                first = ids[self.garden.destination[ids] == coral][0]
                start = self.garden.launch[first]
                for pearl in range(3):
                    fraction = (self._time * 0.12 + pearl / 3) % 1
                    point = start + (self.garden.corals[coral] - start) * fraction
                    self._food.append((school, tuple(point)))
        self._food = self._food[:self._pearl_limit]

    def draw(self, canvas: pygame.Surface) -> None:
        canvas.blit(self._background, (0, 0))
        self._coral_art.draw(canvas, self.garden)
        for x, y in self._bubbles[:self._bubble_count]:
            pygame.draw.circle(canvas, (33, 75, 91), (int(x), int(y)), 2, 1)
        for i, (x, y) in enumerate(self.position[:24]):
            sprite = self._fish[i // 8][int(self.velocity[i, 0] >= 0)]
            canvas.blit(sprite, (int(x) - 24, int(y) - 12))
        for i, (x, y) in enumerate(self.position[24:]):
            sprite = self._jellies[int(self._time * 5 + i * 2) % len(self._jellies)]
            canvas.blit(sprite, (int(x) - 33, int(y) - 28))
        canvas.fblits([(self._coral_art.pearls[color], (round(x) - 6, round(y) - 6))
                       for color, (x, y) in self._food])
