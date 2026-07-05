"""Yes/No confirmation dialog."""

import pygame
from game.core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_UI_BG, COLOR_UI_BORDER,
    COLOR_UI_TEXT, COLOR_UI_ACCENT, COLOR_UI_HIGHLIGHT,
)
from game.ui.widgets import Widget


class ConfirmDialog(Widget):
    """Modal confirmation popup."""

    def __init__(self):
        w, h = 360, 140
        x = (SCREEN_WIDTH - w) // 2
        y = (SCREEN_HEIGHT - h) // 2
        super().__init__(x, y, w, h)
        self.visible = False
        self.message = ""
        self._on_confirm = None
        self._on_cancel = None
        self._build_buttons()

    def _build_buttons(self):
        btn_w, btn_h = 100, 32
        gap = 20
        center_y = self.rect.bottom - 20 - btn_h
        cx = self.rect.centerx
        self.yes_rect = pygame.Rect(cx - btn_w - gap // 2, center_y, btn_w, btn_h)
        self.no_rect = pygame.Rect(cx + gap // 2, center_y, btn_w, btn_h)

    def show(self, message: str, on_confirm, on_cancel=None):
        self.message = message
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        self.visible = True

    def hide(self):
        self.visible = False
        self._on_confirm = None
        self._on_cancel = None

    def handle_event(self, event) -> bool:
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.yes_rect.collidepoint(event.pos):
                cb = self._on_confirm
                self.hide()
                if cb:
                    cb()
                return True
            if self.no_rect.collidepoint(event.pos):
                cb = self._on_cancel
                self.hide()
                if cb:
                    cb()
                return True
            # Block clicks outside dialog while open
            return True

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_y):
                cb = self._on_confirm
                self.hide()
                if cb:
                    cb()
                return True
            if event.key in (pygame.K_ESCAPE, pygame.K_n):
                cb = self._on_cancel
                self.hide()
                if cb:
                    cb()
                return True
            return True

        if self.visible:
            return True
        return False

    def draw(self, screen, font):
        if not self.visible:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, COLOR_UI_BG, self.rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_UI_BORDER, self.rect, 3, border_radius=8)

        title = font.render("Are you sure?", True, COLOR_UI_ACCENT)
        screen.blit(title, (self.rect.x + 16, self.rect.y + 12))

        msg_font = font
        msg_surf = msg_font.render(self.message, True, COLOR_UI_TEXT)
        screen.blit(msg_surf, (self.rect.x + 16, self.rect.y + 40))

        for rect, label, color in (
            (self.yes_rect, "Yes", COLOR_UI_ACCENT),
            (self.no_rect, "No", COLOR_UI_HIGHLIGHT),
        ):
            pygame.draw.rect(screen, color, rect, border_radius=4)
            pygame.draw.rect(screen, COLOR_UI_BORDER, rect, 2, border_radius=4)
            text = font.render(label, True, COLOR_UI_TEXT)
            screen.blit(text, text.get_rect(center=rect.center))
