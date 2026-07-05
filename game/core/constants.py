"""PrairieVille game constants."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
DATA_DIR = ROOT_DIR / "data"
DATABASE_DIR = ROOT_DIR / "database"

# Display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "PrairieVille"
TAGLINE = "Kansas Proud"

# Isometric tile dimensions
TILE_WIDTH = 64
TILE_HEIGHT = 32

# UI layout
TOP_BAR_HEIGHT = 48
BOTTOM_BAR_HEIGHT = 56
SIDEBAR_WIDTH = 180

# Farm
STARTING_FARM_SIZE = 10
STARTING_COINS = 200
STARTING_XP = 0
STARTING_LEVEL = 1
XP_PER_LEVEL = 100

# Time
REAL_SECONDS_PER_GAME_HOUR = 30
HOURS_PER_DAY = 24
DAYS_PER_SEASON = 7
SEASONS = ("Spring", "Summer", "Fall", "Winter")

# Weather growth multipliers
WEATHER_GROWTH = {
    "sunny": 1.0,
    "cloudy": 0.9,
    "rain": 1.3,
    "thunderstorm": 0.7,
}

# Save
AUTOSAVE_INTERVAL = 60

# Colors (Kansas prairie palette)
COLOR_GRASS = (107, 142, 35)
COLOR_DIRT = (139, 90, 43)
COLOR_TILLED = (101, 67, 33)
COLOR_PATH = (160, 130, 90)
COLOR_SKY = (135, 206, 235)
COLOR_UI_BG = (245, 235, 210)
COLOR_UI_BORDER = (139, 90, 43)
COLOR_UI_TEXT = (60, 40, 20)
COLOR_UI_ACCENT = (218, 165, 32)
COLOR_UI_HIGHLIGHT = (255, 248, 220)
COLOR_COIN = (255, 215, 0)
COLOR_XP = (100, 180, 255)

# Plot states
PLOT_GRASS = "grass"
PLOT_DIRT = "dirt"
PLOT_TILLED = "tilled"
PLOT_CROP = "crop"
PLOT_BUILDING = "building"
PLOT_DECORATION = "decoration"

# Tools
TOOL_CURSOR = "cursor"
TOOL_TILL = "till"
TOOL_CLEAR = "clear"
TOOL_PLANT = "plant"
TOOL_HARVEST = "harvest"
TOOL_BUILD = "build"
TOOL_DECORATE = "decorate"
TOOL_FEED = "feed"
