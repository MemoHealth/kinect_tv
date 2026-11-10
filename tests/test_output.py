import pygame
import pytest

from magic_rain.config import SCENE_SIZE
from magic_rain.render.output import Presenter, select_display


def test_4k_is_preferred_and_user_can_override():
    modes = [(1920, 1080), (3840, 2160)]
    assert select_display(modes, None) == 1
    assert select_display(modes, 1) == 0
    assert select_display(modes[:1], None) == 0
    with pytest.raises(pygame.error, match="saknas"):
        select_display(modes, 3)


@pytest.mark.parametrize("size", [(3840, 2160), (1024, 768)])
def test_scene_uses_correct_16_9_bounds_after_resizing(size):
    scene = pygame.Surface(SCENE_SIZE)
    scene.fill((18, 34, 57))
    scene.set_at((0, 0), (220, 200, 70))
    target = pygame.Surface(size)
    presenter = Presenter()
    presenter.draw(scene, target)
    presenter.draw(scene, target)
    center = target.get_at(target.get_rect().center)[:3]
    assert all(abs(a - b) <= 3 for a, b in zip(center, (18, 34, 57), strict=True))
    if size == (3840, 2160):
        assert target.get_at((0, 0))[:3] == (220, 200, 70)
        assert 18 < target.get_at((2, 2)).r < 220
        assert target.get_at((3839, 2159))[:3] == (18, 34, 57)
    else:
        assert target.get_at((0, 95))[:3] == (0, 0, 0)
        assert target.get_at((0, 96))[:3] != (0, 0, 0)
        assert target.get_at((0, 672))[:3] == (0, 0, 0)
