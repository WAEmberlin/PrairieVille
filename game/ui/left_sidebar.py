"""Left sidebar with quests and inventory."""

import pygame
from game.core.constants import (
    SIDEBAR_WIDTH, TOP_BAR_HEIGHT, BOTTOM_BAR_HEIGHT, SCREEN_HEIGHT,
    COLOR_UI_BG, COLOR_UI_BORDER, COLOR_UI_TEXT, COLOR_UI_HIGHLIGHT, COLOR_COIN,
)
from game.core.icon_registry import icon_for
from game.ui.widgets import Panel
from game.ui.icon_draw import blit_icon


class LeftSidebar(Panel):
    """Left panel: quests and inventory."""

    ROW_HEIGHT = 26

    def __init__(self, assets=None, on_sell_item=None, get_sell_price=None):
        h = SCREEN_HEIGHT - TOP_BAR_HEIGHT - BOTTOM_BAR_HEIGHT
        super().__init__(0, TOP_BAR_HEIGHT, SIDEBAR_WIDTH, h)
        self.assets = assets
        self.on_sell_item = on_sell_item
        self.get_sell_price = get_sell_price
        self.quest_items: list[str] = []
        self.inventory_items: list[tuple[str, int]] = []
        self.hovered_inv_index: int | None = None

    def update_quests(self, quests):
        items = []
        for q in quests:
            status = " [DONE]" if q.completed else f" ({q.progress_text})"
            items.append(q.description[:22] + status)
        self.quest_items = items or ["No active quests"]

    def update_inventory(self, inventory: dict):
        self.inventory_items = sorted(inventory.items())

    def _inventory_start_y(self) -> int:
        half = self.rect.height // 2
        return self.rect.y + half + 26

    def _inventory_row_rect(self, index: int) -> pygame.Rect:
        y = self._inventory_start_y() + index * self.ROW_HEIGHT
        return pygame.Rect(self.rect.x + 4, y, SIDEBAR_WIDTH - 8, self.ROW_HEIGHT - 2)

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered_inv_index = None
            if self.inventory_items:
                for i in range(len(self.inventory_items)):
                    if self._inventory_row_rect(i).collidepoint(event.pos):
                        self.hovered_inv_index = i
                        break
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, (key, count) in enumerate(self.inventory_items):
                if self._inventory_row_rect(i).collidepoint(event.pos):
                    if self.on_sell_item:
                        self.on_sell_item(key)
                    return True
        return False

    def _draw_list_section(
        self, screen, font, title: str, y: int, height: int,
        rows: list, show_icons: bool = False, subtitle: str = "",
    ) -> int:
        header_rect = pygame.Rect(self.rect.x + 4, y, SIDEBAR_WIDTH - 8, 22)
        pygame.draw.rect(screen, COLOR_UI_BG, header_rect, border_radius=4)
        pygame.draw.rect(screen, COLOR_UI_BORDER, header_rect, 1, border_radius=4)
        title_surf = font.render(title, True, (218, 165, 32))
        screen.blit(title_surf, (header_rect.x + 8, header_rect.y + 4))

        content_y = y + 26
        if subtitle:
            sub = font.render(subtitle, True, (120, 100, 80))
            screen.blit(sub, (self.rect.x + 8, content_y))
            content_y += 16

        max_rows = (height - 30 - (16 if subtitle else 0)) // self.ROW_HEIGHT
        for i, row in enumerate(rows[:max_rows]):
            row_rect = pygame.Rect(
                self.rect.x + 4, content_y + i * self.ROW_HEIGHT,
                SIDEBAR_WIDTH - 8, self.ROW_HEIGHT - 2,
            )
            if show_icons and isinstance(row, tuple):
                key, count = row
                if self.hovered_inv_index == i:
                    pygame.draw.rect(screen, COLOR_UI_HIGHLIGHT, row_rect, border_radius=3)
                icon_name = icon_for(key)
                icon = self.assets.get_icon(icon_name) if self.assets and icon_name else None
                text_x = blit_icon(screen, icon, row_rect, size=20)
                price = self.get_sell_price(key) if self.get_sell_price else None
                name = key.replace("_", " ").title()
                if price is not None:
                    label_text = f"{name} x{count}  ${price}"
                else:
                    label_text = f"{name}: {count}"
                label = font.render(label_text[:22], True, COLOR_UI_TEXT)
                screen.blit(label, (text_x, row_rect.y + 4))
                if price is not None:
                    coin_label = font.render("$", True, COLOR_COIN)
                    screen.blit(coin_label, (row_rect.right - 14, row_rect.y + 4))
            else:
                text = row if isinstance(row, str) else str(row)
                label = font.render(text[:24], True, COLOR_UI_TEXT)
                screen.blit(label, (row_rect.x + 4, row_rect.y + 4))

        return y + height

    def draw(self, screen, font):
        pygame.draw.rect(screen, COLOR_UI_BG, self.rect)
        pygame.draw.line(screen, COLOR_UI_BORDER,
                         (SIDEBAR_WIDTH - 1, TOP_BAR_HEIGHT),
                         (SIDEBAR_WIDTH - 1, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT), 2)

        half = self.rect.height // 2
        self._draw_list_section(screen, font, "Quests", self.rect.y + 4, half - 8, self.quest_items)

        if not self.inventory_items:
            self._draw_list_section(
                screen, font, "Inventory", self.rect.y + half, half - 8, ["Empty"],
            )
        else:
            self._draw_list_section(
                screen, font, "Inventory", self.rect.y + half, half - 8,
                self.inventory_items, show_icons=True,
                subtitle="Click item to sell",
            )

        social_y = self.rect.bottom - 40
        social_rect = pygame.Rect(self.rect.x + 4, social_y, SIDEBAR_WIDTH - 8, 32)
        pygame.draw.rect(screen, (220, 220, 220), social_rect, border_radius=4)
        if self.assets:
            blit_icon(screen, self.assets.get_icon("farmer"), social_rect, size=22)
        social_text = font.render("Neighbors (Soon)", True, COLOR_UI_TEXT)
        screen.blit(social_text, (social_rect.x + 30, social_rect.y + 8))
