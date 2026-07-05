"""Event types and event bus for decoupled communication."""

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class GameEvent:
    type: str
    data: dict = field(default_factory=dict)


class EventBus:
    """Simple publish/subscribe event bus."""

    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        self._listeners.setdefault(event_type, []).append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        if event_type in self._listeners:
            self._listeners[event_type] = [
                cb for cb in self._listeners[event_type] if cb != callback
            ]

    def emit(self, event_type: str, **data):
        event = GameEvent(type=event_type, data=data)
        for callback in self._listeners.get(event_type, []):
            callback(event)

    def clear(self):
        self._listeners.clear()


# Event type constants
EVT_CROP_PLANTED = "crop_planted"
EVT_CROP_HARVESTED = "crop_harvested"
EVT_COINS_CHANGED = "coins_changed"
EVT_XP_GAINED = "xp_gained"
EVT_LEVEL_UP = "level_up"
EVT_BUILDING_PLACED = "building_placed"
EVT_DECORATION_PLACED = "decoration_placed"
EVT_QUEST_COMPLETED = "quest_completed"
EVT_QUEST_PROGRESS = "quest_progress"
EVT_FARM_EXPANDED = "farm_expanded"
EVT_ANIMAL_FED = "animal_fed"
EVT_ANIMAL_PRODUCT = "animal_product"
EVT_SAVE = "save"
EVT_LOAD = "load"
EVT_TOOL_CHANGED = "tool_changed"
EVT_WEATHER_CHANGED = "weather_changed"
EVT_SEASON_CHANGED = "season_changed"
