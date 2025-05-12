from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from src.core.config import BuildingType, EventType
from src.core.mini_games import MiniGameType, MiniGameDifficulty

@dataclass
class MapMetadata:
    """Metadata for a custom map"""
    name: str
    description: str
    difficulty: int  # 1-5
    max_floors: int
    population_goal: int
    special_events: List[EventType] = field(default_factory=list)
    allowed_buildings: List[BuildingType] = field(default_factory=list)
    starting_cash: int = 1000000
    theme: Optional[str] = None
    custom_properties: Dict = field(default_factory=dict)
    mini_games: Dict[MiniGameType, MiniGameDifficulty] = field(default_factory=dict)

class BaseMap:
    """Base class for all custom maps"""
    def __init__(self, metadata: MapMetadata):
        self.metadata = metadata
        self.special_events = []
        self.restricted_areas = []  # Areas where building is not allowed
        self.predefined_structures = []  # Pre-built structures
        self.mini_game_locations = {}  # Locations where mini-games can be triggered
        
    def initialize_map(self) -> None:
        """Set up any initial map state"""
        pass
    
    def get_special_events(self) -> List[dict]:
        """Return map-specific events"""
        return self.special_events
    
    def validate_build(self, x: int, y: int, building_type: BuildingType) -> bool:
        """Check if building is allowed at the specified location"""
        return True
    
    def on_population_milestone(self, population: int) -> None:
        """Handle population milestone events"""
        pass
    
    def on_star_rating_change(self, stars: int) -> None:
        """Handle star rating change events"""
        pass
    
    def get_available_mini_games(self, x: int, y: int) -> List[Tuple[MiniGameType, MiniGameDifficulty]]:
        """Get available mini-games at the specified location"""
        games = []
        for game_type, locations in self.mini_game_locations.items():
            if (x, y) in locations and game_type in self.metadata.mini_games:
                games.append((game_type, self.metadata.mini_games[game_type]))
        return games
    
    def add_mini_game_location(self, game_type: MiniGameType, x: int, y: int) -> None:
        """Add a location where a mini-game can be triggered"""
        if game_type not in self.mini_game_locations:
            self.mini_game_locations[game_type] = set()
        self.mini_game_locations[game_type].add((x, y))
    
    def remove_mini_game_location(self, game_type: MiniGameType, x: int, y: int) -> None:
        """Remove a mini-game location"""
        if game_type in self.mini_game_locations:
            self.mini_game_locations[game_type].discard((x, y))
            
    def on_mini_game_completed(self, game_type: MiniGameType, success: bool, score: int) -> None:
        """Handle mini-game completion"""
        if success:
            # Apply rewards based on game type and score
            rewards = self._calculate_mini_game_rewards(game_type, score)
            # Handle rewards in the game instance
