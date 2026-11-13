import numpy as np
import pygame

from ..config import SCENE_SIZE
from ..simulation.rain import DemoRain

RAIN_LAYERS = (
    (0.55, (27, 49, 66), (69, 111, 137), (103, 149, 172)),
    (0.85, (38, 72, 95), (113, 168, 192), (176, 211, 225)),
    (1.25, (58, 99, 118), (158, 206, 221), (226, 243, 247)),
)
GLOW_COLOR = (186, 237, 238)
SNOW_COLORS = ((83, 116, 147), (132, 171, 200), (179, 204, 224), (204, 220, 240))
STREAK_LENGTHS = tuple(range(4, 45, 4))
DROP_ANGLES = tuple(range(-64, 65, 16))


def _streak(length: int, tail: tuple, body: tuple, tip: tuple) -> pygame.Surface:
    sprite = pygame.Surface((6, length + 4), pygame.SRCALPHA)
    x, y = np.indices(sprite.get_size(), dtype=np.float32)
    progress = np.clip(y / length, 0, 1)
    width = 0.35 + progress * 0.5
    tail_alpha = np.exp(-((x - 2) / width) ** 2) * progress ** 1.7
    tail_alpha[y > length] = 0
    pearl = np.exp(-((x - 2) / 1.05) ** 2 - ((y - length) / 1.4) ** 2)
    colors = np.array(tail) + progress[:, :, None] * (np.array(body) - tail)
    highlight = np.clip((progress - 0.72) / 0.28, 0, 1)
    colors += highlight[:, :, None] * (np.array(tip) - body)
    pygame.surfarray.blit_array(sprite, np.clip(colors, 0, 255).astype(np.uint8))
    alpha = pygame.surfarray.pixels_alpha(sprite)
    alpha[:] = np.rint(np.maximum(tail_alpha * 0.82, pearl) * 255).astype(np.uint8)
    del alpha
    return sprite


def _orient(
    sprite: pygame.Surface, tip: tuple[float, float], angle: float
) -> tuple[pygame.Surface, tuple[float, float]]:
    rotated = pygame.transform.rotate(sprite, angle)
    radians = np.radians(angle)
    dx = tip[0] - (sprite.get_width() - 1) / 2
    dy = tip[1] - (sprite.get_height() - 1) / 2
    anchor = (
        (rotated.get_width() - 1) / 2 + dx * np.cos(radians) + dy * np.sin(radians),
        (rotated.get_height() - 1) / 2 - dx * np.sin(radians) + dy * np.cos(radians),
    )
    return rotated, anchor


