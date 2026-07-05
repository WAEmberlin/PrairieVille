"""Main game class with event-driven game loop."""

import pygame

from game.core.constants import (
    FPS, SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, AUTOSAVE_INTERVAL,
)
from game.core.events import EventBus
from game.managers.asset_manager import AssetManager
from game.managers.scene_manager import SceneManager
from game.managers.save_manager import SaveManager
from game.scenes.farm_scene import FarmScene


class Game:
    """Central game controller."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"{TITLE} - Kansas Proud")
        self.clock = pygame.time.Clock()
        self.running = True

        self.events = EventBus()
        self.assets = AssetManager()
        self.assets.load_all()
        self.save_manager = SaveManager(self.events)
        self.scene_manager = SceneManager(self)

        self._autosave_timer = 0.0

        # Start with farm scene
        farm = FarmScene(self)
        self.scene_manager.push(farm)

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scene_manager.handle_event(event)

            self.scene_manager.update(dt)

            # Autosave
            self._autosave_timer += dt
            if self._autosave_timer >= AUTOSAVE_INTERVAL:
                self._autosave_timer = 0.0
                scene = self.scene_manager.current
                if scene and hasattr(scene, "get_save_data"):
                    self.save_manager.save(scene.get_save_data())

            self.screen.fill((135, 206, 235))
            self.scene_manager.draw(self.screen)
            pygame.display.flip()

        # Save on exit
        scene = self.scene_manager.current
        if scene and hasattr(scene, "get_save_data"):
            self.save_manager.save(scene.get_save_data())

        pygame.quit()
