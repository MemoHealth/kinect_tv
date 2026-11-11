import numpy as np
import pygame

from magic_rain.config import SCENE_SIZE
from magic_rain.coordinates import Viewport
from magic_rain.interaction.color_slots import ColorSlots
from magic_rain.render.paint_explosion import PaintExplosion


def players() -> np.ndarray:
    mask = np.zeros((80, 120), dtype=bool)
    for x in (8, 49, 90):
        mask[21:63, x:x + 15] = True
    return mask


def test_color_slots_track_three_regions_across_a_short_merge():
    tracker = ColorSlots((80, 120))
    separated = players()
    assert tracker.update(separated, 0)[30, [15, 55, 95]].tolist() == [1, 2, 4]
    merged = separated.copy()
    merged[29:34, 8:64] = True
    assert tracker.update(merged, 0.1)[30, [15, 55, 95]].tolist() == [3, 3, 4]
    assert tracker.update(separated, 0.2)[30, [15, 55, 95]].tolist() == [1, 2, 4]


def test_paint_decay_spray_and_explicit_export(tmp_path):
    paint = PaintExplosion(Viewport(0, 0, 120, 80), (80, 120))
    paint.configure("Kort", "Havsglas")
    mask = players()
    paint.update(mask, 0)
    canvas = pygame.Surface(SCENE_SIZE)
    paint.draw(canvas)
    colors = [canvas.get_at((x, 30))[:3] for x in (8, 49, 90)]
    assert len(set(colors)) == 3
    paint.update(mask, 1.5)
    paint.draw(canvas)
    assert 0.48 < (canvas.get_at((8, 30)).g - 8) / (colors[0][1] - 8) < 0.52
    paint.update(np.roll(mask, 5, axis=1), 1 / 60)
    assert 0 < np.count_nonzero(paint._sparks.life > 0) <= 22
    assert not list(tmp_path.iterdir())
    paint.draw(canvas)
    expected = pygame.image.tobytes(canvas, "RGB")
    canvas.fill((255, 0, 255))  # A UI overdraw cannot enter the exported surface.
    output = paint.save(tmp_path)
    image = pygame.image.load(output)
    assert pygame.image.tobytes(image, "RGB") == expected
    assert list(tmp_path.iterdir()) == [output]
