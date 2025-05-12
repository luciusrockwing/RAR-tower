from src.maps.templates.base_map import BaseMap, MapMetadata
from src.core.config import BuildingType, EventType
from src.core.mini_games import MiniGameType, MiniGameDifficulty

class TokyoTowerMap(BaseMap):
    """Tokyo Tower themed map with special events and mini-games"""
    def __init__(self):
        metadata = MapMetadata(
            name="Tokyo Tower",
            description="Build your tower in the heart of Tokyo! Watch out for Kaiju attacks!",
            difficulty=4,
            max_floors=80,
            population_goal=8500,
            special_events=[
                EventType.FESTIVAL,
                EventType.EMERGENCY_DRILL,
                EventType.KAIJU_ATTACK
            ],
            allowed_buildings=[
                BuildingType.OFFICE,
                BuildingType.APARTMENT,
                BuildingType.HOTEL,
                BuildingType.RESTAURANT,
                BuildingType.SHOP
            ],
            theme="tokyo",
            custom_properties={
                "kaiju_attack_chance": 0.001,
                "festival_boost": 1.5
            },
            mini_games={
                MiniGameType.CATCH_THIEF: MiniGameDifficulty.MEDIUM,
                MiniGameType.CLEAN_ROOM: MiniGameDifficulty.EASY,
                MiniGameType.FIX_ELEVATOR: MiniGameDifficulty.HARD,
                MiniGameType.PEST_CONTROL: MiniGameDifficulty.MEDIUM,
                MiniGameType.FIRE_FIGHTING: MiniGameDifficulty.HARD
            }
        )
        super().__init__(metadata)
        
    def initialize_map(self):
        """Set up initial Tokyo Tower map state"""
        super().initialize_map()
        
        # Add special landmark views that increase property value
        self.custom_properties["landmark_views"] = [
            {"x": 10, "y": 20, "bonus": 1.2},  # View of Mt. Fuji
            {"x": 30, "y": 15, "bonus": 1.1}   # View of Tokyo Bay
        ]
        
        # Add mini-game locations
        # Thief catching locations (security office areas)
        self.add_mini_game_location(MiniGameType.CATCH_THIEF, 10, 20)
        self.add_mini_game_location(MiniGameType.CATCH_THIEF, 30, 40)
        
        # Room cleaning locations (hotel areas)
        self.add_mini_game_location(MiniGameType.CLEAN_ROOM, 15, 25)
        self.add_mini_game_location(MiniGameType.CLEAN_ROOM, 35, 45)
        
        # Elevator repair locations
        self.add_mini_game_location(MiniGameType.FIX_ELEVATOR, 5, 15)
        self.add_mini_game_location(MiniGameType.FIX_ELEVATOR, 25, 35)
        
        # Pest control locations (restaurant areas)
        self.add_mini_game_location(MiniGameType.PEST_CONTROL, 12, 22)
        self.add_mini_game_location(MiniGameType.PEST_CONTROL, 32, 42)
        
        # Fire fighting locations (throughout the building)
        self.add_mini_game_location(MiniGameType.FIRE_FIGHTING, 8, 18)
        self.add_mini_game_location(MiniGameType.FIRE_FIGHTING, 28, 38)
        
    def on_population_milestone(self, population: int):
        """Handle population milestones"""
        if population >= 5000:
            # Unlock additional building types at higher population
            self.metadata.allowed_buildings.append(BuildingType.MOVIE_THEATER)
            
    def on_star_rating_change(self, stars: int):
        """Handle star rating changes"""
        if stars >= 4:
            # Increase chance of special events at higher ratings
            self.custom_properties["kaiju_attack_chance"] *= 1.5
            self.custom_properties["festival_frequency"] = "monthly"
            
    def on_mini_game_completed(self, game_type: MiniGameType, success: bool, score: int) -> None:
        """Handle mini-game completion with custom rewards"""
        super().on_mini_game_completed(game_type, success, score)
        
        if success:
            rewards = {
                MiniGameType.CATCH_THIEF: {
                    'money': score * 2,
                    'reputation': 50,
                    'security_boost': 0.2
                },
                MiniGameType.CLEAN_ROOM: {
                    'money': score,
                    'reputation': 30,
                    'satisfaction_boost': 0.15
                },
                MiniGameType.FIX_ELEVATOR: {
                    'money': score * 3,
                    'reputation': 100,
                    'maintenance_discount': 0.25
                },
                MiniGameType.PEST_CONTROL: {
                    'money': score * 1.5,
                    'reputation': 75,
                    'restaurant_rating_boost': 0.2
                },
                MiniGameType.FIRE_FIGHTING: {
                    'money': score * 4,
                    'reputation': 150,
                    'insurance_discount': 0.3
                }
            }
            
            if game_type in rewards:
                self.custom_properties.update(rewards[game_type])
