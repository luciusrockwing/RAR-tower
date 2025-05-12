from typing import List, Tuple, Optional
from random import randint, choice
from kivy.graphics import Color, Rectangle, Line
from kivy.properties import ListProperty, NumericProperty
from kivy.vector import Vector
from core.mini_games import BaseMiniGame, MiniGameDifficulty
import math

class ThiefGame(BaseMiniGame):
    """A mini-game where the player must catch a thief in the tower"""
    thief_pos = ListProperty([0, 0])
    player_pos = ListProperty([0, 0])
    floor_layout = ListProperty([])
    caught_count = NumericProperty(0)
    
    def __init__(self, difficulty: MiniGameDifficulty = MiniGameDifficulty.MEDIUM, **kwargs):
        super(ThiefGame, self).__init__(difficulty=difficulty, **kwargs)
        self.movement_patterns = []
        self.current_pattern = 0
        self.thief_speed = self._get_thief_speed()
        self.catch_radius = self._get_catch_radius()
        
    def _setup_game(self) -> None:
        """Initialize the thief-catching game"""
        # Set up the floor layout (simplified representation of the tower floor)
        self.floor_layout = self._generate_floor_layout()
        
        # Set initial positions
        self.thief_pos = self._get_random_position()
        self.player_pos = [self.width / 2, self.height / 2]
        
        # Generate movement patterns for the thief
        self._generate_movement_patterns()
        
        # Set game duration based on difficulty
        self.time_remaining = {
            'EASY': 90,
            'MEDIUM': 60,
            'HARD': 45
        }.get(self.difficulty, 60)
        
    def _get_thief_speed(self) -> float:
        """Get thief movement speed based on difficulty"""
        return {
            'EASY': 100,
            'MEDIUM': 150,
            'HARD': 200
        }.get(self.difficulty, 150)
        
    def _get_catch_radius(self) -> float:
        """Get the radius within which the thief can be caught"""
        return {
            'EASY': 50,
            'MEDIUM': 35,
            'HARD': 25
        }.get(self.difficulty, 35)
        
    def _generate_floor_layout(self) -> List[List[bool]]:
        """Generate a random floor layout with walls and obstacles"""
        width = 20
        height = 15
        layout = [[True for _ in range(width)] for _ in range(height)]
        
        # Add some random walls and obstacles
        num_obstacles = {
            'EASY': 5,
            'MEDIUM': 8,
            'HARD': 12
        }.get(self.difficulty, 8)
        
        for _ in range(num_obstacles):
            x = randint(1, width-2)
            y = randint(1, height-2)
            # Create small wall segments
            for dx, dy in [(0,0), (1,0), (0,1), (1,1)]:
                if 0 <= x+dx < width and 0 <= y+dy < height:
                    layout[y+dy][x+dx] = False
                    
        return layout
        
    def _generate_movement_patterns(self) -> None:
        """Generate random movement patterns for the thief"""
        num_patterns = {
            'EASY': 3,
            'MEDIUM': 5,
            'HARD': 7
        }.get(self.difficulty, 5)
        
        self.movement_patterns = []
        for _ in range(num_patterns):
            pattern = []
            duration = randint(2, 4)  # seconds per pattern
            points = randint(3, 6)    # points in the pattern
            
            # Generate random points for the pattern
            for _ in range(points):
                point = self._get_random_position()
                pattern.append((point, duration / points))
                
            self.movement_patterns.append(pattern)
            
    def _get_random_position(self) -> List[float]:
        """Get a random valid position on the floor"""
        valid = False
        pos = [0, 0]
        while not valid:
            pos = [
                randint(0, int(self.width)),
                randint(0, int(self.height))
            ]
            valid = self._is_valid_position(pos)
        return pos
        
    def _is_valid_position(self, pos: List[float]) -> bool:
        """Check if a position is valid (not in a wall/obstacle)"""
        x = int(pos[0] / (self.width / len(self.floor_layout[0])))
        y = int(pos[1] / (self.height / len(self.floor_layout)))
        
        return (0 <= x < len(self.floor_layout[0]) and 
                0 <= y < len(self.floor_layout) and 
                self.floor_layout[y][x])
        
    def _update(self, dt: float) -> None:
        """Update game state"""
        super()._update(dt)
        if not self.is_active:
            return
            
        # Update thief position based on current pattern
        self._update_thief_position(dt)
        
        # Check if player caught the thief
        if self._check_catch():
            self.caught_count += 1
            self.score += self._calculate_catch_score()
            
            if self.caught_count >= self._get_required_catches():
                self.end(True)
            else:
                # Move thief to new position
                self.thief_pos = self._get_random_position()
                
    def _update_thief_position(self, dt: float) -> None:
        """Update the thief's position based on movement pattern"""
        if not self.movement_patterns:
            return
            
        pattern = self.movement_patterns[self.current_pattern]
        target, time = pattern[0]
        
        # Move towards target
        current_pos = Vector(self.thief_pos)
        target_pos = Vector(target)
        
        direction = target_pos - current_pos
        if direction.length() > 0:
            direction = direction.normalize()
            new_pos = current_pos + direction * self.thief_speed * dt
            
            # Check if new position is valid
            if self._is_valid_position([new_pos.x, new_pos.y]):
                self.thief_pos = [new_pos.x, new_pos.y]
                
        # Check if we need to move to next point in pattern
        if Vector(self.thief_pos).distance(target_pos) < 10:
            pattern.pop(0)
            if not pattern:
                self.current_pattern = (self.current_pattern + 1) % len(self.movement_patterns)
                self._generate_movement_patterns()  # Regenerate patterns if needed
                
    def _check_catch(self) -> bool:
        """Check if the player has caught the thief"""
        distance = Vector(self.thief_pos).distance(Vector(self.player_pos))
        return distance <= self.catch_radius
        
    def _calculate_catch_score(self) -> int:
        """Calculate score for catching the thief"""
        base_score = 1000
        time_bonus = int(self.time_remaining * 10)
        difficulty_multiplier = {
            'EASY': 1,
            'MEDIUM': 1.5,
            'HARD': 2
        }.get(self.difficulty, 1)
        
        return int((base_score + time_bonus) * difficulty_multiplier)
        
    def _get_required_catches(self) -> int:
        """Get the number of catches required to win"""
        return {
            'EASY': 2,
            'MEDIUM': 3,
            'HARD': 4
        }.get(self.difficulty, 3)
        
    def on_touch_down(self, touch):
        """Handle player movement"""
        if self.is_active and self.collide_point(*touch.pos):
            self.player_pos = list(touch.pos)
