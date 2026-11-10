import json

import pygame

from magic_rain.audio.ambient import AmbientRain
from magic_rain.settings import Settings, load_settings, save_settings
from magic_rain.ui.parent import ROWS, ParentPanel


def test_settings_round_trip_and_recover_from_corruption(tmp_path):
    path = tmp_path / "user" / "settings.json"
    assert load_settings(path) == Settings()
    settings = Settings().change("sound", -1).change("zone", 1)
    assert save_settings(path, settings)
    assert load_settings(path) == settings
    assert set(json.loads(path.read_text(encoding="utf-8"))) == {
        "version", "scene", "sound", "intensity", "mirror", "zone", "distance"
    }
    path.write_text('{"version":1,"sound":"bad","mirror":"Av"}', encoding="utf-8")
    assert load_settings(path) == Settings(mirror="Av")
    path.write_text("{", encoding="utf-8")
    assert load_settings(path) == Settings()


def test_parent_panel_opens_only_on_shortcut_or_long_escape():
    pygame.font.init()
    try:
        panel = ParentPanel()
        event = pygame.event.Event
        escape = event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        panel.event(escape, 1.0)
        panel.update(2.4)
        assert not panel.visible
        panel.update(2.6)
        assert panel.visible
        panel.event(event(pygame.KEYUP, key=pygame.K_ESCAPE), 2.7)
        assert panel.visible
        panel.event(event(pygame.KEYDOWN, key=pygame.K_DOWN), 2.8)
        left = event(pygame.KEYDOWN, key=pygame.K_LEFT)
        assert panel.event(left, 2.9) == ("scene", -1)
        panel.event(escape, 3.0)
        assert not panel.visible
        panel.event(escape, 3.1)
        panel.event(event(pygame.WINDOWFOCUSLOST), 3.2)
        panel.update(5.0)
        assert not panel.visible
        panel.event(event(pygame.KEYDOWN, key=pygame.K_F1), 4.0)
        assert panel.visible
        camera_row = next(i for i, (action, _) in enumerate(ROWS) if action == "camera")
        assert panel.click(ParentPanel.row(camera_row).center) == ("camera", 1)
    finally:
        pygame.font.quit()


def test_audio_mute_remains_set_during_startup_fade(monkeypatch):
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    ambient = AmbientRain()
    ambient.start()
    try:
        ambient.volume(0)
        pygame.time.wait(80)
        assert ambient._sound.get_volume() == 0
    finally:
        ambient.stop()
