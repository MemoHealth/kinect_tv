import numpy as np
import pygame

from magic_rain.coordinates import Viewport
from magic_rain.render.outline import Outline, boundary


def test_outline_keeps_three_interiors_clear_and_fades_when_people_leave():
    mask = np.zeros((14, 36), dtype=bool)
    for x in (2, 14, 26):
        mask[3:11, x:x + 7] = True
    edges = boundary(mask)
    assert edges[3, [4, 16, 28]].all()
    assert not edges[6, [4, 16, 28]].any()
    canvas = pygame.Surface((80, 35))
    outline = Outline(Viewport(4, 3, 72, 28), mask.shape)
    outline.draw(canvas, mask, 0.15)
    assert canvas.get_at((12, 9))[:3] != (0, 0, 0)
    # The final bilinear upscale may bleed one 8-bit level into a tiny interior.
    assert max(canvas.get_at((12, 15))[:3]) <= 1
    canvas.fill((0, 0, 0))
    outline.draw(canvas, np.zeros_like(mask), 0.25)
    assert canvas.get_at((12, 9))[:3] == (0, 0, 0)


def test_diagonal_outline_has_subpixel_coverage_levels():
    mask = np.tri(24, dtype=bool)
    canvas = pygame.Surface((72, 72))
    Outline(Viewport(0, 0, 72, 72), mask.shape).draw(canvas, mask, 0.15)
    red = pygame.surfarray.array3d(canvas)[:, :, 0]
    assert np.unique(red[red > 0]).size >= 5
    assert not red[8, 60] and not red[60, 8]


def test_outline_damps_edge_jitter_but_follows_fast_moves_without_a_second_body():
    mask = np.zeros((80, 100), dtype=bool)
    mask[15:65, 25:45] = True
    original = mask.copy()
    field = Viewport(0, 0, 300, 240)
    outline = Outline(field, mask.shape)
    canvas = pygame.Surface((300, 240))
    outline.draw(canvas, mask, 1 / 30)
    initial = outline._coverage.copy()
    jitter = np.roll(mask, 1, axis=1)
    outline.draw(canvas, jitter, 1 / 30)
    from magic_rain.render.coverage import soften
    target = soften(soften(jitter))
    assert np.abs(outline._coverage - initial).sum() < np.abs(target - initial).sum()
    fast = np.roll(mask, 30, axis=1)
    outline.draw(canvas, fast, 1 / 30)
    assert outline._coverage[35, 65] > 0.9
    assert outline._coverage[35, 35] < 0.1
    np.testing.assert_array_equal(mask, original)
    # Exit/reentry resets the drawing history instead of morphing across players.
    outline.draw(canvas, np.zeros_like(mask), 0.3)
    outline.draw(canvas, fast.copy(), 1 / 60)
    assert outline._coverage[35, 35] == 0


def test_small_edge_smoothing_is_consistent_at_30_and_60_fps():
    mask = np.zeros((60, 80), dtype=bool)
    mask[10:50, 20:40] = True
    states = []
    for fps in (30, 60):
        outline = Outline(Viewport(0, 0, 160, 120), mask.shape)
        canvas = pygame.Surface((160, 120))
        outline.draw(canvas, mask, 1 / fps)
        target = np.roll(mask, 1, axis=1)
        for _ in range(fps // 10):
            outline.draw(canvas, target, 1 / fps)
        states.append(outline._coverage.copy())
    np.testing.assert_allclose(states[0], states[1], atol=1e-6)
