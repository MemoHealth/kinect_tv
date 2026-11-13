from math import pi

import pygame

from ..coordinates import Viewport
from ..interaction.scene_switch import BodySwitch, cycle_scene


class WorldPortals:
    def __init__(self, field: Viewport, shape: tuple[int, int]) -> None:
        self._field, self._shape = field, shape
        self._font = pygame.font.SysFont("segoeui", 21)

    def draw(
        self, canvas: pygame.Surface, control: BodySwitch, scene: str,
        *, mirror_allowed: bool = False,
    ) -> None:
        if not control.visible:
            return
        for side, point in enumerate(control.centres):
            x = round(self._field.x + point[0] * self._field.width / self._shape[1])
            y = round(self._field.y + point[1] * self._field.height / self._shape[0])
            active = control.progress > 0 and control.side == side
            color = (116, 204, 206) if active else (38, 78, 91)
            pygame.draw.circle(canvas, (7, 24, 36), (x, y), 21)
            pygame.draw.circle(canvas, color, (x, y), 21, 1)
            direction = -1 if side == 0 else 1
            pygame.draw.aalines(canvas, color, False, (
                (x - direction * 3, y - 6), (x + direction * 3, y),
                (x - direction * 3, y + 6),
            ))
            if active:
                pygame.draw.arc(canvas, (179, 237, 229), (x - 28, y - 28, 56, 56),
                                -pi / 2, -pi / 2 + 2 * pi * control.progress, 3)
                name = cycle_scene(scene, direction, mirror_allowed=mirror_allowed)
                text = self._font.render(name, True, (184, 224, 227))
                canvas.blit(text, text.get_rect(midtop=(x, y + 38)))
