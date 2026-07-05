"""Scene stack manager."""

import pygame


class SceneManager:
    """Manages a stack of game scenes."""

    def __init__(self, game):
        self.game = game
        self._stack: list = []

    @property
    def current(self):
        return self._stack[-1] if self._stack else None

    def push(self, scene):
        self._stack.append(scene)
        scene.on_enter()

    def pop(self):
        if self._stack:
            scene = self._stack.pop()
            scene.on_exit()
            return scene
        return None

    def replace(self, scene):
        if self._stack:
            self._stack[-1].on_exit()
            self._stack[-1] = scene
        else:
            self._stack.append(scene)
        scene.on_enter()

    def handle_event(self, event: pygame.event.Event):
        if self.current:
            self.current.handle_event(event)

    def update(self, dt: float):
        if self.current:
            self.current.update(dt)

    def draw(self, screen: pygame.Surface):
        if self.current:
            self.current.draw(screen)
