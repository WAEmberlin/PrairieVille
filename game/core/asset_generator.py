"""Procedural asset generator for PrairieVille placeholder art."""

import math
import struct
import wave
from pathlib import Path

import pygame

from game.core.constants import ASSETS_DIR, ROOT_DIR


def _ensure_dirs():
    for sub in ("sprites/terrain", "sprites/crops", "sprites/buildings",
                "sprites/decorations", "sprites/animals", "ui", "audio", "fonts"):
        (ASSETS_DIR / sub).mkdir(parents=True, exist_ok=True)


def _draw_iso_tile(surface: pygame.Surface, color: tuple, highlight: tuple = None):
    """Draw an isometric diamond tile."""
    w, h = surface.get_size()
    cx, cy = w // 2, h // 2
    points = [(cx, 0), (w, cy), (cx, h), (0, cy)]
    pygame.draw.polygon(surface, color, points)
    if highlight:
        # Top-left highlight
        hl_points = [(cx, 2), (w - 4, cy), (cx, cy), (4, cy)]
        hl_color = tuple(min(255, c + 30) for c in color)
        pygame.draw.polygon(surface, hl_color, hl_points)
    # Outline
    pygame.draw.polygon(surface, tuple(max(0, c - 40) for c in color), points, 1)


def generate_terrain():
    tiles = {
        "grass": (107, 142, 35),
        "dirt": (139, 90, 43),
        "tilled": (101, 67, 33),
        "path": (160, 130, 90),
    }
    for name, color in tiles.items():
        surf = pygame.Surface((64, 32), pygame.SRCALPHA)
        _draw_iso_tile(surf, color, highlight=True)
        if name == "grass":
            # Add grass tufts
            for i in range(5):
                gx = 10 + i * 12
                gy = 14 + (i % 2) * 4
                pygame.draw.line(surf, (80, 120, 30), (gx, gy + 4), (gx, gy), 2)
        elif name == "tilled":
            for i in range(4):
                y = 10 + i * 5
                pygame.draw.line(surf, (80, 50, 20), (8, y), (56, y), 1)
        path = ASSETS_DIR / "sprites" / "terrain" / f"{name}.png"
        pygame.image.save(surf, str(path))


def generate_crops():
    crops = {
        "wheat": (218, 185, 80),
        "corn": (255, 215, 0),
        "soybeans": (144, 190, 109),
    }
    for crop_id, base_color in crops.items():
        for stage in range(1, 5):
            surf = pygame.Surface((32, 48), pygame.SRCALPHA)
            h = 8 + stage * 8
            # Stem
            pygame.draw.line(surf, (60, 100, 30), (16, 44), (16, 44 - h), 2)
            if stage == 1:
                # Sprout
                pygame.draw.circle(surf, (100, 180, 50), (16, 44 - h), 4)
            elif stage == 2:
                pygame.draw.ellipse(surf, base_color, (10, 44 - h - 4, 12, 8))
            elif stage == 3:
                for dx in (-6, 0, 6):
                    pygame.draw.ellipse(surf, base_color, (16 + dx - 4, 44 - h, 8, 12))
            else:
                # Ready - full plant
                for dx in (-8, -3, 3, 8):
                    pygame.draw.ellipse(surf, base_color, (16 + dx - 5, 44 - h - 4, 10, 16))
                # Sparkle for ready
                pygame.draw.circle(surf, (255, 255, 200), (24, 44 - h - 8), 3)
            path = ASSETS_DIR / "sprites" / "crops" / f"{crop_id}_stage_{stage}.png"
            pygame.image.save(surf, str(path))


def generate_buildings():
    buildings = {
        "farmhouse": ((180, 80, 50), (160, 60, 40), 64, 80),
        "barn": ((160, 40, 30), (120, 30, 20), 96, 64),
        "silo": ((180, 180, 190), (140, 140, 150), 32, 80),
        "windmill": ((200, 200, 210), (100, 100, 110), 48, 80),
        "bison_pasture": ((120, 160, 80), (80, 120, 50), 96, 64),
    }
    for bid, (color, dark, w, h) in buildings.items():
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        if bid == "farmhouse":
            pygame.draw.rect(surf, color, (8, 30, 48, 50))
            pygame.draw.polygon(surf, dark, [(4, 30), (32, 8), (60, 30)])
            pygame.draw.rect(surf, (100, 60, 30), (24, 50, 16, 30))
        elif bid == "barn":
            pygame.draw.rect(surf, color, (8, 20, 80, 44))
            pygame.draw.polygon(surf, dark, [(4, 20), (48, 4), (92, 20)])
            pygame.draw.rect(surf, (80, 20, 10), (36, 40, 24, 24))
        elif bid == "silo":
            pygame.draw.rect(surf, color, (8, 10, 16, 70), border_radius=8)
            pygame.draw.ellipse(surf, dark, (6, 4, 20, 12))
        elif bid == "windmill":
            pygame.draw.rect(surf, (120, 80, 40), (20, 40, 8, 40))
            cx, cy = 24, 36
            for angle in range(0, 360, 120):
                rad = math.radians(angle)
                ex = cx + int(math.cos(rad) * 20)
                ey = cy + int(math.sin(rad) * 20)
                pygame.draw.line(surf, color, (cx, cy), (ex, ey), 3)
        elif bid == "bison_pasture":
            pygame.draw.rect(surf, (100, 140, 60), (4, 16, 88, 48), border_radius=4)
            for i in range(0, 88, 12):
                pygame.draw.line(surf, (160, 130, 80), (4 + i, 16), (4 + i, 64), 2)
        path = ASSETS_DIR / "sprites" / "buildings" / f"{bid}.png"
        pygame.image.save(surf, str(path))


