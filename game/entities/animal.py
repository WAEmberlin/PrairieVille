"""Animal entities with wandering and production."""

import random
import time
from dataclasses import dataclass, field

from game.core.config_loader import ConfigLoader


@dataclass
class AnimalInstance:
    """A farm animal that produces resources."""
    animal_id: str
    x: float
    y: float
    last_fed: float = field(default_factory=time.time)
    last_product: float = field(default_factory=time.time)
    fed: bool = True
    wander_target: tuple[float, float] | None = None
    wander_timer: float = 0.0
    anim_frame: int = 0
    anim_timer: float = 0.0

    @property
    def config(self) -> dict | None:
        return ConfigLoader.get_animal(self.animal_id)

    def needs_feed(self) -> bool:
        cfg = self.config
        if not cfg:
            return False
        elapsed = time.time() - self.last_fed
        return elapsed >= cfg["feed_interval_seconds"]

    def can_produce(self) -> bool:
        cfg = self.config
        if not cfg or not self.fed:
            return False
        elapsed = time.time() - self.last_product
        return elapsed >= cfg["product_interval_seconds"]

    def feed(self) -> bool:
        self.last_fed = time.time()
        self.fed = True
        return True

    def collect_product(self) -> tuple[str, int] | None:
        cfg = self.config
        if not cfg or not self.can_produce():
            return None
        self.last_product = time.time()
        return cfg["product"], cfg["product_value"]

    def update_wander(self, dt: float, bounds: tuple[int, int, int, int]):
        """Update wandering behavior for bison."""
        cfg = self.config
        if not cfg or not cfg.get("wander"):
            return

        self.anim_timer += dt
        if self.anim_timer >= 0.3:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % 4

        self.wander_timer -= dt
        if self.wander_timer <= 0 or self.wander_target is None:
            min_x, min_y, max_x, max_y = bounds
            self.wander_target = (
                random.uniform(min_x, max_x),
                random.uniform(min_y, max_y),
            )
            self.wander_timer = random.uniform(2.0, 5.0)

        if self.wander_target:
            tx, ty = self.wander_target
            dx = tx - self.x
            dy = ty - self.y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > 0.5:
                speed = 1.5 * dt
                self.x += (dx / dist) * speed
                self.y += (dy / dist) * speed

    def to_dict(self) -> dict:
        return {
            "animal_id": self.animal_id,
            "x": self.x,
            "y": self.y,
            "last_fed": self.last_fed,
            "last_product": self.last_product,
            "fed": self.fed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AnimalInstance":
        return cls(
            animal_id=data["animal_id"],
            x=data["x"],
            y=data["y"],
            last_fed=data.get("last_fed", time.time()),
            last_product=data.get("last_product", time.time()),
            fed=data.get("fed", True),
        )
