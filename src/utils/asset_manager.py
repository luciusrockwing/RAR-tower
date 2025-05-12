from typing import Dict, Any, Optional
import os
import json
from pathlib import Path

class AssetManager:
    """Manage game assets and themes"""
    
    def __init__(self, base_path: str = "src/assets"):
        self.base_path = Path(base_path)
        self.icons_path = self.base_path / "icons"
        self.themes_path = self.base_path / "themes"
        self.current_theme = None
        self.theme_data = {}
        
    def load_theme(self, theme_name: str) -> bool:
        """Load a theme by name"""
        theme_file = self.themes_path / f"{theme_name}.json"
        if theme_file.exists():
            with open(theme_file, 'r') as f:
                self.theme_data = json.load(f)
                self.current_theme = theme_name
                return True
        return False
    
    def get_icon_path(self, icon_name: str) -> str:
        """Get the full path to an icon"""
        icon_file = self.icons_path / f"{icon_name}.png"
        return str(icon_file) if icon_file.exists() else str(self.icons_path / "default.png")
    
    def get_theme_color(self, color_name: str) -> tuple:
        """Get a color from the current theme"""
        if self.current_theme and color_name in self.theme_data.get('colors', {}):
            return tuple(self.theme_data['colors'][color_name])
        return (1, 1, 1, 1)  # Default white
        
    def get_theme_sound(self, sound_name: str) -> Optional[str]:
        """Get a sound file path from the current theme"""
        if self.current_theme and sound_name in self.theme_data.get('sounds', {}):
            sound_file = self.base_path / "sounds" / self.theme_data['sounds'][sound_name]
            return str(sound_file) if sound_file.exists() else None
        return None
        
    def create_theme(self, theme_name: str, theme_data: Dict[str, Any]) -> bool:
        """Create a new theme"""
        theme_file = self.themes_path / f"{theme_name}.json"
        try:
            with open(theme_file, 'w') as f:
                json.dump(theme_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error creating theme {theme_name}: {e}")
            return False
