"""Helpers for drawing scaled UI icons."""

import pygame


def scale_icon(surface: pygame.Surface, size: int) -> pygame.Surface:
    """Scale icon to fit within a square of `size` pixels, preserving aspect ratio."""
    w, h = surface.get_size()
    if w == 0 or h == 0:
        return surface
    scale = size / max(w, h)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    return pygame.transform.smoothscale(surface, (new_w, new_h))


def blit_icon(
    screen: pygame.Surface,
    icon: pygame.Surface | None,
    rect: pygame.Rect,
    size: int = 24,
):
    """Draw an icon centered vertically on the left side of a rect."""
    if icon is None:
        return rect.x + size + 4
    scaled = scale_icon(icon, size)
    ix = rect.x + 4
    iy = rect.y + (rect.height - scaled.get_height()) // 2
    screen.blit(scaled, (ix, iy))
    return ix + scaled.get_width() + 6
