import pygame

from ..config import SCENE_SIZE, WINDOW_SIZE
from ..coordinates import Viewport


def select_display(sizes: list[tuple[int, int]], requested: int | None) -> int:
    if not sizes:
        raise pygame.error("Windows hittade ingen bildskärm.")
    if requested is not None:
        if not 1 <= requested <= len(sizes):
            raise pygame.error("Bildskärmen saknas. Kör --displays för att se listan.")
        return requested - 1
    return next(
        (index for index, size in enumerate(sizes) if size == (3840, 2160)), 0
    )


def open_display(windowed: bool, requested: int | None) -> pygame.Surface:
    sizes = pygame.display.get_desktop_sizes()
    display = select_display(sizes, requested)
    if windowed:
        return pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE, display=display)
    return pygame.display.set_mode(sizes[display], pygame.FULLSCREEN, display=display)


def list_displays() -> int:
    try:
        pygame.display.init()
        for index, (width, height) in enumerate(pygame.display.get_desktop_sizes(), 1):
            print(f"Bildskärm {index}: {width} × {height}")
        return 0
    except pygame.error as error:
        print(f"Det gick inte att läsa bildskärmarna. {error}")
        return 1
    finally:
        pygame.display.quit()


class Presenter:
    def __init__(self) -> None:
        self._scaled: pygame.Surface | None = None

    def draw(self, canvas: pygame.Surface, display: pygame.Surface) -> None:
        viewport = Viewport.fit(SCENE_SIZE, display.get_size())
        size = viewport.width, viewport.height
        full_frame = size == display.get_size()
        if not full_frame:
            display.fill((0, 0, 0))
        if size != SCENE_SIZE:
            if (
                full_frame
                and canvas.get_bitsize() == display.get_bitsize()
                and canvas.get_masks() == display.get_masks()
            ):
                pygame.transform.smoothscale(canvas, size, display)
                return
            if self._scaled is None or self._scaled.get_size() != size:
                self._scaled = pygame.transform.smoothscale(canvas, size)
            else:
                pygame.transform.smoothscale(canvas, size, self._scaled)
            canvas = self._scaled
        display.blit(canvas, (viewport.x, viewport.y))
