"""Player state entity."""

from game.core.constants import STARTING_COINS, STARTING_XP, STARTING_LEVEL, XP_PER_LEVEL


class Player:
    """Tracks player coins, XP, level, inventory, and statistics."""

    def __init__(self):
        self.coins = STARTING_COINS
        self.xp = STARTING_XP
        self.level = STARTING_LEVEL
        self.inventory: dict[str, int] = {
            "seed_wheat": 5,
            "seed_corn": 3,
            "seed_soybeans": 1,
        }
        self.owned_decorations: list[str] = []
        self.owned_buildings: list[str] = []
        self.stats = {
            "crops_planted": 0,
            "crops_harvested": 0,
            "coins_earned": 0,
            "buildings_built": 0,
            "animals_owned": 0,
            "quests_completed": 0,
        }

    @property
    def xp_to_next_level(self) -> int:
        return self.level * XP_PER_LEVEL

    @property
    def xp_progress(self) -> float:
        needed = self.xp_to_next_level
        if needed == 0:
            return 1.0
        prev_threshold = (self.level - 1) * XP_PER_LEVEL if self.level > 1 else 0
        current = self.xp - prev_threshold
        total = needed - prev_threshold
        return min(1.0, current / total) if total > 0 else 1.0

    def add_coins(self, amount: int):
        self.coins += amount
        if amount > 0:
            self.stats["coins_earned"] += amount

    def spend_coins(self, amount: int) -> bool:
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False

    def add_xp(self, amount: int) -> bool:
        """Add XP and return True if leveled up."""
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_to_next_level:
            self.level += 1
            leveled = True
        return leveled

    def add_item(self, key: str, count: int = 1):
        self.inventory[key] = self.inventory.get(key, 0) + count

    def remove_item(self, key: str, count: int = 1) -> bool:
        current = self.inventory.get(key, 0)
        if current >= count:
            self.inventory[key] = current - count
            if self.inventory[key] == 0:
                del self.inventory[key]
            return True
        return False

    def has_item(self, key: str, count: int = 1) -> bool:
        return self.inventory.get(key, 0) >= count

    def to_dict(self) -> dict:
        return {
            "coins": self.coins,
            "xp": self.xp,
            "level": self.level,
            "inventory": dict(self.inventory),
            "owned_decorations": list(self.owned_decorations),
            "owned_buildings": list(self.owned_buildings),
            "stats": dict(self.stats),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        p = cls()
        p.coins = data.get("coins", STARTING_COINS)
        p.xp = data.get("xp", STARTING_XP)
        p.level = data.get("level", STARTING_LEVEL)
        p.inventory = data.get("inventory", {})
        p.owned_decorations = data.get("owned_decorations", [])
        p.owned_buildings = data.get("owned_buildings", [])
        p.stats = data.get("stats", p.stats)
        return p
