"""Game time, day/night cycle, and seasons."""

import random
from game.core.constants import (
    REAL_SECONDS_PER_GAME_HOUR, HOURS_PER_DAY, DAYS_PER_SEASON, SEASONS,
)
from game.core.events import EVT_SEASON_CHANGED


class TimeManager:
    """Manages in-game clock, day/night, and seasons."""

    def __init__(self, event_bus):
        self.events = event_bus
        self.game_hours = 8.0  # Start at 8 AM
        self.day = 1
        self.season_index = 0
        self.elapsed_real = 0.0

    @property
    def season(self) -> str:
        return SEASONS[self.season_index]

    @property
    def hour(self) -> int:
        return int(self.game_hours) % HOURS_PER_DAY

    @property
    def minute(self) -> int:
        frac = self.game_hours - int(self.game_hours)
        return int(frac * 60)

    @property
    def time_string(self) -> str:
        h = self.hour
        m = self.minute
        ampm = "AM" if h < 12 else "PM"
        display_h = h % 12 or 12
        return f"{display_h}:{m:02d} {ampm}"

    @property
    def date_string(self) -> str:
        return f"{self.season} Day {self.day}"

    @property
    def is_daytime(self) -> bool:
        return 6 <= self.hour < 20

    @property
    def day_night_factor(self) -> float:
        """0.0 = full night, 1.0 = full day."""
        h = self.game_hours % HOURS_PER_DAY
        if 6 <= h < 8:
            return (h - 6) / 2
        elif 8 <= h < 18:
            return 1.0
        elif 18 <= h < 20:
            return 1.0 - (h - 18) / 2
        else:
            return 0.3

    @property
    def sky_color(self) -> tuple[int, int, int]:
        factor = self.day_night_factor
        night = (25, 25, 60)
        day = (135, 206, 235)
        sunset = (255, 140, 60)
        h = self.game_hours % HOURS_PER_DAY
        if 18 <= h < 20:
            t = (h - 18) / 2
            return (
                int(day[0] + (sunset[0] - day[0]) * t * (1 - factor)),
                int(day[1] + (sunset[1] - day[1]) * t * (1 - factor)),
                int(day[2] + (sunset[2] - day[2]) * t * (1 - factor)),
            )
        return (
            int(night[0] + (day[0] - night[0]) * factor),
            int(night[1] + (day[1] - night[1]) * factor),
            int(night[2] + (day[2] - night[2]) * factor),
        )

    def update(self, dt: float):
        self.elapsed_real += dt
        hours_passed = dt / REAL_SECONDS_PER_GAME_HOUR
        self.game_hours += hours_passed

        while self.game_hours >= HOURS_PER_DAY:
            self.game_hours -= HOURS_PER_DAY
            self.day += 1
            if self.day > DAYS_PER_SEASON:
                self.day = 1
                old_season = self.season
                self.season_index = (self.season_index + 1) % len(SEASONS)
                if self.season != old_season:
                    self.events.emit(EVT_SEASON_CHANGED, season=self.season)

    def to_dict(self) -> dict:
        return {
            "game_hours": self.game_hours,
            "day": self.day,
            "season_index": self.season_index,
        }

    @classmethod
    def from_dict(cls, data: dict, event_bus) -> "TimeManager":
        tm = cls(event_bus)
        tm.game_hours = data.get("game_hours", 8.0)
        tm.day = data.get("day", 1)
        tm.season_index = data.get("season_index", 0)
        return tm
