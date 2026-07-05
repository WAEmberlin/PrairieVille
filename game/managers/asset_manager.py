"""Asset loading and caching."""

import pygame
from pathlib import Path

from game.core.constants import ASSETS_DIR, TILE_WIDTH, TILE_HEIGHT
from game.core.icon_registry import icon_for, icon_for_tool


class AssetManager:
    """Loads and caches sprites, fonts, sounds, and UI icons."""

    def __init__(self):
        self.sprites: dict[str, pygame.Surface] = {}
        self.icons: dict[str, pygame.Surface] = {}
        self.sprite_sheets: dict[str, list[pygame.Surface]] = {}
        self.fonts: dict[int, pygame.font.Font] = {}
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self._loaded = False

    def load_all(self):
        if self._loaded:
            return
        self._load_icons()
        self._load_sprites()
        self._load_fonts()
        self._load_sounds()
        self._loaded = True

    def _load_icons(self):
        icon_dir = ASSETS_DIR / "ui" / "icons"
        if not icon_dir.exists():
            return
        for path in icon_dir.glob("*.png"):
            try:
                surf = pygame.image.load(str(path)).convert_alpha()
                self.icons[path.stem] = surf
            except pygame.error:
                pass

    def _load_sprites(self):
        sprite_dir = ASSETS_DIR / "sprites"
        if not sprite_dir.exists():
            return
        for path in sprite_dir.rglob("*.png"):
            key = str(path.relative_to(sprite_dir)).replace("\\", "/").replace(".png", "")
            try:
                surf = pygame.image.load(str(path)).convert_alpha()
                self.sprites[key] = surf
            except pygame.error:
                pass

        ui_dir = ASSETS_DIR / "ui"
        if ui_dir.exists():
            for path in ui_dir.rglob("*.png"):
                if "icons" in path.parts:
                    continue
                key = "ui/" + str(path.relative_to(ui_dir)).replace("\\", "/").replace(".png", "")
                try:
                    surf = pygame.image.load(str(path)).convert_alpha()
                    self.sprites[key] = surf
                except pygame.error:
                    pass

    def _load_fonts(self):
        font_path = ASSETS_DIR / "fonts"
        default_font = None
        if font_path.exists():
            for f in font_path.glob("*.ttf"):
                default_font = str(f)
                break
        for size in (12, 14, 16, 18, 20, 24, 28, 32):
            if default_font:
                self.fonts[size] = pygame.font.Font(default_font, size)
            else:
                self.fonts[size] = pygame.font.SysFont("arial", size)

    def _load_sounds(self):
        audio_dir = ASSETS_DIR / "audio"
        if not audio_dir.exists():
            return
        for path in audio_dir.glob("*.wav"):
            try:
                self.sounds[path.stem] = pygame.mixer.Sound(str(path))
            except pygame.error:
                pass

    def get_icon(self, name: str) -> pygame.Surface | None:
        return self.icons.get(name)

    def get_icon_for_entity(self, entity_id: str) -> pygame.Surface | None:
        icon_name = icon_for(entity_id)
        if icon_name:
            return self.get_icon(icon_name)
        return None

    def get_icon_for_tool(self, tool_id: str) -> pygame.Surface | None:
        icon_name = icon_for_tool(tool_id)
        if icon_name:
            return self.get_icon(icon_name)
        return None

    def get_sprite(self, key: str, fallback_color: tuple = (200, 200, 200)) -> pygame.Surface:
        if key in self.sprites:
            return self.sprites[key]
        surf = pygame.Surface((64, 32), pygame.SRCALPHA)
        surf.fill(fallback_color)
        return surf

    def _fit_sprite(self, source: pygame.Surface, width: int, height: int) -> pygame.Surface:
        """Scale a sprite to fit within the target bounds."""
        sw, sh = source.get_size()
        scale = min(width / sw, height / sh)
        new_w = max(1, int(sw * scale))
        new_h = max(1, int(sh * scale))
        return pygame.transform.smoothscale(source, (new_w, new_h))

    def get_font(self, size: int = 16) -> pygame.font.Font:
        return self.fonts.get(size, pygame.font.SysFont("arial", size))

    def play_sound(self, name: str):
        if name in self.sounds:
            self.sounds[name].play()

    def get_crop_sprite(self, crop_id: str, stage: int) -> pygame.Surface:
        if stage >= 4:
            icon = self.get_icon_for_entity(crop_id)
            if icon:
                return self._fit_sprite(icon, 32, 48)
        key = f"crops/{crop_id}_stage_{stage}"
        return self.get_sprite(key, (100, 180, 50))

    def get_terrain_sprite(self, terrain_type: str) -> pygame.Surface:
        if terrain_type == "path":
            icon = self.get_icon("gravel_road")
            if icon:
                return self._fit_sprite(icon, TILE_WIDTH, TILE_HEIGHT)
        return self.get_sprite(f"terrain/{terrain_type}", (107, 142, 35))

    def get_building_sprite(self, building_id: str) -> pygame.Surface:
        icon = self.get_icon_for_entity(building_id)
        if icon:
            return self._fit_sprite(icon, 96, 80)
        return self.get_sprite(f"buildings/{building_id}", (160, 82, 45))

    def get_decoration_sprite(self, deco_id: str) -> pygame.Surface:
        icon = self.get_icon_for_entity(deco_id)
        if icon:
            return self._fit_sprite(icon, 32, 36)
        return self.get_sprite(f"decorations/{deco_id}", (100, 150, 80))

    def get_animal_sprite(self, animal_id: str, frame: int = 0) -> pygame.Surface:
        icon = self.get_icon_for_entity(animal_id)
        if icon:
            return self._fit_sprite(icon, 32, 24)
        return self.get_sprite(f"animals/{animal_id}_{frame}", (80, 60, 40))
