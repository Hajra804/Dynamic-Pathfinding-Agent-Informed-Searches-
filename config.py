"""
Configuration module for the Dynamic Pathfinding Agent.
Allows easy customization of application parameters.
"""

from dataclasses import dataclass


@dataclass
class GridConfig:
    """Configuration for the grid environment."""
    default_rows: int = 20
    default_cols: int = 20
    cell_size: int = 24
    allow_diagonal_movement: bool = False


@dataclass
class AlgorithmConfig:
    """Configuration for search algorithms."""
    # A* vs GBFS - A_STAR for optimal, GBFS for faster
    default_algorithm: str = "A_STAR"
    # Manhattan or Euclidean
    default_heuristic: str = "MANHATTAN"


@dataclass
class DynamicConfig:
    """Configuration for dynamic mode."""
    enabled_by_default: bool = False
    obstacle_spawn_rate: float = 0.02  # Probability per step (2%)
    max_obstacles_per_step: int = 1
    respawn_interval: int = 1  # Steps between spawn attempts


@dataclass
class UIConfig:
    """Configuration for the user interface."""
    window_width: int = 1200
    window_height: int = 800
    fps: int = 60
    # Colors (RGB tuples)
    colors = {
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'gray': (128, 128, 128),
        'light_gray': (200, 200, 200),
        'dark_gray': (64, 64, 64),
        'red': (200, 0, 0),
        'green': (0, 200, 0),
        'blue': (0, 0, 200),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'orange': (255, 165, 0),
    }


@dataclass
class GenerationConfig:
    """Configuration for random map generation."""
    default_obstacle_density: float = 0.3  # 30%
    min_density: float = 0.0
    max_density: float = 0.8


class Config:
    """Main configuration class."""
    
    def __init__(self):
        self.grid = GridConfig()
        self.algorithm = AlgorithmConfig()
        self.dynamic = DynamicConfig()
        self.ui = UIConfig()
        self.generation = GenerationConfig()
    
    @staticmethod
    def get_default():
        """Get default configuration."""
        return Config()


# Global configuration instance
_config = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def set_config(config: Config):
    """Set the global configuration instance."""
    global _config
    _config = config