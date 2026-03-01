"""
Grid and Node classes for the Dynamic Pathfinding Agent.
"""

import random
from enum import Enum
from typing import List, Tuple, Set, Optional


class NodeType(Enum):
    """Types of nodes in the grid."""
    EMPTY = 0
    OBSTACLE = 1
    START = 2
    GOAL = 3


class Node:
    """Represents a single node in the grid."""
    
    def __init__(self, x: int, y: int, node_type: NodeType = NodeType.EMPTY):
        self.x = x
        self.y = y
        self.node_type = node_type
        self.g = float('inf')  # Cost from start
        self.h = 0.0  # Heuristic cost to goal
        self.f = float('inf')  # Total cost (g + h)
        self.parent: Optional['Node'] = None
        self.in_open = False
        self.in_closed = False
    
    def __lt__(self, other: 'Node') -> bool:
        """Comparison for priority queue."""
        return self.f < other.f
    
    def __eq__(self, other: object) -> bool:
        """Check equality based on coordinates."""
        if not isinstance(other, Node):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        """Hash based on coordinates."""
        return hash((self.x, self.y))
    
    def reset(self):
        """Reset search-related attributes."""
        self.g = float('inf')
        self.h = 0.0
        self.f = float('inf')
        self.parent = None
        self.in_open = False
        self.in_closed = False
    
    def __repr__(self) -> str:
        return f"Node({self.x}, {self.y}, {self.node_type.name})"


class Grid:
    """Represents the grid environment for pathfinding."""
    
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid: List[List[Node]] = []
        self.start_node: Optional[Node] = None
        self.goal_node: Optional[Node] = None
        
        # Initialize grid
        for y in range(rows):
            row = []
            for x in range(cols):
                row.append(Node(x, y))
            self.grid.append(row)
    
    def get_node(self, x: int, y: int) -> Optional[Node]:
        """Get a node by coordinates."""
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.grid[y][x]
        return None
    
    def set_start(self, x: int, y: int) -> bool:
        """Set the start node."""
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return False
        
        # Clear previous start
        if self.start_node:
            self.start_node.node_type = NodeType.EMPTY
        
        # Set new start
        self.start_node = self.grid[y][x]
        self.start_node.node_type = NodeType.START
        return True
    
    def set_goal(self, x: int, y: int) -> bool:
        """Set the goal node."""
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return False
        
        # Clear previous goal
        if self.goal_node:
            self.goal_node.node_type = NodeType.EMPTY
        
        # Set new goal
        self.goal_node = self.grid[y][x]
        self.goal_node.node_type = NodeType.GOAL
        return True
    
    def set_obstacle(self, x: int, y: int, is_obstacle: bool) -> bool:
        """Set or remove an obstacle at the given coordinates."""
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return False
        
        node = self.grid[y][x]
        
        # Don't place obstacles on start or goal
        if node.node_type in [NodeType.START, NodeType.GOAL]:
            return False
        
        if is_obstacle:
            node.node_type = NodeType.OBSTACLE
        else:
            node.node_type = NodeType.EMPTY
        
        return True
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a node is walkable (not an obstacle)."""
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return False
        
        node = self.grid[y][x]
        return node.node_type != NodeType.OBSTACLE
    
    def get_neighbors(self, x: int, y: int, diagonal: bool = False) -> List[Node]:
        """Get walkable neighbors of a node."""
        neighbors = []
        
        # 4-directional neighbors (up, down, left, right)
        directions = [
            (0, -1),  # up
            (0, 1),   # down
            (-1, 0),  # left
            (1, 0),   # right
        ]
        
        # Add diagonal neighbors
        if diagonal:
            directions.extend([
                (-1, -1),  # up-left
                (1, -1),   # up-right
                (-1, 1),   # down-left
                (1, 1),    # down-right
            ])
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                neighbors.append(self.get_node(nx, ny))
        
        return neighbors
    
    def generate_random_obstacles(self, obstacle_density: float = 0.3) -> None:
        """Generate random obstacles with given density (0.0 to 1.0)."""
        if not (0 <= obstacle_density <= 1):
            raise ValueError("Obstacle density must be between 0 and 1")
        
        for y in range(self.rows):
            for x in range(self.cols):
                node = self.grid[y][x]
                # Don't place obstacles on start or goal
                if node.node_type not in [NodeType.START, NodeType.GOAL]:
                    if random.random() < obstacle_density:
                        node.node_type = NodeType.OBSTACLE
    
    def reset_search_state(self) -> None:
        """Reset search-related attributes for all nodes."""
        for y in range(self.rows):
            for x in range(self.cols):
                self.grid[y][x].reset()
    
    def clear_obstacles(self) -> None:
        """Clear all obstacles from the grid."""
        for y in range(self.rows):
            for x in range(self.cols):
                node = self.grid[y][x]
                if node.node_type == NodeType.OBSTACLE:
                    node.node_type = NodeType.EMPTY
    
    def spawn_random_obstacle(self) -> Optional[Node]:
        """Spawn a single random obstacle. Returns the spawned node or None."""
        walkable_nodes = []
        for y in range(self.rows):
            for x in range(self.cols):
                node = self.grid[y][x]
                if node.node_type == NodeType.EMPTY:
                    walkable_nodes.append(node)
        
        if not walkable_nodes:
            return None
        
        node = random.choice(walkable_nodes)
        node.node_type = NodeType.OBSTACLE
        return node
    
    def is_path_blocked(self, path: List[Tuple[int, int]]) -> bool:
        """Check if any node in the path is an obstacle."""
        for x, y in path:
            if not self.is_walkable(x, y):
                return True
        return False
    
    def find_first_blocked_index(self, path: List[Tuple[int, int]]) -> int:
        """Find the first blocked node in the path. Returns -1 if none blocked."""
        for i, (x, y) in enumerate(path):
            if not self.is_walkable(x, y):
                return i
        return -1
    
    def display(self) -> str:
        """Return a string representation of the grid."""
        lines = []
        for y in range(self.rows):
            row = []
            for x in range(self.cols):
                node = self.grid[y][x]
                if node.node_type == NodeType.START:
                    row.append('S')
                elif node.node_type == NodeType.GOAL:
                    row.append('G')
                elif node.node_type == NodeType.OBSTACLE:
                    row.append('#')
                else:
                    row.append('.')
            lines.append(' '.join(row))
        return '\n'.join(lines)