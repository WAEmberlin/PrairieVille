"""Base UI widget."""

import pygame
from game.core.constants import (
    COLOR_UI_BG, COLOR_UI_BORDER, COLOR_UI_TEXT, COLOR_UI_HIGHLIGHT, COLOR_UI_ACCENT,
)


class Widget:
    """Base class for UI widgets."""

    def __init__(self, x: int, y: int, w: int, h: int):
        self.rect = pygame.Rect(x, y, w, h)
        self.visible = True
        self.enabled = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

    def update(self, dt: float):
        pass

    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        pass

    def contains(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


class Panel(Widget):
    """A bordered panel container."""

    def __init__(self, x, y, w, h, title: str = ""):
        super().__init__(x, y, w, h)
        self.title = title
        self.children: list[Widget] = []

    def add_child(self, widget: Widget):
        self.children.append(widget)

    def draw(self, screen, font):
        if not self.visible:
            return
        pygame.draw.rect(screen, COLOR_UI_BG, self.rect, border_radius=4)
        pygame.draw.rect(screen, COLOR_UI_BORDER, self.rect, 2, border_radius=4)
        if self.title:
            title_surf = font.render(self.title, True, COLOR_UI_ACCENT)
            screen.blit(title_surf, (self.rect.x + 8, self.rect.y + 4))
        for child in self.children:
            child.draw(screen, font)


class Button(Widget):
    """Clickable button."""

    def __init__(self, x, y, w, h, text: str, callback=None, color=None):
        super().__init__(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = color or COLOR_UI_ACCENT
        self.hovered = False
        self.pressed = False

    def handle_event(self, event) -> bool:
        if not self.visible or not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                if self.callback:
                    self.callback()
                return True
            self.pressed = False
        return False

    def draw(self, screen, font):
        if not self.visible:
            return
        bg = COLOR_UI_HIGHLIGHT if self.hovered else COLOR_UI_BG
        if self.pressed:
            bg = self.color
        pygame.draw.rect(screen, bg, self.rect, border_radius=4)
        border_color = self.color if self.hovered else COLOR_UI_BORDER
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=4)
        text_surf = font.render(self.text, True, COLOR_UI_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class Label(Widget):
    """Text label."""

    def __init__(self, x, y, w, h, text: str = "", color=None):
        super().__init__(x, y, w, h)
        self.text = text
        self.color = color or COLOR_UI_TEXT

    def set_text(self, text: str):
        self.text = text

    def draw(self, screen, font):
        if not self.visible or not self.text:
            return
        surf = font.render(self.text, True, self.color)
        screen.blit(surf, (self.rect.x, self.rect.y))


class ScrollList(Panel):
    """Scrollable list of text items."""

    def __init__(self, x, y, w, h, title="", item_height=22):
        super().__init__(x, y, w, h, title)
        self.items: list[str] = []
        self.item_height = item_height
        self.scroll_offset = 0

    def set_items(self, items: list[str]):
        self.items = items

    def draw(self, screen, font):
        if not self.visible:
            return
        pygame.draw.rect(screen, COLOR_UI_BG, self.rect, border_radius=4)
        pygame.draw.rect(screen, COLOR_UI_BORDER, self.rect, 2, border_radius=4)
        if self.title:
            title_surf = font.render(self.title, True, COLOR_UI_ACCENT)
            screen.blit(title_surf, (self.rect.x + 8, self.rect.y + 4))

        y = self.rect.y + (28 if self.title else 8)
        max_y = self.rect.bottom - 8
        for i, item in enumerate(self.items[self.scroll_offset:]):
            if y + self.item_height > max_y:
                break
            surf = font.render(item, True, COLOR_UI_TEXT)
            screen.blit(surf, (self.rect.x + 8, y))
            y += self.item_height
