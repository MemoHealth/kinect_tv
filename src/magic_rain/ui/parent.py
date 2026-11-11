import numpy as np
import pygame
from numpy.typing import NDArray

from ..config import SCENE_SIZE
from ..settings import DANCE_SCENE, PAINT_EXPLOSION, PAINT_SCENE, Settings

ROWS = (
    ("continue", "Fortsätt leka"),
    ("scene", "Bana"),
    ("tilt", "Kameravinkel"),
    ("sound", "Ljud"),
    ("intensity", "Regnets styrka"),
    ("mirror", "Spegelbild"),
    ("zone", "Spelzon"),
    ("distance", "Spelavstånd"),
    ("color_assist", "Färgstöd"),
    ("camera", "Kalibrera kameran"),
    ("quit", "Avsluta"),
)
PANEL = pygame.Rect(210, 56, 860, 608)
PAINT_ROWS = (
    ("paint_fade", "Färgens toning"),
    ("paint_palette", "Spelarfärger"),
    ("save_art", "Spara tavla"),
)


class ParentPanel:
    def __init__(self) -> None:
        self.visible = False
        self.selected = 0
        self.warning = ""
        self.rows = ROWS
        self._preview_source: NDArray[np.uint16] | None = None
        self._preview_mask: NDArray[np.bool_] | None = None
        self._preview_surface: pygame.Surface | None = None
        self._title = pygame.font.SysFont("segoeui", 31, bold=True)
        self._text = pygame.font.SysFont("segoeui", 23)
        self._small = pygame.font.SysFont("segoeui", 18)
        self._shade = pygame.Surface(SCENE_SIZE, pygame.SRCALPHA)
        self._shade.fill((3, 8, 16, 155))

    @staticmethod
    def row(index: int) -> pygame.Rect:
        return pygame.Rect(PANEL.x + 28, PANEL.y + 94 + index * 41, 510, 38)

    def _row(self, index: int) -> pygame.Rect:
        if self.rows == ROWS:
            return self.row(index)
        return pygame.Rect(PANEL.x + 28, PANEL.y + 94 + index * 33, 510, 31)

    def set_scene(self, scene: str) -> None:
        extra = ()
        if scene == PAINT_EXPLOSION:
            extra = PAINT_ROWS
        elif scene == PAINT_SCENE:
            extra = PAINT_ROWS[:1]
        elif scene == DANCE_SCENE:
            extra = (("dance_style", "Figur"),)
        self.rows = ROWS[:-1] + extra + ROWS[-1:]
        self.selected = min(self.selected, len(self.rows) - 1)

    @staticmethod
    def tilt_buttons(row: pygame.Rect) -> tuple[pygame.Rect, pygame.Rect]:
        return (
            pygame.Rect(row.right - 148, row.centery - 14, 37, 28),
            pygame.Rect(row.right - 44, row.centery - 14, 37, 28),
        )

    def toggle(self) -> None:
        self.visible = not self.visible
        self.selected = 0
        if not self.visible:
            self._preview_source = None
            self._preview_mask = None
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
            self.selected = (self.selected - 1) % len(self.rows)
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.rows)
        elif key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RETURN, pygame.K_SPACE):
            delta = -1 if key == pygame.K_LEFT else 1
            action = self.rows[self.selected][0]
            if action == "tilt" and key not in (pygame.K_LEFT, pygame.K_RIGHT):
                return None
            if key in (pygame.K_LEFT, pygame.K_RIGHT) and action in (
                "continue", "camera", "quit", "save_art"
            ):
                return None
            return action, delta
        return None

    def click(self, point: tuple[float, float]) -> tuple[str, int] | None:
        for index, (action, _) in enumerate(self.rows):
            if self._row(index).collidepoint(point):
                self.selected = index
                if action == "tilt":
                    down, up = self.tilt_buttons(self._row(index))
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
        mask: NDArray[np.bool_] | None = None,
        calibration: str = "",
        color_status: str = "",
    ) -> None:
        angle, moving, tilt_warning = tilt_status
        canvas.blit(self._shade, (0, 0))
        pygame.draw.rect(canvas, (13, 25, 43), PANEL, border_radius=23)
        pygame.draw.rect(canvas, (54, 79, 101), PANEL, width=1, border_radius=23)
        header = self._title.render("Magiskt regn", True, (230, 242, 249))
        canvas.blit(header, (PANEL.x + 30, PANEL.y + 22))
        sub = self._small.render("För vuxna", True, (148, 176, 192))
        canvas.blit(sub, (PANEL.x + 31, PANEL.y + 62))
        for index, (action, label) in enumerate(self.rows):
            rect = self._row(index)
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
        self._draw_depth(canvas, depth, mask, settings, (calibration, color_status))

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
        self, canvas: pygame.Surface, depth: NDArray[np.uint16] | None,
        mask: NDArray[np.bool_] | None, settings: Settings, status: tuple[str, str],
    ) -> None:
        x, y = PANEL.x + 565, PANEL.y + 94
        view = pygame.Rect(x, y + 32, 256, 192)
        label = self._text.render("Spelzon i kameran", True, (226, 239, 247))
        canvas.blit(label, (x, y))
        pygame.draw.rect(canvas, (5, 15, 26), view)
        if depth is not self._preview_source or mask is not self._preview_mask:
            self._preview_source = depth
            self._preview_mask = mask
            self._preview_surface = None
            if depth is not None:
                level = np.where(depth != 0, np.clip((4000.0 - depth) / 18, 0, 170), 0)
                colors = np.stack((level * 0.65, level * 0.93, level), axis=2)
                if mask is not None:
                    colors[mask] = (56, 196, 188)
                rgb = colors.swapaxes(0, 1).astype(np.uint8)
                image = pygame.surfarray.make_surface(rgb)
                self._preview_surface = pygame.transform.scale(image, view.size)
        if self._preview_surface is not None:
            canvas.blit(self._preview_surface, view)
        margin = 0.12 if settings.zone == "Centrerad" else 0.0
        inset = round(view.width * margin)
        zone = view.inflate(-2 * inset, 0)
        pygame.draw.rect(canvas, (108, 151, 172), zone, 1)
        cut = False
        if depth is not None and mask is not None:
            cut = self._draw_clipped_edges(canvas, zone, mask, margin)
        framing = "Konturen når kanten" if cut else "Hela kroppen ska rymmas."
        adjustment = "Backa eller justera vinkeln." if cut else "Justera med − och +."
        muted = (161, 185, 204)
        lines = (
            (status[0], (141, 217, 216)),
            (status[1], muted),
            (framing, (237, 182, 113) if cut else muted),
            (adjustment, muted),
            ("Töm ytan när du kalibrerar.", muted),
        )
        for index, (line, color) in enumerate(lines):
            label = self._small.render(line, True, color)
            canvas.blit(label, (x, view.bottom + 13 + index * 24))

    @staticmethod
    def _draw_clipped_edges(
        canvas: pygame.Surface, zone: pygame.Rect,
        mask: NDArray[np.bool_], margin: float,
    ) -> bool:
        border = round(mask.shape[1] * margin)
        active = mask[:, border:mask.shape[1] - border]
        edges = (
            (active[:3, :], zone.topleft, zone.topright),
            (active[-3:, :], zone.bottomleft, zone.bottomright),
            (active[:, :3], zone.topleft, zone.bottomleft),
            (active[:, -3:], zone.topright, zone.bottomright),
        )
        cut = False
        for region, start, end in edges:
            if np.count_nonzero(region) >= 8:
                pygame.draw.line(canvas, (237, 182, 113), start, end, 3)
                cut = True
        return cut
