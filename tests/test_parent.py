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
        "version", "scene", "sound", "intensity", "mirror", "zone", "distance",
        "color_assist", "paint_fade", "paint_palette",
    }
    path.write_text('{"version":1,"sound":"bad","mirror":"Av"}', encoding="utf-8")
    assert load_settings(path) == Settings(mirror="Av")
    path.write_text("{", encoding="utf-8")
    assert load_settings(path) == Settings()


def test_parent_panel_toggles_and_tilt_requires_an_explicit_direction():
    pygame.font.init()
    try:
        panel = ParentPanel()
        event = pygame.event.Event
        escape = event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        panel.event(escape)
        assert panel.visible
        panel.event(event(pygame.KEYDOWN, key=pygame.K_ESCAPE, repeat=True))
        assert panel.visible
        panel.event(event(pygame.KEYDOWN, key=pygame.K_DOWN))
        left = event(pygame.KEYDOWN, key=pygame.K_LEFT)
        assert panel.event(left) == ("scene", -1)
        panel.event(event(pygame.KEYDOWN, key=pygame.K_DOWN))
        assert panel.event(left) == ("tilt", -1)
        assert panel.event(event(pygame.KEYDOWN, key=pygame.K_RETURN)) is None
        down, up = panel.tilt_buttons(ParentPanel.row(panel.selected))
        assert panel.click(down.center) == ("tilt", -1)
        assert panel.click(up.center) == ("tilt", 1)
        panel.event(escape)
        assert not panel.visible
        panel.event(event(pygame.KEYDOWN, key=pygame.K_F1))
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
