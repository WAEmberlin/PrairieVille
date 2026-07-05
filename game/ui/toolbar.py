"""Bottom toolbar with tool selection."""

import pygame
from game.core.constants import (
    BOTTOM_BAR_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_UI_BG, COLOR_UI_BORDER, COLOR_UI_TEXT, COLOR_UI_ACCENT, COLOR_UI_HIGHLIGHT,
    TOOL_CURSOR, TOOL_TILL, TOOL_CLEAR, TOOL_PLANT, TOOL_HARVEST,
    TOOL_BUILD, TOOL_DECORATE, TOOL_FEED,
)
from game.ui.widgets import Widget
from game.ui.icon_draw import scale_icon


TOOLS = [
    (TOOL_CURSOR, "Hand"),
    (TOOL_TILL, "Till"),
    (TOOL_CLEAR, "Clear"),
    (TOOL_PLANT, "Plant"),
    (TOOL_HARVEST, "Harvest"),
    (TOOL_BUILD, "Build"),
    (TOOL_DECORATE, "Decorate"),
    (TOOL_FEED, "Feed"),
]


class BottomToolbar(Widget):
    """Bottom tool selection bar."""

    def __init__(self, on_tool_selected, assets=None):
        y = SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT
        super().__init__(0, y, SCREEN_WIDTH, BOTTOM_BAR_HEIGHT)
        self.on_tool_selected = on_tool_selected
        self.assets = assets
        self.current_tool = TOOL_CURSOR
        self.buttons: list[tuple[pygame.Rect, str, str]] = []
        self._build_buttons()

    def _build_buttons(self):
        btn_w = 80
        btn_h = 44
        gap = 8
        total_w = len(TOOLS) * (btn_w + gap) - gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        y = self.rect.y + (BOTTOM_BAR_HEIGHT - btn_h) // 2
        self.buttons = []
        for i, (tool_id, label) in enumerate(TOOLS):
            rect = pygame.Rect(start_x + i * (btn_w + gap), y, btn_w, btn_h)
            self.buttons.append((rect, tool_id, label))

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, tool_id, _ in self.buttons:
                if rect.collidepoint(event.pos):
                    self.current_tool = tool_id
                    if self.on_tool_selected:
                        self.on_tool_selected(tool_id)
                    return True
        return False

    def draw(self, screen, font):
        pygame.draw.rect(screen, COLOR_UI_BG, self.rect)
        pygame.draw.line(screen, COLOR_UI_BORDER, (0, self.rect.y),
                         (SCREEN_WIDTH, self.rect.y), 2)

        for rect, tool_id, label in self.buttons:
            is_active = tool_id == self.current_tool
            bg = COLOR_UI_ACCENT if is_active else COLOR_UI_HIGHLIGHT
            pygame.draw.rect(screen, bg, rect, border_radius=4)
            pygame.draw.rect(screen, COLOR_UI_BORDER, rect, 1, border_radius=4)

            icon = self.assets.get_icon_for_tool(tool_id) if self.assets else None
            if icon:
                scaled = scale_icon(icon, 22)
                icon_x = rect.centerx - scaled.get_width() // 2
                screen.blit(scaled, (icon_x, rect.y + 4))
                text = font.render(label, True, COLOR_UI_TEXT)
                text_rect = text.get_rect(centerx=rect.centerx, bottom=rect.bottom - 3)
                screen.blit(text, text_rect)
            else:
                text = font.render(label, True, COLOR_UI_TEXT)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
