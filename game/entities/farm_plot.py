"""Farm plot and crop entities."""

import time
from dataclasses import dataclass

from game.core.constants import PLOT_GRASS, PLOT_DIRT, PLOT_TILLED, PLOT_CROP
from game.core.config_loader import ConfigLoader


@dataclass
class CropInstance:
    """A crop planted on a plot."""
    crop_id: str
    planted_at: float
    stage: int = 0

    @property
    def config(self) -> dict | None:
        return ConfigLoader.get_crop(self.crop_id)

    def get_growth_progress(self, growth_multiplier: float = 1.0) -> float:
        cfg = self.config
        if not cfg:
            return 0.0
        elapsed = time.time() - self.planted_at
        growth_time = cfg["growth_seconds"] / growth_multiplier
        return min(1.0, elapsed / growth_time)

    def get_current_stage(self, growth_multiplier: float = 1.0) -> int:
        progress = self.get_growth_progress(growth_multiplier)
        cfg = self.config
        if not cfg:
            return 0
        stages = cfg["stages"]
        if progress >= 1.0:
            return stages
        return max(1, min(stages - 1, int(progress * (stages - 1)) + 1))

    def is_ready(self, growth_multiplier: float = 1.0) -> bool:
        return self.get_growth_progress(growth_multiplier) >= 1.0

    def to_dict(self) -> dict:
        return {
            "crop_id": self.crop_id,
            "planted_at": self.planted_at,
            "stage": self.stage,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CropInstance":
        return cls(
            crop_id=data["crop_id"],
            planted_at=data["planted_at"],
            stage=data.get("stage", 0),
        )


@dataclass
class FarmPlot:
    """Single tile on the farm grid."""
    x: int
    y: int
    state: str = PLOT_GRASS
    crop: CropInstance | None = None
    building_id: str | None = None
    decoration_id: str | None = None
    building_origin: bool = False

    def is_tillable(self) -> bool:
        return self.state in (PLOT_GRASS, PLOT_DIRT) and not self.building_id

    def is_plantable(self) -> bool:
        return self.state == PLOT_TILLED and self.crop is None and not self.building_id

    def is_harvestable(self, growth_multiplier: float = 1.0) -> bool:
        return self.crop is not None and self.crop.is_ready(growth_multiplier)

    def is_clearable(self) -> bool:
        return self.state != PLOT_GRASS or self.crop is not None or self.decoration_id is not None

    def clear_requires_confirmation(self) -> bool:
        return self.crop is not None or self.decoration_id is not None

    def till(self):
        if self.is_tillable():
            self.state = PLOT_TILLED

    def clear(self):
        self.crop = None
        self.decoration_id = None
        if not self.building_id:
            self.state = PLOT_GRASS

    def plant(self, crop_id: str):
        if self.is_plantable():
            self.crop = CropInstance(crop_id=crop_id, planted_at=time.time())
            self.state = PLOT_CROP

    def harvest(self, growth_multiplier: float = 1.0) -> str | None:
        if self.crop and self.crop.is_ready(growth_multiplier):
            crop_id = self.crop.crop_id
            self.crop = None
            self.state = PLOT_TILLED
            return crop_id
        return None

    def to_dict(self) -> dict:
        d = {"x": self.x, "y": self.y, "state": self.state}
        if self.crop:
            d["crop"] = self.crop.to_dict()
        if self.building_id:
            d["building_id"] = self.building_id
            d["building_origin"] = self.building_origin
        if self.decoration_id:
            d["decoration_id"] = self.decoration_id
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "FarmPlot":
        plot = cls(x=data["x"], y=data["y"], state=data.get("state", PLOT_GRASS))
        if "crop" in data:
            plot.crop = CropInstance.from_dict(data["crop"])
        plot.building_id = data.get("building_id")
        plot.building_origin = data.get("building_origin", False)
        plot.decoration_id = data.get("decoration_id")
        return plot