def generate_decorations():
    decos = {
        "fence": lambda s: pygame.draw.rect(s, (160, 130, 80), (4, 8, 24, 20)) or
                           pygame.draw.line(s, (140, 110, 60), (8, 8), (8, 28), 2),
        "tree": lambda s: (pygame.draw.rect(s, (100, 60, 30), (14, 20, 6, 16)) or
                           pygame.draw.circle(s, (60, 120, 40), (17, 14), 12)),
        "wildflowers": lambda s: [pygame.draw.circle(s, (c), (8 + i * 6, 20), 4)
                                   for i, c in enumerate([(255, 100, 150), (255, 200, 50), (150, 100, 255)])],
        "hay_bale": lambda s: pygame.draw.ellipse(s, (200, 170, 80), (4, 12, 28, 20)),
        "bench": lambda s: (pygame.draw.rect(s, (120, 80, 40), (4, 18, 28, 6)) or
                            pygame.draw.rect(s, (100, 60, 30), (6, 24, 4, 10)) or
                            pygame.draw.rect(s, (100, 60, 30), (22, 24, 4, 10))),
        "bird_bath": lambda s: (pygame.draw.rect(s, (180, 180, 190), (14, 20, 6, 14)) or
                                 pygame.draw.ellipse(s, (200, 220, 240), (8, 10, 20, 12))),
        "prairie_rock": lambda s: pygame.draw.ellipse(s, (130, 120, 110), (6, 16, 24, 16)),
    }
    for did, draw_fn in decos.items():
        surf = pygame.Surface((32, 36), pygame.SRCALPHA)
        draw_fn(surf)
        path = ASSETS_DIR / "sprites" / "decorations" / f"{did}.png"
        pygame.image.save(surf, str(path))


def generate_animals():
    animals = {
        "bison": (80, 55, 35),
        "cattle": (60, 40, 30),
        "chicken": (220, 180, 60),
    }
    for aid, color in animals.items():
        for frame in range(4):
            surf = pygame.Surface((32, 24), pygame.SRCALPHA)
            ox = frame % 2
            if aid == "bison":
                pygame.draw.ellipse(surf, color, (4 + ox, 8, 22, 14))
                pygame.draw.circle(surf, color, (6, 10), 6)
                pygame.draw.line(surf, (60, 40, 20), (4, 6), (2, 2), 2)
                pygame.draw.line(surf, (60, 40, 20), (8, 6), (10, 2), 2)
            elif aid == "cattle":
                pygame.draw.ellipse(surf, color, (6, 10, 18, 12))
                pygame.draw.circle(surf, color, (8, 8), 5)
                pygame.draw.ellipse(surf, (240, 240, 240), (14, 8, 8, 8))
            else:
                pygame.draw.ellipse(surf, color, (8 + ox, 12, 14, 10))
                pygame.draw.circle(surf, color, (10, 8), 5)
                pygame.draw.polygon(surf, (200, 50, 30), [(14, 4), (18, 8), (12, 8)])
            path = ASSETS_DIR / "sprites" / "animals" / f"{aid}_{frame}.png"
            pygame.image.save(surf, str(path))


def generate_sounds():
    """Generate simple placeholder WAV sounds."""
    audio_dir = ASSETS_DIR / "audio"
    sounds = {
        "planting": (440, 0.1),
        "harvesting": (660, 0.15),
        "coins": (880, 0.1),
        "ui_click": (520, 0.05),
        "ambient": (220, 0.5),
    }
    sample_rate = 22050
    for name, (freq, duration) in sounds.items():
        path = audio_dir / f"{name}.wav"
        n_samples = int(sample_rate * duration)
        with wave.open(str(path), "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            for i in range(n_samples):
                t = i / sample_rate
                envelope = min(1.0, 1.0 - t / duration)
                value = int(32767 * envelope * 0.3 * math.sin(2 * math.pi * freq * t))
                wf.writeframes(struct.pack("<h", value))


def generate_all():
    pygame.init()
    _ensure_dirs()
    generate_terrain()
    generate_crops()
    generate_buildings()
    generate_decorations()
    generate_animals()
    generate_sounds()
    pygame.quit()
    print("All assets generated successfully!")


if __name__ == "__main__":
    generate_all()
