from typing import List, Dict, Tuple
from random import randint, choice, random
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.properties import ListProperty, NumericProperty, BooleanProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from core.mini_games import BaseMiniGame, MiniGameDifficulty
import math

class VIPEscortGame(BaseMiniGame):
    """A mini-game where player must safely escort VIPs through the tower"""
    vip_pos = ListProperty([0, 0])
    guard_pos = ListProperty([0, 0])
    crowd_npcs = ListProperty([])
    paparazzi = ListProperty([])
    vip_status = StringProperty('normal')  # 'normal', 'harassed', 'protected'
    stress_level = NumericProperty(0)
    power_ups = ListProperty([])
    active_power_up = StringProperty('')  # 'speed_boost', 'shield', 'crowd_control'
    power_up_duration = NumericProperty(0)
    
    def __init__(self, difficulty: MiniGameDifficulty = MiniGameDifficulty.MEDIUM, **kwargs):
        super(VIPEscortGame, self).__init__(difficulty=difficulty, **kwargs)
        self.movement_timer = None
        self.path_points = []
        self.current_point = 0
        self.vip_speed = self._get_vip_speed()
        self.guard_radius = self._get_guard_radius()
        self.power_up_timer = None
        
    def _setup_game(self) -> None:
        """Initialize the VIP escort game"""
        # Generate path from entrance to destination
        self.path_points = self._generate_path()
        self.vip_pos = list(self.path_points[0])
        self.guard_pos = [self.vip_pos[0], self.vip_pos[1]]
        
        # Generate NPCs and paparazzi
        self.crowd_npcs = self._generate_npcs()
        self.paparazzi = self._generate_paparazzi()
        
        self.stress_level = 0
        self.vip_status = 'normal'
        
        # Generate power-ups
        self.power_ups = self._generate_power_ups()
        self.active_power_up = ''
        self.power_up_duration = 0
        
        # Set game duration
        self.time_remaining = {
            'EASY': 180,
            'MEDIUM': 120,
            'HARD': 90
        }.get(self.difficulty, 120)
        
        # Start movement timer
        self.movement_timer = Clock.schedule_interval(self._update_movement, 1/60)
        
    def _generate_path(self) -> List[Tuple[float, float]]:
        """Generate a path through the tower"""
        points = []
        start_x = 50
        end_x = self.width - 50
        
        # Create waypoints
        num_points = {
            'EASY': 4,
            'MEDIUM': 6,
            'HARD': 8
        }.get(self.difficulty, 6)
        
        points.append((start_x, self.height/2))
        
        for i in range(num_points - 2):
            x = start_x + (end_x - start_x) * ((i + 1) / (num_points - 1))
            y = randint(100, int(self.height - 100))
            points.append((x, y))
            
        points.append((end_x, self.height/2))
        return points
        
    def _generate_npcs(self) -> List[Dict]:
        """Generate crowd NPCs"""
        npcs = []
        num_npcs = {
            'EASY': 10,
            'MEDIUM': 15,
            'HARD': 20
        }.get(self.difficulty, 15)
        
        for _ in range(num_npcs):
            npc = {
                'pos': [randint(50, int(self.width - 50)),
                       randint(50, int(self.height - 50))],
                'velocity': [random() * 2 - 1, random() * 2 - 1],
                'state': 'walking'  # 'walking' or 'excited'
            }
            npcs.append(npc)
            
        return npcs
        
    def _generate_paparazzi(self) -> List[Dict]:
        """Generate paparazzi NPCs"""
        paparazzi = []
        num_paparazzi = {
            'EASY': 2,
            'MEDIUM': 4,
            'HARD': 6
        }.get(self.difficulty, 4)
        
        for _ in range(num_paparazzi):
            pap = {
                'pos': [randint(50, int(self.width - 50)),
                       randint(50, int(self.height - 50))],
                'velocity': [0, 0],
                'state': 'searching'  # 'searching' or 'pursuing'
            }
            paparazzi.append(pap)
            
        return paparazzi
        
    def _generate_power_ups(self) -> List[Dict]:
        """Generate power-up items"""
        power_ups = []
        num_power_ups = {
            'EASY': 4,
            'MEDIUM': 3,
            'HARD': 2
        }.get(self.difficulty, 3)
        
        power_up_types = ['speed_boost', 'shield', 'crowd_control']
        start_x = 100
        end_x = self.width - 100
        
        for _ in range(num_power_ups):
            power_up = {
                'type': choice(power_up_types),
                'pos': [randint(start_x, end_x),
                       randint(100, int(self.height - 100))],
                'active': True
            }
            power_ups.append(power_up)
        
        return power_ups
        
    def _get_vip_speed(self) -> float:
        """Get VIP movement speed"""
        return {
            'EASY': 100,
            'MEDIUM': 120,
            'HARD': 150
        }.get(self.difficulty, 120)
        
    def _get_guard_radius(self) -> float:
        """Get guard protection radius"""
        return {
            'EASY': 100,
            'MEDIUM': 80,
            'HARD': 60
        }.get(self.difficulty, 80)
        
    def _update_movement(self, dt: float) -> None:
        """Update positions of all entities"""
        if not self.is_active:
            return
            
        # Update power-ups
        self._update_power_ups(dt)
            
        # Update VIP movement
        if self.current_point < len(self.path_points):
            target = self.path_points[self.current_point]
            current_pos = Vector(self.vip_pos)
            target_vec = Vector(target)
            direction = target_vec - current_pos
            distance = direction.length()
            
            # Check if we should move to next waypoint
            if distance < self.vip_speed * dt:
                # Smoothly arrive at current waypoint
                self.vip_pos = [target[0], target[1]]
                self.current_point += 1
                
                # Start moving towards next waypoint immediately if available
                if self.current_point < len(self.path_points):
                    next_target = self.path_points[self.current_point]
                    new_direction = Vector(next_target) - Vector(target)
                    if new_direction.length() > 0:
                        new_direction = new_direction.normalize()
                        remaining_move = self.vip_speed * dt - distance
                        new_pos = Vector(target) + new_direction * remaining_move
                        self.vip_pos = [new_pos.x, new_pos.y]
            else:
                # Normal movement towards target
                direction = direction.normalize()
                new_pos = current_pos + direction * self.vip_speed * dt
                self.vip_pos = [new_pos.x, new_pos.y]
                
        # Update NPCs
        for npc in self.crowd_npcs:
            # Update position
            pos = Vector(npc['pos'])
            vel = Vector(npc['velocity'])
            new_pos = pos + vel * 50 * dt
            
            # Bounce off walls
            if not (0 < new_pos.x < self.width):
                vel.x *= -1
            if not (0 < new_pos.y < self.height):
                vel.y *= -1
                
            new_pos.x = max(0, min(new_pos.x, self.width))
            new_pos.y = max(0, min(new_pos.y, self.height))
            
            npc['pos'] = [new_pos.x, new_pos.y]
            npc['velocity'] = [vel.x, vel.y]
            
            # Random direction changes
            if random() < 0.02:
                npc['velocity'] = [random() * 2 - 1, random() * 2 - 1]
                
        # Update paparazzi
        vip_vec = Vector(self.vip_pos)
        for pap in self.paparazzi:
            pap_vec = Vector(pap['pos'])
            to_vip = vip_vec - pap_vec
            
            # Check if VIP is visible
            if to_vip.length() < 200:
                pap['state'] = 'pursuing'
                direction = to_vip.normalize()
                speed = 180 if pap['state'] == 'pursuing' else 80
                new_pos = pap_vec + direction * speed * dt
                
                # Avoid getting too close if guard is nearby
                if Vector(self.guard_pos).distance(new_pos) > self.guard_radius:
                    pap['pos'] = [new_pos.x, new_pos.y]
            else:
                pap['state'] = 'searching'
                # Random movement when searching
                if random() < 0.05:
                    pap['velocity'] = [random() * 2 - 1, random() * 2 - 1]
                    
                vel = Vector(pap['velocity'])
                new_pos = pap_vec + vel * 80 * dt
                new_pos.x = max(0, min(new_pos.x, self.width))
                new_pos.y = max(0, min(new_pos.y, self.height))
                pap['pos'] = [new_pos.x, new_pos.y]
                
        # Update VIP status and stress
        self._update_vip_status()
        
        # Update power-ups
        self._update_power_ups(dt)
        
    def _update_power_ups(self, dt: float) -> None:
        """Update power-up effects"""
        # Check for power-up collection
        guard_vec = Vector(self.guard_pos)
        for power_up in self.power_ups:
            if not power_up['active']:
                continue
                
            if guard_vec.distance(Vector(power_up['pos'])) < 30:
                self._activate_power_up(power_up['type'])
                power_up['active'] = False
                
        # Update active power-up duration
        if self.active_power_up:
            self.power_up_duration = max(0, self.power_up_duration - dt)
            if self.power_up_duration <= 0:
                self._deactivate_power_up()
                
    def _activate_power_up(self, power_up_type: str) -> None:
        """Activate a power-up effect"""
        self.active_power_up = power_up_type
        self.power_up_duration = 10.0  # 10 seconds duration
        
        if power_up_type == 'speed_boost':
            self.guard_radius *= 1.5  # Increase protection radius
        elif power_up_type == 'shield':
            # Shield effect handled in _update_vip_status
            pass
        elif power_up_type == 'crowd_control':
            # Temporarily stun all paparazzi
            for pap in self.paparazzi:
                pap['state'] = 'stunned'
                pap['stun_duration'] = 5.0
                
    def _deactivate_power_up(self) -> None:
        """Deactivate current power-up effect"""
        if self.active_power_up == 'speed_boost':
            self.guard_radius = self._get_guard_radius()  # Reset to normal
            
        self.active_power_up = ''
        self.power_up_duration = 0
        
    def _update_vip_status(self) -> None:
        """Update VIP status based on nearby entities"""
        vip_vec = Vector(self.vip_pos)
        guard_vec = Vector(self.guard_pos)
        
        # Check if guard is protecting
        is_protected = guard_vec.distance(vip_vec) < self.guard_radius
        
        # Count nearby paparazzi (shield power-up blocks all paparazzi)
        if self.active_power_up == 'shield':
            nearby_paparazzi = 0
        else:
            nearby_paparazzi = sum(1 for p in self.paparazzi 
                                  if Vector(p['pos']).distance(vip_vec) < 100 
                                  and p.get('state') != 'stunned')
        
        # Update status
        if is_protected:
            self.vip_status = 'protected'
            self.stress_level = max(0, self.stress_level - 1)
        elif nearby_paparazzi > 0:
            self.vip_status = 'harassed'
            self.stress_level = min(100, self.stress_level + nearby_paparazzi * 2)
        else:
            self.vip_status = 'normal'
            self.stress_level = max(0, self.stress_level - 0.5)
            
        # Check lose condition
        if self.stress_level >= 100:
            self.end(False)
            
        # Check win condition
        if self.current_point >= len(self.path_points):
            self.score += int((100 - self.stress_level) * 100)
            self.end(True)
            
    def on_touch_down(self, touch):
        """Handle touch down event"""
        if self.is_active and self.collide_point(*touch.pos):
            self.guard_pos = list(touch.pos)
            
    def on_touch_move(self, touch):
        """Handle touch move event"""
        if self.is_active and self.collide_point(*touch.pos):
            self.guard_pos = list(touch.pos)
            
    def end(self, success: bool = False) -> None:
        """Clean up when game ends"""
        if self.movement_timer:
            self.movement_timer.cancel()
        super().end(success)
