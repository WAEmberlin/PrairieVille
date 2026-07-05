"""Basic tests for PrairieVille game systems."""

import time
import pytest

from game.entities.player import Player
from game.entities.farm_plot import FarmPlot, CropInstance
from game.systems.farm_manager import FarmManager
from game.systems.economy import EconomyManager
from game.core.events import EventBus
from game.core.config_loader import ConfigLoader
from game.core.isometric import get_farm_offset, grid_to_screen, screen_to_grid, tile_center_screen, point_in_tile
from game.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_WIDTH, TILE_HEIGHT
from game.core.constants import TOP_BAR_HEIGHT, BOTTOM_BAR_HEIGHT, SIDEBAR_WIDTH


@pytest.fixture
def event_bus():
    return EventBus()


@pytest.fixture
def player():
    return Player()


@pytest.fixture
def economy(player, event_bus):
    return EconomyManager(player, event_bus)


class TestPlayer:
    def test_starting_coins(self, player):
        assert player.coins == 200

    def test_spend_coins(self, player):
        assert player.spend_coins(50)
        assert player.coins == 150

    def test_spend_insufficient(self, player):
        assert not player.spend_coins(9999)

    def test_add_xp_levels_up(self, player):
        leveled = player.add_xp(100)
        assert leveled
        assert player.level == 2

    def test_inventory(self, player):
        player.add_item("seed_wheat", 5)
        assert player.has_item("seed_wheat", 3)
        before = player.inventory["seed_wheat"]
        assert player.remove_item("seed_wheat", 2)
        assert player.inventory["seed_wheat"] == before - 2


class TestFarmPlot:
    def test_till(self):
        plot = FarmPlot(0, 0)
        plot.till()
        assert plot.state == "tilled"

    def test_plant_and_harvest(self):
        plot = FarmPlot(0, 0)
        plot.till()
        plot.plant("soybeans")
        plot.crop.planted_at = __import__("time").time() - 200
        assert plot.is_harvestable(1.3)
        crop_id = plot.harvest(1.3)
        assert crop_id == "soybeans"

    def test_harvest_respects_weather_multiplier(self):
        plot = FarmPlot(0, 0)
        plot.till()
        plot.plant("soybeans")
        plot.crop.planted_at = __import__("time").time() - 93
        assert plot.is_harvestable(1.3)
        assert not plot.is_harvestable(1.0)
        crop_id = plot.harvest(1.3)
        assert crop_id == "soybeans"

    def test_crop_stages(self):
        crop = CropInstance(crop_id="wheat", planted_at=time.time() - 15)
        assert crop.get_current_stage() >= 1
        assert not crop.is_ready()

    def test_crop_ready_at_full_growth(self):
        crop = CropInstance(crop_id="wheat", planted_at=time.time() - 30)
        assert crop.is_ready()
        assert crop.get_current_stage() == 4

    def test_crop_not_ready_at_three_quarters(self):
        crop = CropInstance(crop_id="wheat", planted_at=time.time() - 22)
        assert not crop.is_ready()
        assert crop.get_current_stage() == 3


class TestFarmManager:
    def test_grid_size(self):
        farm = FarmManager()
        assert farm.size == 10
        assert len(farm.plots) == 100

    def test_expand(self):
        farm = FarmManager()
        farm.expand(15)
        assert farm.size == 15
        assert len(farm.plots) == 225

    def test_place_building(self):
        farm = FarmManager()
        assert farm.place_building("windmill", 5, 5)
        plot = farm.get_plot(5, 5)
        assert plot.building_id == "windmill"


class TestEconomy:
    def test_buy_seeds(self, economy, player):
        assert economy.buy_seeds("wheat", 2)
        assert player.has_item("seed_wheat")

    def test_plant_crop(self, economy, player):
        assert economy.plant_crop("wheat")
        assert player.stats["crops_planted"] == 1

    def test_harvest_crop(self, economy, player):
        value = economy.harvest_crop("wheat")
        assert value == 10
        assert player.has_item("crop_wheat")
        assert player.coins == 200  # coins come from selling, not harvesting

    def test_sell_crop(self, economy, player):
        economy.harvest_crop("wheat")
        earned = economy.sell_item("crop_wheat")
        assert earned == 10
        assert player.coins == 210

    def test_sell_seeds(self, economy, player):
        earned = economy.sell_item("seed_wheat")
        assert earned == 2  # half of $5 seed cost
        assert player.inventory.get("seed_wheat", 0) == 4


class TestConfigLoader:
    def test_crops_loaded(self):
        crops = ConfigLoader.get_crops()
        assert len(crops) == 3
        wheat = ConfigLoader.get_crop("wheat")
        assert wheat["cost"] == 5
        assert wheat["harvest_value"] == 10

    def test_buildings_loaded(self):
        buildings = ConfigLoader.get_buildings()
        assert len(buildings) >= 5

    def test_animals_loaded(self):
        animals = ConfigLoader.get_animals()
        assert len(animals) == 3


class TestFarmOffset:
    def test_farm_centered_in_play_area(self):
        size = 10
        ox, oy = get_farm_offset(
            size, SCREEN_WIDTH, SCREEN_HEIGHT,
            TOP_BAR_HEIGHT, BOTTOM_BAR_HEIGHT, SIDEBAR_WIDTH, SIDEBAR_WIDTH,
        )
        play_left = SIDEBAR_WIDTH
        play_right = SCREEN_WIDTH - SIDEBAR_WIDTH
        play_center_x = (play_left + play_right) / 2

        left_sx, _ = grid_to_screen(0, size - 1, ox, oy)
        right_sx, _ = grid_to_screen(size - 1, 0, ox, oy)
        farm_left = left_sx
        farm_right = right_sx + TILE_WIDTH
        farm_center_x = (farm_left + farm_right) / 2

        assert farm_left >= play_left
        assert farm_right <= play_right
        assert abs(farm_center_x - play_center_x) < 1

        play_top = TOP_BAR_HEIGHT
        play_bottom = SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT
        play_center_y = (play_top + play_bottom) / 2
        _, top_sy = grid_to_screen(0, 0, ox, oy)
        _, bottom_sy = grid_to_screen(size - 1, size - 1, ox, oy)
        farm_bottom = bottom_sy + TILE_HEIGHT
        farm_center_y = (top_sy + farm_bottom) / 2
        assert abs(farm_center_y - play_center_y) < TILE_HEIGHT


class TestIsometricPicking:
    def test_tile_center_round_trip(self):
        ox, oy = 200.0, 100.0
        for gx, gy in ((0, 0), (3, 2), (5, 5), (2, 7)):
            cx, cy = tile_center_screen(gx, gy, ox, oy)
            picked_gx, picked_gy = screen_to_grid(cx, cy, ox, oy)
            assert (picked_gx, picked_gy) == (gx, gy)

    def test_point_in_tile_accepts_full_diamond(self):
        ox, oy = 200.0, 100.0
        cx, cy = tile_center_screen(2, 2, ox, oy)
        assert point_in_tile(cx, cy, 2, 2, ox, oy)
        assert point_in_tile(cx + TILE_WIDTH / 4, cy, 2, 2, ox, oy)
        assert point_in_tile(cx - TILE_WIDTH / 4, cy, 2, 2, ox, oy)
        assert not point_in_tile(cx + TILE_WIDTH, cy, 2, 2, ox, oy)
