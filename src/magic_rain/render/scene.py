import numpy as np
import pygame

from ..config import SCENE_SIZE
from ..simulation.rain import DemoRain

RAIN_COLORS = ((33, 61, 88), (42, 85, 113), (56, 112, 140), (99, 130, 174))
GLOW_COLOR = (114, 210, 223)
SNOW_COLORS = ((83, 116, 147), (132, 171, 200), (179, 204, 224), (204, 220, 240))


class Scene:
    def __init__(self) -> None:
        width, height = SCENE_SIZE
        x = np.linspace(0, 1, 320)[:, None]
        y = np.linspace(0, 1, 180)[None, :]
        mist = np.exp(-((x - 0.53) / 0.56) ** 2 - ((y - 0.45) / 0.65) ** 2)
        violet = np.exp(-((x - 0.84) / 0.42) ** 2 - ((y - 0.75) / 0.44) ** 2)
        sky = (
            np.array((5, 10, 24))
            + mist[:, :, None] * np.array((4, 16, 24))
            + violet[:, :, None] * np.array((12, 4, 20))
        )
        base = pygame.surfarray.make_surface(sky.astype(np.uint8))
        self.background = pygame.transform.smoothscale(base, (width, height)).convert()
        winter = (
            np.array((9, 16, 31))
            + mist[:, :, None] * np.array((15, 33, 49))
            + violet[:, :, None] * np.array((5, 11, 20))
        )
        base = pygame.surfarray.make_surface(winter.astype(np.uint8))
        self.winter = pygame.transform.smoothscale(base, (width, height)).convert()
        self.canvas = self.background.copy()
        self.glow = pygame.Surface((13, 13), pygame.SRCALPHA)
        for radius, alpha in ((6, 12), (4, 22), (2, 46)):
            pygame.draw.circle(self.glow, (*GLOW_COLOR, alpha), (6, 6), radius)

    def draw(
        self, rain: DemoRain, strength: float = 0.0, intensity: float = 1.0
    ) -> pygame.Surface:
        self.canvas.blit(self.winter if rain.snow else self.background, (0, 0))
        for index, (x, y, speed, slide, shimmer) in enumerate(
            zip(rain.x, rain.y, rain.speed, rain.slide, rain.shimmer, strict=True)
        ):
            if intensity < 0.9 and index % 2:
                continue
            if rain.snow:
                color = SNOW_COLORS[index % len(SNOW_COLORS)]
                radius = 1 + int(speed > 60) + int(shimmer > 0.3)
                pygame.draw.circle(self.canvas, color, (round(x), round(y)), radius)
                continue
            length = speed * (0.055 + 0.012 * strength) * intensity
            color = RAIN_COLORS[index % len(RAIN_COLORS)]
            if shimmer > 0.04:
                color = tuple(
                    round(base + (glow - base) * shimmer)
                    for base, glow in zip(color, GLOW_COLOR, strict=True)
                )
            pygame.draw.aaline(
                self.canvas, color, (x - 0.045 * slide - 1, y - length), (x, y)
            )
            if shimmer > 0.15:
                self.glow.set_alpha(round(190 * shimmer * intensity))
                self.canvas.blit(self.glow, (round(x) - 6, round(y) - 6))
        return self.canvas
