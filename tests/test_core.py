import pytest
from core.config import Config
from core.tower import Tower
from entities.business import Business

def test_tower_initialization():
    config = Config()
    tower = Tower(config)
    
    # Test initial floors
    assert len(tower.floors) == 3
    assert all(len(floor) == 20 for floor in tower.floors)
    
def test_business_placement():
    config = Config()
    tower = Tower(config)
    
    # Test valid business placement
    assert tower.can_place_building((0, 0), 'hotel')
    assert tower.add_business((0, 0), 'hotel')
    
    # Test invalid placement (overlapping)
    assert not tower.can_place_building((0, 0), 'hotel')
    assert not tower.add_business((0, 0), 'hotel')
    
def test_business_creation():
    config = Config()
    business = Business((0, 0), 'hotel', config)
    
    assert business.type == 'hotel'
    assert business.size == config.BUSINESS_TYPES['hotel']['size']
    assert business.satisfaction == 100  # Initial satisfaction
