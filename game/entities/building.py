"""Building and decoration entities."""

from dataclasses import dataclass
from game.core.config_loader import ConfigLoader


@dataclass
class BuildingInstance:
    """A placed building on the farm."""
    building_id: str
    origin_x: int
    origin_y: int

    @property
    def config(self) -> dict | None:
        return ConfigLoader.get_building(self.building_id)

    @property
    def width(self) -> int:
        cfg = self.config
        return cfg["width"] if cfg else 1

    @property
    def height(self) -> int:
        cfg = self.config
        return cfg["height"] if cfg else 1

    def occupies(self, x: int, y: int) -> bool:
        return (
            self.origin_x <= x < self.origin_x + self.width
            and self.origin_y <= y < self.origin_y + self.height
        )

    def to_dict(self) -> dict:
        return {
            "building_id": self.building_id,
            "origin_x": self.origin_x,
            "origin_y": self.origin_y,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BuildingInstance":
        return cls(
            building_id=data["building_id"],
            origin_x=data["origin_x"],
            origin_y=data["origin_y"],
        )


@dataclass
class DecorationInstance:
    """A placed decoration on the farm."""
    decoration_id: str
    x: int
    y: int

    @property
    def config(self) -> dict | None:
        decorations = ConfigLoader.get_decorations()
        return next((d for d in decorations if d["id"] == self.decoration_id), None)

    def to_dict(self) -> dict:
        return {
            "decoration_id": self.decoration_id,
            "x": self.x,
            "y": self.y,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DecorationInstance":
        return cls(
            decoration_id=data["decoration_id"],
            x=data["x"],
            y=data["y"],
        )
