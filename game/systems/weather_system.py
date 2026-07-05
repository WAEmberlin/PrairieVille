"""Weather system affecting crop growth."""

import random
from game.core.constants import WEATHER_GROWTH
from game.core.events import EVT_WEATHER_CHANGED


WEATHER_TYPES = ["sunny", "cloudy", "rain", "thunderstorm"]
WEATHER_WEIGHTS = [40, 30, 20, 10]


class WeatherManager:
    """Manages weather state and crop growth modifiers."""

    def __init__(self, event_bus):
        self.events = event_bus
        self.current = "sunny"
        self.timer = 0.0
        self.change_interval = 120.0  # Change weather every 2 real minutes

    @property
    def growth_multiplier(self) -> float:
        return WEATHER_GROWTH.get(self.current, 1.0)

    @property
    def display_name(self) -> str:
        return self.current.capitalize()

    @property
    def icon_char(self) -> str:
        icons = {"sunny": "☀", "cloudy": "☁", "rain": "🌧", "thunderstorm": "⛈"}
        return icons.get(self.current, "☀")

    def update(self, dt: float):
        self.timer += dt
        if self.timer >= self.change_interval:
            self.timer = 0.0
            self._change_weather()

    def _change_weather(self):
        old = self.current
        self.current = random.choices(WEATHER_TYPES, weights=WEATHER_WEIGHTS)[0]
        if self.current != old:
            self.events.emit(EVT_WEATHER_CHANGED, weather=self.current)

    def to_dict(self) -> dict:
        return {"current": self.current, "timer": self.timer}

    @classmethod
    def from_dict(cls, data: dict, event_bus) -> "WeatherManager":
        wm = cls(event_bus)
        wm.current = data.get("current", "sunny")
        wm.timer = data.get("timer", 0.0)
        return wm
