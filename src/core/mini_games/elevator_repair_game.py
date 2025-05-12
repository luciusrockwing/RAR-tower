from typing import List, Dict, Tuple
from random import randint, shuffle
from kivy.graphics import Color, Rectangle, Line
from kivy.properties import ListProperty, NumericProperty, BooleanProperty, DictProperty
from core.mini_games import BaseMiniGame, MiniGameDifficulty
import math

class ElevatorRepairGame(BaseMiniGame):
    """A mini-game where the player must repair an elevator by solving circuit puzzles"""
    selected_wire = NumericProperty(-1)
    connections = DictProperty({})
    correct_connections = DictProperty({})
    nodes = ListProperty([])
    wires = ListProperty([])
    is_dragging = BooleanProperty(False)
    
    def __init__(self, difficulty: MiniGameDifficulty = MiniGameDifficulty.MEDIUM, **kwargs):
        super(ElevatorRepairGame, self).__init__(difficulty=difficulty, **kwargs)
        self.num_connections = self._get_num_connections()
        self.mistakes_allowed = self._get_mistakes_allowed()
        self.mistakes_made = 0
        self.completed_connections = set()
        
    def _setup_game(self) -> None:
        """Initialize the elevator repair game"""
        # Generate circuit nodes
        self.nodes = self._generate_nodes()
        
        # Generate correct connections
        self.correct_connections = self._generate_connections()
        
        # Clear current connections
        self.connections = {}
        
        # Set game duration
        self.time_remaining = {
            'EASY': 180,
            'MEDIUM': 120,
            'HARD': 90
        }.get(self.difficulty, 120)
        
    def _get_num_connections(self) -> int:
        """Get number of connections needed"""
        return {
            'EASY': 4,
            'MEDIUM': 6,
            'HARD': 8
        }.get(self.difficulty, 6)
        
    def _get_mistakes_allowed(self) -> int:
        """Get number of wrong connections allowed"""
        return {
            'EASY': 3,
            'MEDIUM': 2,
            'HARD': 1
        }.get(self.difficulty, 2)
        
    def _generate_nodes(self) -> List[Dict]:
        """Generate circuit nodes positions"""
        nodes = []
        margin = 80
        node_pairs = self.num_connections
        
        # Left side nodes (inputs)
        for i in range(node_pairs):
            y = margin + (self.height - 2 * margin) * (i / (node_pairs - 1))
            nodes.append({
                'id': f'input_{i}',
                'pos': [margin, y],
                'type': 'input'
            })
            
        # Right side nodes (outputs)
        output_ids = list(range(node_pairs))
        shuffle(output_ids)  # Randomize connections
        
        for i in range(node_pairs):
            y = margin + (self.height - 2 * margin) * (i / (node_pairs - 1))
            nodes.append({
                'id': f'output_{output_ids[i]}',
                'pos': [self.width - margin, y],
                'type': 'output'
            })
            
        return nodes
        
    def _generate_connections(self) -> Dict:
        """Generate correct connections between nodes"""
        connections = {}
        for i in range(self.num_connections):
            input_node = f'input_{i}'
            output_node = f'output_{i}'
            connections[input_node] = output_node
        return connections
        
    def _update(self, dt: float) -> None:
        """Update game state"""
        super()._update(dt)
        if not self.is_active:
            return
            
        # Check win condition
        if self._check_all_connections():
            self.score += int(self.time_remaining * 100)
            self.end(True)
            
        # Check lose condition
        if self.mistakes_made >= self.mistakes_allowed:
            self.end(False)
            
    def _check_all_connections(self) -> bool:
        """Check if all connections are correct"""
        if len(self.connections) != len(self.correct_connections):
            return False
            
        for input_node, output_node in self.connections.items():
            if self.correct_connections.get(input_node) != output_node:
                return False
                
        return True
        
    def _get_node_at_pos(self, pos: Tuple[float, float]) -> str:
        """Get node ID at position"""
        for node in self.nodes:
            node_pos = node['pos']
            if math.dist(pos, node_pos) < 20:  # Node radius
                return node['id']
        return None
        
    def on_touch_down(self, touch):
        """Handle touch down event"""
        if not self.is_active or not self.collide_point(*touch.pos):
            return
            
        # Check if touching a node
        node_id = self._get_node_at_pos(touch.pos)
        if node_id and node_id.startswith('input_'):
            self.selected_wire = int(node_id.split('_')[1])
            self.is_dragging = True
            
    def on_touch_move(self, touch):
        """Handle touch move event"""
        if not self.is_active or not self.is_dragging:
            return
            
        # Update wire position for visual feedback
        if self.selected_wire >= 0:
            self.wires = [(
                self.nodes[self.selected_wire]['pos'],
                touch.pos
            )]
            
    def on_touch_up(self, touch):
        """Handle touch up event"""
        if not self.is_active or not self.is_dragging:
            return
            
        if self.selected_wire >= 0:
            end_node = self._get_node_at_pos(touch.pos)
            if end_node and end_node.startswith('output_'):
                # Make connection
                input_node = f'input_{self.selected_wire}'
                
                # Check if connection is correct
                if self.correct_connections[input_node] == end_node:
                    self.connections[input_node] = end_node
                    self.completed_connections.add(input_node)
                    self.score += 500
                else:
                    self.mistakes_made += 1
                    
            self.selected_wire = -1
            self.is_dragging = False
            self.wires = []
