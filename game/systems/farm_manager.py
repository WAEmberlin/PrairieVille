"""Farm grid management."""

from game.core.constants import STARTING_FARM_SIZE, PLOT_BUILDING, PLOT_DECORATION
from game.core.config_loader import ConfigLoader
from game.entities.farm_plot import FarmPlot
from game.entities.building import BuildingInstance, DecorationInstance
from game.entities.animal import AnimalInstance


class FarmManager:
    """Manages the farm grid, buildings, decorations, and animals."""

    def __init__(self):
        self.size = STARTING_FARM_SIZE
        self.plots: dict[tuple[int, int], FarmPlot] = {}
        self.buildings: list[BuildingInstance] = []
        self.decorations: list[DecorationInstance] = []
        self.animals: list[AnimalInstance] = []
        self._init_grid()

    def _init_grid(self):
        for x in range(self.size):
            for y in range(self.size):
                self.plots[(x, y)] = FarmPlot(x=x, y=y)

    def expand(self, new_size: int):
        old_size = self.size
        self.size = new_size
        for x in range(old_size, new_size):
            for y in range(new_size):
                self.plots[(x, y)] = FarmPlot(x=x, y=y)
        for x in range(old_size):
            for y in range(old_size, new_size):
                self.plots[(x, y)] = FarmPlot(x=x, y=y)

    def get_plot(self, x: int, y: int) -> FarmPlot | None:
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.plots.get((x, y))
        return None

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size

    def can_place_building(self, building_id: str, ox: int, oy: int) -> bool:
        cfg = ConfigLoader.get_building(building_id)
        if not cfg:
            return False
        w, h = cfg["width"], cfg["height"]
        for dx in range(w):
            for dy in range(h):
                px, py = ox + dx, oy + dy
                plot = self.get_plot(px, py)
                if not plot or plot.building_id or plot.crop:
                    return False
        return True

    def place_building(self, building_id: str, ox: int, oy: int) -> bool:
        if not self.can_place_building(building_id, ox, oy):
            return False
        cfg = ConfigLoader.get_building(building_id)
        w, h = cfg["width"], cfg["height"]
        building = BuildingInstance(building_id=building_id, origin_x=ox, origin_y=oy)
        self.buildings.append(building)
        for dx in range(w):
            for dy in range(h):
                plot = self.plots[(ox + dx, oy + dy)]
                plot.building_id = building_id
                plot.state = PLOT_BUILDING
                plot.building_origin = (dx == 0 and dy == 0)
        return True

    def can_place_decoration(self, x: int, y: int) -> bool:
        plot = self.get_plot(x, y)
        return plot is not None and not plot.building_id and not plot.decoration_id and plot.crop is None

    def place_decoration(self, decoration_id: str, x: int, y: int) -> bool:
        if not self.can_place_decoration(x, y):
            return False
        deco = DecorationInstance(decoration_id=decoration_id, x=x, y=y)
        self.decorations.append(deco)
        plot = self.plots[(x, y)]
        plot.decoration_id = decoration_id
        plot.state = PLOT_DECORATION
        return True

    def add_animal(self, animal_id: str, x: float, y: float) -> AnimalInstance:
        animal = AnimalInstance(animal_id=animal_id, x=x, y=y)
        self.animals.append(animal)
        return animal

    def get_building_at(self, x: int, y: int) -> BuildingInstance | None:
        for b in self.buildings:
            if b.occupies(x, y):
                return b
        return None

    def update(self, dt: float, growth_multiplier: float = 1.0):
        for animal in self.animals:
            if animal.config and animal.config.get("wander"):
                pasture = next(
                    (b for b in self.buildings if b.building_id == "bison_pasture"), None
                )
                if pasture:
                    bounds = (
                        pasture.origin_x + 0.5,
                        pasture.origin_y + 0.5,
                        pasture.origin_x + pasture.width - 0.5,
                        pasture.origin_y + pasture.height - 0.5,
                    )
                    animal.update_wander(dt, bounds)

    def to_dict(self) -> dict:
        return {
            "size": self.size,
            "plots": [p.to_dict() for p in self.plots.values()],
            "buildings": [b.to_dict() for b in self.buildings],
            "decorations": [d.to_dict() for d in self.decorations],
            "animals": [a.to_dict() for a in self.animals],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FarmManager":
        fm = cls.__new__(cls)
        fm.size = data.get("size", STARTING_FARM_SIZE)
        fm.plots = {}
        fm.buildings = [BuildingInstance.from_dict(b) for b in data.get("buildings", [])]
        fm.decorations = [DecorationInstance.from_dict(d) for d in data.get("decorations", [])]
        fm.animals = [AnimalInstance.from_dict(a) for a in data.get("animals", [])]
        for pd in data.get("plots", []):
            plot = FarmPlot.from_dict(pd)
            fm.plots[(plot.x, plot.y)] = plot
        # Fill missing plots
        for x in range(fm.size):
            for y in range(fm.size):
                if (x, y) not in fm.plots:
                    fm.plots[(x, y)] = FarmPlot(x=x, y=y)
        return fm
