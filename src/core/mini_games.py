from enum import Enum, auto
from typing import Dict, Any, List, Optional, Callable
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.clock import Clock
from datetime import datetime, timedelta

class MiniGameType(Enum):
    """Types of mini-games available"""
    CATCH_THIEF = auto()
    CLEAN_ROOM = auto()
    FIX_ELEVATOR = auto()
    PEST_CONTROL = auto()
    STOP_FIRE = auto()

class MiniGameDifficulty(Enum):
    """Difficulty levels for mini-games"""
    EASY = 1
    MEDIUM = 2
    HARD = 3

class MiniGameResult:
    """Result of a mini-game session"""
    def __init__(self, success: bool, score: int, bonus: Dict[str, Any]):
        self.success = success
        self.score = score
        self.bonus = bonus
        self.completion_time = datetime.now()

class BaseMiniGame(Widget):
    """Base class for all mini-games"""
    score = NumericProperty(0)
    time_remaining = NumericProperty(60)  # Default 60 seconds
    is_active = BooleanProperty(False)
    difficulty = StringProperty('MEDIUM')
    
    def __init__(self, difficulty: MiniGameDifficulty = MiniGameDifficulty.MEDIUM, **kwargs):
        super(BaseMiniGame, self).__init__(**kwargs)
        self.difficulty = difficulty.name
        self.callbacks = {
            'on_complete': None,
            'on_fail': None,
            'on_score_change': None
        }
        self._game_clock = None
    
    def start(self) -> None:
        """Start the mini-game"""
        self.is_active = True
        self.score = 0
        self._setup_game()
        self._game_clock = Clock.schedule_interval(self._update, 1.0 / 60.0)
    
    def end(self, success: bool = False) -> None:
        """End the mini-game"""
        self.is_active = False
        if self._game_clock:
            self._game_clock.cancel()
        
        result = MiniGameResult(
            success=success,
            score=self.score,
            bonus=self._calculate_bonus()
        )
        
        if success and self.callbacks['on_complete']:
            self.callbacks['on_complete'](result)
        elif not success and self.callbacks['on_fail']:
            self.callbacks['on_fail'](result)
    
    def _setup_game(self) -> None:
        """Set up the mini-game (override in subclass)"""
        pass
    
    def _update(self, dt: float) -> None:
        """Update game state (override in subclass)"""
        if self.is_active:
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.end(False)
    
    def _calculate_bonus(self) -> Dict[str, Any]:
        """Calculate bonus rewards based on score and difficulty"""
        base_bonus = {
            'money': self.score * 100,
            'reputation': self.score * 5
        }
        
        # Apply difficulty multiplier
        multiplier = {
            'EASY': 1.0,
            'MEDIUM': 1.5,
            'HARD': 2.0
        }.get(self.difficulty, 1.0)
        
        return {
            k: int(v * multiplier) for k, v in base_bonus.items()
        }
    
    def set_callback(self, event: str, callback: Callable) -> None:
        """Set a callback for a specific event"""
        if event in self.callbacks:
            self.callbacks[event] = callback
