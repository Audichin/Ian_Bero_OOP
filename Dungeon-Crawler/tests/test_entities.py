"""Testing module for all in game entities"""
from hypothesis import given
import hypothesis.strategies as some
from unittest.mock import Mock, patch
import unittest

from src.entities.entity_mod import Entity

class TestEntities(unittest.TestCase):
    """Test Entities"""

    def test_entity_init(self) -> None:
        """Test the creation of an entity"""
        mock_world = Mock(return_value=True)
        entity: Entity = Entity(mock_world)
        assert entity.position.x == 0
        assert entity.position.y == 0