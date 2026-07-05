"""Icon sheet slicing and entity-to-icon mapping."""

from pathlib import Path

from game.core.constants import ASSETS_DIR

ICON_SHEET_PATH = ASSETS_DIR / "prairieville_icon_sheet.png"
ICONS_DIR = ASSETS_DIR / "ui" / "icons"

# Grid layout: 5 columns x 3 rows (matches prairieville_icon_sheet.png)
ICON_GRID = [
    ["corn", "soybeans", "wheat", "barn", "cow"],
    ["chicken", "sheep", "tractor", "flag_pole", "farmer"],
    ["hay_pile", "hay_bale", "gravel_road", "mailbox", "truck"],
]

# Map game entity IDs to icon filenames
ENTITY_ICON_MAP: dict[str, str] = {
    # Crops
    "wheat": "wheat",
    "corn": "corn",
    "soybeans": "soybeans",
    "crop_wheat": "wheat",
    "crop_corn": "corn",
    "crop_soybeans": "soybeans",
    "seed_wheat": "wheat",
    "seed_corn": "corn",
    "seed_soybeans": "soybeans",
    # Buildings
    "barn": "barn",
    "farmhouse": "farmer",
    "silo": "hay_pile",
    "windmill": "flag_pole",
    "bison_pasture": "hay_pile",
    # Animals
    "cattle": "cow",
    "cow": "cow",
    "chicken": "chicken",
    "bison": "cow",
    "sheep": "sheep",
    # Decorations
    "hay_bale": "hay_bale",
    "fence": "gravel_road",
    "tree": "hay_pile",
    "wildflowers": "hay_pile",
    "bench": "farmer",
    "bird_bath": "mailbox",
    "prairie_rock": "gravel_road",
    # Terrain / misc
    "path": "gravel_road",
    "gravel_road": "gravel_road",
}

TOOL_ICON_MAP: dict[str, str] = {
    "cursor": "farmer",
    "till": "tractor",
    "clear": "hay_pile",
    "plant": "wheat",
    "harvest": "corn",
    "build": "barn",
    "decorate": "flag_pole",
    "feed": "hay_bale",
}


def icon_for(entity_id: str) -> str | None:
    """Return icon name for a game entity, or None if no mapping."""
    return ENTITY_ICON_MAP.get(entity_id)


def icon_for_tool(tool_id: str) -> str | None:
    return TOOL_ICON_MAP.get(tool_id)


SLICE_VERSION = 2  # bump when slice output format changes


def _matches_background(r: int, g: int, b: int, bg: tuple[int, int, int], tolerance: int) -> bool:
    dr, dg, db = r - bg[0], g - bg[1], b - bg[2]
    return dr * dr + dg * dg + db * db <= tolerance * tolerance


def make_background_transparent(surface, tolerance: int = 48):
    """Remove cream/white sheet background via edge flood fill."""
    import collections

    import pygame

    result = surface.copy().convert_alpha()
    w, h = result.get_size()

    corner_samples = [
        result.get_at((0, 0)),
        result.get_at((w - 1, 0)),
        result.get_at((0, h - 1)),
        result.get_at((w - 1, h - 1)),
    ]
    bg = (
        sum(c[0] for c in corner_samples) // len(corner_samples),
        sum(c[1] for c in corner_samples) // len(corner_samples),
        sum(c[2] for c in corner_samples) // len(corner_samples),
    )

    def is_background(x: int, y: int) -> bool:
        r, g, b, a = result.get_at((x, y))
        if a == 0:
            return True
        return _matches_background(r, g, b, bg, tolerance)

    visited: set[tuple[int, int]] = set()
    queue: collections.deque[tuple[int, int]] = collections.deque()

    for x in range(w):
        for y in (0, h - 1):
            if is_background(x, y):
                queue.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if is_background(x, y):
                queue.append((x, y))

    while queue:
        x, y = queue.popleft()
        if (x, y) in visited or x < 0 or x >= w or y < 0 or y >= h:
            continue
        if not is_background(x, y):
            continue
        visited.add((x, y))
        result.set_at((x, y), (0, 0, 0, 0))
        queue.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    return result


def slice_icon_sheet(force: bool = False) -> list[str]:
    """Slice the master icon sheet into individual PNG files."""
    import pygame

    if not ICON_SHEET_PATH.exists():
        raise FileNotFoundError(f"Icon sheet not found: {ICON_SHEET_PATH}")

    ICONS_DIR.mkdir(parents=True, exist_ok=True)

    marker = ICONS_DIR / ".sliced"
    if marker.exists() and not force:
        version = marker.read_text(encoding="utf-8").strip()
        existing = list(ICONS_DIR.glob("*.png"))
        if version == str(SLICE_VERSION) and len(existing) >= 15:
            return [p.stem for p in existing]

    pygame.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1), pygame.HIDDEN)
    sheet = pygame.image.load(str(ICON_SHEET_PATH)).convert_alpha()
    sheet_w, sheet_h = sheet.get_size()
    cols = len(ICON_GRID[0])
    rows = len(ICON_GRID)
    cell_w = sheet_w // cols
    cell_h = sheet_h // rows
    pad_x, pad_y = 20, 24

    saved: list[str] = []
    for row_idx, row in enumerate(ICON_GRID):
        for col_idx, name in enumerate(row):
            x = col_idx * cell_w + pad_x
            y = row_idx * cell_h + pad_y
            w = cell_w - pad_x * 2
            h = cell_h - pad_y * 2
            sub = sheet.subsurface(pygame.Rect(x, y, w, h)).copy()
            sub = make_background_transparent(sub)
            out_path = ICONS_DIR / f"{name}.png"
            pygame.image.save(sub, str(out_path))
            saved.append(name)

    marker.write_text(f"{SLICE_VERSION}\n", encoding="utf-8")
    pygame.quit()
    return saved
