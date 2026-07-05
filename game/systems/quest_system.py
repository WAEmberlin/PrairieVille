"""Quest generation and tracking."""

import random
from dataclasses import dataclass, field

from game.core.events import (
    EVT_CROP_PLANTED, EVT_CROP_HARVESTED, EVT_COINS_CHANGED,
    EVT_BUILDING_PLACED, EVT_QUEST_COMPLETED, EVT_QUEST_PROGRESS,
    EVT_FARM_EXPANDED,
)
from game.core.config_loader import ConfigLoader


@dataclass
class Quest:
    """A single quest task."""
    id: str
    description: str
    quest_type: str
    target: str | int
    current: int = 0
    reward_coins: int = 0
    reward_xp: int = 0
    reward_item: str | None = None
    completed: bool = False
    crop_id: str | None = None

    @property
    def progress(self) -> float:
        if isinstance(self.target, int) and self.target > 0:
            return min(1.0, self.current / self.target)
        return 1.0 if self.completed else 0.0

    @property
    def progress_text(self) -> str:
        if isinstance(self.target, int):
            return f"{self.current}/{self.target}"
        return "Done" if self.completed else "Pending"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "quest_type": self.quest_type,
            "target": self.target,
            "current": self.current,
            "reward_coins": self.reward_coins,
            "reward_xp": self.reward_xp,
            "reward_item": self.reward_item,
            "completed": self.completed,
            "crop_id": self.crop_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quest":
        return cls(**data)


QUEST_TEMPLATES = [
    {"type": "plant", "target_key": "crop_id", "targets": ["wheat", "corn", "soybeans"],
     "counts": [5, 10, 15], "desc": "Plant {n} {crop}", "coins": 50, "xp": 25},
    {"type": "harvest", "target_key": "crop_id", "targets": ["wheat", "corn", "soybeans"],
     "counts": [3, 5, 8], "desc": "Harvest {n} {crop}", "coins": 75, "xp": 30},
    {"type": "earn_coins", "targets": [200, 500, 1000],
     "desc": "Earn {n} coins", "coins": 100, "xp": 50},
    {"type": "buy_building", "targets": ["windmill", "barn", "silo", "farmhouse"],
     "desc": "Buy a {building}", "coins": 150, "xp": 40},
    {"type": "raise_bison", "counts": [1, 3, 5],
     "desc": "Raise {n} bison", "coins": 200, "xp": 60},
]


