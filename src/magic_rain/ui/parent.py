import pygame

from ..config import SCENE_SIZE
from ..settings import Settings

ROWS = (
    ("continue", "Fortsätt leka"),
    ("sound", "Ljud"),
    ("intensity", "Regnets styrka"),
    ("mirror", "Spegelbild"),
    ("zone", "Spelzon"),
    ("distance", "Spelavstånd"),
    ("camera", "Kalibrera kameran"),
    ("quit", "Avsluta"),
)
PANEL = pygame.Rect(345, 101, 590, 518)


class ParentPanel:
    def __init__(self) -> None:
        self.visible = False
        self.selected = 0
        self.warning = ""
        self._escape_started: float | None = None
        self._title = pygame.font.SysFont("segoeui", 31, bold=True)
        self._text = pygame.font.SysFont("segoeui", 23)
        self._small = pygame.font.SysFont("segoeui", 18)
        self._shade = pygame.Surface(SCENE_SIZE, pygame.SRCALPHA)
        self._shade.fill((3, 8, 16, 155))

    @staticmethod
    def row(index: int) -> pygame.Rect:
        return pygame.Rect(PANEL.x + 28, PANEL.y + 94 + index * 45, PANEL.w - 56, 39)

    def toggle(self) -> None:
        self.visible = not self.visible
        self.selected = 0
        self._escape_started = None

    def update(self, now: float) -> None:
        if self._escape_started is not None and now - self._escape_started >= 1.5:
            self.toggle()

    def event(self, event: pygame.event.Event, now: float) -> tuple[str, int] | None:
        if event.type == pygame.WINDOWFOCUSLOST:
            self._escape_started = None
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            self._escape_started = None
        if event.type != pygame.KEYDOWN:
            return None
        if event.key == pygame.K_F1:
            self.toggle()
        elif event.key == pygame.K_ESCAPE:
            if self.visible:
                self.toggle()
            elif self._escape_started is None:
                self._escape_started = now
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
                return action, 1
        return None

    def draw(
        self, canvas: pygame.Surface, settings: Settings, camera_fault: bool
    ) -> None:
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
            value = getattr(settings, action, "")
            if value:
                text = self._text.render(value, True, (141, 217, 216))
                value_rect = text.get_rect(midright=(rect.right - 14, rect.centery))
                canvas.blit(text, value_rect)
        hint = self.warning or "Piltangenter · Enter väljer · Esc stänger"
        footer = self._small.render(hint, True, (161, 185, 204))
        canvas.blit(footer, (PANEL.x + 31, PANEL.bottom - 39))
