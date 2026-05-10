"""Testing module for all in game entities"""
import os

from hypothesis import given
import hypothesis.strategies as some
from unittest.mock import Mock, patch, PropertyMock
import unittest

import pygame
from pygame import Vector2

from src.game import Game
from src.items.projectile import Projectile
from src.entities.entity_mod import Entity
from src.entities.player import Player, PlayerController
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
        self.change_mock_world_vals()
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

    def test_position_setter(self) -> None:
        """test setting the position"""
        entity: Entity = Entity(self._mock_world)
        entity.position = Vector2(1234, 1234)

        # check
        assert entity.position == Vector2(1234, 1234)

    def test_speed_setter(self) -> None:
        """test setting the position"""
        entity: Entity = Entity(self._mock_world)
        entity.speed = 50

        # check
        assert entity.speed == 50

    def test_entity_loop(self) -> None:
        """test loop method"""
        entity: Entity = Entity(self._mock_world)
        pre_pos: Vector2 = entity.position

        for i in range(60 * 1):
            entity.loop(self._delta_time)

        assert entity.position == pre_pos

        # invincibility frame test
        entity.damage(1)
        for i in range(60 * 1):
            entity.loop(self._delta_time)

        # test with a hitbox to the right of entity
        self.change_mock_world_vals(new_scol=[pygame.Rect(40, 40, 120, 120)])
        entity.static_collide()


class TestPlayer(BaseEntityTest):

    @patch('src.entities.player.PlayerController')
    def test_player_init(self, mock_controller) -> None:
        """test init player"""
        mock_controller.controller_status.return_value = False
        player: Player = Player(self._mock_world)

        # check values
        assert player.position == Vector2()
        assert player.HP == 10
        assert player.speed == 100
        assert player.move_speed == 0
        assert player.look_dir == (1, 0)

    @given(some.integers(1, 10))
    def test_player_damage(self, damage: int):
        """Test player damage"""
        with patch("src.entities.player.PlayerController") as mock_controller:
            mock_controller.controller_stats.return_value = False
            player: Player = Player(self._mock_world)

            # deal damage
            pre_dmg: int = player.HP
            player.damage(damage)
            self.assertEqual(pre_dmg - damage, player.HP)

    @patch('src.entities.player.PlayerController')
    @patch.object(Player, "player_movement")
    def test_player_movement(self, mock_player, mock_controller) -> None:
        """Test player movement"""
        mock_controller.controller_status.return_value = False
        mock_player.return_value = Vector2(1, 0)

        player: Player = Player(self._mock_world)
        pos_start: tuple[float, float] = (player.position.x, player.position.y)

        pseudo_time: float = 0

        for i in range(60):  # simulate one second
            pseudo_time += self._delta_time
            player.loop(self._delta_time)
            player.render(pseudo_time)

        pos_end: tuple[float, float] = (player.position.x, player.position.y)
        self.assertNotEqual(pos_start, pos_end)

        for i in range(60 * 10):  # ten seconds
            pseudo_time += self._delta_time
            player.loop(self._delta_time)
            player.render(pseudo_time)

    @patch.object(PlayerController, "controller_status")
    @patch.object(PlayerController, "right_movement", new_callable=PropertyMock)
    @patch.object(PlayerController, "left_movement", new_callable=PropertyMock)
    @patch.object(PlayerController, "up_movement", new_callable=PropertyMock)
    @patch.object(PlayerController, "down_movement", new_callable=PropertyMock)
    def test_player_orient(self,
                           mock_down, mock_up,
                           mock_left, mock_right,
                           mock_controller) -> None:
        """Test player movement"""
        mock_controller.return_value = False
        mock_down.return_value = False
        mock_up.return_value = False
        mock_left.return_value = False
        mock_right.return_value = False

        player: Player = Player(self._mock_world)

        mock_right.return_value = True
        player.loop(self._delta_time)
        assert player.look_dir == (1, 0)
        mock_right.return_value = False

        mock_left.return_value = True
        player.loop(self._delta_time)
        assert player.look_dir == (-1, 0)
        mock_left.return_value = False

        mock_up.return_value = True
        player.loop(self._delta_time)
        assert player.look_dir == (0, -1)
        mock_up.return_value = False

        mock_down.return_value = True
        player.loop(self._delta_time)
        assert player.look_dir == (0, 1)
        mock_down.return_value = False


