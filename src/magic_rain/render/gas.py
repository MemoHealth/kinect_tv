import numpy as np
import pygame
from numpy.typing import NDArray

from ..config import SCENE_SIZE
from ..coordinates import Viewport
from ..simulation.gas import GasParticles


class StarGas:
    def __init__(self, field: Viewport, shape: tuple[int, int]) -> None:
        self.particles = GasParticles(field, shape)
        self._sprites = []
        colors = ((119, 194, 215), (150, 223, 229), (209, 226, 219), (255, 204, 139))
        for color in colors:
            sprite = pygame.Surface((17, 17), pygame.SRCALPHA)
            x, y = np.indices((17, 17))
            distance = (x - 8) ** 2 + (y - 8) ** 2
            alpha = pygame.surfarray.pixels_alpha(sprite)
            alpha[:] = np.rint(np.maximum(
                32 * np.exp(-distance / 15), 235 * np.exp(-distance / 2.5)
            )).astype(np.uint8)
            del alpha
            rgb = pygame.surfarray.pixels3d(sprite)
            rgb[:] = color
            del rgb
            self._sprites.append(sprite)
        self._backdrop = pygame.Surface(SCENE_SIZE)
        for y in range(SCENE_SIZE[1]):
            glow = np.exp(-((y / SCENE_SIZE[1] - 0.45) / 0.48) ** 2)
            pygame.draw.line(
                self._backdrop, (round(4 + 2 * glow), round(12 + 7 * glow),
                                 round(22 + 10 * glow)), (0, y), (SCENE_SIZE[0], y)
            )
        self.configure("Normalt")

    def configure(self, intensity: str) -> None:
        self._visible, self._tail_limit, brightness = {
            "Milt": (300, 48, 180),
            "Normalt": (600, 120, 230),
            "Livligt": (600, 200, 255),
        }[intensity]
        self._indices = np.linspace(
            0, len(self.particles.position) - 1, self._visible, dtype=int
        )
        for sprite in self._sprites:
            sprite.set_alpha(brightness)

    def update(self, mask: NDArray[np.bool_], dt: float) -> None:
        self.particles.step(mask, dt)

    def draw(self, canvas: pygame.Surface) -> None:
        canvas.blit(self._backdrop, (0, 0))
        gas = self.particles
        position = gas.position[self._indices]
        velocity = gas.velocity[self._indices]
        speed = np.linalg.norm(velocity, axis=1)
        bands = np.digitize(speed, (25, 75, 160))
        for index in np.flatnonzero(speed > 55)[:self._tail_limit]:
            point = position[index]
            tail = point - velocity[index] * min(0.045, 18 / speed[index])
            color = (101, 73, 43) if speed[index] > 160 else (31, 74, 88)
            pygame.draw.aaline(canvas, color, tail, point)
        points = (np.rint(position).astype(int) - 8).tolist()
        canvas.fblits([
            (self._sprites[band], point)
            for point, band in zip(points, bands.tolist(), strict=True)
        ])
