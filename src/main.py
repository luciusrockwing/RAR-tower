#!/usr/bin/env python3
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty

from core.game import Game
from core.config import Config
from ui.game_ui import MenuScreen, GameScreen, NotificationItem

# Set window size for desktop development
Window.size = (1280, 720)

class RARTowerApp(MDApp):
    game = ObjectProperty(None)
    config = ObjectProperty(None)
    
    def build(self):
        # Initialize config
        self.config = Config()
        
        # Initialize game
        self.game = Game()
        
        # Load the KV file
        Builder.load_file('src/ui/rartower.kv')
        
        # Create screen manager with fade transitions
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        
        return sm
    
    def on_start(self):
        """Initialize game resources when app starts"""
        # Start game loop
        Clock.schedule_interval(self._update, 1.0/60.0)
    
    def _update(self, dt):
        """Main game loop update"""
        if self.game and not self.game.paused:
            self.game.update(dt)
    
    def on_stop(self):
        """Clean up resources when app stops"""
        # Stop game loop
        Clock.unschedule(self._update)

if __name__ == '__main__':
    RARTowerApp().run()
