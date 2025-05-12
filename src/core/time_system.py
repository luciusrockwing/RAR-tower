from typing import Callable, List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
from enum import Enum
from src.core.config import EventType

class EventPriority(Enum):
    LOW = 0      # Regular events like weather changes
    MEDIUM = 1   # Rush hours, sales
    HIGH = 2     # VIP visits, maintenance
    CRITICAL = 3 # Kaiju attacks, emergencies

class EventStatus(Enum):
    SCHEDULED = 'scheduled'
    ACTIVE = 'active'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class GameEvent:
    def __init__(self, time: datetime, callback: Callable, repeating: bool = False, 
                 repeat_interval: timedelta = None, data: Dict[str, Any] = None,
                 priority: EventPriority = EventPriority.MEDIUM):
        self.time = time
        self.callback = callback
        self.repeating = repeating
        self.repeat_interval = repeat_interval
        self.data = data or {}
        self.priority = priority
        self.status = EventStatus.SCHEDULED
        self.notification_sent = False
        
    def __lt__(self, other):
        # Sort by time first, then by priority
        if self.time == other.time:
            return self.priority.value > other.priority.value
        return self.time < other.time

class EventNotification:
    def __init__(self, event_type: str, message: str, time: datetime, 
                 priority: EventPriority, data: Dict[str, Any] = None):
        self.event_type = event_type
        self.message = message
        self.time = time
        self.priority = priority
        self.data = data or {}
        self.read = False

class TimeSystem:
    def __init__(self, config):
        self.config = config
        self.current_time = datetime(2025, 1, 1, hour=self.config.OPENING_HOUR)
        self.events = []
        self.notifications = []
        self.speed_multiplier = 1.0
        self.paused = False
        
        # Event callbacks
        self.on_event_check = None
        self.on_festival_start = None
        self.on_festival_end = None
        self.on_kaiju_attack = None
        self.on_emergency_drill = None
        
        # Initialize recurring events
        self._setup_recurring_events()
    
    def _setup_recurring_events(self):
        """Set up recurring events like rush hours and daily checks"""
        # Rush hours (morning and evening)
        self.schedule_recurring_event(
            callback=self._trigger_rush_hour,
            start_time=datetime(2025, 1, 1, 8),  # 8 AM
            interval=timedelta(days=1),
            priority=EventPriority.MEDIUM,
            data={'rush_type': 'morning'}
        )
        
        self.schedule_recurring_event(
            callback=self._trigger_rush_hour,
            start_time=datetime(2025, 1, 1, 17),  # 5 PM
            interval=timedelta(days=1),
            priority=EventPriority.MEDIUM,
            data={'rush_type': 'evening'}
        )
        
        # Daily event check
        self.schedule_recurring_event(
            callback=self._daily_event_check,
            start_time=self.current_time,
            interval=timedelta(days=1),
            priority=EventPriority.LOW
        )
    
    def schedule_recurring_event(self, callback: Callable, start_time: datetime,
                               interval: timedelta, priority: EventPriority,
                               data: Dict[str, Any] = None) -> None:
        """Schedule a recurring event"""
        event = GameEvent(
            time=start_time,
            callback=callback,
            repeating=True,
            repeat_interval=interval,
            data=data,
            priority=priority
        )
        self.events.append(event)
        self.events.sort()  # Keep events sorted by time and priority
    
    def schedule_event(self, callback: Callable, delay: timedelta,
                      data: Dict[str, Any] = None, 
                      priority: EventPriority = EventPriority.MEDIUM) -> None:
        """Schedule a one-time event"""
        event = GameEvent(
            time=self.current_time + delay,
            callback=callback,
            data=data,
            priority=priority
        )
        self.events.append(event)
        self.events.sort()
    
    def _daily_event_check(self, data: Dict[str, Any] = None) -> None:
        """Perform daily check for random events"""
        if self.on_event_check:
            self.on_event_check()
    
    def _trigger_rush_hour(self, data: Dict[str, Any]) -> None:
        """Handle rush hour events"""
        rush_type = data.get('rush_type', 'morning')
        # Implement rush hour logic
        
    def update(self, dt: float) -> None:
        """Update the time system"""
        if self.paused:
            return
            
        # Update current time
        time_delta = timedelta(seconds=dt * self.speed_multiplier)
        self.current_time += time_delta
        
        # Process events
        self._process_events()
        
    def _process_events(self) -> None:
        """Process all pending events"""
        # Process events that are due
        while self.events and self.events[0].time <= self.current_time:
            event = self.events.pop(0)
            if event.status != EventStatus.CANCELLED:
                # Execute event callback
                event.callback(event.data)
                event.status = EventStatus.COMPLETED
                
                # If event is recurring, schedule next occurrence
                if event.repeating and event.repeat_interval:
                    next_time = event.time + event.repeat_interval
                    new_event = GameEvent(
                        time=next_time,
                        callback=event.callback,
                        repeating=True,
                        repeat_interval=event.repeat_interval,
                        data=event.data,
                        priority=event.priority
                    )
                    self.events.append(new_event)
                    self.events.sort()
    
    def set_speed(self, speed: str) -> None:
        """Set game speed"""
        speeds = {
            'pause': 0.0,
            'normal': 1.0,
            'fast': 2.0,
            'ultra': 5.0
        }
        self.speed_multiplier = speeds.get(speed, 1.0)
        self.paused = (speed == 'pause')