class QuestManager:
    """Generates and tracks player quests."""

    MAX_ACTIVE = 3

    def __init__(self, player, event_bus):
        self.player = player
        self.events = event_bus
        self.active_quests: list[Quest] = []
        self.completed_quests: list[str] = []
        self._quest_counter = 0
        self._subscribe_events()
        self._generate_initial_quests()

    def _subscribe_events(self):
        self.events.subscribe(EVT_CROP_PLANTED, self._on_crop_planted)
        self.events.subscribe(EVT_CROP_HARVESTED, self._on_crop_harvested)
        self.events.subscribe(EVT_COINS_CHANGED, self._on_coins_changed)
        self.events.subscribe(EVT_BUILDING_PLACED, self._on_building_placed)

    def _generate_initial_quests(self):
        while len(self.active_quests) < self.MAX_ACTIVE:
            self.generate_quest()

    def generate_quest(self) -> Quest | None:
        if len(self.active_quests) >= self.MAX_ACTIVE:
            return None
        template = random.choice(QUEST_TEMPLATES)
        self._quest_counter += 1
        qtype = template["type"]

        if qtype in ("plant", "harvest"):
            crop = random.choice(template["targets"])
            count = random.choice(template["counts"])
            crop_name = ConfigLoader.get_crop(crop)["name"]
            desc = template["desc"].format(n=count, crop=crop_name)
            quest = Quest(
                id=f"quest_{self._quest_counter}",
                description=desc,
                quest_type=qtype,
                target=count,
                current=0,
                reward_coins=template["coins"],
                reward_xp=template["xp"],
                crop_id=crop,
            )

        elif qtype == "earn_coins":
            amount = random.choice(template["targets"])
            desc = template["desc"].format(n=amount)
            quest = Quest(
                id=f"quest_{self._quest_counter}",
                description=desc,
                quest_type=qtype,
                target=amount,
                current=self.player.stats.get("coins_earned", 0),
                reward_coins=template["coins"],
                reward_xp=template["xp"],
            )

        elif qtype == "buy_building":
            building = random.choice(template["targets"])
            bname = ConfigLoader.get_building(building)["name"]
            desc = template["desc"].format(building=bname)
            quest = Quest(
                id=f"quest_{self._quest_counter}",
                description=desc,
                quest_type=qtype,
                target=building,
                reward_coins=template["coins"],
                reward_xp=template["xp"],
            )

        elif qtype == "raise_bison":
            count = random.choice(template["counts"])
            desc = template["desc"].format(n=count)
            quest = Quest(
                id=f"quest_{self._quest_counter}",
                description=desc,
                quest_type=qtype,
                target=count,
                current=0,
                reward_coins=template["coins"],
                reward_xp=template["xp"],
            )
        else:
            return None

        self.active_quests.append(quest)
        return quest

    def _complete_quest(self, quest: Quest):
        quest.completed = True
        self.player.add_coins(quest.reward_coins)
        self.player.add_xp(quest.reward_xp)
        if quest.reward_item:
            self.player.add_item(quest.reward_item)
        self.player.stats["quests_completed"] += 1
        self.completed_quests.append(quest.id)
        self.active_quests.remove(quest)
        self.events.emit(EVT_QUEST_COMPLETED, quest_id=quest.id)
        self.generate_quest()

    def _on_crop_planted(self, event):
        crop_id = event.data.get("crop_id")
        for q in self.active_quests:
            if q.quest_type == "plant" and q.crop_id == crop_id:
                q.current += 1
                self.events.emit(EVT_QUEST_PROGRESS, quest_id=q.id)
                if q.current >= q.target:
                    self._complete_quest(q)

    def _on_crop_harvested(self, event):
        crop_id = event.data.get("crop_id")
        for q in self.active_quests:
            if q.quest_type == "harvest" and q.crop_id == crop_id:
                q.current += 1
                self.events.emit(EVT_QUEST_PROGRESS, quest_id=q.id)
                if q.current >= q.target:
                    self._complete_quest(q)

    def _on_coins_changed(self, event):
        earned = self.player.stats.get("coins_earned", 0)
        for q in self.active_quests:
            if q.quest_type == "earn_coins":
                q.current = earned
                self.events.emit(EVT_QUEST_PROGRESS, quest_id=q.id)
                if q.current >= q.target:
                    self._complete_quest(q)

    def _on_building_placed(self, event):
        building_id = event.data.get("building_id")
        for q in self.active_quests:
            if q.quest_type == "buy_building" and q.target == building_id:
                self._complete_quest(q)

    def on_bison_added(self):
        for q in self.active_quests:
            if q.quest_type == "raise_bison":
                q.current += 1
                self.events.emit(EVT_QUEST_PROGRESS, quest_id=q.id)
                if q.current >= q.target:
                    self._complete_quest(q)

    def to_dict(self) -> dict:
        return {
            "active": [q.to_dict() for q in self.active_quests],
            "completed": list(self.completed_quests),
            "counter": self._quest_counter,
        }

    @classmethod
    def from_dict(cls, data: dict, player, event_bus) -> "QuestManager":
        qm = cls(player, event_bus)
        qm.active_quests = [Quest.from_dict(q) for q in data.get("active", [])]
        qm.completed_quests = data.get("completed", [])
        qm._quest_counter = data.get("counter", 0)
        if not qm.active_quests:
            qm._generate_initial_quests()
        return qm
