import numpy as np
import pygame
from numpy.typing import NDArray

from ..config import SCENE_SIZE
from ..settings import Settings

ROWS = (
    ("continue", "Fortsätt leka"),
    ("scene", "Bana"),
    ("tilt", "Kameravinkel"),
    ("sound", "Ljud"),
    ("intensity", "Regnets styrka"),
    ("mirror", "Spegelbild"),
    ("zone", "Spelzon"),
    ("distance", "Spelavstånd"),
    ("camera", "Kalibrera kameran"),
    ("quit", "Avsluta"),
)
PANEL = pygame.Rect(210, 56, 860, 608)


class ParentPanel:
    def __init__(self) -> None:
        self.visible = False
        self.selected = 0
        self.warning = ""
        self._preview_source: NDArray[np.uint16] | None = None
        self._preview_surface: pygame.Surface | None = None
        self._title = pygame.font.SysFont("segoeui", 31, bold=True)
        self._text = pygame.font.SysFont("segoeui", 23)
        self._small = pygame.font.SysFont("segoeui", 18)
        self._shade = pygame.Surface(SCENE_SIZE, pygame.SRCALPHA)
        self._shade.fill((3, 8, 16, 155))

    @staticmethod
    def row(index: int) -> pygame.Rect:
        return pygame.Rect(PANEL.x + 28, PANEL.y + 94 + index * 44, 510, 38)

    @staticmethod
    def tilt_buttons(row: pygame.Rect) -> tuple[pygame.Rect, pygame.Rect]:
        return (
            pygame.Rect(row.right - 148, row.y + 4, 37, 30),
            pygame.Rect(row.right - 44, row.y + 4, 37, 30),
        )

    def toggle(self) -> None:
        self.visible = not self.visible
        self.selected = 0
        if not self.visible:
            self._preview_source = None
            self._preview_surface = None

    def event(self, event: pygame.event.Event) -> tuple[str, int] | None:
        if event.type != pygame.KEYDOWN:
            return None
        if event.key in (pygame.K_F1, pygame.K_ESCAPE):
            if getattr(event, "repeat", False):
                return None
            self.toggle()
        elif self.visible:
            return self.key(event.key)
        return None

    def key(self, key: int) -> tuple[str, int] | None:
        if key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(ROWS)
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(ROWS)
        elif key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RETURN, pygame.K_SPACE):
            delta = -1 if key == pygame.K_LEFT else 1
            action = ROWS[self.selected][0]
            if action == "tilt" and key not in (pygame.K_LEFT, pygame.K_RIGHT):
                return None
            if key in (pygame.K_LEFT, pygame.K_RIGHT) and action in (
                "continue", "camera", "quit"
            ):
                return None
            return action, delta
        return None

    def click(self, point: tuple[float, float]) -> tuple[str, int] | None:
        for index, (action, _) in enumerate(ROWS):
            if self.row(index).collidepoint(point):
                self.selected = index
                if action == "tilt":
                    down, up = self.tilt_buttons(self.row(index))
                    if down.collidepoint(point):
                        return action, -1
                    if up.collidepoint(point):
                        return action, 1
                    return None
                return action, 1
        return None

    def draw(
        self,
        canvas: pygame.Surface,
        settings: Settings,
        camera_fault: bool,
        tilt_status: tuple[int | None, bool, str],
        depth: NDArray[np.uint16] | None,
    ) -> None:
        angle, moving, tilt_warning = tilt_status
        canvas.blit(self._shade, (0, 0))
        pygame.draw.rect(canvas, (13, 25, 43), PANEL, border_radius=23)
        pygame.draw.rect(canvas, (54, 79, 101), PANEL, width=1, border_radius=23)
        header = self._title.render("Magiskt regn", True, (230, 242, 249))
        canvas.blit(header, (PANEL.x + 30, PANEL.y + 22))
        sub = self._small.render("För vuxna", True, (148, 176, 192))
        canvas.blit(sub, (PANEL.x + 31, PANEL.y + 62))
        for index, (action, label) in enumerate(ROWS):
            rect = self.row(index)
            if index == self.selected:
                pygame.draw.rect(canvas, (29, 56, 75), rect, border_radius=10)
                pygame.draw.rect(canvas, (104, 180, 187), rect, 1, border_radius=10)
            if action == "camera" and camera_fault:
                label = "Försök ansluta igen"
            text = self._text.render(label, True, (226, 239, 247))
            canvas.blit(text, text.get_rect(midleft=(rect.x + 14, rect.centery)))
            if action == "tilt":
                self._draw_tilt(canvas, rect, angle, moving)
            value = getattr(settings, action, "")
            if value:
                text = self._text.render(value, True, (141, 217, 216))
                value_rect = text.get_rect(midright=(rect.right - 14, rect.centery))
                canvas.blit(text, value_rect)
        default_hint = "Piltangenter · Enter väljer · Esc stänger"
        hint = self.warning or tilt_warning or default_hint
        footer = self._small.render(hint, True, (161, 185, 204))
        canvas.blit(footer, (PANEL.x + 31, PANEL.bottom - 39))
        self._draw_depth(canvas, depth)

    def _draw_tilt(
        self, canvas: pygame.Surface, row: pygame.Rect, angle: int | None, moving: bool
    ) -> None:
        down, up = self.tilt_buttons(row)
        for button, symbol in ((down, "−"), (up, "+")):
            pygame.draw.rect(canvas, (36, 64, 81), button, border_radius=6)
            text = self._text.render(symbol, True, (176, 222, 227))
            canvas.blit(text, text.get_rect(center=button.center))
        value = "…" if moving else ("–" if angle is None else f"{angle:+d}°")
        text = self._text.render(value, True, (141, 217, 216))
        canvas.blit(text, text.get_rect(center=(row.right - 78, row.centery)))

    def _draw_depth(
        self, canvas: pygame.Surface, depth: NDArray[np.uint16] | None
    ) -> None:
        x, y = PANEL.x + 565, PANEL.y + 94
        view = pygame.Rect(x, y + 32, 256, 192)
        canvas.blit(self._text.render("Djupvy", True, (226, 239, 247)), (x, y))
        pygame.draw.rect(canvas, (5, 15, 26), view)
        if depth is not self._preview_source:
            self._preview_source = depth
            self._preview_surface = None
            if depth is not None:
                level = np.where(depth != 0, np.clip((4000.0 - depth) / 18, 0, 170), 0)
                colors = np.stack((level * 0.65, level * 0.93, level), axis=2)
                rgb = colors.swapaxes(0, 1).astype(np.uint8)
                image = pygame.surfarray.make_surface(rgb)
                self._preview_surface = pygame.transform.scale(image, view.size)
        if self._preview_surface is not None:
            canvas.blit(self._preview_surface, view)
        for index, line in enumerate((
            "Ljust är nära.",
            "Töm spelzonen innan du fortsätter.",
        )):
            label = self._small.render(line, True, (161, 185, 204))
            canvas.blit(label, (x, view.bottom + 13 + index * 24))
