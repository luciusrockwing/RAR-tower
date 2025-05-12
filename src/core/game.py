from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line
from kivy.properties import NumericProperty, BooleanProperty, StringProperty, ObjectProperty, ListProperty
from core.tower import Tower
from core.economy import Economy
from core.time_system import TimeSystem
from core.config import Config, EventType
from utils.asset_manager import AssetManager
from datetime import timedelta
from typing import Dict, Any, List, Optional
import random
from entities.business import BusinessType

class Game(Widget):
    money = NumericProperty(1000000)
    paused = BooleanProperty(False)
    selected_tool = StringProperty(None)
    grid_size = NumericProperty(32)
    current_time = StringProperty("")
    active_notifications = ListProperty([])
    current_speed = StringProperty('normal')
    population = NumericProperty(0)
    star_rating = NumericProperty(1)
    
    def __init__(self, map_name: str = "tokyo_tower", **kwargs):
        super(Game, self).__init__(**kwargs)
        
        # Initialize asset manager
        self.asset_manager = AssetManager()
        
        # Initialize game systems
        self.tower = Tower(map_name=map_name)
        self.economy = Economy()
        self.time_system = TimeSystem(Config)
        self.active_events = {}
        
        # Load theme based on map
        if self.tower.current_map and self.tower.current_map.metadata.theme:
            self.asset_manager.load_theme(self.tower.current_map.metadata.theme)
        
        # Set up time system callbacks
        self._setup_event_callbacks()
        
        # Bind to size and position changes
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        
        # Initial graphics setup
        self.setup_graphics()
        
    def _setup_event_callbacks(self):
        """Set up callbacks for different event types"""
        # Map-specific event handlers
        self.time_system.on_event_check = self._check_map_events
        
        # Standard event handlers
        self.time_system.on_vip_arrival = self._handle_vip_arrival
        self.time_system.on_vip_departure = self._handle_vip_departure
        
        self.time_system.on_maintenance_start = self._handle_maintenance_start
        self.time_system.on_maintenance_end = self._handle_maintenance_end
        
        self.time_system.on_sale_start = self._handle_sale_start
        self.time_system.on_sale_end = self._handle_sale_end
        
        self.time_system.on_power_outage = self._handle_power_outage
        self.time_system.on_power_restore = self._handle_power_restore
        
        # New event handlers
        self.time_system.on_festival_start = self._handle_festival_start
        self.time_system.on_festival_end = self._handle_festival_end
        self.time_system.on_kaiju_attack = self._handle_kaiju_attack
        self.time_system.on_emergency_drill = self._handle_emergency_drill
        
    def _check_map_events(self) -> None:
        """Check and trigger map-specific events"""
        if self.tower.current_map:
            # Get map-specific events
            special_events = self.tower.current_map.get_special_events()
            
            # Check each event's probability
            for event_type in special_events:
                prob = Config.EVENT_PROBABILITIES.get(event_type, 0)
                if random.random() < prob:
                    self._trigger_event(event_type)
    
    def _trigger_event(self, event_type: EventType) -> None:
        """Trigger a specific event"""
        if event_type not in self.active_events:
            event_config = Config.EVENT_EFFECTS.get(event_type, {})
            duration = event_config.get('duration_days', 1)
            
            # Store event details
            self.active_events[event_type] = {
                'start_time': self.time_system.current_time,
                'duration': duration,
                'effects': event_config
            }
            
            # Apply immediate effects
            self._apply_event_effects(event_type, True)
            
            # Add notification
            self._add_event_notification(event_type)
            
            # Schedule event end
            self.time_system.schedule_event(
                self._end_event,
                timedelta(days=duration),
                {'event_type': event_type}
            )
    
    def _apply_event_effects(self, event_type: EventType, start: bool = True) -> None:
        """Apply or remove event effects"""
        if event_type in self.active_events:
            effects = self.active_events[event_type]['effects']
            multiplier = 1 if start else (1 / effects.get('revenue_multiplier', 1))
            
            # Apply economic effects
            self.economy.apply_multiplier(multiplier)
            
            # Apply visitor effects
            if 'visitor_multiplier' in effects:
                self._adjust_visitor_rate(effects['visitor_multiplier'] if start else 1)
            
            # Handle special effects
            if event_type == EventType.KAIJU_ATTACK and start:
                self._handle_kaiju_damage()
    
    def _handle_kaiju_damage(self) -> None:
        """Handle potential damage from kaiju attacks"""
        if random.random() < Config.EVENT_EFFECTS[EventType.KAIJU_ATTACK]['damage_chance']:
            # Select random floor for damage
            floor = random.randint(0, len(self.tower.floors) - 1)
            # Apply damage (implement damage system)
            self._damage_floor(floor)
            
    def _damage_floor(self, floor: int) -> None:
        """Apply damage to a specific floor"""
        # Implementation of damage system
        pass
        
    def update(self, dt: float) -> None:
        """Update game state"""
        if not self.paused:
            # Update time system
            self.time_system.update(dt)
            
            # Update economy
            self.economy.update(dt)
            
            # Check population milestones
            self._check_population_milestones()
            
            # Check star rating changes
            self._check_star_rating()
            
    def _check_population_milestones(self) -> None:
        """Check and handle population milestones"""
        if self.tower.current_map:
            self.tower.current_map.on_population_milestone(self.population)
            
    def _check_star_rating(self) -> None:
        """Check and handle star rating changes"""
        if self.tower.current_map:
            self.tower.current_map.on_star_rating_change(self.star_rating)
            
    def _add_event_notification(self, event_type: EventType) -> None:
        """Add a notification for an event with theme-specific styling"""
        theme_colors = {}
        if self.asset_manager.current_theme:
            theme_colors = {
                EventType.FESTIVAL: self.asset_manager.get_theme_color('accent'),
                EventType.KAIJU_ATTACK: self.asset_manager.get_theme_color('primary'),
                # Add more theme colors for other events
            }
        
        notification = {
            'type': 'event',
            'event_type': event_type,
            'message': self._get_event_message(event_type),
            'icon': self.asset_manager.get_icon_path(event_type.name.lower()),
            'time': self.time_system.current_time,
            'theme_color': theme_colors.get(event_type, (1, 1, 1, 1))
        }
        self.active_notifications.append(notification)
        
        # Play theme-specific sound if available
        sound_file = self.asset_manager.get_theme_sound(event_type.name.lower())
        if sound_file:
            # Play sound (implement sound system)
            pass
        
    def _get_event_message(self, event_type: EventType) -> str:
        """Get the message for an event notification"""
        messages = {
            EventType.FESTIVAL: "A festival has started! Expect increased visitors and revenue!",
            EventType.KAIJU_ATTACK: "Warning: Kaiju attack! Take precautionary measures!",
            EventType.EMERGENCY_DRILL: "Emergency drill in progress. Temporary decrease in visitors.",
            # Add more messages for other event types
        }
        return messages.get(event_type, "An event has occurred!")
        
    def _get_event_icon(self, event_type: EventType) -> str:
        """Get the icon path for an event type"""
        icons = {
            EventType.FESTIVAL: "assets/icons/festival.png",
            EventType.KAIJU_ATTACK: "assets/icons/kaiju.png",
            EventType.EMERGENCY_DRILL: "assets/icons/drill.png",
            # Add more icons for other event types
        }
        return icons.get(event_type, "assets/icons/default.png")
    
    def setup_graphics(self):
        """Set up the initial graphics for the game"""
        with self.canvas:
            # Background
            Color(0.9, 0.9, 0.9, 1)  # Light gray
            self.background = Rectangle(pos=self.pos, size=self.size)
            
            # Grid lines
            Color(0.8, 0.8, 0.8, 1)  # Darker gray for grid
            self.grid_lines = []
            self.draw_grid()
    
    def draw_grid(self):
        """Draw the grid lines"""
        # Clear existing grid lines
        for line in self.grid_lines:
            self.canvas.remove(line)
        self.grid_lines.clear()
        
        # Draw vertical lines
        for x in range(0, int(self.width), self.grid_size):
            with self.canvas:
                line = Line(points=[x, 0, x, self.height])
                self.grid_lines.append(line)
        
        # Draw horizontal lines
        for y in range(0, int(self.height), self.grid_size):
            with self.canvas:
                line = Line(points=[0, y, self.width, y])
                self.grid_lines.append(line)
    
    def update_graphics(self, *args):
        """Update graphics when widget size or position changes"""
        self.background.pos = self.pos
        self.background.size = self.size
        self.draw_grid()
        self.draw_tower()
    
    def draw_tower(self):
        """Draw the tower and all its businesses"""
        if hasattr(self, 'tower'):
            self.tower.draw()
    
    def update(self, dt):
        """Update game state"""
        if not self.paused:
            self.time_system.update(dt)
            
            # Process any new notifications
            self._process_notifications()
            
            # Get active events and apply their effects
            active_events = self.time_system.get_active_events()
            self._apply_event_effects(active_events)
            
            # Update game systems
            spawn_multiplier = self._calculate_spawn_multiplier(active_events)
            self.tower.update(dt, spawn_multiplier)
            self.economy.update(dt)
            
            # Update UI
            self.current_time = self.time_system.get_time_string()
    
    def _process_notifications(self):
        """Process and update notifications"""
        new_notifications = self.time_system.get_notifications(unread_only=True)
        for notification in new_notifications:
            self._add_notification(notification)
            self.time_system.mark_notification_read(notification)
        
        # Remove old notifications
        self.time_system.clear_old_notifications()
    
    def _add_notification(self, notification):
        """Add a new notification to the UI"""
        self.active_notifications.append({
            'message': notification.message,
            'priority': notification.priority.value,
            'time': notification.time,
            'type': notification.event_type,
            'data': notification.data
        })
        # Keep only last 5 notifications
        if len(self.active_notifications) > 5:
            self.active_notifications.pop(0)
    
    def _calculate_spawn_multiplier(self, active_events):
        """Calculate customer spawn rate multiplier based on active events"""
        multiplier = 1.0
        
        if active_events['rush_hour']:
            multiplier *= 2.0
        if not active_events['business_hours']:
            multiplier *= 0.2
        if active_events['sale']:
            multiplier *= 1.5
        if active_events['weather'] == 'rainy':
            multiplier *= 0.7
        if active_events['vip']:
            multiplier *= 1.2
            
        return multiplier
    
    def _apply_event_effects(self, active_events):
        """Apply effects from active events"""
        if active_events['power_outage']:
            self._apply_power_outage_effects()
        
        if active_events['sale']:
            self._apply_sale_effects(active_events['sale'])
        
        if active_events['vip']:
            self._check_vip_satisfaction(active_events['vip'])
    
    def _apply_power_outage_effects(self):
        """Apply effects of a power outage"""
        # Reduce income
        self.economy.add_modifier('power_outage', 0.5)  # 50% income
        # Reduce customer satisfaction
        self.tower.add_satisfaction_modifier('power_outage', -2)
    
    def _apply_sale_effects(self, sale_data):
        """Apply effects of an active sale"""
        discount = sale_data['discount']
        # Increase customer spawn rate
        self.tower.set_customer_multiplier(1.5)
        # Reduce prices
        self.economy.set_price_multiplier(1 - discount)
    
    def _check_vip_satisfaction(self, vip_data):
        """Check if VIP requirements are met"""
        vip_type = vip_data['type']
        config = vip_data['config']
        
        # Check if required businesses exist and meet rating
        requirements_met = True
        for req in config['requirements']:
            if not self.tower.has_business_type(req):
                requirements_met = False
                break
            if self.tower.get_business_rating(req) < config['min_rating']:
                requirements_met = False
                break
        
        if requirements_met:
            reward = self.config.EVENT_TYPES['vip_visit']['reward']
            reward *= config['reward_multiplier']
            self.money += reward
            self._add_notification({
                'message': f"VIP {vip_type.replace('_', ' ').title()} satisfied! Received ${reward:,}",
                'priority': 2,
                'time': self.time_system.current_time,
                'type': 'vip_satisfaction'
            })
    
    # Event handlers
    def _handle_vip_arrival(self, data):
        vip_type = data['vip_type'].replace('_', ' ').title()
        self.tower.add_satisfaction_modifier('vip_visit', 1)  # Temporary boost
    
    def _handle_vip_departure(self, data):
        self.tower.remove_satisfaction_modifier('vip_visit')
    
    def _handle_maintenance_start(self, data):
        self.money -= data.get('cost', 0)
        self.tower.add_satisfaction_modifier('maintenance', -1)
    
    def _handle_maintenance_end(self, data):
        self.tower.remove_satisfaction_modifier('maintenance')
        self.tower.repair_all_facilities()
    
    def _handle_sale_start(self, data):
        pass  # Handled in _apply_sale_effects
    
    def _handle_sale_end(self, data):
        self.tower.set_customer_multiplier(1.0)
        self.economy.set_price_multiplier(1.0)
    
    def _handle_power_outage(self, data):
        pass  # Handled in _apply_power_outage_effects
    
    def _handle_power_restore(self, data):
        self.economy.remove_modifier('power_outage')
        self.tower.remove_satisfaction_modifier('power_outage')
    
    def _handle_festival_start(self, data):
        pass  # Implement festival start effects
    
    def _handle_festival_end(self, data):
        pass  # Implement festival end effects
    
    def _handle_kaiju_attack(self, data):
        pass  # Implement kaiju attack effects
    
    def _handle_emergency_drill(self, data):
        pass  # Implement emergency drill effects
    
    def on_touch_down(self, touch):
        """Handle touch/click events"""
        if self.collide_point(*touch.pos):
            # Convert touch position to grid coordinates
            grid_x = int((touch.x - self.x) // self.grid_size)
            grid_y = int((touch.y - self.y) // self.grid_size)
            
            if self.selected_tool:
                self.try_place_building(grid_x, grid_y)
        return super(Game, self).on_touch_down(touch)
    
    def try_place_building(self, grid_x, grid_y):
        """Try to place a building at the given grid coordinates"""
        if self.tower.can_place_building((grid_x, grid_y), self.selected_tool):
            cost = self.tower.get_building_cost(self.selected_tool)
            if self.money >= cost:
                if self.tower.add_business((grid_x, grid_y), self.selected_tool):
                    self.money -= cost
    
    def toggle_pause(self):
        """Toggle the game pause state"""
        self.paused = not self.paused
        self.time_system.toggle_pause()
    
    def set_game_speed(self, speed: str):
        """Set the game speed"""
        self.time_system.set_speed(speed)
        
    def get_financial_report(self):
        """Get current financial status"""
        return {
            'money': self.money,
            'income': self.economy.get_current_income(),
            'expenses': self.economy.get_current_expenses()
        }
    
    def _hourly_update(self, data: Dict[str, Any]):
        """Handle hourly game updates"""
        if self.time_system.is_business_hours():
            # Update economy based on business hours
            self.economy.calculate_hourly_income(self.tower)
            
        # Update UI
        self.current_time = self.time_system.get_time_string()
    
    def add_business(self, business_type: BusinessType, floor: int) -> bool:
        """Add a new business to the tower"""
        business_costs = {
            BusinessType.RESTAURANT: 50000,
            BusinessType.HOTEL: 200000,
            BusinessType.OFFICE: 100000,
            BusinessType.RETAIL: 30000,
            BusinessType.GYM: 80000,
            BusinessType.CINEMA: 150000,
            BusinessType.ARCADE: 100000,
            BusinessType.SPA: 120000,
            BusinessType.CONFERENCE: 80000,
            BusinessType.OBSERVATION: 300000,
            BusinessType.BAR: 70000,
            BusinessType.PARKING: 150000
        }
        
        # Check if we can afford it
        cost = business_costs.get(business_type, 100000)
        if self.economy.balance < cost:
            return False
        
        # Try to add the business
        if self.tower.add_business(business_type, floor):
            self.economy.balance -= cost
            return True
        return False
    
    def remove_business(self, floor: int) -> bool:
        """Remove a business from the tower"""
        return self.tower.remove_business(floor)
    
    def get_game_state(self) -> Dict:
        """Get current game state"""
        return {
            'time': self.time_system.get_time_state(),
            'tower': self.tower.get_tower_stats(),
            'economy': {
                'balance': self.economy.balance,
                'daily_revenue': self.economy.calculate_daily_revenue(),
                'daily_expenses': self.economy.calculate_daily_expenses()
            },
            'paused': self.paused,
            'game_speed': self.game_speed
        }
    
    def toggle_pause(self):
        """Toggle game pause state"""
        self.paused = not self.paused
    
    def set_game_speed(self, speed: float):
        """Set game simulation speed"""
        if speed in [1.0, 2.0, 3.0]:
            self.game_speed = speed
