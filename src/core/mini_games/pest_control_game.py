from typing import List, Dict, Tuple
from random import randint, choice, random
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import ListProperty, NumericProperty, BooleanProperty
from kivy.vector import Vector
from kivy.clock import Clock
from core.mini_games import BaseMiniGame, MiniGameDifficulty
import math

class PestControlGame(BaseMiniGame):
    """A mini-game where player must catch pests before they multiply"""
    cursor_pos = ListProperty([0, 0])
    pests = ListProperty([])
    traps = ListProperty([])
    spray_radius = NumericProperty(40)
    is_spraying = BooleanProperty(False)
    caught_count = NumericProperty(0)
    
    def __init__(self, difficulty: MiniGameDifficulty = MiniGameDifficulty.MEDIUM, **kwargs):
        super(PestControlGame, self).__init__(difficulty=difficulty, **kwargs)
        self.spawn_timer = None
        self.move_timer = None
        self.reproduction_timer = None
        self.pest_speed = self._get_pest_speed()
        self.spawn_interval = self._get_spawn_interval()
        
    def _setup_game(self) -> None:
        """Initialize the pest control game"""
        self.pests = self._generate_initial_pests()
        self.traps = []
        self.caught_count = 0
        self.is_spraying = False
        
        # Set game duration
        self.time_remaining = {
            'EASY': 120,
            'MEDIUM': 90,
            'HARD': 60
        }.get(self.difficulty, 90)
        
        # Start timers
        self.spawn_timer = Clock.schedule_interval(self._spawn_pest, self.spawn_interval)
        self.move_timer = Clock.schedule_interval(self._move_pests, 1/30)
        self.reproduction_timer = Clock.schedule_interval(self._reproduce_pests, 5)
        
    def _generate_initial_pests(self) -> List[Dict]:
        """Generate initial pests"""
        pests = []
        num_pests = {
            'EASY': 3,
            'MEDIUM': 5,
            'HARD': 7
        }.get(self.difficulty, 5)
        
        for _ in range(num_pests):
            pest = self._create_pest()
            pests.append(pest)
            
        return pests
        
    def _create_pest(self, x: float = None, y: float = None) -> Dict:
        """Create a new pest"""
        if x is None:
            x = randint(50, int(self.width - 50))
        if y is None:
            y = randint(50, int(self.height - 50))
            
        return {
            'pos': [x, y],
            'velocity': [random() * 2 - 1, random() * 2 - 1],
            'size': randint(10, 15),
            'type': choice(['cockroach', 'rat', 'spider'])
        }
        
    def _get_pest_speed(self) -> float:
        """Get pest movement speed"""
        return {
            'EASY': 100,
            'MEDIUM': 150,
            'HARD': 200
        }.get(self.difficulty, 150)
        
    def _get_spawn_interval(self) -> float:
        """Get interval between pest spawns"""
        return {
            'EASY': 8,
            'MEDIUM': 6,
            'HARD': 4
        }.get(self.difficulty, 6)
        
    def _spawn_pest(self, dt: float) -> None:
        """Spawn a new pest"""
        if len(self.pests) < self._get_max_pests():
            self.pests.append(self._create_pest())
            
    def _get_max_pests(self) -> int:
        """Get maximum number of allowed pests"""
        return {
            'EASY': 10,
            'MEDIUM': 15,
            'HARD': 20
        }.get(self.difficulty, 15)
        
    def _move_pests(self, dt: float) -> None:
        """Update pest positions"""
        if not self.is_active:
            return
            
        for pest in self.pests:
            # Update position
            pos = pest['pos']
            vel = pest['velocity']
            new_x = pos[0] + vel[0] * self.pest_speed * dt
            new_y = pos[1] + vel[1] * self.pest_speed * dt
            
            # Bounce off walls
            if new_x < 0 or new_x > self.width:
                vel[0] *= -1
                new_x = max(0, min(new_x, self.width))
            if new_y < 0 or new_y > self.height:
                vel[1] *= -1
                new_y = max(0, min(new_y, self.height))
                
            pest['pos'] = [new_x, new_y]
            
            # Random direction changes
            if random() < 0.02:
                pest['velocity'] = [random() * 2 - 1, random() * 2 - 1]
                
    def _reproduce_pests(self, dt: float) -> None:
        """Handle pest reproduction"""
        if not self.is_active or len(self.pests) >= self._get_max_pests():
            return
            
        # Check for nearby pests and reproduce
        for i, pest1 in enumerate(self.pests):
            for pest2 in self.pests[i+1:]:
                if (Vector(pest1['pos']).distance(Vector(pest2['pos'])) < 30 and
                    random() < 0.3):
                    x = (pest1['pos'][0] + pest2['pos'][0]) / 2
                    y = (pest1['pos'][1] + pest2['pos'][1]) / 2
                    self.pests.append(self._create_pest(x, y))
                    break
                    
    def _update(self, dt: float) -> None:
        """Update game state"""
        super()._update(dt)
        if not self.is_active:
            return
            
        if self.is_spraying:
            self._check_spray_hits()
            
        # Check lose condition (too many pests)
        if len(self.pests) >= self._get_max_pests():
            self.end(False)
            
        # Check win condition (enough pests caught)
        if self.caught_count >= self._get_required_catches():
            self.score += int(self.time_remaining * 100)
            self.end(True)
            
    def _check_spray_hits(self) -> None:
        """Check if spray hits any pests"""
        cursor_vec = Vector(self.cursor_pos)
        pests_to_remove = []
        
        for pest in self.pests:
            pest_vec = Vector(pest['pos'])
            if cursor_vec.distance(pest_vec) < self.spray_radius + pest['size']:
                pests_to_remove.append(pest)
                self.caught_count += 1
                self.score += 100
                
        for pest in pests_to_remove:
            self.pests.remove(pest)
            
    def _get_required_catches(self) -> int:
        """Get number of catches needed to win"""
        return {
            'EASY': 10,
            'MEDIUM': 15,
            'HARD': 20
        }.get(self.difficulty, 15)
        
    def on_touch_down(self, touch):
        """Handle touch down event"""
        if self.is_active and self.collide_point(*touch.pos):
            self.cursor_pos = list(touch.pos)
            self.is_spraying = True
            
    def on_touch_move(self, touch):
        """Handle touch move event"""
        if self.is_active and self.is_spraying and self.collide_point(*touch.pos):
            self.cursor_pos = list(touch.pos)
            
    def on_touch_up(self, touch):
        """Handle touch up event"""
        self.is_spraying = False
        
    def end(self, success: bool = False) -> None:
        """Clean up when game ends"""
        if self.spawn_timer:
            self.spawn_timer.cancel()
        if self.move_timer:
            self.move_timer.cancel()
        if self.reproduction_timer:
            self.reproduction_timer.cancel()
        super().end(success)