class Scene:
    def __init__(self) -> None:
        width, height = SCENE_SIZE
        x = np.linspace(0, 1, 320)[:, None]
        y = np.linspace(0, 1, 180)[None, :]
        mist = np.exp(-((x - 0.53) / 0.56) ** 2 - ((y - 0.45) / 0.65) ** 2)
        violet = np.exp(-((x - 0.84) / 0.42) ** 2 - ((y - 0.75) / 0.44) ** 2)
        ground = np.exp(-((x - 0.52) / 0.68) ** 2 - ((y - 0.86) / 0.13) ** 2)
        sky = (
            np.array((4, 10, 20))
            + mist[:, :, None] * np.array((2, 8, 12))
            + ground[:, :, None] * np.array((5, 16, 19))
        )
        shaft = np.exp(-((x - 0.58 - y * 0.18) / 0.14) ** 2) * (1 - y * 0.7)
        moon = np.exp(-((x - 0.62) / 0.23) ** 2 - ((y + 0.12) / 0.38) ** 2)
        sky += shaft[:, :, None] * np.array((7, 14, 19))
        sky += moon[:, :, None] * np.array((13, 21, 26))
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
        palettes.append(((55, 64, 66), (149, 158, 146), (231, 218, 177)))
        self.streaks = []
        for band, colors in enumerate(palettes):
            lengths = []
            for length in STREAK_LENGTHS:
                source = _streak(length, *colors)
                angles = []
                for angle in DROP_ANGLES:
                    sprite, anchor = _orient(source, (2, length), angle)
                    sprite.set_alpha((105, 161, 212, 180)[band])
                    angles.append((sprite, anchor))
                lengths.append(angles)
            self.streaks.append(lengths)
        self._glows = [self._halo(23, 8 + level * 12) for level in range(3)]
        self._lens = pygame.transform.smoothscale(self._halo(45, 10), (24, 64))
        self._rings = []
        for index in range(24):
            phase = index / 24
            ring = pygame.Surface((144, 40), pygame.SRCALPHA)
            rect = pygame.Rect(0, 0, 12 + phase * 112, 3 + phase * 17)
            rect.center = 72, 20
            pygame.draw.ellipse(ring, (*GLOW_COLOR, round(66 * (1 - phase) ** 1.7)),
                                rect, 2)
            self._rings.append(pygame.transform.smoothscale(ring, (72, 20)))
        self._ripples: list[tuple[float, float, float]] = []
        self._rain: DemoRain | None = None
        self._last_impact_time: float | None = None
        rng = np.random.default_rng(970)
        self._lens_x = rng.uniform(12, 140, 8) + np.array((0, 1120) * 4)
        self._lens_y = rng.uniform(-40, height, 8)

    @staticmethod
    def _halo(size: int, opacity: int) -> pygame.Surface:
        halo = pygame.Surface((size, size), pygame.SRCALPHA)
        x, y = np.indices((size, size), dtype=np.float32)
        radius = (size - 1) / 2
        distance = (x - radius) ** 2 + (y - radius) ** 2
        coverage = np.exp(-distance / (radius * 0.48) ** 2)
        halo.fill((*GLOW_COLOR, 0))
        alpha = pygame.surfarray.pixels_alpha(halo)
        alpha[:] = np.rint(coverage * opacity).astype(np.uint8)
        del alpha
        return halo

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
        ids = np.arange(rain.x.size)
        contact = rain.shimmer > 0.2
        visible = (rain.y >= 0) & (rain.y < SCENE_SIZE[1] + 30)
        visible &= (rain.depth_band != 2) | (ids % 2 == 0) | contact
        if intensity < 0.9:
            visible &= (ids % 2 == 0) | contact
        length_scale = np.array([layer[0] for layer in RAIN_LAYERS])[rain.depth_band]
        length = rain.speed * (0.045 + strength * 0.009) * length_scale * intensity
        length = np.where(contact, 5 + rain.shimmer * 7, length)
        slots = np.clip((length / 4 - 0.5).astype(int), 0, len(STREAK_LENGTHS) - 1)
        angle = np.degrees(
            np.arctan2(rain.velocity_x, np.where(contact, 3, rain.speed))
        )
        angles = np.clip(np.rint((angle + 64) / 16), 0, 8).astype(int)
        sprites = []
        for index in ids[visible]:
            band = int(rain.depth_band[index])
            palette = 3 if band == 2 and index % 97 == 0 else band
            sprite, anchor = self.streaks[palette][slots[index]][angles[index]]
            sprites.append((sprite, (int(rain.x[index] - anchor[0]),
                                     int(rain.y[index] - anchor[1]))))
        self.canvas.fblits(sprites)
        for index in ids[visible & contact & (ids % 3 == 0)][:48]:
            level = min(2, int(rain.shimmer[index] * 3))
            self.canvas.blit(self._glows[level], (int(rain.x[index]) - 11,
                                                   int(rain.y[index]) - 11))
        self._draw_ripples(rain)
        self.canvas.fblits([
            (self._lens, (int(x + np.sin(rain.time * 0.23 + i) * 8),
                          int((y + rain.time * (35 + i * 3)) % 810) - 45))
            for i, (x, y) in enumerate(zip(self._lens_x, self._lens_y, strict=True))
        ])

    def _draw_ripples(self, rain: DemoRain) -> None:
        if self._rain is not rain:
            self._rain = rain
            self._last_impact_time = None
            self._ripples.clear()
        if self._last_impact_time != rain.time:
            ids = np.arange(rain.x.size)
            hits = np.flatnonzero(rain.floor_hits & (ids % 9 == 0))
            self._ripples.extend(
                (float(rain.floor_x[index]), SCENE_SIZE[1] - 10 - index % 11, rain.time)
                for index in hits
            )
            self._last_impact_time = rain.time
        self._ripples = [
            ripple for ripple in self._ripples if rain.time - ripple[2] < 0.96
        ][-24:]
        for x, y, born in self._ripples:
            age = min(23, int((rain.time - born) * 25))
            self.canvas.blit(self._rings[age], (int(x) - 36, int(y) - 10))
