import numpy as np
import pygame

from ..simulation.coral_garden import CoralGarden

SEA_COLORS = ((242, 173, 112), (92, 202, 210), (169, 159, 236))


class CoralArt:
    def __init__(self) -> None:
        self._stages = [[self._sprite(kind, step / 8) for step in range(9)]
                        for kind in range(3)]
        self.pearls = []
        x, y = np.indices((13, 13))
        distance = (x - 6) ** 2 + (y - 6) ** 2
        for color in SEA_COLORS:
            pearl = pygame.Surface((13, 13), pygame.SRCALPHA)
            pearl.fill((*color, 0))
            alpha = pygame.surfarray.pixels_alpha(pearl)
            glow = np.maximum(30 * np.exp(-distance / 13),
                              205 * np.exp(-distance / 2.3))
            alpha[:] = np.rint(glow).astype(np.uint8)
            del alpha
            self.pearls.append(pearl)

    @staticmethod
    def _sprite(kind: int, amount: float) -> pygame.Surface:
        image = pygame.Surface((360, 320), pygame.SRCALPHA)
        color = tuple(round(a + (b - a) * amount)
                      for a, b in zip((24, 67, 77), SEA_COLORS[kind], strict=True))
        base = np.array((180, 300))
        for branch in range(9):
            angle = -np.pi / 2 + (branch - 4) * (0.18 if kind == 1 else 0.27)
            length = (160 + (branch % 3) * 19) * (0.45 + amount * 0.55)
            tip = base + (np.cos(angle) * length, np.sin(angle) * length)
            mid = base + (tip - base) * 0.57 + (np.sin(branch) * 12, 0)
            points = [tuple(np.rint(point).astype(int)) for point in (base, mid, tip)]
            pygame.draw.lines(image, (*color, 210), False, points,
                              round(3 + amount * (5 if kind == 2 else 3)))
            if kind != 2:
                for sign in (-1, 1):
                    twig = mid + ((tip[0] - mid[0]) * 0.7 + sign * 22,
                                  (tip[1] - mid[1]) * 0.65)
                    pygame.draw.line(image, (*color, 190), points[1], twig,
                                     round(2 + amount * 3))
            radius = round(3 + amount * (7 if kind == 2 else 4))
            pygame.draw.circle(image, (*color, 210), points[-1], radius)
            if amount > 0.3:
                pygame.draw.circle(image, (235, 229, 212, round(amount * 115)),
                                   points[-1], max(1, radius // 3))
        return pygame.transform.smoothscale(image, (180, 160))

    def draw(self, canvas: pygame.Surface, garden: CoralGarden) -> None:
        for coral, (x, _) in enumerate(garden.corals):
            level = float(np.clip(garden.bloom[coral], 0, 1) * 8)
            low = int(level)
            fraction = level - low
            for stage, alpha in ((low, 1 - fraction), (min(8, low + 1), fraction)):
                sprite = self._stages[coral][stage]
                sprite.set_alpha(round(alpha * 255))
                canvas.blit(sprite, (round(x) - 90, 500))
