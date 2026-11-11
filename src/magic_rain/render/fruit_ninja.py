from dataclasses import dataclass

import numpy as np
import pygame
from numpy.typing import NDArray

from ..config import SCENE_SIZE
from ..coordinates import Viewport
from .sparks import Sparks

FRUIT_COLORS = ((245, 145, 125), (244, 193, 98), (143, 218, 168))


@dataclass
class Fruit:
    x: float
    y: float
    vx: float
    vy: float
    color: int


@dataclass
class Half:
    x: float
    y: float
    vx: float
    vy: float
    color: int
    side: int
    life: float = 1.5


class FruitNinja:
    def __init__(self, field: Viewport, shape: tuple[int, int]) -> None:
        self._field, self._shape = field, shape
        self._rng = np.random.default_rng(180)
        self._previous = np.zeros(shape, dtype=bool)
        self._motion = np.zeros(shape, dtype=bool)
        self._motion_age = 1.0
        self._next_fruit = 0.3
        self.fruits: list[Fruit] = []
        self.halves: list[Half] = []
        self._juice = Sparks(120, seed=872)
        self._juice.palette(FRUIT_COLORS)
        self._sprites, self._pieces = self._fruit_sprites()
        self._background = self._sky()

    @staticmethod
    def _sky() -> pygame.Surface:
        canvas = pygame.Surface(SCENE_SIZE, depth=32)
        for y in range(SCENE_SIZE[1]):
            glow = np.exp(-((y - 500) / 260) ** 2)
            color = (round(9 + glow * 13), round(13 + glow * 12), round(25 + glow * 12))
            pygame.draw.line(canvas, color, (0, y), (SCENE_SIZE[0], y))
        return canvas

    @staticmethod
    def _fruit_sprites() -> tuple[list[pygame.Surface], list[list[pygame.Surface]]]:
        sprites = []
        pieces = []
        for color in FRUIT_COLORS:
            image = pygame.Surface((144, 144), pygame.SRCALPHA)
            pygame.draw.circle(image, (*color, 255), (72, 78), 51)
            dark = tuple(round(channel * 0.72) for channel in color)
            pygame.draw.arc(image, (*dark, 170), (21, 27, 102, 102), 3.4, 6, 9)
            light = tuple(min(255, channel + 30) for channel in color)
            pygame.draw.ellipse(image, (*light, 150), (39, 43, 25, 38))
            pygame.draw.line(image, (112, 140, 119), (72, 29), (76, 15), 6)
            pygame.draw.ellipse(image, (103, 177, 131), (78, 14, 25, 12))
            sprite = pygame.transform.smoothscale(image, (60, 60))
            sprites.append(sprite)
            halves = []
            for side in (0, 1):
                half = sprite.copy()
                blank = pygame.Rect(30 if side == 0 else 0, 0, 30, 60)
                half.fill((0, 0, 0, 0), blank)
                halves.append(pygame.transform.rotate(half, 15 if side == 0 else -15))
            pieces.append(halves)
        return sprites, pieces

    def _moving_hit(self, fruit: Fruit, previous: tuple[float, float]) -> bool:
        if self._motion_age > 0.12:
            return False
        scale_x = self._shape[1] / self._field.width
        scale_y = self._shape[0] / self._field.height
        x0 = max(0, int((min(fruit.x, previous[0]) - 29 - self._field.x) * scale_x))
        x1 = min(self._shape[1],
                 int((max(fruit.x, previous[0]) + 29 - self._field.x) * scale_x) + 1)
        y0 = max(0, int((min(fruit.y, previous[1]) - 29 - self._field.y) * scale_y))
        y1 = min(self._shape[0],
                 int((max(fruit.y, previous[1]) + 29 - self._field.y) * scale_y) + 1)
        if x1 <= x0 or y1 <= y0:
            return False
        rows, cols = np.nonzero(self._motion[y0:y1, x0:x1])
        if not rows.size:
            return False
        x = self._field.x + (cols + x0 + 0.5) / scale_x
        y = self._field.y + (rows + y0 + 0.5) / scale_y
        dx, dy = fruit.x - previous[0], fruit.y - previous[1]
        projected = (x - previous[0]) * dx + (y - previous[1]) * dy
        fraction = np.clip(projected / max(dx * dx + dy * dy, 1), 0, 1)
        distance = (x - previous[0] - fraction * dx) ** 2
        distance += (y - previous[1] - fraction * dy) ** 2
        return bool((distance <= 29 ** 2).any())

    def _split(self, fruit: Fruit) -> None:
        for side in (0, 1):
            self.halves.append(Half(
                fruit.x, fruit.y, fruit.vx + (-70 if side == 0 else 70),
                min(-35, fruit.vy * 0.3), fruit.color, side,
            ))
        self.halves = self.halves[-14:]
        self._juice.emit(
            np.full(12, fruit.x), np.full(12, fruit.y),
            np.full(12, fruit.color, dtype=np.uint8), 95, life=0.7,
        )

    def update(self, mask: NDArray[np.bool_], dt: float) -> None:
        self._motion_age += dt
        if mask is not self._previous:
            self._motion = mask & ~self._previous
            self._motion_age = 0
            self._previous = mask
        self._next_fruit -= dt
        if self._next_fruit <= 0:
            self._next_fruit = float(self._rng.uniform(0.65, 1.05))
            if len(self.fruits) < 7:
                self.fruits.append(Fruit(
                    float(self._rng.uniform(self._field.x + 70,
                                            self._field.x + self._field.width - 70)),
                    770, float(self._rng.uniform(-38, 38)),
                    float(self._rng.uniform(-530, -420)), int(self._rng.integers(3)),
                ))
        remaining = []
        for fruit in self.fruits:
            previous = fruit.x, fruit.y
            fruit.vy += 240 * dt
            fruit.x += fruit.vx * dt
            fruit.y += fruit.vy * dt
            if self._moving_hit(fruit, previous):
                self._split(fruit)
            elif fruit.y < 815:
                remaining.append(fruit)
        self.fruits = remaining
        for half in self.halves:
            half.vy += 220 * dt
            half.x += half.vx * dt
            half.y += half.vy * dt
            half.life -= dt
        self.halves = [half for half in self.halves if half.life > 0]
        self._juice.update(dt, gravity=45)

    def draw(self, canvas: pygame.Surface) -> None:
        canvas.blit(self._background, (0, 0))
        for fruit in self.fruits:
            canvas.blit(
                self._sprites[fruit.color], (round(fruit.x) - 30, round(fruit.y) - 30)
            )
        for half in self.halves:
            sprite = self._pieces[half.color][half.side]
            sprite.set_alpha(round(235 * min(1, half.life * 2)))
            canvas.blit(sprite, (round(half.x) - sprite.get_width() // 2,
                                 round(half.y) - sprite.get_height() // 2))
        self._juice.draw(canvas)
