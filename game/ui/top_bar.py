"""Top bar showing coins, level, XP, date, season, weather."""

import pygame
from game.core.constants import (
    TOP_BAR_HEIGHT, SCREEN_WIDTH, COLOR_UI_BG, COLOR_UI_BORDER,
    COLOR_UI_TEXT, COLOR_COIN, COLOR_XP, COLOR_UI_ACCENT,
)
from game.ui.widgets import Widget


class TopBar(Widget):
    """Game top status bar."""

    def __init__(self):
        super().__init__(0, 0, SCREEN_WIDTH, TOP_BAR_HEIGHT)
        self.coins = 0
        self.level = 1
        self.xp_progress = 0.0
        self.date_str = ""
        self.season_str = ""
        self.weather_str = ""
        self.time_str = ""

    def update_stats(self, player, time_mgr, weather_mgr):
        self.coins = player.coins
        self.level = player.level
        self.xp_progress = player.xp_progress
        self.date_str = time_mgr.date_string
        self.time_str = time_mgr.time_string
        self.season_str = time_mgr.season
        self.weather_str = weather_mgr.display_name

    def draw(self, screen, font):
        pygame.draw.rect(screen, COLOR_UI_BG, self.rect)
        pygame.draw.line(screen, COLOR_UI_BORDER, (0, TOP_BAR_HEIGHT - 1),
                         (SCREEN_WIDTH, TOP_BAR_HEIGHT - 1), 2)

        x = 12
        y = (TOP_BAR_HEIGHT - 16) // 2

        # Coins — label + value for clarity
        label = font.render("Coins:", True, COLOR_UI_TEXT)
        screen.blit(label, (x, y))
        x += label.get_width() + 6
        coin_text = font.render(f"{self.coins:,}", True, COLOR_COIN)
        # Dark outline for readability on light background
        shadow = font.render(f"{self.coins:,}", True, (80, 60, 20))
        screen.blit(shadow, (x + 1, y + 1))
        screen.blit(coin_text, (x, y))
        x += coin_text.get_width() + 20

        # Level
        level_text = font.render(f"Lv.{self.level}", True, COLOR_UI_ACCENT)
        screen.blit(level_text, (x, y))
        x += level_text.get_width() + 12

        # XP bar
        bar_w = 100
        bar_h = 12
        bar_y = (TOP_BAR_HEIGHT - bar_h) // 2
        pygame.draw.rect(screen, (200, 200, 200), (x, bar_y, bar_w, bar_h), border_radius=3)
        fill_w = int(bar_w * self.xp_progress)
        if fill_w > 0:
            pygame.draw.rect(screen, COLOR_XP, (x, bar_y, fill_w, bar_h), border_radius=3)
        x += bar_w + 20

        # Time and date (center)
        center_x = SCREEN_WIDTH // 2
        time_surf = font.render(f"{self.time_str}  |  {self.date_str}", True, COLOR_UI_TEXT)
        time_rect = time_surf.get_rect(centerx=center_x, centery=TOP_BAR_HEIGHT // 2)
        screen.blit(time_surf, time_rect)

        # Season and weather (right)
        right_text = f"{self.season_str}  |  {self.weather_str}"
        right_surf = font.render(right_text, True, COLOR_UI_TEXT)
        screen.blit(right_surf, (SCREEN_WIDTH - right_surf.get_width() - 12, y))
