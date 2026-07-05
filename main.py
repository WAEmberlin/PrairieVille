#!/usr/bin/env python3
"""PrairieVille - Kansas Proud farm simulation game."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.core.asset_generator import generate_all
from game.core.icon_registry import slice_icon_sheet, ICONS_DIR, SLICE_VERSION
from game.core.game import Game


def _icons_need_update() -> bool:
    if not (ICONS_DIR / "corn.png").exists():
        return True
    marker = ICONS_DIR / ".sliced"
    if not marker.exists():
        return True
    return marker.read_text(encoding="utf-8").strip() != str(SLICE_VERSION)


def main():
    assets_marker = ROOT / "assets" / "sprites" / "terrain" / "grass.png"
    if not assets_marker.exists():
        print("Generating placeholder assets...")
        generate_all()

    if _icons_need_update():
        print("Slicing icon sheet...")
        slice_icon_sheet(force=True)

    game = Game()
    game.run()


if __name__ == "__main__":
    main()
