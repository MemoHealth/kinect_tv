from pathlib import Path
from time import monotonic

import numpy as np
import pygame

from .audio.ambient import AmbientRain
from .config import DEMO_FPS, SCENE_SIZE, DemoConfig
from .coordinates import Viewport
from .interaction.field import MotionField
from .live import LiveInput
from .render.aquarium import LivingAquarium
from .render.arm_water import draw_arm_water
from .render.dance import DanceMirror
from .render.fruit_ninja import FruitNinja
from .render.galaxy import GalaxyMirror
from .render.lightpaint import LightPaint
from .render.mirror_studio import MirrorStudio
from .render.outline import Outline
from .render.output import Presenter, init_display, open_display
from .render.paint_explosion import PaintExplosion
from .render.scene import Scene
from .sensors.simulated import FRAME_SIZE, OBSTACLE_DEPTH_MM, SimulatedSensor
from .settings import (
    AQUARIUM_SCENE,
    DANCE_SCENE,
    FRUIT_SCENE,
    GALAXY_SCENE,
    HALF_LIVES,
    MIRROR_SCENE,
    PAINT_EXPLOSION,
    PAINT_SCENE,
    Settings,
    load_settings,
    save_settings,
    settings_path,
)
from .simulation.arm_water import ArmWater
from .simulation.rain import DemoRain
from .ui.parent import ParentPanel

STEP = 1 / DEMO_FPS
VOLUME = {"Av": 0.0, "Lågt": 0.62, "Normal": 1.0}
INTENSITY = {"Milt": 0.78, "Normalt": 1.0, "Livligt": 1.12}
World = (
    PaintExplosion | GalaxyMirror | LivingAquarium
    | DanceMirror | MirrorStudio | FruitNinja
)


def make_world(
    settings: Settings, field: Viewport, shape: tuple[int, int]
) -> World | None:
    if settings.scene == PAINT_EXPLOSION:
        world = PaintExplosion(field, shape)
        world.configure(settings.paint_fade, settings.paint_palette)
        return world
    if settings.scene == GALAXY_SCENE:
        return GalaxyMirror(field, shape)
    if settings.scene == AQUARIUM_SCENE:
        return LivingAquarium(field, shape)
    if settings.scene == DANCE_SCENE:
        dancer = DanceMirror(field, shape)
        dancer.configure(settings.dance_style)
        return dancer
    if settings.scene == MIRROR_SCENE:
        mirror = MirrorStudio(field, shape)
        mirror.configure(settings.mirror_style)
        return mirror
    if settings.scene == FRUIT_SCENE:
        return FruitNinja(field, shape)
    return None


def run_demo(windowed: bool, display: int | None = None, *, scene: str = "Regn") -> int:
    return run_scene(SimulatedSensor(), windowed, display, demo_scene=scene)


def run_live(windowed: bool, display: int | None = None) -> int:
    return run_scene(LiveInput(), windowed, display)


def run_scene(
    sensor: SimulatedSensor | LiveInput, windowed: bool, screen: int | None = None,
    *, demo_scene: str = "Regn",
) -> int:
    ambient = AmbientRain()
    try:
        init_display()
        pygame.font.init()
        ambient.start()
        return animate(sensor, windowed, ambient, screen, demo_scene=demo_scene)
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
    *,
    demo_scene: str = "Regn",
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
    lightpaint = LightPaint(field, mask.shape)
    clock = pygame.time.Clock()
    motion = MotionField()
    notice_font = pygame.font.SysFont("segoeui", 25)
    panel = ParentPanel() if not demo else None
    path = settings_path()
    settings = load_settings(path) if panel is not None else Settings(scene=demo_scene)
    if panel is not None:
        panel.set_scene(settings.scene)
    world = make_world(settings, field, mask.shape)
    rain = DemoRain(DemoConfig(), snow=settings.scene != "Regn")
    arm_water = ArmWater()
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
            action = panel.event(event)
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
                sensor.calibrate_or_retry(now, from_menu=True)
            elif name == "tilt":
                panel.warning = sensor.tilt(delta, now)
            elif name == "save_art" and isinstance(world, PaintExplosion):
                if getattr(event, "repeat", False):
                    continue
                try:
                    world.save(Path.home() / "Pictures" / "Magic Rain")
                    panel.warning = "Tavlan sparades i Bilder / Magic Rain."
                except (OSError, pygame.error):
                    panel.warning = "Tavlan kunde inte sparas."
            else:
                settings = settings.change(name, delta)
                if name in ("scene", "mirror", "zone", "distance", "color_assist"):
                    sensor.configure(settings)
                if name == "color_assist" and settings.color_assist == "På":
                    sensor.calibrate_or_retry(now, from_menu=True)
                if name == "scene":
                    panel.set_scene(settings.scene)
                    rain = DemoRain(DemoConfig(), snow=settings.scene != "Regn")
                    arm_water = ArmWater()
                    lightpaint.clear()
                    world = make_world(settings, field, mask.shape)
                if isinstance(world, PaintExplosion):
                    world.configure(settings.paint_fade, settings.paint_palette)
                if isinstance(world, DanceMirror):
                    world.configure(settings.dance_style)
                if isinstance(world, MirrorStudio):
                    world.configure(settings.mirror_style)
                ambient.volume(0 if rain.snow else VOLUME[settings.sound])
                saved = save_settings(path, settings)
                panel.warning = "" if saved else "Inställningen sparades inte."
        panel_visible = panel is not None and panel.visible
        cursor_visible = windowed or panel_visible
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
            mask = sensor.mask(now, preview=panel_visible)
            notice = sensor.notice

        water = arm_water if settings.scene in ("Regn", "Snö") else None
        if water is not None:
            water.update(mask, field)
        painting = settings.scene == PAINT_SCENE
        if isinstance(world, MirrorStudio):
            rgb = sensor.color_image if isinstance(sensor, LiveInput) else None
            world.set_color(rgb, mirrored=settings.mirror == "På")
        while remaining >= STEP:
            if world is not None:
                if not (panel_visible and isinstance(world, PaintExplosion)):
                    world.update(mask, STEP)
            elif painting:
                lightpaint.update(mask, STEP, half_life=HALF_LIVES[settings.paint_fade])
            else:
                motion.update(mask, STEP)
                rain.step(STEP, mask, field, motion.wind, water=water)
            remaining -= STEP

        if world is not None:
            canvas = scene.canvas
            world.draw(canvas)
        elif painting:
            canvas = scene.canvas
            canvas.fill((5, 8, 21))
            lightpaint.draw(canvas)
        else:
            canvas = scene.draw(
                rain,
                motion.strength,
                INTENSITY[settings.intensity],
            )
        if water is not None:
            draw_arm_water(canvas, water, field, snow=rain.snow)
        hide_outline = isinstance(world, (DanceMirror, MirrorStudio)) or (
            isinstance(world, PaintExplosion) and panel_visible
        )
        if not hide_outline:
            outline.draw(canvas, mask, dt)
        if notice:
            caption = notice_font.render(notice, True, (199, 216, 230))
            rect = caption.get_rect(center=(SCENE_SIZE[0] // 2, SCENE_SIZE[1] - 65))
            pygame.draw.rect(
                canvas, (11, 19, 34), rect.inflate(36, 20), border_radius=12
            )
            canvas.blit(caption, rect)
        if panel_visible:
            panel.draw(
                canvas,
                settings,
                sensor.fault,
                sensor.tilt_status(now),
                sensor.preview_depth,
                mask,
                sensor.calibration_status(now),
                sensor.color_status(now),
            )
        presenter.draw(canvas, display)
        pygame.display.flip()
