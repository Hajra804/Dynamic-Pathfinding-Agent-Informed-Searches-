"""
Pathfinding algorithms: A* and Greedy Best-First Search (GBFS).
"""

import heapq
import time
from enum import Enum
from typing import List, Tuple, Callable, Optional
from grid import Grid, Node
from heuristics import HeuristicType, get_heuristic


class AlgorithmType(Enum):
    """Types of pathfinding algorithms."""
    A_STAR = "A* Search"
    GBFS = "Greedy Best-First Search"


class SearchMetrics:
    """Tracks metrics for search algorithms."""
    
    def __init__(self):
        self.nodes_visited = 0
        self.nodes_expanded = 0
        self.start_time = 0.0
        self.end_time = 0.0
        self.path_cost = 0
        self.path_length = 0
    
    @property
    def execution_time(self) -> float:
        """Return execution time in milliseconds."""
        return (self.end_time - self.start_time) * 1000
    
    def __repr__(self) -> str:
        return (f"SearchMetrics(nodes_visited={self.nodes_visited}, "
                f"nodes_expanded={self.nodes_expanded}, "
                f"execution_time={self.execution_time:.2f}ms, "
                f"path_cost={self.path_cost}, path_length={self.path_length})")


class PathFinder:
    """Finds paths using A* or GBFS algorithms."""
    
    def __init__(self, grid: Grid, algorithm: AlgorithmType, heuristic: HeuristicType):
        self.grid = grid
        self.algorithm = algorithm
        self.heuristic = heuristic
        self.heuristic_fn = get_heuristic(heuristic)
        self.metrics = SearchMetrics()
        self.frontier_nodes: set = set()
        self.visited_nodes: set = set()
    
    def find_path(self) -> Optional[List[Tuple[int, int]]]:
        """
        Find a path from start to goal node.
        
        Returns:
            A list of (x, y) coordinates representing the path, or None if no path found.
        """
        if not self.grid.start_node or not self.grid.goal_node:
            return None
        
        # Reset grid search state
        self.grid.reset_search_state()
        self.frontier_nodes.clear()
        self.visited_nodes.clear()
        
        # Record start time
        self.metrics.start_time = time.time()
        
        # Initialize
        start = self.grid.start_node
        goal = self.grid.goal_node
        
        start.g = 0
        start.h = self.heuristic_fn(start.x, start.y, goal.x, goal.y)
        start.f = start.g + start.h if self.algorithm == AlgorithmType.A_STAR else start.h
        
        # Create priority queue
        open_set: List[Tuple[float, int, Node]] = []
        counter = 0  # For tie-breaking in priority queue
        heapq.heappush(open_set, (start.f, counter, start))
        counter += 1
        
        start.in_open = True
        self.frontier_nodes.add(start)
        closed_set: set = set()
        
        while open_set:
            _, _, current = heapq.heappop(open_set)
            
            # Check if we reached the goal
            if current == goal:
                self.metrics.end_time = time.time()
                path = self._reconstruct_path(goal)
                self.metrics.path_cost = goal.g
                self.metrics.path_length = len(path)
                return path
            
            current.in_open = False
            self.frontier_nodes.discard(current)
            closed_set.add(current)
            current.in_closed = True
            self.visited_nodes.add(current)
            self.metrics.nodes_expanded += 1
            self.metrics.nodes_visited = len(self.visited_nodes)
            
            # Explore neighbors
            neighbors = self.grid.get_neighbors(current.x, current.y, diagonal=False)
            
            for neighbor in neighbors:
                if neighbor in closed_set:
                    continue
                
                tentative_g = current.g + 1
                
                # If neighbor is not in open set or we found a better path
                if not neighbor.in_open:
                    neighbor.g = tentative_g
                    neighbor.h = self.heuristic_fn(neighbor.x, neighbor.y, goal.x, goal.y)
                    neighbor.f = neighbor.g + neighbor.h if self.algorithm == AlgorithmType.A_STAR else neighbor.h
                    neighbor.parent = current
                    neighbor.in_open = True
                    heapq.heappush(open_set, (neighbor.f, counter, neighbor))
                    counter += 1
                    self.frontier_nodes.add(neighbor)
                
                elif tentative_g < neighbor.g:
                    # Update the node if we found a better path
                    neighbor.g = tentative_g
                    neighbor.f = neighbor.g + neighbor.h if self.algorithm == AlgorithmType.A_STAR else neighbor.h
                    neighbor.parent = current
                    # Re-add to priority queue (Python heapq doesn't support update)
                    heapq.heappush(open_set, (neighbor.f, counter, neighbor))
                    counter += 1
        
        # No path found
        self.metrics.end_time = time.time()
        return None

    def find_path_stepwise(self):
        """
        Generator version of find_path that yields control after each node expansion
        so a GUI can animate the search. Yields after expanding each node and
        returns the final path when found (StopIteration value).
        """
        if not self.grid.start_node or not self.grid.goal_node:
            return None

        # Reset grid search state
        self.grid.reset_search_state()
        self.frontier_nodes.clear()
        self.visited_nodes.clear()

        # Record start time
        self.metrics.start_time = time.time()

        # Initialize
        start = self.grid.start_node
        goal = self.grid.goal_node

        start.g = 0
        start.h = self.heuristic_fn(start.x, start.y, goal.x, goal.y)
        start.f = start.g + start.h if self.algorithm == AlgorithmType.A_STAR else start.h

        # Create priority queue
        open_set: List[Tuple[float, int, Node]] = []
        counter = 0  # For tie-breaking in priority queue
        heapq.heappush(open_set, (start.f, counter, start))
        counter += 1

        start.in_open = True
        self.frontier_nodes.add(start)
        closed_set: set = set()

        while open_set:
            _, _, current = heapq.heappop(open_set)

            # Check if we reached the goal
            if current == goal:
                self.metrics.end_time = time.time()
                path = self._reconstruct_path(goal)
                self.metrics.path_cost = goal.g
                self.metrics.path_length = len(path)
                # Return final path to caller
                return path

            current.in_open = False
            self.frontier_nodes.discard(current)
            closed_set.add(current)
            current.in_closed = True
            self.visited_nodes.add(current)
            self.metrics.nodes_expanded += 1
            self.metrics.nodes_visited = len(self.visited_nodes)

            # Yield to allow GUI to render current frontier/visited
            yield None

            # Explore neighbors
            neighbors = self.grid.get_neighbors(current.x, current.y, diagonal=False)

            for neighbor in neighbors:
                if neighbor in closed_set:
                    continue

                tentative_g = current.g + 1

                # If neighbor is not in open set or we found a better path
                if not neighbor.in_open:
                    neighbor.g = tentative_g
                    neighbor.h = self.heuristic_fn(neighbor.x, neighbor.y, goal.x, goal.y)
                    neighbor.f = neighbor.g + neighbor.h if self.algorithm == AlgorithmType.A_STAR else neighbor.h
                    neighbor.parent = current
                    neighbor.in_open = True
                    heapq.heappush(open_set, (neighbor.f, counter, neighbor))
                    counter += 1
                    self.frontier_nodes.add(neighbor)

                elif tentative_g < neighbor.g:
                    # Update the node if we found a better path
                    neighbor.g = tentative_g
                    neighbor.f = neighbor.g + neighbor.h if self.algorithm == AlgorithmType.A_STAR else neighbor.h
                    neighbor.parent = current
                    # Re-add to priority queue (Python heapq doesn't support update)
                    heapq.heappush(open_set, (neighbor.f, counter, neighbor))
                    counter += 1

        # No path found
        self.metrics.end_time = time.time()
        return None
    
    def _reconstruct_path(self, node: Node) -> List[Tuple[int, int]]:
        """Reconstruct the path from start to the given node."""
        path = []
        current = node
        
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
        
        path.reverse()
        return path
    
    def replan_from_position(self, x: int, y: int) -> Optional[List[Tuple[int, int]]]:
        """
        Replan from a given position to the goal.
        
        Args:
            x, y: The current position
            
        Returns:
            A new path from the current position to the goal, or None if no path found.
        """
        if not self.grid.goal_node:
            return None
        
        # Get or create the current position node
        current_node = self.grid.get_node(x, y)
        if not current_node:
            return None
        
        # Reset grid search state
        self.grid.reset_search_state()
        self.frontier_nodes.clear()
        self.visited_nodes.clear()
        
        # Record start time
        self.metrics.start_time = time.time()
        
        # Initialize from current position
        goal = self.grid.goal_node
        
        current_node.g = 0
        current_node.h = self.heuristic_fn(current_node.x, current_node.y, goal.x, goal.y)
        current_node.f = current_node.g + current_node.h if self.algorithm == AlgorithmType.A_STAR else current_node.h
        
        # Create priority queue
        open_set: List[Tuple[float, int, Node]] = []
        counter = 0
        heapq.heappush(open_set, (current_node.f, counter, current_node))
        counter += 1
        
        current_node.in_open = True
        self.frontier_nodes.add(current_node)
        closed_set: set = set()
        
        while open_set:
            _, _, current = heapq.heappop(open_set)
            
            # Check if we reached the goal
            if current == goal:
                self.metrics.end_time = time.time()
                path = self._reconstruct_path(goal)
                self.metrics.path_cost = goal.g
                self.metrics.path_length = len(path)
                return path
            
            current.in_open = False
            self.frontier_nodes.discard(current)
            closed_set.add(current)
            current.in_closed = True
            self.visited_nodes.add(current)
            self.metrics.nodes_expanded += 1
            self.metrics.nodes_visited = len(self.visited_nodes)
            
            # Explore neighbors
            neighbors = self.grid.get_neighbors(current.x, current.y, diagonal=False)
            
            for neighbor in neighbors:
                if neighbor in closed_set:
                    continue
                
                tentative_g = current.g + 1
                
                # If neighbor is not in open set or we found a better path
                if not neighbor.in_open:
                    neighbor.g = tentative_g
                    neighbor.h = self.heuristic_fn(neighbor.x, neighbor.y, goal.x, goal.y)
                    neighbor.f = neighbor.g + neighbor.h if self.algorithm == AlgorithmType.A_STAR else neighbor.h
                    neighbor.parent = current
                    neighbor.in_open = True
                    heapq.heappush(open_set, (neighbor.f, counter, neighbor))
                    counter += 1
                    self.frontier_nodes.add(neighbor)
                
                elif tentative_g < neighbor.g:
                    neighbor.g = tentative_g
                    neighbor.f = neighbor.g + neighbor.h if self.algorithm == AlgorithmType.A_STAR else neighbor.h
                    neighbor.parent = current
                    heapq.heappush(open_set, (neighbor.f, counter, neighbor))
                    counter += 1
        
        # No path found
        self.metrics.end_time = time.time()
        return None

    def replan_from_position_stepwise(self, x: int, y: int):
        """
        Generator version of replan_from_position to allow stepwise replanning.
        """
        if not self.grid.goal_node:
            return None

        # Get or create the current position node
        current_node = self.grid.get_node(x, y)
        if not current_node:
            return None

        # Reset grid search state
        self.grid.reset_search_state()
        self.frontier_nodes.clear()
        self.visited_nodes.clear()

        # Record start time
        self.metrics.start_time = time.time()

        # Initialize from current position
        goal = self.grid.goal_node

        current_node.g = 0
        current_node.h = self.heuristic_fn(current_node.x, current_node.y, goal.x, goal.y)
        current_node.f = current_node.g + current_node.h if self.algorithm == AlgorithmType.A_STAR else current_node.h

        # Create priority queue
        open_set: List[Tuple[float, int, Node]] = []
        counter = 0
        heapq.heappush(open_set, (current_node.f, counter, current_node))
        counter += 1

        current_node.in_open = True
        self.frontier_nodes.add(current_node)
        closed_set: set = set()

        while open_set:
            _, _, current = heapq.heappop(open_set)

            # Check if we reached the goal
            if current == goal:
                self.metrics.end_time = time.time()
                path = self._reconstruct_path(goal)
                self.metrics.path_cost = goal.g
                self.metrics.path_length = len(path)
                return path

            current.in_open = False
            self.frontier_nodes.discard(current)
            closed_set.add(current)
            current.in_closed = True
            self.visited_nodes.add(current)
            self.metrics.nodes_expanded += 1
            self.metrics.nodes_visited = len(self.visited_nodes)

            # Yield to allow GUI to render current frontier/visited
            yield None

            # Explore neighbors
            neighbors = self.grid.get_neighbors(current.x, current.y, diagonal=False)

            for neighbor in neighbors:
                if neighbor in closed_set:
                    continue

                tentative_g = current.g + 1

                # If neighbor is not in open set or we found a better path
                if not neighbor.in_open:
                    neighbor.g = tentative_g
                    neighbor.h = self.heuristic_fn(neighbor.x, neighbor.y, goal.x, goal.y)
                    neighbor.f = neighbor.g + neighbor.h if self.algorithm == AlgorithmType.A_STAR else neighbor.h
                    neighbor.parent = current
                    neighbor.in_open = True
                    heapq.heappush(open_set, (neighbor.f, counter, neighbor))
                    counter += 1
                    self.frontier_nodes.add(neighbor)

                elif tentative_g < neighbor.g:
                    neighbor.g = tentative_g
                    neighbor.f = neighbor.g + neighbor.h if self.algorithm == AlgorithmType.A_STAR else neighbor.h
                    neighbor.parent = current
                    heapq.heappush(open_set, (neighbor.f, counter, neighbor))
                    counter += 1

        # No path found
        self.metrics.end_time = time.time()
        return None