class TestJelly(BaseEntityTest):

    def test_jelly_init(self):
        """test jelly init"""
        jelly: Jelly = Jelly(self._mock_world)

        # check vals
        assert jelly.position == Vector2()
        assert jelly.speed == 300
        assert jelly.move_speed == 0
        assert jelly.HP == 3

    @given(some.integers(1, 3))
    def test_jelly_damage(self, damage: int):
        """Test jelly damage"""
        jelly: Jelly = Jelly(self._mock_world)

        # deal damage
        pre_dmg: int = jelly.HP
        jelly.damage(damage)
        self.assertEqual(pre_dmg - damage, jelly.HP)

    def test_jelly_loop(self):
        """test jelly loop"""
        jelly: Jelly = Jelly(self._mock_world)
        self.change_mock_world_vals(new_pos=Vector2(1000, 1000))

        for i in range(60 * 5):
            jelly.loop(self._delta_time)

        assert jelly.position == Vector2()  # no movement

        # test with player nearby
        self.change_mock_world_vals(new_pos=Vector2(100, 200))
        for i in range(60 * 5):
            jelly.loop(self._delta_time)

        # test attacking player
        self.change_mock_world_vals(new_col=True)
        for i in range(60 * 5):
            jelly.loop(self._delta_time)

        # test static collision
        self.change_mock_world_vals(new_scol=[pygame.Rect()])

    def test_coral_render(self):
        """Test jelly render method"""
        jelly: Jelly = Jelly(self._mock_world)

        pseudo_time: float = 0

        # test without damage
        for i in range(60 * 10):
            pseudo_time += self._delta_time
            jelly.render(pseudo_time)

        # damage and render
        jelly.damage(1)
        for i in range(60 * 10):
            pseudo_time += self._delta_time
            jelly.render(pseudo_time)


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
        """Test coral damage"""
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
        """Test coral render method"""
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


class TestUrchin(BaseEntityTest):

    def setUp(self) -> None:
        self._ROOM_BOUNDS: dict[str, tuple[int, int]] = {
            'X': (284, 1160),
            'Y': (205, 685)
        }
        return super().setUp()

    def test_urchin_init(self):
        """Test urchin init"""
        urchin: Urchin = Urchin(self._mock_world, self._ROOM_BOUNDS)

        # check values
        assert urchin.position == Vector2()
        assert urchin.speed == 50
        assert urchin.move_speed == 0
        assert urchin.HP == 3

    @given(some.integers(1, 15))
    def test_urchin_damage(self, damage: int):
        """Test urchin damage"""
        urchin: Urchin = Urchin(self._mock_world, self._ROOM_BOUNDS)

        # deal damage
        pre_dmg: int = urchin.HP
        urchin.damage(damage)
        self.assertEqual(pre_dmg - damage, urchin.HP)

    def test_urchin_loop(self):
        """Test urchin loop method"""
        urchin: Urchin = Urchin(self._mock_world, self._ROOM_BOUNDS)

        for i in range(60 * 10):
            urchin.loop(self._delta_time)

        # run for a minute
        self.change_mock_world_vals(new_pos=Vector2(300, 500), new_col=True)
        for i in range(60 * 30):
            urchin.loop(self._delta_time)

        self.change_mock_world_vals(new_pos=Vector2(1400, 800), new_col=True)
        for i in range(60 * 30):
            urchin.loop(self._delta_time)

        # check theoretical run into wall

        self.change_mock_world_vals(new_scol=[pygame.Rect()])
        for i in range(60 * 10):  # run for 10 seconds
            urchin.loop(self._delta_time)

    def test_urchin_render(self):
        """Test urchin render method"""
        urchin: Urchin = Urchin(self._mock_world, self._ROOM_BOUNDS)

        pseudo_time: float = 0

        # test without damage
        for i in range(60 * 10):
            pseudo_time += self._delta_time
            urchin.render(pseudo_time)

        # damage and render
        urchin.damage(1)
        for i in range(60 * 10):
            pseudo_time += self._delta_time
            urchin.render(pseudo_time)


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
