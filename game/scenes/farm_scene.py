"""Main farm gameplay scene."""

import pygame

from game.core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TOP_BAR_HEIGHT, BOTTOM_BAR_HEIGHT, SIDEBAR_WIDTH,
    TILE_WIDTH, TILE_HEIGHT, TOOL_CURSOR, TOOL_TILL, TOOL_CLEAR, TOOL_PLANT,
    TOOL_HARVEST, TOOL_BUILD, TOOL_DECORATE, TOOL_FEED,
    PLOT_GRASS, PLOT_TILLED, PLOT_CROP, PLOT_BUILDING, PLOT_DECORATION,
)
from game.core.isometric import grid_to_screen, screen_to_grid, get_farm_offset, tile_center_screen
from game.core.config_loader import ConfigLoader
from game.entities.player import Player
from game.systems.farm_manager import FarmManager
from game.systems.economy import EconomyManager
from game.systems.time_system import TimeManager
from game.systems.weather_system import WeatherManager
from game.systems.quest_system import QuestManager
from game.ui.top_bar import TopBar
from game.ui.toolbar import BottomToolbar
from game.ui.left_sidebar import LeftSidebar
from game.ui.right_sidebar import RightSidebar
from game.ui.confirm_dialog import ConfirmDialog


class FarmScene:
    """Main isometric farm gameplay scene."""

    def __init__(self, game):
        self.game = game
        self.events = game.events
        self.assets = game.assets
        self.save_manager = game.save_manager

        # Try loading save
        save_data = self.save_manager.load()
        if save_data:
            self._load_from_save(save_data)
        else:
            self._init_new_game()

        # UI
        self.font = self.assets.get_font(16)
        self.font_small = self.assets.get_font(12)
        self.top_bar = TopBar()
        self.toolbar = BottomToolbar(self._on_tool_selected, self.assets)
        self.left_sidebar = LeftSidebar(
            self.assets,
            on_sell_item=self._on_sell_inventory_item,
            get_sell_price=self.economy.get_sell_price,
        )
        self.right_sidebar = RightSidebar(self._on_shop_item_selected, self.assets)

        self.current_tool = TOOL_CURSOR
        self.selected_crop: str | None = None
        self.selected_building: str | None = None
        self.selected_decoration: str | None = None
        self.selected_animal: str | None = None
        self.message = ""
        self.message_timer = 0.0
        self.confirm_dialog = ConfirmDialog()
        self._pending_clear_plot: tuple[int, int] | None = None

        self._calc_offset()
        self.right_sidebar.set_tab("crops")

    def _on_sell_inventory_item(self, item_key: str):
        price = self.economy.get_sell_price(item_key)
        if price is None:
            self._show_message("This item can't be sold")
            return
        earned = self.economy.sell_item(item_key)
        if earned > 0:
            name = self.economy.get_item_display_name(item_key)
            self.assets.play_sound("coins")
            self._show_message(f"Sold {name} for ${earned}!")
        else:
            self._show_message("Nothing to sell")

    def _init_new_game(self):
        self.player = Player()
        self.farm = FarmManager()
        self.economy = EconomyManager(self.player, self.events)
        self.time_mgr = TimeManager(self.events)
        self.weather_mgr = WeatherManager(self.events)
        self.quest_mgr = QuestManager(self.player, self.events)

    def _load_from_save(self, data: dict):
        self.player = Player.from_dict(data.get("player", {}))
        self.farm = FarmManager.from_dict(data.get("farm", {}))
        self.economy = EconomyManager(self.player, self.events)
        self.time_mgr = TimeManager.from_dict(data.get("time", {}), self.events)
        self.weather_mgr = WeatherManager.from_dict(data.get("weather", {}), self.events)
        self.quest_mgr = QuestManager.from_dict(data.get("quests", {}), self.player, self.events)

    def _calc_offset(self):
        self.offset_x, self.offset_y = get_farm_offset(
            self.farm.size, SCREEN_WIDTH, SCREEN_HEIGHT,
            TOP_BAR_HEIGHT, BOTTOM_BAR_HEIGHT, SIDEBAR_WIDTH, SIDEBAR_WIDTH,
        )

    def get_save_data(self) -> dict:
        return {
            "player": self.player.to_dict(),
            "farm": self.farm.to_dict(),
            "time": self.time_mgr.to_dict(),
            "weather": self.weather_mgr.to_dict(),
            "quests": self.quest_mgr.to_dict(),
        }

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def _show_message(self, msg: str, duration: float = 2.0):
        self.message = msg
        self.message_timer = duration

    def _on_tool_selected(self, tool: str):
        self.current_tool = tool
        if tool == TOOL_CURSOR:
            self._show_message("Hand: inspect tiles, harvest ready crops, place animals")
        if tool != TOOL_PLANT:
            self.selected_crop = None
        if tool != TOOL_BUILD:
            self.selected_building = None
        if tool != TOOL_DECORATE:
            self.selected_decoration = None
        if tool != TOOL_CURSOR:
            self.selected_animal = None

    def _on_shop_item_selected(self, tab: str, item_id: str):
        if tab == "crops":
            self.selected_crop = item_id
            self.current_tool = TOOL_PLANT
            self.toolbar.current_tool = TOOL_PLANT
            cfg = ConfigLoader.get_crop(item_id)
            if cfg:
                self._show_message(f"Selected {cfg['name']} - click tilled soil to plant")
        elif tab == "buildings":
            self.selected_building = item_id
            self.current_tool = TOOL_BUILD
            self.toolbar.current_tool = TOOL_BUILD
            cfg = ConfigLoader.get_building(item_id)
            if cfg:
                self._show_message(f"Selected {cfg['name']} - click farm to place")
        elif tab == "shop":
            animal = ConfigLoader.get_animal(item_id)
            if animal:
                self.selected_animal = item_id
                self.current_tool = TOOL_CURSOR
                self.toolbar.current_tool = TOOL_CURSOR
                self._show_message(f"Selected {animal['name']} — click a tile with Hand to place")
            else:
                self.selected_decoration = item_id
                self.current_tool = TOOL_DECORATE
                self.toolbar.current_tool = TOOL_DECORATE
                deco = next((d for d in ConfigLoader.get_decorations() if d["id"] == item_id), None)
                if deco:
                    self._show_message(f"Selected {deco['name']} - click to place")
        elif tab == "expand":
            new_size = int(item_id)
            if new_size <= self.farm.size:
                self._show_message("Already own this expansion!")
                return
            if self.economy.buy_expansion(new_size):
                self.farm.expand(new_size)
                self._calc_offset()
                self._show_message(f"Farm expanded to {new_size}x{new_size}!")
            else:
                self._show_message("Not enough coins!")

    def _clear_plot(self, plot, gx: int, gy: int):
        plot.clear()
        self._pending_clear_plot = None
        self._show_message("Plot cleared!")

    def _request_clear_plot(self, plot, gx: int, gy: int):
        if plot.clear_requires_confirmation():
            crop_name = ""
            if plot.crop:
                cfg = plot.crop.config
                crop_name = cfg["name"] if cfg else "crop"
                if plot.is_harvestable(self.weather_mgr.growth_multiplier):
                    msg = f"Clear this ready {crop_name}? You will lose the harvest!"
                else:
                    progress = int(plot.crop.get_growth_progress(self.weather_mgr.growth_multiplier) * 100)
                    msg = f"Clear this {crop_name} ({progress}% grown)?"
            elif plot.decoration_id:
                msg = "Remove this decoration?"
            else:
                msg = "Clear this plot?"
            self._pending_clear_plot = (gx, gy)
            self.confirm_dialog.show(
                msg,
                on_confirm=lambda: self._clear_plot(plot, gx, gy),
                on_cancel=lambda: setattr(self, "_pending_clear_plot", None),
            )
        elif plot.is_clearable():
            self._clear_plot(plot, gx, gy)
        else:
            self._show_message("Nothing to clear")

    def _try_harvest(self, plot) -> bool:
        growth = self.weather_mgr.growth_multiplier
        if not plot.is_harvestable(growth):
            if plot.crop:
                cfg = plot.crop.config
                name = cfg["name"] if cfg else "Crop"
                progress = int(plot.crop.get_growth_progress(growth) * 100)
                stage = plot.crop.get_current_stage(growth)
                total = cfg["stages"] if cfg else 4
                self._show_message(f"{name} growing... {progress}% (stage {stage}/{total})")
            return False
        crop_id = plot.harvest(growth)
        if crop_id:
            value = self.economy.harvest_crop(crop_id)
            self.assets.play_sound("harvesting")
            self._show_message(f"Harvested! Sell in inventory for ${value}")
            return True
        return False

    def _handle_hand_tool(self, plot, gx: int, gy: int):
        """Hand tool: harvest ready crops, place animals, or inspect tiles."""
        if self.selected_animal:
            cfg = ConfigLoader.get_animal(self.selected_animal)
            if cfg and cfg.get("pasture_required"):
                pasture = self.farm.get_building_at(gx, gy)
                if not pasture or pasture.building_id != cfg["pasture_required"]:
                    self._show_message("Place bison inside a bison pasture")
                    return
            if plot.crop or plot.building_id or plot.decoration_id:
                self._show_message("Need an empty grass tile for animals")
                return
            if self.economy.buy_animal(self.selected_animal):
                self.farm.add_animal(self.selected_animal, float(gx), float(gy))
                if self.selected_animal == "bison":
                    self.quest_mgr.on_bison_added()
                self._show_message(f"Added {self.selected_animal}!")
                self.selected_animal = None
            else:
                self._show_message("Not enough coins!")
            return

        if self._try_harvest(plot):
            return

        growth = self.weather_mgr.growth_multiplier
        if plot.crop:
            cfg = plot.crop.config
            name = cfg["name"] if cfg else "Crop"
            progress = int(plot.crop.get_growth_progress(growth) * 100)
            stage = plot.crop.get_current_stage(growth)
            total = cfg["stages"] if cfg else 4
            if plot.is_harvestable(growth):
                self._show_message(f"{name} is ready to harvest!")
            else:
                self._show_message(f"{name}: {progress}% grown (stage {stage}/{total})")
            return

        building = self.farm.get_building_at(gx, gy)
        if building:
            cfg = building.config
            self._show_message(cfg["name"] if cfg else building.building_id)
            return

        if plot.decoration_id:
            name = plot.decoration_id.replace("_", " ").title()
            self._show_message(f"Decoration: {name}")
            return

        hints = {
            PLOT_GRASS: "Grass — use Till to prepare soil",
            PLOT_TILLED: "Tilled soil — select a seed and plant",
            PLOT_DIRT: "Dirt — use Till to prepare soil",
        }
        self._show_message(hints.get(plot.state, "Empty plot"))

    def _handle_farm_click(self, pos: tuple[int, int]):
        gx, gy = screen_to_grid(pos[0], pos[1], self.offset_x, self.offset_y)
        if not self.farm.in_bounds(gx, gy):
            return

        plot = self.farm.get_plot(gx, gy)
        if not plot:
            return

        tool = self.current_tool

        if tool == TOOL_TILL:
            if plot.is_tillable():
                plot.till()
                self.assets.play_sound("planting")
                self._show_message("Soil tilled!")
            else:
                self._show_message("Can't till here")

        elif tool == TOOL_CLEAR:
            self._request_clear_plot(plot, gx, gy)

        elif tool == TOOL_PLANT:
            if not self.selected_crop:
                self._show_message("Select a crop from the right panel first")
                return
            if plot.is_plantable():
                if self.economy.plant_crop(self.selected_crop):
                    plot.plant(self.selected_crop)
                    self.assets.play_sound("planting")
                    self._show_message(f"Planted {self.selected_crop}!")
                else:
                    self._show_message("Not enough coins for seeds!")
            else:
                self._show_message("Till the soil first")

        elif tool == TOOL_HARVEST:
            if not self._try_harvest(plot):
                self._show_message("Nothing ready to harvest here")

        elif tool == TOOL_BUILD:
            if not self.selected_building:
                self._show_message("Select a building from the right panel")
                return
            if self.economy.buy_building(self.selected_building):
                if self.farm.place_building(self.selected_building, gx, gy):
                    self.player.owned_buildings.append(self.selected_building)
                    self.assets.play_sound("coins")
                    self._show_message(f"Built {self.selected_building}!")
                else:
                    cost = ConfigLoader.get_building(self.selected_building)["cost"]
                    self.player.add_coins(cost)
                    self.player.stats["buildings_built"] -= 1
                    self._show_message("Can't place building here")
            else:
                self._show_message("Not enough coins!")

        elif tool == TOOL_DECORATE:
            if not self.selected_decoration:
                self._show_message("Select a decoration from Shop tab")
                return
            if self.economy.buy_decoration(self.selected_decoration):
                if self.farm.place_decoration(self.selected_decoration, gx, gy):
                    self._show_message("Decoration placed!")
                else:
                    self._show_message("Can't place here")
            else:
                self._show_message("Not enough coins!")

        elif tool == TOOL_FEED:
            for animal in self.farm.animals:
                ax, ay = int(animal.x), int(animal.y)
                if abs(ax - gx) <= 1 and abs(ay - gy) <= 1:
                    if animal.needs_feed():
                        if self.economy.feed_animal(animal.animal_id):
                            animal.feed()
                            self._show_message(f"Fed {animal.animal_id}!")
                        else:
                            self._show_message("Not enough coins to feed")
                    else:
                        product = animal.collect_product()
                        if product:
                            key, value = product
                            self.player.add_item(key)
                            self.assets.play_sound("harvesting")
                            self._show_message(f"Collected {key}! Sell in inventory for ${value}")
                    return
            self._show_message("No animals nearby")

        elif tool == TOOL_CURSOR:
            self._handle_hand_tool(plot, gx, gy)

    def handle_event(self, event: pygame.event.Event):
        if self.confirm_dialog.visible and self.confirm_dialog.handle_event(event):
            return
        if self.toolbar.handle_event(event):
            return
        if self.left_sidebar.handle_event(event):
            return
        if self.right_sidebar.handle_event(event):
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            # Check if click is in farm area
            if (SIDEBAR_WIDTH <= pos[0] <= SCREEN_WIDTH - SIDEBAR_WIDTH and
                    TOP_BAR_HEIGHT <= pos[1] <= SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT):
                self._handle_farm_click(pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_0:
                self._on_tool_selected(TOOL_CURSOR)
                self.toolbar.current_tool = TOOL_CURSOR
            elif event.key == pygame.K_1:
                self._on_tool_selected(TOOL_TILL)
                self.toolbar.current_tool = TOOL_TILL
            elif event.key == pygame.K_2:
                self._on_tool_selected(TOOL_PLANT)
                self.toolbar.current_tool = TOOL_PLANT
            elif event.key == pygame.K_3:
                self._on_tool_selected(TOOL_HARVEST)
                self.toolbar.current_tool = TOOL_HARVEST
            elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.save_manager.save(self.get_save_data())
                self._show_message("Game saved!")

    def update(self, dt: float):
        self.time_mgr.update(dt)
        self.weather_mgr.update(dt)
        self.farm.update(dt, self.weather_mgr.growth_multiplier)

        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

        self.top_bar.update_stats(self.player, self.time_mgr, self.weather_mgr)
        self.left_sidebar.update_quests(self.quest_mgr.active_quests)
        self.left_sidebar.update_inventory(self.player.inventory)

    def _draw_tile(self, screen, plot, sx, sy):
        """Draw a single isometric tile."""
        # Terrain base
        if plot.state == PLOT_TILLED:
            terrain_key = "tilled"
        elif plot.state in (PLOT_CROP,):
            terrain_key = "tilled"
        elif plot.decoration_id:
            terrain_key = "grass"
        elif plot.building_id:
            terrain_key = "dirt"
        else:
            terrain_key = plot.state if plot.state in ("grass", "dirt") else "grass"

        sprite = self.assets.get_terrain_sprite(terrain_key)
        tile_rect = sprite.get_rect(centerx=int(sx + TILE_WIDTH // 2), bottom=int(sy + TILE_HEIGHT))
        screen.blit(sprite, tile_rect)

        # Crop
        if plot.crop:
            stage = plot.crop.get_current_stage(self.weather_mgr.growth_multiplier)
            crop_sprite = self.assets.get_crop_sprite(plot.crop.crop_id, min(stage, 4))
            crop_rect = crop_sprite.get_rect(centerx=int(sx + TILE_WIDTH // 2),
                                              bottom=int(sy + TILE_HEIGHT // 2))
            screen.blit(crop_sprite, crop_rect)

        # Decoration
        if plot.decoration_id:
            deco_sprite = self.assets.get_decoration_sprite(plot.decoration_id)
            deco_rect = deco_sprite.get_rect(centerx=int(sx + TILE_WIDTH // 2),
                                              bottom=int(sy + TILE_HEIGHT // 2 + 8))
            screen.blit(deco_sprite, deco_rect)

        # Building (draw at origin tile only)
        if plot.building_id and plot.building_origin:
            bld_sprite = self.assets.get_building_sprite(plot.building_id)
            bld_rect = bld_sprite.get_rect(centerx=int(sx + TILE_WIDTH // 2),
                                            bottom=int(sy + TILE_HEIGHT + 16))
            screen.blit(bld_sprite, bld_rect)

    def draw(self, screen: pygame.Surface):
        # Sky
        screen.fill(self.time_mgr.sky_color)

        # Draw farm tiles back-to-front
        for x in range(self.farm.size):
            for y in range(self.farm.size):
                plot = self.farm.get_plot(x, y)
                if plot:
                    sx, sy = grid_to_screen(x, y, self.offset_x, self.offset_y)
                    self._draw_tile(screen, plot, sx, sy)

        # Draw animals
        for animal in self.farm.animals:
            ax, ay = grid_to_screen(animal.x, animal.y, self.offset_x, self.offset_y)
            sprite = self.assets.get_animal_sprite(animal.animal_id, animal.anim_frame)
            rect = sprite.get_rect(centerx=int(ax + TILE_WIDTH // 2), bottom=int(ay + TILE_HEIGHT))
            screen.blit(sprite, rect)

        # UI layers (top bar drawn last so stats aren't covered by sidebars)
        self.left_sidebar.draw(screen, self.font_small)
        self.right_sidebar.draw(screen, self.font_small)
        self.toolbar.draw(screen, self.font)
        self.top_bar.draw(screen, self.font)

        # Message toast
        if self.message:
            msg_font = self.assets.get_font(18)
            msg_surf = msg_font.render(self.message, True, (255, 255, 255))
            msg_bg = pygame.Surface((msg_surf.get_width() + 20, msg_surf.get_height() + 10), pygame.SRCALPHA)
            msg_bg.fill((0, 0, 0, 180))
            msg_x = (SCREEN_WIDTH - msg_bg.get_width()) // 2
            msg_y = SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT - 40
            screen.blit(msg_bg, (msg_x, msg_y))
            screen.blit(msg_surf, (msg_x + 10, msg_y + 5))

        # Hover highlight
        mouse_pos = pygame.mouse.get_pos()
        if (SIDEBAR_WIDTH <= mouse_pos[0] <= SCREEN_WIDTH - SIDEBAR_WIDTH and
                TOP_BAR_HEIGHT <= mouse_pos[1] <= SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT):
            gx, gy = screen_to_grid(mouse_pos[0], mouse_pos[1], self.offset_x, self.offset_y)
            if self.farm.in_bounds(gx, gy):
                cx, cy = tile_center_screen(gx, gy, self.offset_x, self.offset_y)
                highlight = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 40))
                hl_rect = highlight.get_rect(centerx=int(cx), centery=int(cy))
                screen.blit(highlight, hl_rect)

        self.confirm_dialog.draw(screen, self.font)
