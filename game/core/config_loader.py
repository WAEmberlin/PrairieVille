"""JSON configuration loader."""

import json
from pathlib import Path

from game.core.constants import DATA_DIR


class ConfigLoader:
    """Loads and caches JSON game configuration files."""

    _cache: dict[str, dict] = {}

    @classmethod
    def load(cls, filename: str) -> dict:
        if filename not in cls._cache:
            path = DATA_DIR / filename
            with open(path, encoding="utf-8") as f:
                cls._cache[filename] = json.load(f)
        return cls._cache[filename]

    @classmethod
    def get_crops(cls) -> list[dict]:
        return cls.load("crops.json")["crops"]

    @classmethod
    def get_crop(cls, crop_id: str) -> dict | None:
        return next((c for c in cls.get_crops() if c["id"] == crop_id), None)

    @classmethod
    def get_buildings(cls) -> list[dict]:
        return cls.load("buildings.json")["buildings"]

    @classmethod
    def get_building(cls, building_id: str) -> dict | None:
        return next((b for b in cls.get_buildings() if b["id"] == building_id), None)

    @classmethod
    def get_animals(cls) -> list[dict]:
        return cls.load("animals.json")["animals"]

    @classmethod
    def get_animal(cls, animal_id: str) -> dict | None:
        return next((a for a in cls.get_animals() if a["id"] == animal_id), None)

    @classmethod
    def get_decorations(cls) -> list[dict]:
        return cls.load("decorations.json")["decorations"]

    @classmethod
    def get_expansions(cls) -> list[dict]:
        return cls.load("decorations.json")["expansions"]

    @classmethod
    def clear_cache(cls):
        cls._cache.clear()
