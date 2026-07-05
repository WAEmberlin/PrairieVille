"""Isometric coordinate conversion utilities."""

import math

from game.core.constants import TILE_WIDTH, TILE_HEIGHT


def grid_to_screen(gx: int, gy: int, offset_x: float = 0, offset_y: float = 0) -> tuple[float, float]:
    """Convert grid coordinates to the top-left of a tile's bounding box."""
    sx = (gx - gy) * (TILE_WIDTH / 2) + offset_x
    sy = (gx + gy) * (TILE_HEIGHT / 2) + offset_y
    return sx, sy


def tile_center_screen(gx: int, gy: int, offset_x: float = 0, offset_y: float = 0) -> tuple[float, float]:
    """Return the screen center of a tile (matches how sprites are drawn)."""
    sx, sy = grid_to_screen(gx, gy, offset_x, offset_y)
    return sx + TILE_WIDTH / 2, sy + TILE_HEIGHT / 2


def point_in_tile(px: float, py: float, gx: int, gy: int,
                  offset_x: float = 0, offset_y: float = 0) -> bool:
    """Return True if a screen point lies inside the isometric diamond tile."""
    cx, cy = tile_center_screen(gx, gy, offset_x, offset_y)
    dx = abs(px - cx) / (TILE_WIDTH / 2)
    dy = abs(py - cy) / (TILE_HEIGHT / 2)
    return dx + dy <= 1.0


def screen_to_grid(sx: float, sy: float, offset_x: float = 0, offset_y: float = 0) -> tuple[int, int]:
    """Convert screen coordinates to grid coordinates using diamond hit testing."""
    # Approximate tile from the visual center offset used when drawing sprites
    adj_x = sx - offset_x - TILE_WIDTH / 2
    adj_y = sy - offset_y - TILE_HEIGHT / 2
    gx_f = (adj_x / (TILE_WIDTH / 2) + adj_y / (TILE_HEIGHT / 2)) / 2
    gy_f = (adj_y / (TILE_HEIGHT / 2) - adj_x / (TILE_WIDTH / 2)) / 2

    gx = round(gx_f)
    gy = round(gy_f)

    # Check the nearest candidates in case rounding lands on a neighbor
    candidates: list[tuple[int, int]] = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            cx, cy = gx + dx, gy + dy
            if (cx, cy) not in candidates:
                candidates.append((cx, cy))

    # Prefer exact hits; fall back to closest diamond center
    for cx, cy in candidates:
        if point_in_tile(sx, sy, cx, cy, offset_x, offset_y):
            return cx, cy

    best = (gx, gy)
    best_dist = math.inf
    for cx, cy in candidates:
        tx, ty = tile_center_screen(cx, cy, offset_x, offset_y)
        dist = (sx - tx) ** 2 + (sy - ty) ** 2
        if dist < best_dist:
            best_dist = dist
            best = (cx, cy)
    return best


def get_farm_offset(farm_size: int, screen_w: int, screen_h: int,
                    top: int, bottom: int, left: int, right: int) -> tuple[float, float]:
    """Calculate offset to center the farm in the playable area.

    For an NxN isometric grid, tile (0,0) anchors at (ox, oy). Tiles span
    x from ox - (N-1)*TW/2 to ox + (N-1)*TW/2 + TW, so the visual center
    is at ox + TW/2. Likewise the vertical center is at oy + N*TH/2.
    """
    area_w = screen_w - left - right
    area_h = screen_h - top - bottom
    n = farm_size

    ox = left + area_w / 2 - TILE_WIDTH / 2
    oy = top + area_h / 2 - (n * TILE_HEIGHT) / 2
    return ox, oy
