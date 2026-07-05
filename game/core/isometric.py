"""Isometric coordinate conversion utilities."""

from game.core.constants import TILE_WIDTH, TILE_HEIGHT


def grid_to_screen(gx: int, gy: int, offset_x: float = 0, offset_y: float = 0) -> tuple[float, float]:
    """Convert grid coordinates to screen (pixel) coordinates."""
    sx = (gx - gy) * (TILE_WIDTH / 2) + offset_x
    sy = (gx + gy) * (TILE_HEIGHT / 2) + offset_y
    return sx, sy


def screen_to_grid(sx: float, sy: float, offset_x: float = 0, offset_y: float = 0) -> tuple[int, int]:
    """Convert screen coordinates to grid coordinates."""
    adj_x = sx - offset_x
    adj_y = sy - offset_y
    gx = (adj_x / (TILE_WIDTH / 2) + adj_y / (TILE_HEIGHT / 2)) / 2
    gy = (adj_y / (TILE_HEIGHT / 2) - adj_x / (TILE_WIDTH / 2)) / 2
    return int(gx), int(gy)


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

    # Position tile (0,0) so the isometric grid is centered in the play area
    ox = left + area_w / 2 - TILE_WIDTH / 2
    oy = top + area_h / 2 - (n * TILE_HEIGHT) / 2
    return ox, oy
