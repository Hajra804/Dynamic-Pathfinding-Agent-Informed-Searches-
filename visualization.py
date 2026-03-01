"""
Visualization utilities for enhanced GUI features.
"""

import time
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PathAnimation:
    """Handles path animation and visualization."""
    path: List[Tuple[int, int]]
    current_step: int = 0
    total_steps: int = 0
    speed: float = 1.0  # Steps per second
    started: bool = False
    finished: bool = False
    paused: bool = False
    
    def __post_init__(self):
        self.total_steps = len(self.path)
        self.start_time = time.time()
    
    def update(self) -> Optional[Tuple[int, int]]:
        """Update animation and return current position."""
        if self.finished or self.paused:
            return self.path[self.current_step] if self.current_step < len(self.path) else None
        
        elapsed = time.time() - self.start_time
        target_step = min(int(elapsed * self.speed), self.total_steps - 1)
        
        if target_step >= self.total_steps - 1:
            self.finished = True
            self.current_step = self.total_steps - 1
        else:
            self.current_step = target_step
        
        return self.path[self.current_step] if self.current_step < len(self.path) else None
    
    def reset(self):
        """Reset animation."""
        self.current_step = 0
        self.finished = False
        self.paused = False
        self.start_time = time.time()
    
    def pause(self):
        """Pause animation."""
        self.paused = True
    
    def resume(self):
        """Resume animation."""
        self.paused = False
        self.start_time = time.time() - (self.current_step / self.speed)
    
    def get_progress(self) -> float:
        """Get animation progress as percentage (0.0 to 1.0)."""
        if self.total_steps == 0:
            return 1.0
        return min(self.current_step / (self.total_steps - 1), 1.0)


class StatisticsTracker:
    """Track algorithm statistics for comparison."""
    
    def __init__(self):
        self.last_execution = {
            'algorithm': None,
            'heuristic': None,
            'nodes_visited': 0,
            'path_cost': 0,
            'execution_time': 0.0,
        }
        self.history: List[dict] = []
        self.max_history = 50
    
    def record_execution(self, algorithm: str, heuristic: str, nodes_visited: int,
                        path_cost: float, execution_time: float):
        """Record an algorithm execution."""
        execution = {
            'algorithm': algorithm,
            'heuristic': heuristic,
            'nodes_visited': nodes_visited,
            'path_cost': path_cost,
            'execution_time': execution_time,
            'timestamp': time.time(),
        }
        
        self.last_execution = execution
        self.history.append(execution)
        
        # Keep history bounded
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_average_time(self, algorithm: Optional[str] = None) -> float:
        """Get average execution time for an algorithm."""
        if not self.history:
            return 0.0
        
        filtered = self.history
        if algorithm:
            filtered = [e for e in filtered if e['algorithm'] == algorithm]
        
        if not filtered:
            return 0.0
        
        return sum(e['execution_time'] for e in filtered) / len(filtered)
    
    def get_average_nodes_visited(self, algorithm: Optional[str] = None) -> float:
        """Get average nodes visited for an algorithm."""
        if not self.history:
            return 0.0
        
        filtered = self.history
        if algorithm:
            filtered = [e for e in filtered if e['algorithm'] == algorithm]
        
        if not filtered:
            return 0.0
        
        return sum(e['nodes_visited'] for e in filtered) / len(filtered)
    
    def clear(self):
        """Clear all statistics."""
        self.last_execution = {
            'algorithm': None,
            'heuristic': None,
            'nodes_visited': 0,
            'path_cost': 0,
            'execution_time': 0.0,
        }
        self.history.clear()


class HeatmapData:
    """Generate heatmap data for visualization of explored regions."""
    
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.exploration_count = [[0] * cols for _ in range(rows)]
    
    def record_exploration(self, x: int, y: int, count: int = 1):
        """Record exploration at a cell."""
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.exploration_count[y][x] += count
    
    def get_max_exploration(self) -> int:
        """Get the maximum exploration count."""
        max_count = 0
        for row in self.exploration_count:
            for count in row:
                if count > max_count:
                    max_count = count
        return max_count
    
    def get_normalized_value(self, x: int, y: int) -> float:
        """Get normalized exploration value (0.0 to 1.0)."""
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return 0.0
        
        max_val = self.get_max_exploration()
        if max_val == 0:
            return 0.0
        
        return self.exploration_count[y][x] / max_val
    
    def reset(self):
        """Reset all exploration data."""
        self.exploration_count = [[0] * self.cols for _ in range(self.rows)]