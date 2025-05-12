from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from entities.business import Business, BusinessType
from kivy.properties import ListProperty, NumericProperty, ObjectProperty, StringProperty
from typing import Optional, List, Dict
from src.maps.templates.base_map import BaseMap
from src.core.config import Config
import importlib
import os
from dataclasses import dataclass

@dataclass
class Floor:
    """Represents a floor in the tower"""
    number: int
    business: Optional[Business] = None
    is_occupied: bool = False
    maintenance_level: float = 100  # 0-100
    traffic: int = 0  # Number of people on this floor

from random import random
from entities.business import Business, BusinessType, BusinessEvent

class Tower(Widget):
    floors = ListProperty([])
    max_floors = NumericProperty(100)
    floor_width = NumericProperty(20)
    current_map = ObjectProperty(None)
    current_theme = StringProperty(None)
    MAX_FLOORS = 300  # Maximum number of floors allowed
    
    def __init__(self, map_name: str = "tokyo_tower", **kwargs):
        super(Tower, self).__init__(**kwargs)
        self.businesses = []
        self.total_visitors = 0
        self.elevator_capacity = 20
        self.elevator_speed = 1.0  # floors per second
        self.reputation = 50  # 0-100
        self.load_map(map_name)
        self.initialize_tower()
        
        # Bind to size and position changes
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        
    def load_map(self, map_name: str) -> None:
        """Load a custom map by name"""
        try:
            # Import the map module dynamically
            module = importlib.import_module(f"src.maps.{map_name}")
            # Get the map class (assuming it's the only class in the module)
            map_class = next(obj for name, obj in module.__dict__.items() 
                           if isinstance(obj, type) and issubclass(obj, BaseMap))
            self.current_map = map_class()
            
            # Apply map settings
            self.max_floors = self.current_map.metadata.max_floors
            self.current_theme = self.current_map.metadata.theme
            
            # Initialize map-specific features
            self.current_map.initialize_map()
            
        except Exception as e:
            print(f"Error loading map {map_name}: {e}")
            # Load default empty map
            self.max_floors = 100
            self.current_theme = None
    
    def initialize_tower(self):
        """Initialize the tower with map-specific settings"""
        self.floors.clear()
        # Start with 3 empty floors
        for _ in range(3):
            self.add_floor()
            
        # Apply any predefined structures from the map
        if self.current_map and self.current_map.predefined_structures:
            for structure in self.current_map.predefined_structures:
                self.add_predefined_structure(structure)

    def add_predefined_structure(self, structure: Dict) -> None:
        """Add a predefined structure from the map configuration"""
        if 'type' in structure and 'position' in structure:
            business_type = structure['type']
            x, y = structure['position']
            if self.can_place_building((x, y), business_type):
                self.add_business(business_type, (x, y))
    
    def add_floor(self):
        """Add a new floor to the tower"""
        if len(self.floors) < self.MAX_FLOORS:
            new_floor = [None] * self.floor_width
            self.floors.append(new_floor)
            self.update_graphics()
            return True
        else:
            print("Maximum floor limit reached!")
        return False
    
    def update_graphics(self, *args):
        """Update the tower's graphics with theme-specific colors"""
        self.canvas.clear()
        with self.canvas:
            # Apply theme-specific colors if available
            theme_colors = self.get_theme_colors()
            
            # Draw floors
            for floor_num, floor in enumerate(self.floors):
                y = floor_num * self.parent.grid_size
                
                # Draw floor background with theme color
                Color(*theme_colors.get('floor_bg', (0.95, 0.95, 0.95, 1)))
                Rectangle(pos=(self.x, self.y + y),
                         size=(self.floor_width * self.parent.grid_size, self.parent.grid_size))
                
                # Draw businesses on this floor with theme-specific colors
                for tile_num, business in enumerate(floor):
                    if business:
                        business.draw(self.canvas, (tile_num, floor_num), 
                                   self.parent.grid_size, theme_colors)
    
    def get_theme_colors(self) -> Dict:
        """Get the current theme's color scheme"""
        if self.current_theme and self.current_theme in Config.AVAILABLE_THEMES:
            return Config.AVAILABLE_THEMES[self.current_theme]['color_scheme']
        return {}
    
    def can_place_building(self, position: tuple, business_type: str) -> bool:
        """Check if a building can be placed at the specified position"""
        x, y = position
        
        # Check map-specific building restrictions
        if self.current_map and not self.current_map.validate_build(x, y, business_type):
            return False
            
        # Check if the position is within restricted areas
        if self.current_map and any(area.contains(x, y) for area in self.current_map.restricted_areas):
            return False
            
        # Continue with regular placement checks
        if not self.is_position_valid(position):
            return False
            
        # Get business size from app config
        business_config = self.parent.config.BUSINESS_TYPES.get(business_type)
        if not business_config:
            return False
            
        width, height = business_config['size']
        
        # Check if space is available
        for dx in range(width):
            for dy in range(height):
                check_pos = (x + dx, y + dy)
                if not self.is_position_empty(check_pos):
                    return False
        
        return True
    
    def add_business(self, business_type: BusinessType, floor_number: int) -> bool:
        """Add a new business to the tower"""
        if not 0 <= floor_number < self.MAX_FLOORS:
            return False
            
        # Check if target floors are available
        business = Business(business_type, floor_number)
        required_floors = range(floor_number, floor_number + business.size)
        
        if not all(0 <= f < self.MAX_FLOORS and not self.floors[f].is_occupied 
                  for f in required_floors):
            return False
        
        # Occupy the floors
        for f in required_floors:
            self.floors[f].is_occupied = True
            self.floors[f].business = business
        
        self.businesses.append(business)
        self.update_graphics()
        return True
    
    def remove_business(self, floor_number: int) -> bool:
        """Remove a business from the tower"""
        if not 0 <= floor_number < self.MAX_FLOORS:
            return False
            
        floor = self.floors[floor_number]
        if not floor.business:
            return False
            
        business = floor.business
        # Free up all floors occupied by this business
        for f in range(business.floor, business.floor + business.size):
            self.floors[f].is_occupied = False
            self.floors[f].business = None
        
        self.businesses.remove(business)
        self.update_graphics()
        return True
    
    def is_position_valid(self, position):
        """Check if the position is within tower bounds"""
        x, y = position
        return (0 <= y < len(self.floors) and 
                0 <= x < self.floor_width)
    
    def is_position_empty(self, position):
        """Check if the position is empty"""
        x, y = position
        if not self.is_position_valid(position):
            return False
        return self.floors[y][x] is None
    
    def update(self, dt: float):
        """Update tower state"""
        self.total_visitors = 0
        current_hour = self.time_system.current_hour if hasattr(self, 'time_system') else 12
        
        # Update nearby business lists and synergies
        for business in self.businesses:
            nearby = self._get_nearby_businesses(business.floor, 5)  # 5 floor radius
            business.update_synergy(nearby)
            
            # Random events
            self._check_random_events(business)
            
            # Update business with current time
            business.update(dt, current_hour)
            self.total_visitors += len(business.customers)
            
            # Update floor traffic
            for f in range(business.floor, business.floor + business.size):
                self.floors[f].traffic = len(business.customers) // business.size
        
        # Update tower reputation based on business satisfaction and synergies
        if self.businesses:
            avg_satisfaction = sum(b.satisfaction for b in self.businesses) / len(self.businesses)
            avg_synergy = sum(b.synergy_bonus for b in self.businesses) / len(self.businesses)
            self.reputation = (self.reputation * 0.9 + 
                             avg_satisfaction * 0.07 +
                             avg_synergy * 100 * 0.03)
    
    def _get_nearby_businesses(self, floor: int, radius: int) -> List[Business]:
        """Get list of businesses within specified floor radius"""
        nearby = []
        for f in range(max(0, floor - radius), min(self.MAX_FLOORS, floor + radius + 1)):
            if f != floor and self.floors[f].business:
                nearby.append(self.floors[f].business)
        return nearby
    
    def _check_random_events(self, business: Business) -> None:
        """Check for random business events"""
        if random() < 0.01:  # 1% chance per update
            event_chances = {
                BusinessEvent.SPECIAL_PROMOTION: 0.3,
                BusinessEvent.CELEBRITY_VISIT: 0.1,
                BusinessEvent.STAFF_SHORTAGE: 0.2,
                BusinessEvent.EQUIPMENT_FAILURE: 0.2,
                BusinessEvent.HEALTH_INSPECTION: 0.15,
                BusinessEvent.RENOVATION: 0.05
            }
            
            for event, chance in event_chances.items():
                if random() < chance:
                    business.trigger_event(event)
                    break
    
    def get_floor_stats(self, floor_number: int) -> Dict:
        """Get statistics for a specific floor"""
        if not 0 <= floor_number < self.MAX_FLOORS:
            return {}
            
        floor = self.floors[floor_number]
        stats = {
            'number': floor.number,
            'occupied': floor.is_occupied,
            'maintenance': floor.maintenance_level,
            'traffic': floor.traffic,
        }
        
        if floor.business:
            stats.update({
                'business_type': floor.business.type.value,
                'business_name': floor.business.name,
                'income': floor.business.actual_income,
                'satisfaction': floor.business.satisfaction,
                'customers': len(floor.business.customers),
                'synergy_bonus': floor.business.synergy_bonus,
                'events': floor.business.events,
                'peak_hours': floor.business.peak_hours
            })
        
        return stats
    
    def get_tower_stats(self) -> Dict:
        """Get overall tower statistics"""
        return {
            'total_floors': self.MAX_FLOORS,
            'occupied_floors': sum(1 for f in self.floors if f.is_occupied),
            'total_businesses': len(self.businesses),
            'total_visitors': self.total_visitors,
            'reputation': self.reputation,
            'total_income': sum(b.income for b in self.businesses),
            'total_maintenance': sum(b.maintenance_cost for b in self.businesses)
        }
    
    def get_building_cost(self, business_type):
        """Get the cost of building a specific business type"""
        business_config = self.parent.config.BUSINESS_TYPES.get(business_type)
        return business_config['cost'] if business_config else 0

    def get_all_businesses(self):
        """Return a list of all business types available."""
        return [
            "Restaurant",
            "Retail Store",
            "Office",
            "Hotel",
            "Gym",
            "Cinema",
            "Arcade",
            "Spa",
            "Conference Room",
            "Rooftop Bar"
        ]

    def include_all_businesses(self):
        """Ensure all business types are included in the tower."""
        for business_type in self.get_all_businesses():
            if business_type not in [b.type for b in self.businesses]:
                self.add_business(Business(type=business_type))
