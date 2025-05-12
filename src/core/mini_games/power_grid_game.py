from typing import List, Dict, Tuple, Set
from random import randint, choice, random
from kivy.graphics import Color, Rectangle, Line
from kivy.properties import ListProperty, NumericProperty, DictProperty
from kivy.vector import Vector
from kivy.clock import Clock
from core.mini_games import BaseMiniGame, MiniGameDifficulty
import math

class PowerNode:
    """Represents a node in the power grid"""
    def __init__(self, x: float, y: float, node_type: str):
        self.pos = (x, y)
        self.type = node_type  # 'generator', 'consumer', 'junction'
        self.connected_to = set()
        self.power_level = 0.0
        self.demand = 0.0 if node_type != 'consumer' else random() * 50 + 50
        self.supply = 100.0 if node_type == 'generator' else 0.0
        self.overloaded = False
        self.active = True

class PowerGridGame(BaseMiniGame):
    """A mini-game where player must manage power distribution in the tower"""
    nodes = ListProperty([])
    connections = ListProperty([])
    selected_node = NumericProperty(-1)
    power_stats = DictProperty({
        'total_supply': 0,
        'total_demand': 0,
        'efficiency': 100
    })
    
    def __init__(self, difficulty: MiniGameDifficulty = MiniGameDifficulty.MEDIUM, **kwargs):
        super(PowerGridGame, self).__init__(difficulty=difficulty, **kwargs)
        self.simulation_timer = None
        self.max_connections = self._get_max_connections()
        self.power_loss_rate = self._get_power_loss_rate()
        self.grid_nodes: List[PowerNode] = []
        
    def _setup_game(self) -> None:
        """Initialize the power grid game"""
        # Generate grid layout
        self.grid_nodes = self._generate_grid()
        self.selected_node = -1
        
        # Set game duration
        self.time_remaining = {
            'EASY': 180,
            'MEDIUM': 150,
            'HARD': 120
        }.get(self.difficulty, 150)
        
        # Start simulation
        self.simulation_timer = Clock.schedule_interval(self._update_simulation, 1/30)
        
    def _generate_grid(self) -> List[PowerNode]:
        """Generate power grid layout"""
        nodes = []
        
        # Configure grid parameters based on difficulty
        num_generators = {
            'EASY': 2,
            'MEDIUM': 3,
            'HARD': 4
        }.get(self.difficulty, 3)
        
        num_consumers = {
            'EASY': 4,
            'MEDIUM': 6,
            'HARD': 8
        }.get(self.difficulty, 6)
        
        num_junctions = {
            'EASY': 3,
            'MEDIUM': 5,
            'HARD': 7
        }.get(self.difficulty, 5)
        
        # Place generators at the edges
        margin = 80
        for i in range(num_generators):
            x = margin
            y = margin + (self.height - 2 * margin) * (i / (num_generators - 1))
            nodes.append(PowerNode(x, y, 'generator'))
            
        # Place consumers on the right side
        for i in range(num_consumers):
            x = self.width - margin
            y = margin + (self.height - 2 * margin) * (i / (num_consumers - 1))
            nodes.append(PowerNode(x, y, 'consumer'))
            
        # Place junction nodes in the middle
        for _ in range(num_junctions):
            x = randint(int(self.width * 0.3), int(self.width * 0.7))
            y = randint(margin, int(self.height - margin))
            nodes.append(PowerNode(x, y, 'junction'))
            
        return nodes
        
    def _get_max_connections(self) -> int:
        """Get maximum allowed connections per node"""
        return {
            'EASY': 4,
            'MEDIUM': 3,
            'HARD': 2
        }.get(self.difficulty, 3)
        
    def _get_power_loss_rate(self) -> float:
        """Get power loss rate per unit distance"""
        return {
            'EASY': 0.001,
            'MEDIUM': 0.002,
            'HARD': 0.003
        }.get(self.difficulty, 0.002)
        
    def _update_simulation(self, dt: float) -> None:
        """Update power grid simulation"""
        if not self.is_active:
            return
            
        # Reset power levels
        for node in self.grid_nodes:
            node.power_level = node.supply
            node.overloaded = False
            
        # Distribute power through the network
        self._distribute_power()
        
        # Calculate statistics
        total_supply = sum(n.supply for n in self.grid_nodes if n.type == 'generator')
        total_demand = sum(n.demand for n in self.grid_nodes if n.type == 'consumer')
        supplied_demand = sum(min(n.power_level, n.demand) 
                            for n in self.grid_nodes if n.type == 'consumer')
        
        self.power_stats.update({
            'total_supply': total_supply,
            'total_demand': total_demand,
            'efficiency': (supplied_demand / total_demand * 100) if total_demand > 0 else 100
        })
        
        # Check win/lose conditions
        self._check_game_state()
        
    def _distribute_power(self) -> None:
        """Distribute power through the connected nodes"""
        # Implement breadth-first distribution from generators
        for node in self.grid_nodes:
            if node.type == 'generator':
                self._distribute_from_node(node)
                
    def _distribute_from_node(self, node: PowerNode) -> None:
        """Distribute power from a specific node to its connections"""
        visited = set()
        queue = [(node, 0)]  # (node, distance from source)
        
        while queue:
            current, distance = queue.pop(0)
            if current in visited:
                continue
                
            visited.add(current)
            
            # Calculate power loss based on distance
            power_loss = distance * self.power_loss_rate
            available_power = current.power_level * (1 - power_loss)
            
            # Distribute power to connected nodes
            connected_consumers = [n for n in current.connected_to if n.type == 'consumer']
            if connected_consumers:
                power_per_consumer = available_power / len(connected_consumers)
                for consumer in connected_consumers:
                    consumer.power_level += power_per_consumer
                    
            # Add connected junctions to queue
            for connected in current.connected_to:
                if connected.type == 'junction' and connected not in visited:
                    queue.append((connected, distance + 1))
                    
    def _check_game_state(self) -> None:
        """Check win/lose conditions"""
        if not self.is_active:
            return
            
        # Check for overloaded nodes
        overloaded = any(node.overloaded for node in self.grid_nodes)
        if overloaded:
            self.end(False)
            return
            
        # Check if all consumers are receiving sufficient power
        all_powered = all(
            node.power_level >= node.demand * 0.9  # 90% of demand is acceptable
            for node in self.grid_nodes
            if node.type == 'consumer'
        )
        
        # Win if maintained for 10 seconds
        if all_powered:
            self.score += int(self.power_stats['efficiency'] * 100)
            if self.time_remaining > 0:
                self.score += int(self.time_remaining * 50)
            self.end(True)
            
    def can_connect(self, node1: PowerNode, node2: PowerNode) -> bool:
        """Check if two nodes can be connected"""
        # Check maximum connections
        if (len(node1.connected_to) >= self.max_connections or 
            len(node2.connected_to) >= self.max_connections):
            return False
            
        # Prevent direct generator-generator connections
        if node1.type == 'generator' and node2.type == 'generator':
            return False
            
        # Check distance (prevent too long connections)
        max_distance = self.width * 0.4
        distance = math.dist(node1.pos, node2.pos)
        return distance <= max_distance
        
    def connect_nodes(self, node1: PowerNode, node2: PowerNode) -> bool:
        """Connect two nodes"""
        if self.can_connect(node1, node2):
            node1.connected_to.add(node2)
            node2.connected_to.add(node1)
            return True
        return False
        
    def disconnect_nodes(self, node1: PowerNode, node2: PowerNode) -> None:
        """Disconnect two nodes"""
        node1.connected_to.discard(node2)
        node2.connected_to.discard(node1)
        
    def on_touch_down(self, touch):
        """Handle touch down event"""
        if not self.is_active or not self.collide_point(*touch.pos):
            return
            
        # Find clicked node
        for i, node in enumerate(self.grid_nodes):
            if math.dist(touch.pos, node.pos) < 20:
                if self.selected_node == -1:
                    self.selected_node = i
                else:
                    # Try to connect nodes
                    node1 = self.grid_nodes[self.selected_node]
                    node2 = node
                    if node1 != node2:
                        if node2 in node1.connected_to:
                            self.disconnect_nodes(node1, node2)
                        else:
                            self.connect_nodes(node1, node2)
                    self.selected_node = -1
                break
                
    def end(self, success: bool = False) -> None:
        """Clean up when game ends"""
        if self.simulation_timer:
            self.simulation_timer.cancel()
        super().end(success)
