"""Right sidebar with shop, crops, and buildings."""

import pygame
from game.core.constants import (
    SIDEBAR_WIDTH, TOP_BAR_HEIGHT, BOTTOM_BAR_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_UI_BG, COLOR_UI_BORDER, COLOR_UI_TEXT, COLOR_UI_ACCENT, COLOR_UI_HIGHLIGHT,
)
from game.core.config_loader import ConfigLoader
from game.ui.widgets import Panel
from game.ui.icon_draw import blit_icon


class RightSidebar(Panel):
    """Right panel: shop items."""

    ITEM_HEIGHT = 36

    def __init__(self, on_item_selected, assets=None):
        h = SCREEN_HEIGHT - TOP_BAR_HEIGHT - BOTTOM_BAR_HEIGHT
        x = SCREEN_WIDTH - SIDEBAR_WIDTH
        super().__init__(x, TOP_BAR_HEIGHT, SIDEBAR_WIDTH, h)
        self.on_item_selected = on_item_selected
        self.assets = assets
        self.tab = "crops"
        self.tabs = ["crops", "buildings", "shop", "expand"]
        self.tab_labels = {"crops": "Seeds", "buildings": "Build", "shop": "Shop", "expand": "Land"}
        self.scroll = 0
        self._items: list[tuple[str, str, int]] = []

    def set_tab(self, tab: str):
        self.tab = tab
        self.scroll = 0
        self._refresh_items()

    def _icon_for_item(self, item_id: str) -> pygame.Surface | None:
        if not self.assets:
            return None
        if self.tab == "expand":
            return self.assets.get_icon("gravel_road")
        return self.assets.get_icon_for_entity(item_id)

    def _refresh_items(self):
        self._items = []
        if self.tab == "crops":
            for c in ConfigLoader.get_crops():
                self._items.append((c["id"], f"{c['name']} ${c['cost']}", c["cost"]))
        elif self.tab == "buildings":
            for b in ConfigLoader.get_buildings():
                self._items.append((b["id"], f"{b['name']} ${b['cost']}", b["cost"]))
        elif self.tab == "shop":
            for d in ConfigLoader.get_decorations():
                self._items.append((d["id"], f"{d['name']} ${d['cost']}", d["cost"]))
            for a in ConfigLoader.get_animals():
                self._items.append((a["id"], f"{a['name']} ${a['cost']}", a["cost"]))
        elif self.tab == "expand":
            for e in ConfigLoader.get_expansions():
                if e["cost"] > 0:
                    self._items.append((str(e["size"]), f"{e['label']} ${e['cost']}", e["cost"]))

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            tab_h = 28
            tab_w = SIDEBAR_WIDTH // len(self.tabs)
            for i, tab in enumerate(self.tabs):
                tab_rect = pygame.Rect(self.rect.x + i * tab_w, self.rect.y, tab_w, tab_h)
                if tab_rect.collidepoint(event.pos):
                    self.set_tab(tab)
                    return True

            item_y = self.rect.y + 32
            for i, (item_id, label, cost) in enumerate(self._items[self.scroll:]):
                item_rect = pygame.Rect(
                    self.rect.x + 4, item_y + i * self.ITEM_HEIGHT,
                    SIDEBAR_WIDTH - 8, self.ITEM_HEIGHT - 2,
                )
                if item_rect.collidepoint(event.pos):
                    if self.on_item_selected:
                        self.on_item_selected(self.tab, item_id)
                    return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll = max(0, self.scroll - 1)
                return True
            elif event.button == 5:
                max_visible = max(1, (self.rect.height - 40) // self.ITEM_HEIGHT)
                self.scroll = min(max(0, len(self._items) - max_visible), self.scroll + 1)
                return True
        return False

    def draw(self, screen, font):
        pygame.draw.rect(screen, COLOR_UI_BG, self.rect)
        pygame.draw.line(screen, COLOR_UI_BORDER,
                         (self.rect.x, TOP_BAR_HEIGHT),
                         (self.rect.x, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT), 2)

        tab_h = 28
        tab_w = SIDEBAR_WIDTH // len(self.tabs)
        for i, tab in enumerate(self.tabs):
            tab_rect = pygame.Rect(self.rect.x + i * tab_w, self.rect.y, tab_w, tab_h)
            bg = COLOR_UI_ACCENT if tab == self.tab else COLOR_UI_BG
            pygame.draw.rect(screen, bg, tab_rect)
            label = font.render(self.tab_labels[tab][:5], True, COLOR_UI_TEXT)
            label_rect = label.get_rect(center=tab_rect.center)
            screen.blit(label, label_rect)

        if not self._items:
            self._refresh_items()

        item_y = self.rect.y + 32
        max_items = (self.rect.height - 40) // self.ITEM_HEIGHT
        for i, (item_id, label, cost) in enumerate(self._items[self.scroll:self.scroll + max_items]):
            item_rect = pygame.Rect(
                self.rect.x + 4, item_y + i * self.ITEM_HEIGHT,
                SIDEBAR_WIDTH - 8, self.ITEM_HEIGHT - 2,
            )
            pygame.draw.rect(screen, COLOR_UI_HIGHLIGHT, item_rect, border_radius=3)
            icon = self._icon_for_item(item_id)
            text_x = blit_icon(screen, icon, item_rect, size=28)
            text = font.render(label[:18], True, COLOR_UI_TEXT)
            screen.blit(text, (text_x, item_rect.y + (item_rect.height - text.get_height()) // 2))

        hint_y = self.rect.bottom - 24
        hint = font.render("Click to select", True, COLOR_UI_TEXT)
        screen.blit(hint, (self.rect.x + 8, hint_y))
