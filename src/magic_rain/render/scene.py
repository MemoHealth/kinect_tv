import numpy as np
import pygame

from ..config import SCENE_SIZE
from ..simulation.rain import DemoRain

RAIN_LAYERS = (
    (0.78, (19, 25, 43), (38, 61, 87), (56, 77, 110)),
    (1.0, (22, 39, 63), (60, 106, 143), (89, 148, 178)),
    (1.18, (27, 51, 75), (83, 151, 175), (152, 209, 224)),
)
GLOW_COLOR = (146, 227, 231)
SNOW_COLORS = ((83, 116, 147), (132, 171, 200), (179, 204, 224), (204, 220, 240))
STREAK_LENGTHS = tuple(range(4, 49, 4))


def _streak(length: int, tail: tuple, body: tuple, tip: tuple) -> pygame.Surface:
    sprite = pygame.Surface((4, length + 1), pygame.SRCALPHA)
    mid = (1.55, length * 0.55)
    pygame.draw.aaline(sprite, tail, (1, 0), mid)
    pygame.draw.aaline(sprite, body, mid, (2, length))
    pygame.draw.aaline(sprite, tip, (1.87, length * 0.87), (2, length))
    return sprite


class Scene:
    def __init__(self) -> None:
        width, height = SCENE_SIZE
        x = np.linspace(0, 1, 320)[:, None]
        y = np.linspace(0, 1, 180)[None, :]
        mist = np.exp(-((x - 0.53) / 0.56) ** 2 - ((y - 0.45) / 0.65) ** 2)
        violet = np.exp(-((x - 0.84) / 0.42) ** 2 - ((y - 0.75) / 0.44) ** 2)
        ground = np.exp(-((x - 0.52) / 0.68) ** 2 - ((y - 0.86) / 0.13) ** 2)
        sky = (
            np.array((5, 10, 24))
            + mist[:, :, None] * np.array((4, 16, 24))
            + violet[:, :, None] * np.array((12, 4, 20))
            + ground[:, :, None] * np.array((3, 10, 13))
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
        palettes = [layer[1:] for layer in RAIN_LAYERS]
        palettes.append((*palettes[-1][:2], (162, 153, 126)))
        self.streaks = [
            [_streak(length, *colors) for length in STREAK_LENGTHS]
            for colors in palettes
        ]
        self.glow = pygame.Surface((13, 13), pygame.SRCALPHA)
        for radius, alpha in ((6, 12), (4, 22), (2, 46)):
            pygame.draw.circle(self.glow, (*GLOW_COLOR, alpha), (6, 6), radius)

    def draw(
        self,
        rain: DemoRain,
        strength: float = 0.0,
        intensity: float = 1.0,
    ) -> pygame.Surface:
        background = self.winter if rain.snow else self.background
        self.canvas.blit(background, (0, 0))
        if not rain.snow:
            self._draw_rain(rain, strength, intensity)
            return self.canvas
        for index, (x, y, speed, shimmer) in enumerate(
            zip(rain.x, rain.y, rain.speed, rain.shimmer, strict=True)
        ):
            if intensity < 0.9 and index % 2:
                continue
            color = SNOW_COLORS[index % len(SNOW_COLORS)]
            radius = 1 + int(speed > 60) + int(shimmer > 0.3)
            pygame.draw.circle(self.canvas, color, (round(x), round(y)), radius)
        return self.canvas

    def _draw_rain(self, rain: DemoRain, strength: float, intensity: float) -> None:
        streaks = []
        contacts = []
        for index, (x, y, speed, slide, shimmer, band) in enumerate(
            zip(
                rain.x, rain.y, rain.speed, rain.slide, rain.shimmer,
                rain.depth_band, strict=True,
            )
        ):
            if intensity < 0.9 and index % 2:
                continue
            if y < 0:
                continue
            length_scale, tail, body, tip = RAIN_LAYERS[band]
            length = speed * (0.055 + 0.012 * strength) * length_scale * intensity
            if shimmer <= 0.18:
                palette = 3 if band == 2 and index % 19 == 0 else band
                slot = min(len(STREAK_LENGTHS) - 1, max(0, int(length / 4 - 0.5)))
                sprite = self.streaks[palette][slot]
                position = (int(x + 0.5) - 2, int(y + 0.5) - STREAK_LENGTHS[slot])
                streaks.append((sprite, position))
                continue
            contacts.append((x, y, length, slide, shimmer, tail, body, tip))
        self.canvas.fblits(streaks)

        for x, y, length, slide, shimmer, tail, body, tip in contacts:
            slant = 0.045 * slide + 1
            midpoint = (x - 0.45 * slant, y - 0.45 * length)
            endpoint = (x, y)
            pygame.draw.aaline(self.canvas, tail, (x - slant, y - length), midpoint)
            pygame.draw.aaline(self.canvas, body, midpoint, endpoint)
            tip = tuple(
                round(base + (glow - base) * shimmer)
                for base, glow in zip(tip, GLOW_COLOR, strict=True)
            )
            highlight = (x - 0.13 * slant, y - 0.13 * length)
            pygame.draw.aaline(self.canvas, tip, highlight, endpoint)
            if shimmer > 0.15:
                self.glow.set_alpha(round(190 * shimmer * intensity))
                self.canvas.blit(self.glow, (round(x) - 6, round(y) - 6))
