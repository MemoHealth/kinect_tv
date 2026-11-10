import numpy as np
import pygame

from .audio.ambient import AmbientRain
from .config import DEMO_FPS, SCENE_SIZE, WINDOW_SIZE, DemoConfig
from .coordinates import Viewport
from .render.scene import Scene
from .sensors.simulated import FRAME_SIZE, OBSTACLE_DEPTH_MM, SimulatedSensor
from .simulation.rain import DemoRain

STEP = 1 / DEMO_FPS


def open_display(windowed: bool) -> pygame.Surface:
    if windowed:
        return pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
    desktop_size = pygame.display.get_desktop_sizes()[0]
    return pygame.display.set_mode(desktop_size, pygame.FULLSCREEN)


def run_demo(windowed: bool) -> int:
    sensor = SimulatedSensor()
    ambient = AmbientRain()
    try:
        pygame.display.init()
        ambient.start()
        return animate(sensor, windowed)
    except pygame.error as error:
        print(f"Det gick inte att visa regnscenen. {error}")
        return 1
    finally:
        sensor.stop()
        ambient.stop()
        pygame.display.quit()


def animate(sensor: SimulatedSensor, windowed: bool) -> int:
    display = open_display(windowed)
    pygame.display.set_caption("Magic Rain · Simulerad sensor")
    pygame.mouse.set_visible(windowed)
    scene = Scene()
    rain = DemoRain(DemoConfig())
    field = Viewport.fit(FRAME_SIZE, SCENE_SIZE)
    mask = np.zeros(FRAME_SIZE[::-1], dtype=np.bool_)
    clock = pygame.time.Clock()
    remaining = 0.0
    next_sample_ms = 0
    sensor.start()

    while True:
        remaining += min(clock.tick(DEMO_FPS) / 1000, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                return 0
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                windowed = not windowed
                display = open_display(windowed)
                pygame.mouse.set_visible(windowed)

        output = Viewport.fit(SCENE_SIZE, display.get_size())
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

        while remaining >= STEP:
            rain.step(STEP, mask, field)
            remaining -= STEP

        canvas = scene.draw(rain)
        display.fill((0, 0, 0))
        if (output.width, output.height) != SCENE_SIZE:
            canvas = pygame.transform.scale(canvas, (output.width, output.height))
        display.blit(canvas, (output.x, output.y))
        pygame.display.flip()
