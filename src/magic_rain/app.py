from time import monotonic

import numpy as np
import pygame

from .audio.ambient import AmbientRain
from .config import DEMO_FPS, SCENE_SIZE, DemoConfig
from .coordinates import Viewport
from .interaction.field import MotionField
from .live import LiveInput
from .render.outline import Outline
from .render.output import Presenter, open_display
from .render.scene import Scene
from .sensors.simulated import FRAME_SIZE, OBSTACLE_DEPTH_MM, SimulatedSensor
from .settings import Settings, load_settings, save_settings, settings_path
from .simulation.rain import DemoRain
from .ui.parent import ParentPanel

STEP = 1 / DEMO_FPS
VOLUME = {"Av": 0.0, "Lågt": 0.62, "Normal": 1.0}
INTENSITY = {"Milt": 0.78, "Normalt": 1.0, "Livligt": 1.12}


def run_demo(windowed: bool, display: int | None = None) -> int:
    return run_scene(SimulatedSensor(), windowed, display)


def run_live(windowed: bool, display: int | None = None) -> int:
    return run_scene(LiveInput(), windowed, display)


def run_scene(
    sensor: SimulatedSensor | LiveInput, windowed: bool, screen: int | None = None
) -> int:
    ambient = AmbientRain()
    try:
        pygame.display.init()
        pygame.font.init()
        ambient.start()
        return animate(sensor, windowed, ambient, screen)
    except pygame.error as error:
        print(f"Det gick inte att visa regnscenen. {error}")
        return 1
    finally:
        sensor.stop()
        ambient.stop()
        pygame.font.quit()
        pygame.display.quit()


def animate(
    sensor: SimulatedSensor | LiveInput,
    windowed: bool,
    ambient: AmbientRain,
    screen: int | None,
) -> int:
    display = open_display(windowed, screen)
    presenter = Presenter()
    demo = isinstance(sensor, SimulatedSensor)
    title = "Magic Rain · Simulerad sensor" if demo else "Magic Rain"
    pygame.display.set_caption(title)
    pygame.mouse.set_visible(windowed)
    scene = Scene()
    field = Viewport.fit(FRAME_SIZE, SCENE_SIZE)
    mask = np.zeros(FRAME_SIZE[::-1], dtype=np.bool_)
    outline = Outline(field, mask.shape)
    clock = pygame.time.Clock()
    motion = MotionField()
    notice_font = pygame.font.SysFont("segoeui", 25)
    panel = ParentPanel() if not demo else None
    path = settings_path()
    settings = load_settings(path) if panel is not None else Settings()
    rain = DemoRain(DemoConfig(), snow=settings.scene == "Snö")
    ambient.volume(0 if rain.snow else VOLUME[settings.sound])
    if isinstance(sensor, LiveInput):
        sensor.configure(settings)
    remaining = 0.0
    next_sample_ms = 0
    sensor.start()

    while True:
        dt = min(clock.tick(DEMO_FPS) / 1000, 0.05)
        remaining += dt
        now = monotonic()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                demo and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                return 0
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                windowed = not windowed
                display = open_display(windowed, screen)
            if panel is None:
                continue
            action = panel.event(event, now)
            if (
                panel.visible
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                viewport = Viewport.fit(SCENE_SIZE, display.get_size())
                point = viewport.normalized_point(event.pos)
                if point is not None:
                    action = panel.click(
                        (point[0] * SCENE_SIZE[0], point[1] * SCENE_SIZE[1])
                    )
            if action is None:
                continue
            name, delta = action
            if name == "quit":
                return 0
            if name == "continue":
                panel.toggle()
            elif name == "camera":
                sensor.calibrate_or_retry(now)
                panel.toggle()
            else:
                settings = settings.change(name, delta)
                sensor.configure(settings)
                if name == "scene":
                    rain = DemoRain(DemoConfig(), snow=settings.scene == "Snö")
                ambient.volume(0 if rain.snow else VOLUME[settings.sound])
                saved = save_settings(path, settings)
                panel.warning = "" if saved else "Inställningen sparades inte."
        if panel is not None:
            panel.update(now)
        cursor_visible = windowed or (panel is not None and panel.visible)
        if pygame.mouse.get_visible() != cursor_visible:
            pygame.mouse.set_visible(cursor_visible)

        output = Viewport.fit(SCENE_SIZE, display.get_size())
        notice = ""
        if isinstance(sensor, SimulatedSensor):
            pointer = output.normalized_point(pygame.mouse.get_pos())
            sensor.pointer = None
            if pygame.mouse.get_pressed()[0] and pointer is not None:
                logical = (pointer[0] * SCENE_SIZE[0], pointer[1] * SCENE_SIZE[1])
                sensor.pointer = field.normalized_point(logical)
            now_ms = pygame.time.get_ticks()
            if now_ms >= next_sample_ms:
                frame = sensor.read_latest(timeout_s=0)
                if frame is not None:
                    mask = frame.depth_mm == OBSTACLE_DEPTH_MM
                next_sample_ms = now_ms + 33
        else:
            mask = sensor.mask(now)
            notice = sensor.notice

        while remaining >= STEP:
            motion.update(mask, STEP)
            rain.step(STEP, mask, field, motion.wind)
            remaining -= STEP

        canvas = scene.draw(rain, motion.strength, INTENSITY[settings.intensity])
        outline.draw(canvas, mask, dt)
        if notice:
            caption = notice_font.render(notice, True, (199, 216, 230))
            rect = caption.get_rect(center=(SCENE_SIZE[0] // 2, SCENE_SIZE[1] - 65))
            pygame.draw.rect(
                canvas, (11, 19, 34), rect.inflate(36, 20), border_radius=12
            )
            canvas.blit(caption, rect)
        panel_visible = panel is not None and panel.visible
        if panel_visible:
            panel.draw(canvas, settings, sensor.fault)
        presenter.draw(canvas, display, text=bool(notice) or panel_visible)
        pygame.display.flip()
