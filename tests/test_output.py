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
    assert target.get_at(target.get_rect().center)[:3] == (18, 34, 57)
    presenter.draw(scene, target, text=True)
    if size == (3840, 2160):
        assert target.get_at((0, 0))[:3] == (220, 200, 70)
        assert target.get_at((2, 2))[:3] == (220, 200, 70)
        assert target.get_at((3839, 2159))[:3] == (18, 34, 57)
    else:
        assert target.get_at((0, 95))[:3] == (0, 0, 0)
        assert target.get_at((0, 96))[:3] != (0, 0, 0)
        assert target.get_at((0, 672))[:3] == (0, 0, 0)
