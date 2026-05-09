"""Testing module for all in game entities"""
import os

from hypothesis import given
import hypothesis.strategies as some
from unittest.mock import Mock, patch
import unittest

import pygame
from pygame import Vector2

from src.game import Game
from src.items.projectile import Projectile
from src.entities.entity_mod import Entity
from src.entities.player import Player
from src.entities.coral import Coral
from src.entities.urchin import Urchin
from src.entities.jelly import Jelly
from src.entities.boss import Boss

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


class WorldMockSettings:

    s_col = []
    player_pos = Vector2()
    player_col = False

    @staticmethod
    def entity_actions_returns(entity: Entity, action: str,
                               projectile: Projectile | None = None):
        match action:
            case "s_col":
                return WorldMockSettings.s_col
            case "player_pos":
                return WorldMockSettings.player_pos
            case "player_col":
                return WorldMockSettings.player_col


class BaseEntityTest(unittest.TestCase):

    def setUp(self) -> None:
        self._mock_world: Mock = Mock()
        self._mock_world.entity_action.side_effect = WorldMockSettings.entity_actions_returns
        self._delta_time: float = .01667  # 60 frames per second
        pygame.display.init()
        pygame.display.set_mode(Game._RESOLUTION, pygame.FULLSCREEN)
        return super().setUp()

    def tearDown(self) -> None:
        pygame.quit()
        return super().tearDown()

    def change_mock_world_vals(self, new_scol: list[pygame.Rect] = [],
                               new_pos: Vector2 = Vector2(),
                               new_col: bool = False):
        worldMock = WorldMockSettings
        worldMock.s_col = new_scol
        worldMock.player_pos = new_pos
        worldMock.player_col = new_col
        self._mock_world.entity_aciton.side_effect = worldMock.entity_actions_returns


class TestEntity(BaseEntityTest):
    """Test Entities"""

    def test_entity_init(self) -> None:
        """Test the creation of an entity"""
        entity: Entity = Entity(self._mock_world)

        # check standard vals
        assert entity.position.x == 0
        assert entity.position.y == 0
        assert entity.HP == 100
        assert entity.speed == 100
        assert entity.move_speed == 0


class TestPlayer(BaseEntityTest):
    @patch('src.entities.player.PlayerController')
    @patch.object(Player, "player_movement")
    def test_player_movement(self, mock_player, mock_controller) -> None:
        """Test player movement"""
        mock_controller.controller_status.return_value = False
        mock_player.return_value = Vector2(1, 1)

        player: Player = Player(self._mock_world)
        pos_start: tuple[float, float] = (player.position.x, player.position.y)

        for i in range(60):  # simulate one second
            player.loop(self._delta_time)

        pos_end: tuple[float, float] = (player.position.x, player.position.y)
        self.assertNotEqual(pos_start, pos_end)


class TestCoral(BaseEntityTest):

    def test_coral_init(self):
        """test init coral"""
        coral: Coral = Coral(self._mock_world)

        # check vals
        assert coral.position == Vector2()
        assert coral.speed == 0
        assert coral.move_speed == 0
        assert coral.HP == 2

    @given(some.integers(1, 2))
    def test_coral_damage(self, damage: int):
        """Test boss damage"""
        coral: Coral = Coral(self._mock_world)

        # deal damage
        pre_dmg: int = coral.HP
        coral.damage(damage)
        self.assertEqual(pre_dmg - damage, coral.HP)

    def test_coral_loop(self):
        """Test coral loop method"""
        self.change_mock_world_vals(new_pos=Vector2(100, 100))
        coral: Coral = Coral(self._mock_world)

        for i in range(60 * 1):
            coral.loop(self._delta_time)
        assert not coral._shots  # nothing shot yet

        for i in range(60 * 2):
            coral.loop(self._delta_time)
        assert len(coral._shots) > 0  # a shot!

        # hit the player with shot
        self.change_mock_world_vals(new_pos=Vector2(100, 100), new_col=True)
        coral.loop(self._delta_time)
        assert not coral._shots  # no shots

        # run for 30 seconds
        self.change_mock_world_vals(new_pos=Vector2(100, 100))
        for i in range(60 * 30):
            coral.loop(self._delta_time)
        assert len(coral._shots) < 3  # should never have more than 2 shots

    def test_coral_render(self):
        """Test boss render method"""
        coral: Coral = Coral(self._mock_world)

        pseudo_time: float = 0

        # test without damage
        for i in range(60 * 10):
            pseudo_time += self._delta_time
            coral.render(pseudo_time)

        # damage and render
        coral.damage(1)
        for i in range(60 * 10):
            pseudo_time += self._delta_time
            coral.render(pseudo_time)

        # render projectile
        coral._shot_timer = 0
        coral.coral_attack(self._delta_time)
        coral.render(pseudo_time)


class TestBoss(BaseEntityTest):

    def setUp(self) -> None:
        self._ROOM_BOUNDS: dict[str, tuple[int, int]] = {
            'X': (284, 1160),
            'Y': (205, 685)
        }
        return super().setUp()

    def test_boss_init(self):
        """Test boss initialization"""
        boss: Boss = Boss(self._mock_world, self._ROOM_BOUNDS)

        # check values
        assert boss.position == Vector2()
        assert boss.speed == boss._JELLY_ATTRIBUTES['speed']
        assert boss.move_speed == 0
        assert boss.HP == 15

    @given(some.integers(1, 15))
    def test_boss_damage(self, damage: int):
        """Test boss damage"""
        boss: Boss = Boss(self._mock_world, self._ROOM_BOUNDS)

        # deal damage
        pre_dmg: int = boss.HP
        boss.damage(damage)
        self.assertEqual(pre_dmg - damage, boss.HP)

    def test_boss_loop(self):
        """Test boss loop method"""
        boss: Boss = Boss(self._mock_world, self._ROOM_BOUNDS)

        for i in range(60 * 4):
            boss.loop(self._delta_time)
        assert boss._mode == boss._JELLY

        for i in range(60 * 4):
            boss.loop(self._delta_time)
        assert boss._mode == boss._URCHIN

        for i in range(60 * 4):
            boss.loop(self._delta_time)
        assert boss._mode == boss._JELLY

        # run for a minute
        self.change_mock_world_vals(new_pos=Vector2(300, 500), new_col=True)
        for i in range(60 * 30):
            boss.loop(self._delta_time)

        self.change_mock_world_vals(new_pos=Vector2(1400, 800), new_col=True)
        for i in range(60 * 30):
            boss.loop(self._delta_time)

        # check theoretical run into wall

        self.change_mock_world_vals(new_scol=[pygame.Rect()])
        for i in range(60 * 10):  # run for 10 seconds
            boss.loop(self._delta_time)

    def test_boss_render(self):
        """Test boss render method"""
        boss: Boss = Boss(self._mock_world, self._ROOM_BOUNDS)

        pseudo_time: float = 0

        # test without damage
        for i in range(60 * 10):
            pseudo_time += self._delta_time
            boss.render(pseudo_time)

        # damage and render
        boss.damage(1)
        for i in range(60 * 10):
            pseudo_time += self._delta_time
            boss.render(pseudo_time)

        # render projectile
        boss.boss_shoot()
        boss.render(pseudo_time)
