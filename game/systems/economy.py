"""Economy system for purchases and income."""

from game.core.config_loader import ConfigLoader
from game.core.events import (
    EVT_COINS_CHANGED, EVT_CROP_HARVESTED, EVT_CROP_PLANTED,
    EVT_BUILDING_PLACED, EVT_FARM_EXPANDED,
)
from game.entities.player import Player


class EconomyManager:
    """Handles all coin transactions."""

    def __init__(self, player: Player, event_bus):
        self.player = player
        self.events = event_bus

    def buy_seeds(self, crop_id: str, quantity: int = 1) -> bool:
        cfg = ConfigLoader.get_crop(crop_id)
        if not cfg:
            return False
        total_cost = cfg["cost"] * quantity
        if not self.player.spend_coins(total_cost):
            return False
        seed_key = cfg["seed_inventory_key"]
        self.player.add_item(seed_key, quantity)
        self.events.emit(EVT_COINS_CHANGED, coins=self.player.coins)
        return True

    def plant_crop(self, crop_id: str) -> bool:
        cfg = ConfigLoader.get_crop(crop_id)
        if not cfg:
            return False
        seed_key = cfg["seed_inventory_key"]
        if not self.player.has_item(seed_key):
            if not self.buy_seeds(crop_id):
                return False
        if not self.player.remove_item(seed_key):
            return False
        self.player.stats["crops_planted"] += 1
        self.events.emit(EVT_CROP_PLANTED, crop_id=crop_id)
        return True

    def harvest_crop(self, crop_id: str) -> int:
        cfg = ConfigLoader.get_crop(crop_id)
        if not cfg:
            return 0
        value = cfg["harvest_value"]
        harvest_key = cfg["harvest_inventory_key"]
        self.player.add_item(harvest_key)
        self.player.stats["crops_harvested"] += 1
        self.player.add_xp(5)
        self.events.emit(EVT_CROP_HARVESTED, crop_id=crop_id, value=value)
        return value

    def get_sell_price(self, item_key: str) -> int | None:
        """Return coin value for one unit of an inventory item."""
        for crop in ConfigLoader.get_crops():
            if item_key == crop["seed_inventory_key"]:
                return max(1, crop["cost"] // 2)
            if item_key == crop["harvest_inventory_key"]:
                return crop["harvest_value"]
        for animal in ConfigLoader.get_animals():
            if item_key == animal["product"]:
                return animal["product_value"]
        return None

    def sell_item(self, item_key: str, quantity: int = 1) -> int:
        """Sell inventory items for coins. Returns total coins earned."""
        unit_price = self.get_sell_price(item_key)
        if unit_price is None or not self.player.has_item(item_key, quantity):
            return 0
        total = unit_price * quantity
        self.player.remove_item(item_key, quantity)
        self.player.add_coins(total)
        if item_key.startswith("crop_"):
            self.player.stats["coins_earned"] += total
        self.events.emit(EVT_COINS_CHANGED, coins=self.player.coins)
        return total

    def get_item_display_name(self, item_key: str) -> str:
        for crop in ConfigLoader.get_crops():
            if item_key == crop["seed_inventory_key"]:
                return f"{crop['name']} Seed"
            if item_key == crop["harvest_inventory_key"]:
                return crop["name"]
        for animal in ConfigLoader.get_animals():
            if item_key == animal["product"]:
                return animal["product"].replace("_", " ").title()
        return item_key.replace("_", " ").title()

    def buy_building(self, building_id: str) -> bool:
        cfg = ConfigLoader.get_building(building_id)
        if not cfg:
            return False
        if not self.player.spend_coins(cfg["cost"]):
            return False
        self.player.stats["buildings_built"] += 1
        self.player.add_xp(20)
        self.events.emit(EVT_BUILDING_PLACED, building_id=building_id)
        self.events.emit(EVT_COINS_CHANGED, coins=self.player.coins)
        return True

    def buy_decoration(self, decoration_id: str) -> bool:
        decorations = ConfigLoader.get_decorations()
        cfg = next((d for d in decorations if d["id"] == decoration_id), None)
        if not cfg:
            return False
        if not self.player.spend_coins(cfg["cost"]):
            return False
        self.player.owned_decorations.append(decoration_id)
        self.events.emit(EVT_COINS_CHANGED, coins=self.player.coins)
        return True

    def buy_expansion(self, new_size: int) -> bool:
        expansions = ConfigLoader.get_expansions()
        cfg = next((e for e in expansions if e["size"] == new_size), None)
        if not cfg:
            return False
        if not self.player.spend_coins(cfg["cost"]):
            return False
        self.player.add_xp(50)
        self.events.emit(EVT_FARM_EXPANDED, size=new_size)
        self.events.emit(EVT_COINS_CHANGED, coins=self.player.coins)
        return True

    def buy_animal(self, animal_id: str) -> bool:
        cfg = ConfigLoader.get_animal(animal_id)
        if not cfg:
            return False
        if not self.player.spend_coins(cfg["cost"]):
            return False
        self.player.stats["animals_owned"] += 1
        self.events.emit(EVT_COINS_CHANGED, coins=self.player.coins)
        return True

    def feed_animal(self, animal_id: str) -> bool:
        cfg = ConfigLoader.get_animal(animal_id)
        if not cfg:
            return False
        if not self.player.spend_coins(cfg["feed_cost"]):
            return False
        self.events.emit(EVT_COINS_CHANGED, coins=self.player.coins)
        return True

    def sell_product(self, product_key: str, value: int):
        self.player.add_coins(value)
        self.events.emit(EVT_COINS_CHANGED, coins=self.player.coins)
