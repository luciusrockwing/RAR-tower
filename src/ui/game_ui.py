from kivy.uix.screenmanager import Screen
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, DictProperty, ListProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.app import App
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList
from datetime import datetime
from core.config import EventType, Config

class NotificationItem(ButtonBehavior, MDCard):
    title = StringProperty("")
    message = StringProperty("")
    time_str = StringProperty("")
    notification_data = DictProperty({})
    icon = StringProperty("information")
    icon_color = ListProperty([1, 1, 1, 1])
    
    def __init__(self, **kwargs):
        super(NotificationItem, self).__init__(**kwargs)
        self.notification_data = kwargs.get('data', {})
        self.message = kwargs.get('message', "")
        self.title = kwargs.get('title', "")
        notification_time = kwargs.get('time', datetime.now())
        self.time_str = notification_time.strftime("%H:%M")
        
        # Set colors based on event type and priority
        event_type = kwargs.get('event_type', None)
        priority = kwargs.get('priority', 1)
        self._set_appearance(event_type, priority)
        
    def _set_appearance(self, event_type: EventType, priority: int) -> None:
        """Set the notification's visual appearance based on event type and priority"""
        # Set background color based on priority
        if priority == 3:  # CRITICAL
            self.md_bg_color = (0.8, 0.2, 0.2, 1)  # Red
            self.icon_color = [1, 0.8, 0.8, 1]
        elif priority == 2:  # HIGH
            self.md_bg_color = (0.8, 0.6, 0.2, 1)  # Orange
            self.icon_color = [1, 0.9, 0.8, 1]
        elif priority == 1:  # MEDIUM
            self.md_bg_color = (0.2, 0.6, 0.8, 1)  # Blue
            self.icon_color = [0.8, 0.9, 1, 1]
        else:  # LOW
            self.md_bg_color = (0.3, 0.3, 0.3, 1)  # Gray
            self.icon_color = [0.9, 0.9, 0.9, 1]
            
        # Set icon based on event type
        if event_type:
            self.icon = self._get_event_icon(event_type)
            
    def _get_event_icon(self, event_type: EventType) -> str:
        """Get the appropriate icon for the event type"""
        icons = {
            EventType.FESTIVAL: "party-popper",
            EventType.KAIJU_ATTACK: "skull-crossbones-outline",
            EventType.EMERGENCY_DRILL: "alarm-light-outline",
            EventType.INSPECTION: "clipboard-check-outline",
            EventType.VIP_VISIT: "account-star",
            EventType.RENOVATION: "hammer-wrench",
            EventType.WEATHER_EVENT: "weather-lightning-rainy",
            EventType.CELEBRITY_VISIT: "star-face"
        }
        return icons.get(event_type, "information")

class GameScreen(Screen):
    # Properties
    money = NumericProperty(1000000)
    population = NumericProperty(0)
    star_rating = NumericProperty(1)
    current_time = StringProperty("")
    current_speed = StringProperty("normal")
    active_notifications = ListProperty([])
    
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self._notification_update_scheduled = False
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        
    def update(self, dt: float) -> None:
        """Update the game screen"""
        # Update notification list if needed
        if self.active_notifications and not self._notification_update_scheduled:
            self._notification_update_scheduled = True
            Clock.schedule_once(self._update_notifications)
            
    def _update_notifications(self, dt: float) -> None:
        """Update the notifications list"""
        notifications_list = self.ids.notifications_list
        notifications_list.clear_widgets()
        
        # Add notifications, most recent first
        for notification in reversed(self.active_notifications[-10:]):  # Show last 10
            item = NotificationItem(
                title=self._get_notification_title(notification),
                message=notification.get('message', ''),
                time=notification.get('time', datetime.now()),
                event_type=notification.get('event_type'),
                priority=notification.get('priority', 1),
                data=notification
            )
            notifications_list.add_widget(item)
            
        self._notification_update_scheduled = False
        
    def _get_notification_title(self, notification: dict) -> str:
        """Get a title for the notification based on its type"""
        event_type = notification.get('event_type')
        if event_type:
            titles = {
                EventType.FESTIVAL: "Festival Event!",
                EventType.KAIJU_ATTACK: "KAIJU ATTACK!",
                EventType.EMERGENCY_DRILL: "Emergency Drill",
                EventType.INSPECTION: "Building Inspection",
                EventType.VIP_VISIT: "VIP Visitor Arriving",
                EventType.RENOVATION: "Renovation Notice",
                EventType.WEATHER_EVENT: "Weather Alert",
                EventType.CELEBRITY_VISIT: "Celebrity Sighting!"
            }
            return titles.get(event_type, "Event Notification")
        return "Notification"
        
    def set_speed(self, speed: str) -> None:
        """Set the game speed"""
        self.current_speed = speed
        if hasattr(self, 'game'):
            self.game.time_system.set_speed(speed)

class MenuScreen(Screen):
    """Menu screen implementation"""
    pass  # All functionality is handled in KV file
