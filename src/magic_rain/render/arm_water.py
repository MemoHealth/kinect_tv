import pygame

from ..coordinates import Viewport
from ..simulation.arm_water import ArmWater


def draw_arm_water(
    canvas: pygame.Surface, water: ArmWater, field: Viewport, *, snow: bool
) -> None:
    sx = field.width / water.width
    sy = field.height / water.height
    for pool in water.pools:
        if pool.amount <= 0:
            continue
        basin = pool.basin
        start, level = basin.surface(pool.amount)
        left, right = basin.spans[start]
        y = field.y + (basin.top + level) * sy
        surface = [(field.x + left * sx, y), (field.x + right * sx, y)]
        sides = [[], []]
        for index in range(start, len(basin.spans)):
            left, right = basin.spans[index]
            bottom = field.y + (basin.top + index + 1) * sy
            sides[0].append((field.x + left * sx, bottom))
            sides[1].append((field.x + right * sx, bottom))
        color = (171, 199, 224) if snow else (38, 122, 157)
        pygame.draw.polygon(canvas, color, surface + sides[1] + sides[0][::-1])
        pygame.draw.aaline(canvas, (167, 222, 235), *surface)
