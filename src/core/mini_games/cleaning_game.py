from typing import List, Tuple
from random import randint, choice
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.properties import ListProperty, NumericProperty, BooleanProperty
from kivy.vector import Vector
from core.mini_games import BaseMiniGame, MiniGameDifficulty
import math

class CleaningGame(BaseMiniGame):
    """A mini-game where the player must clean dirty areas of a room"""
    cursor_pos = ListProperty([0, 0])
    dirty_spots = ListProperty([])
    clean_spots = ListProperty([])
    cleaning_radius = NumericProperty(30)
    is_cleaning = BooleanProperty(False)
    
    def __init__(self, difficulty: MiniGameDifficulty = MiniGameDifficulty.MEDIUM, **kwargs):
        super(CleaningGame, self).__init__(difficulty=difficulty, **kwargs)
        self.spots_to_clean = self._get_required_spots()
        self.clean_effectiveness = self._get_clean_effectiveness()
        
    def _setup_game(self) -> None:
        """Initialize the cleaning game"""
        self.dirty_spots = self._generate_dirty_spots()
        self.clean_spots = []
        self.is_cleaning = False
        
        # Set game duration based on difficulty
        self.time_remaining = {
            'EASY': 120,
            'MEDIUM': 90,
            'HARD': 60
        }.get(self.difficulty, 90)
        
    def _generate_dirty_spots(self) -> List[Tuple[float, float, float]]:
        """Generate random dirty spots (x, y, size)"""
        spots = []
        num_spots = self.spots_to_clean
        
        for _ in range(num_spots):
            x = randint(50, int(self.width - 50))
            y = randint(50, int(self.height - 50))
            size = randint(20, 40)
            spots.append((x, y, size))
            
        return spots
        
    def _get_required_spots(self) -> int:
        """Get number of spots that need to be cleaned"""
        return {
            'EASY': 8,
            'MEDIUM': 12,
            'HARD': 15
        }.get(self.difficulty, 12)
        
    def _get_clean_effectiveness(self) -> float:
        """Get cleaning effectiveness (speed multiplier)"""
        return {
            'EASY': 1.5,
            'MEDIUM': 1.0,
            'HARD': 0.7
        }.get(self.difficulty, 1.0)
        
    def _update(self, dt: float) -> None:
        """Update game state"""
        super()._update(dt)
        if not self.is_active:
            return
            
        if self.is_cleaning:
            self._clean_spots(dt)
            
        # Check win condition
        if len(self.dirty_spots) == 0:
            self.score += int(self.time_remaining * 100)
            self.end(True)
            
    def _clean_spots(self, dt: float) -> None:
        """Process cleaning of dirty spots"""
        cursor_vec = Vector(self.cursor_pos)
        spots_to_remove = []
        
        for i, (x, y, size) in enumerate(self.dirty_spots):
            spot_vec = Vector(x, y)
            distance = cursor_vec.distance(spot_vec)
            
            if distance < self.cleaning_radius + size:
                # Reduce spot size based on cleaning effectiveness
                new_size = size - (30 * self.clean_effectiveness * dt)
                
                if new_size <= 0:
                    spots_to_remove.append(i)
                    self.clean_spots.append((x, y))
                    self.score += 100
                else:
                    self.dirty_spots[i] = (x, y, new_size)
                    
        # Remove cleaned spots
        for i in reversed(spots_to_remove):
            self.dirty_spots.pop(i)
            
    def on_touch_down(self, touch):
        """Handle touch down event"""
        if self.is_active and self.collide_point(*touch.pos):
            self.cursor_pos = list(touch.pos)
            self.is_cleaning = True
            
    def on_touch_move(self, touch):
        """Handle touch move event"""
        if self.is_active and self.is_cleaning and self.collide_point(*touch.pos):
            self.cursor_pos = list(touch.pos)
            
    def on_touch_up(self, touch):
        """Handle touch up event"""
        self.is_cleaning = False
