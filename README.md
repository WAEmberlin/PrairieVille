# PrairieVille

**Kansas Proud** — A single-player farm simulation game inspired by classic social farming games, built with Python and Pygame.

## Features

- **Isometric farm grid** — Start with a 10×10 plot, expand up to 25×25
- **Crop farming** — Plant wheat, corn, and soybeans with growth stages and withering
- **Economy** — Earn coins from harvests, buy seeds, buildings, and decorations
- **Buildings** — Farmhouse, barn, silo, windmill, and bison pasture
- **Animals** — Bison (wandering), cattle, and chickens with feeding and products
- **Quests** — Dynamic tasks with coin and XP rewards
- **World systems** — Day/night cycle, seasons, and weather affecting crop growth
- **Save system** — Auto-save every 60 seconds to SQLite

## Requirements

- Python 3.12+
- pygame-ce 2.5+

## Installation

```bash
# Clone the repository
git clone https://github.com/WAEmberlin/PrairieVille.git
cd PrairieVille

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

On first launch, placeholder art assets are generated automatically.

## Controls

| Action | Input |
|--------|-------|
| Till soil | Select **Till** tool, click plot |
| Plant crop | Select crop in right panel, click tilled soil |
| Harvest | Select **Harvest** tool, click ready crop |
| Build | Select building in right panel, click farm |
| Clear plot | Select **Clear** tool, click plot |
| Quick till | `1` |
| Quick plant | `2` |
| Quick harvest | `3` |
| Manual save | `Ctrl+S` |

## Project Structure

```
PrairieVille/
├── main.py                 # Entry point
├── requirements.txt
├── data/                   # JSON game configuration
│   ├── crops.json
│   ├── buildings.json
│   ├── animals.json
│   └── decorations.json
├── assets/                 # Generated sprites and sounds
├── database/               # SQLite save files
└── game/
    ├── core/               # Engine, constants, events
    ├── entities/           # Player, crops, buildings, animals
    ├── systems/            # Economy, time, weather, quests, farm
    ├── ui/                 # HUD components
    ├── scenes/             # Game scenes
    └── managers/           # Asset, scene, save managers
```

## Platform Support

Tested on Windows. Compatible with macOS and Linux via Python 3.12+ and pygame-ce.

## License

Original game code and assets. Not affiliated with any existing farming game franchise.
