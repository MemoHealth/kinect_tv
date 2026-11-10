import pygame

from ..simulation.bowl import BOWL_BOTTOM, BOWL_LEFT, BOWL_RIGHT, BOWL_RIM, Bowl


def draw_bowl(canvas: pygame.Surface, bowl: Bowl, *, snow: bool) -> None:
    left, right = BOWL_LEFT, BOWL_RIGHT
    bottom_left, bottom_right = left + 46, right - 46
    hull = [
        (left, BOWL_RIM), (right, BOWL_RIM),
        (bottom_right, BOWL_BOTTOM), (bottom_left, BOWL_BOTTOM),
    ]
    pygame.draw.polygon(canvas, (14, 32, 51), hull)
    if bowl.level:
        surface = round(BOWL_BOTTOM - (BOWL_BOTTOM - BOWL_RIM - 5) * bowl.level)
        inset = round(46 * (surface - BOWL_RIM) / (BOWL_BOTTOM - BOWL_RIM))
        fill = [
            (left + inset, surface), (right - inset, surface),
            (bottom_right, BOWL_BOTTOM), (bottom_left, BOWL_BOTTOM),
        ]
        color = (159, 195, 217) if snow else (39, 139, 168)
        pygame.draw.polygon(canvas, color, fill)
        pygame.draw.aaline(canvas, (166, 221, 233), fill[0], fill[1])
    pygame.draw.aalines(canvas, (117, 177, 197), True, hull)
