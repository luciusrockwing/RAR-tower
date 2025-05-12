from typing import List, Dict, Tuple
from random import randint, random
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import ListProperty, NumericProperty, BooleanProperty
from kivy.vector import Vector
from kivy.clock import Clock
from core.mini_games import BaseMiniGame, MiniGameDifficulty
import math

class FireFightingGame(BaseMiniGame):
    """A mini-game where player must extinguish fires before they spread"""
    cursor_pos = ListProperty([0, 0])
    fires = ListProperty([])
    water_level = NumericProperty(100)
    is_spraying = BooleanProperty(False)
    spray_radius = NumericProperty(50)
    saved_items = NumericProperty(0)
    
    def __init__(self, difficulty: MiniGameDifficulty = MiniGameDifficulty.MEDIUM, **kwargs):
        super(FireFightingGame, self).__init__(difficulty=difficulty, **kwargs)
        self.spread_timer = None
        self.water_timer = None
        self.items = []  # Valuable items to save
        self.water_usage_rate = self._get_water_usage_rate()
        self.water_recharge_rate = self._get_water_recharge_rate()
        
    def _setup_game(self) -> None:
        """Initialize the fire fighting game"""
        self.fires = self._generate_initial_fires()
        self.items = self._place_valuable_items()
        self.water_level = 100
        self.saved_items = 0
        self.is_spraying = False
        
        # Set game duration
        self.time_remaining = {
            'EASY': 180,
            'MEDIUM': 120,
            'HARD': 90
        }.get(self.difficulty, 120)
        
        # Start timers
        self.spread_timer = Clock.schedule_interval(self._spread_fires, 2)
        self.water_timer = Clock.schedule_interval(self._update_water, 1/30)
        
    def _generate_initial_fires(self) -> List[Dict]:
        """Generate initial fire locations"""
        fires = []
        num_fires = {
            'EASY': 2,
            'MEDIUM': 3,
            'HARD': 4
        }.get(self.difficulty, 3)
        
        for _ in range(num_fires):
            fire = self._create_fire()
            fires.append(fire)
            
        return fires
        
    def _create_fire(self, x: float = None, y: float = None, intensity: float = None) -> Dict:
        """Create a new fire"""
        if x is None:
            x = randint(50, int(self.width - 50))
        if y is None:
            y = randint(50, int(self.height - 50))
        if intensity is None:
            intensity = random() * 0.5 + 0.5  # 0.5 to 1.0
            
        return {
            'pos': [x, y],
            'intensity': intensity,
            'size': 30 + intensity * 20,
            'damage': 0
        }
        
    def _place_valuable_items(self) -> List[Dict]:
        """Place valuable items that need to be protected"""
        items = []
        num_items = {
            'EASY': 5,
            'MEDIUM': 8,
            'HARD': 12
        }.get(self.difficulty, 8)
        
        for _ in range(num_items):
            item = {
                'pos': [randint(50, int(self.width - 50)),
                       randint(50, int(self.height - 50))],
                'value': randint(500, 2000),
                'saved': False,
                'damaged': False
            }
            items.append(item)
            
        return items
        
    def _get_water_usage_rate(self) -> float:
        """Get water usage rate when spraying"""
        return {
            'EASY': 15,
            'MEDIUM': 20,
            'HARD': 25
        }.get(self.difficulty, 20)
        
    def _get_water_recharge_rate(self) -> float:
        """Get water recharge rate when not spraying"""
        return {
            'EASY': 10,
            'MEDIUM': 7,
            'HARD': 5
        }.get(self.difficulty, 7)
        
    def _spread_fires(self, dt: float) -> None:
        """Handle fire spreading"""
        if not self.is_active:
            return
            
        # Grow existing fires
        for fire in self.fires:
            fire['intensity'] = min(1.0, fire['intensity'] + 0.1)
            fire['size'] = 30 + fire['intensity'] * 20
            
        # Spread to new locations
        new_fires = []
        for fire in self.fires:
            if random() < fire['intensity'] * 0.3:
                angle = random() * 2 * math.pi
                distance = randint(50, 100)
                x = fire['pos'][0] + math.cos(angle) * distance
                y = fire['pos'][1] + math.sin(angle) * distance
                
                if 0 < x < self.width and 0 < y < self.height:
                    new_fire = self._create_fire(x, y, fire['intensity'] * 0.8)
                    new_fires.append(new_fire)
                    
        self.fires.extend(new_fires)
        
    def _update_water(self, dt: float) -> None:
        """Update water level"""
        if not self.is_active:
            return
            
        if self.is_spraying:
            self.water_level = max(0, self.water_level - self.water_usage_rate * dt)
        else:
            self.water_level = min(100, self.water_level + self.water_recharge_rate * dt)
            
    def _update(self, dt: float) -> None:
        """Update game state"""
        super()._update(dt)
        if not self.is_active:
            return
            
        if self.is_spraying and self.water_level > 0:
            self._check_spray_hits()
            
        # Update fire damage to items
        self._check_fire_damage()
        
        # Check lose condition (too many items damaged)
        damaged_items = sum(1 for item in self.items if item['damaged'])
        if damaged_items > len(self.items) * 0.4:  # 40% items damaged
            self.end(False)
            
        # Check win condition (enough items saved)
        if self.saved_items >= self._get_required_saves():
            self.score += int(self.time_remaining * 100)
            self.end(True)
            
    def _check_spray_hits(self) -> None:
        """Check if water spray hits any fires"""
        if self.water_level <= 0:
            return
            
        cursor_vec = Vector(self.cursor_pos)
        fires_to_remove = []
        
        for fire in self.fires:
            fire_vec = Vector(fire['pos'])
            if cursor_vec.distance(fire_vec) < self.spray_radius:
                fire['intensity'] -= 0.1
                if fire['intensity'] <= 0:
                    fires_to_remove.append(fire)
                    self.score += 200
                    
        for fire in fires_to_remove:
            self.fires.remove(fire)
            
    def _check_fire_damage(self) -> None:
        """Check if fires are damaging any items"""
        for item in self.items:
            if item['damaged'] or item['saved']:
                continue
                
            item_vec = Vector(item['pos'])
            for fire in self.fires:
                fire_vec = Vector(fire['pos'])
                if fire_vec.distance(item_vec) < fire['size']:
                    item['damaged'] = True
                    break
                    
    def _get_required_saves(self) -> int:
        """Get number of items that need to be saved"""
        return len(self.items) * {
            'EASY': 0.5,    # 50% of items
            'MEDIUM': 0.6,  # 60% of items
            'HARD': 0.7     # 70% of items
        }.get(self.difficulty, 0.6)
        
    def on_touch_down(self, touch):
        """Handle touch down event"""
        if self.is_active and self.collide_point(*touch.pos):
            self.cursor_pos = list(touch.pos)
            self.is_spraying = True
            
            # Check if touched item can be saved
            item_vec = Vector(touch.pos)
            for item in self.items:
                if not item['damaged'] and not item['saved']:
                    if item_vec.distance(Vector(item['pos'])) < 30:
                        item['saved'] = True
                        self.saved_items += 1
                        self.score += item['value']
                        break
                        
    def on_touch_move(self, touch):
        """Handle touch move event"""
        if self.is_active and self.is_spraying and self.collide_point(*touch.pos):
            self.cursor_pos = list(touch.pos)
            
    def on_touch_up(self, touch):
        """Handle touch up event"""
        self.is_spraying = False
        
    def end(self, success: bool = False) -> None:
        """Clean up when game ends"""
        if self.spread_timer:
            self.spread_timer.cancel()
        if self.water_timer:
            self.water_timer.cancel()
        super().end(success)
