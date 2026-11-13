import numpy as np
import pygame

from magic_rain import app
from magic_rain.app import make_world
from magic_rain.config import SCENE_SIZE
from magic_rain.coordinates import Viewport
from magic_rain.interaction.scene_switch import BodySwitch, cycle_scene
from magic_rain.live import LiveInput
from magic_rain.render.scene_switch import WorldPortals
from magic_rain.settings import MIRROR_SCENE, OPTIONS, PAINT_EXPLOSION, Settings
from magic_rain.ui.parent import PANEL, ParentPanel

SHAPE = (240, 320)


def person(*, side=None, tip=None, three=False):
    surface = pygame.Surface(SHAPE[::-1])
    for x in ((90, 160, 230) if three else (230 if side == 1 else 90,)):
        pygame.draw.circle(surface, 'white', (x, 67), 12)
        pygame.draw.rect(surface, 'white', (x - 12, 78, 25, 108))
        pygame.draw.line(surface, 'white', (x - 7, 175), (x - 12, 220), 7)
        pygame.draw.line(surface, 'white', (x + 7, 175), (x + 12, 220), 7)
        if (side == 0 and x == 90) or (side == 1 and x == 230):
            target = tip or ((51, 77) if side == 0 else (269, 77))
            pygame.draw.line(surface, 'white', (x, 103), target, 5)
    return pygame.surfarray.array3d(surface)[:, :, 0].T != 0


def advance(control, mask, seconds, *, enabled=True):
    return [value for _ in range(round(seconds * 30))
            if (value := control.update(mask.copy(), 1 / 30, enabled=enabled))]


def test_deliberate_hold_switches_once_then_requires_release():
    control = BodySwitch(SHAPE)
    assert not advance(control, person(side=1), 3)  # Must release before first use.
    advance(control, person(), 0.6)
    assert advance(control, person(side=1), 2.2) == [1]
    assert not advance(control, person(side=1), 4)
    advance(control, person(), 0.6)
    assert advance(control, person(side=0), 2.2) == [-1]


def test_body_head_speckles_sweeps_and_stale_frames_do_not_change_worlds():
    control = BodySwitch(SHAPE)
    advance(control, person(), 0.6)
    # A normal body or head at the portal is not an outstretched hand.
    assert not advance(control, np.roll(person(), -39, axis=1), 3)
    noise = np.zeros(SHAPE, dtype=bool)
    noise[70:85, 45:60] = True
    assert not advance(control, noise, 3)
    broad = np.zeros(SHAPE, dtype=bool)
    broad[40:200, 10:110] = True
    assert not advance(control, broad, 3)
    advance(control, person(), 0.6)
    for x in range(245, 295):
        assert not control.update(person(side=1, tip=(x, 77)), 1 / 15)
    hand = person(side=1)
    for _ in range(100):
        assert not control.update(hand, 1 / 30)  # Reusing a frozen frame isn't a hold.


def test_jitter_tolerant_hold_with_three_players_and_disable_reset():
    control = BodySwitch(SHAPE)
    advance(control, person(three=True), 0.6)
    events = []
    for frame in range(65):
        events.append(control.update(
            person(side=1, tip=(269 + frame % 3 - 1, 77), three=True), 1 / 30
        ))
    assert [value for value in events if value] == [1]
    advance(control, person(three=True), 0.6)
    advance(control, person(side=0, three=True), 1)
    advance(control, person(side=0, three=True), 0.2, enabled=False)
    assert not advance(control, person(side=0, three=True), 2.5)
    advance(control, person(three=True), 0.6)
    assert advance(control, person(side=0, three=True), 2.2) == [-1]


def test_two_portals_or_known_merged_people_are_ambiguous():
    control = BodySwitch(SHAPE)
    advance(control, person(three=True), 0.6)
    both = person(side=0, three=True) | person(side=1, three=True)
    assert not advance(control, both, 3)
    merged = person(side=1, three=True)
    merged[120:130, 90:240] = True
    assert not advance(control, merged, 3)


def test_scene_cycle_reflection_opt_in_and_artwork_retention():
    current = 'Regn'
    visited = set()
    for _ in range(len(OPTIONS['scene'])):
        current = cycle_scene(current, 1)
        visited.add(current)
    assert MIRROR_SCENE not in visited
    assert len(visited) == len(OPTIONS['scene']) - 1
    assert cycle_scene('Dansspegel', 1, mirror_allowed=True) == MIRROR_SCENE
    field = Viewport.fit((320, 240), SCENE_SIZE)
    settings = Settings(scene=PAINT_EXPLOSION)
    paint = make_world(settings, field, SHAPE)
    paint._art.fill((71, 82, 93))
    restored = make_world(settings, field, SHAPE, painting=paint)
    assert restored is paint and restored._art.get_at((45, 45))[:3] == (71, 82, 93)


def test_portals_are_local_and_parent_controls_fit_the_panel():
    pygame.font.init()
    try:
        control = BodySwitch(SHAPE)
        advance(control, person(), 0.6)
        advance(control, person(side=0), 0.8)
        canvas = pygame.Surface(SCENE_SIZE)
        WorldPortals(Viewport.fit((320, 240), SCENE_SIZE), SHAPE).draw(
            canvas, control, 'Regn'
        )
        assert pygame.surfarray.array3d(canvas).any()
        assert canvas.get_at((640, 360))[:3] == (0, 0, 0)
        panel = ParentPanel()
        for scene in OPTIONS['scene']:
            panel.set_scene(scene)
            assert panel._row(len(panel.rows) - 1).bottom < PANEL.bottom - 39
            assert any(action == 'body_navigation' for action, _ in panel.rows)
    finally:
        pygame.font.quit()


def test_app_body_switch_returns_to_the_same_painting(monkeypatch, tmp_path):
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    monkeypatch.setenv('SDL_AUDIODRIVER', 'dummy')

    class Fixture(LiveInput):
        def __init__(self):
            self.notice = ''

        def configure(self, settings):
            pass

        def start(self):
            pass

        def stop(self):
            return True

        def mask(self, now, *, preview=False):
            return person()

    class ScriptedSwitch(BodySwitch):
        def __init__(self, shape):
            super().__init__(shape)
            self.calls = 0

        def update(self, mask, dt, *, enabled=True):
            self.calls += 1
            return {5: 1, 10: -1}.get(self.calls, 0)

    made = []
    factory = app.make_world

    def observe(settings, field, shape, **kwargs):
        world = factory(settings, field, shape, **kwargs)
        if settings.scene == PAINT_EXPLOSION:
            if not made:
                world._trail._history.fill(0.8)
            else:
                assert world is made[0]
                assert world._trail._history[120, 160].min() > 0.5
        made.append(world)
        return world

    flips = 0
    flip = pygame.display.flip

    def quit_after_return():
        nonlocal flips
        flip()
        flips += 1
        if flips == 12:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    path = tmp_path / 'settings.json'
    monkeypatch.setattr(app, 'settings_path', lambda: path)
    monkeypatch.setattr(app, 'load_settings', lambda _: Settings(scene=PAINT_EXPLOSION))
    monkeypatch.setattr(app, 'BodySwitch', ScriptedSwitch)
    monkeypatch.setattr(app, 'make_world', observe)
    monkeypatch.setattr(pygame.display, 'flip', quit_after_return)
    assert app.run_scene(Fixture(), True) == 0
    assert len(made) == 3 and made[0] is made[2]
