"""
Heuristic functions for pathfinding algorithms.
"""

import math
from enum import Enum
from typing import Callable


class HeuristicType(Enum):
    """Types of heuristic functions."""
    MANHATTAN = "Manhattan Distance"
    EUCLIDEAN = "Euclidean Distance"


def manhattan_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate Manhattan distance between two points.
    D_manhattan = |x1 - x2| + |y1 - y2|
    """
    return abs(x1 - x2) + abs(y1 - y2)


def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate Euclidean distance between two points.
    D_euclidean = sqrt((x1 - x2)^2 + (y1 - y2)^2)
    """
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def get_heuristic(heuristic_type: HeuristicType) -> Callable[[float, float, float, float], float]:
    """
    Get the heuristic function for the given type.
    
    Args:
        heuristic_type: The type of heuristic to use
        
    Returns:
        A callable heuristic function
    """
    if heuristic_type == HeuristicType.MANHATTAN:
        return manhattan_distance
    elif heuristic_type == HeuristicType.EUCLIDEAN:
        return euclidean_distance
    else:
        raise ValueError(f"Unknown heuristic type: {heuristic_type}")