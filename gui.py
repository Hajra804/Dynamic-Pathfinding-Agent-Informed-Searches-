"""
Pygame GUI for the Dynamic Pathfinding Agent.
"""

import pygame
import time
import sys
from typing import Optional, List, Tuple
from enum import Enum
from grid import Grid, NodeType
from algorithms import PathFinder, AlgorithmType
from heuristics import HeuristicType


class UIState(Enum):
    """States of the UI."""
    IDLE = 1
    EDITING = 2
    SEARCHING = 3
    FINISHED = 4
    DYNAMIC_MODE = 5


class Colors:
    """Color definitions for the GUI."""
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (64, 64, 64)
    RED = (200, 0, 0)
    GREEN = (0, 200, 0)
    BLUE = (0, 0, 200)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    ORANGE = (255, 165, 0)


class Button:
    """A simple button class."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw the button."""
        color = tuple(min(c + 50, 255) for c in self.color) if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, Colors.BLACK, self.rect, 2)
        
        text_surface = font.render(self.text, True, Colors.BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if button is clicked."""
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos: Tuple[int, int]):
        """Update hover state."""
        self.hover = self.rect.collidepoint(pos)


class PathFindingGUI:
    """Main GUI class for the pathfinding application."""
    
    def __init__(self, width: int = 800, height: int = 600, algorithm: AlgorithmType = AlgorithmType.A_STAR, heuristic: HeuristicType = HeuristicType.MANHATTAN):
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Dynamic Pathfinding Agent")
        
        # Grid settings
        self.grid_rows = 20
        self.grid_cols = 20
        self.cell_size = 22
        self.grid_x = 20
        self.grid_y = 60
        
        # Initialize grid
        self.grid = Grid(self.grid_rows, self.grid_cols)
        self.grid.set_start(0, 0)
        self.grid.set_goal(self.grid_cols - 1, self.grid_rows - 1)
        
        # Pathfinding (may be set from terminal before launching GUI)
        self.algorithm = algorithm
        self.heuristic = heuristic
        self.path_finder: Optional[PathFinder] = None
        self.current_path: List[Tuple[int, int]] = []
        self.search_generator = None
        
        # UI state
        self.state = UIState.IDLE
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Dynamic mode
        self.dynamic_mode = False
        self.dynamic_obstacle_spawn_rate = 0.02  # 2% chance per step
        self.agent_position = (0, 0)
        self.agent_step_count = 0
        
        # Buttons
        self.buttons = self._create_buttons()
        
        # Metrics
        self.execution_time = 0.0
        self.nodes_visited = 0
        self.path_cost = 0
    
    def _create_buttons(self) -> dict:
        """Create all UI buttons."""
        buttons = {
            'start_search': Button(self.grid_x + self.grid_cols * self.cell_size + 30, 60, 120, 40, "Find Path", Colors.GREEN),
            'clear_obstacles': Button(self.grid_x + self.grid_cols * self.cell_size + 30, 110, 120, 40, "Clear Map", Colors.LIGHT_GRAY),
            'generate_obstacles': Button(self.grid_x + self.grid_cols * self.cell_size + 30, 160, 120, 40, "Generate 30%", Colors.LIGHT_GRAY),
            'reset': Button(self.grid_x + self.grid_cols * self.cell_size + 30, 210, 120, 40, "Reset", Colors.ORANGE),
            'toggle_dynamic': Button(self.grid_x + self.grid_cols * self.cell_size + 30, 310, 120, 40, "Dynamic OFF", Colors.RED),
        }
        return buttons
    
    def _handle_grid_click(self, pos: Tuple[int, int], button: int):
        """Handle clicks on the grid."""
        x_offset = pos[0] - self.grid_x
        y_offset = pos[1] - self.grid_y
        
        if x_offset < 0 or y_offset < 0:
            return
        
        grid_x = x_offset // self.cell_size
        grid_y = y_offset // self.cell_size
        
        if grid_x < 0 or grid_x >= self.grid_cols or grid_y < 0 or grid_y >= self.grid_rows:
            return
        
        # Left click: toggle obstacle
        if button == 1:
            node = self.grid.get_node(grid_x, grid_y)
            if node and node.node_type == NodeType.OBSTACLE:
                self.grid.set_obstacle(grid_x, grid_y, False)
            else:
                self.grid.set_obstacle(grid_x, grid_y, True)
        # Right click: set goal (Shift+Right-click -> set start)
        elif button == 3:
            mods = pygame.key.get_mods()
            if mods & pygame.KMOD_SHIFT:
                self.grid.set_start(grid_x, grid_y)
            else:
                self.grid.set_goal(grid_x, grid_y)
        # Middle click: set start (if available)
        elif button == 2:
            self.grid.set_start(grid_x, grid_y)
    
    def _start_search(self):
        """Start pathfinding."""
        if self.state not in (UIState.IDLE, UIState.FINISHED):
            return

        self.path_finder = PathFinder(self.grid, self.algorithm, self.heuristic)
        # Use stepwise generator to animate search
        self.search_generator = self.path_finder.find_path_stepwise()
        self.state = UIState.SEARCHING
    
    def _toggle_algorithm(self):
        """Toggle between A* and GBFS."""
        # Algorithm selection moved to terminal menu; keep placeholder
        pass
    
    def _toggle_heuristic(self):
        """Toggle between Manhattan and Euclidean distance."""
        # Heuristic selection moved to terminal menu; keep placeholder
        pass
    
    def _toggle_dynamic_mode(self):
        """Toggle dynamic mode"""
        self.dynamic_mode = not self.dynamic_mode
    
    def _clear_obstacles(self):
        """Clear all obstacles."""
        # Clear obstacles and reset any search/visualization state
        self.grid.clear_obstacles()

        # Reset node search attributes so visited/frontier highlighting clears
        self.grid.reset_search_state()

        # Clear path and metrics
        self.current_path = []
        self.execution_time = 0.0
        self.nodes_visited = 0
        self.path_cost = 0

        # Clear pathfinder visualization sets if present
        if self.path_finder:
            try:
                self.path_finder.frontier_nodes.clear()
                self.path_finder.visited_nodes.clear()
            except Exception:
                pass

        # Stop any running search generator
        self.search_generator = None
        self.state = UIState.IDLE
    
    def _generate_obstacles(self):
        """Generate random obstacles."""
        self.grid.clear_obstacles()
        self.grid.generate_random_obstacles(0.3)
        self.current_path = []
        self.state = UIState.IDLE
    
    def _reset(self):
        """Reset everything."""
        self.grid = Grid(self.grid_rows, self.grid_cols)
        self.grid.set_start(0, 0)
        self.grid.set_goal(self.grid_cols - 1, self.grid_rows - 1)
        self.current_path = []
        self.state = UIState.IDLE
        self.dynamic_mode = False
        self.agent_step_count = 0
    
    def _update_dynamic_mode(self):
        """Update dynamic mode step."""
        if self.state != UIState.DYNAMIC_MODE or not self.current_path:
            return
        
        self.agent_step_count += 1
        
        # Move agent along the path
        if self.agent_step_count < len(self.current_path):
            self.agent_position = self.current_path[self.agent_step_count]
        else:
            # Finished
            self.state = UIState.FINISHED
            return
        
        # Randomly spawn new obstacles
        if self.grid.spawn_random_obstacle() is not None:
            # Check if path is still valid
            if self.grid.is_path_blocked(self.current_path):
                # Replan from current position
                self.path_finder = PathFinder(self.grid, self.algorithm, self.heuristic)
                new_path = self.path_finder.replan_from_position(self.agent_position[0], self.agent_position[1])
                
                if new_path:
                    # Adjust path to start from current position in path
                    self.current_path = new_path
                    self.agent_step_count = 0
    
    def _draw_grid(self):
        """Draw the grid."""
        for y in range(self.grid_rows):
            for x in range(self.grid_cols):
                node = self.grid.get_node(x, y)
                if node is None:
                    continue
                
                rect = pygame.Rect(
                    self.grid_x + x * self.cell_size,
                    self.grid_y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                # Draw cell background
                if node.node_type == NodeType.OBSTACLE:
                    color = Colors.BLACK
                elif self.path_finder and node in self.path_finder.visited_nodes:
                    color = Colors.RED
                elif self.path_finder and node in self.path_finder.frontier_nodes:
                    color = Colors.YELLOW
                elif (x, y) in self.current_path:
                    color = Colors.GREEN
                else:
                    color = Colors.WHITE
                
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, Colors.GRAY, rect, 1)
                
                # Draw node type
                if node.node_type == NodeType.START:
                    pygame.draw.circle(self.screen, Colors.BLUE, rect.center, self.cell_size // 3)
                elif node.node_type == NodeType.GOAL:
                    pygame.draw.circle(self.screen, Colors.ORANGE, rect.center, self.cell_size // 3)
        
        # Draw agent position in dynamic mode
        if self.state == UIState.DYNAMIC_MODE:
            x, y = self.agent_position
            rect = pygame.Rect(
                self.grid_x + x * self.cell_size,
                self.grid_y + y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.circle(self.screen, Colors.CYAN, rect.center, self.cell_size // 4)
    
    def _draw_ui(self):
        """Draw UI elements."""
        # Draw title
        title = self.font.render("Dynamic Pathfinding Agent", True, Colors.BLACK)
        self.screen.blit(title, (10, 10))
        
        # Draw buttons
        for button in self.buttons.values():
            button.draw(self.screen, self.small_font)
        
        # Update dynamic toggle button text
        self.buttons['toggle_dynamic'].text = "Dynamic ON" if self.dynamic_mode else "Dynamic OFF"
        self.buttons['toggle_dynamic'].color = Colors.GREEN if self.dynamic_mode else Colors.RED
        
        # Draw metrics
        metrics_x = self.grid_x + self.grid_cols * self.cell_size + 30
        metrics_y = 550
        
        # Compute real-time metrics from the active PathFinder if available
        nodes_visited_val = self.nodes_visited
        path_cost_val = self.path_cost
        exec_time_val = self.execution_time
        
        if self.path_finder:
            try:
                nodes_visited_val = self.path_finder.metrics.nodes_visited
                path_cost_val = self.path_finder.metrics.path_cost
                # If the search has started but not finished, compute elapsed time
                if self.path_finder.metrics.start_time and not self.path_finder.metrics.end_time:
                    exec_time_val = (time.time() - self.path_finder.metrics.start_time) * 1000
                else:
                    exec_time_val = self.path_finder.metrics.execution_time
            except Exception:
                pass

        metrics_info = [
            f"Algorithm: {self.algorithm.value}",
            f"Heuristic: {self.heuristic.value}",
            "",
            f"Nodes Visited: {nodes_visited_val}",
            f"Path Cost: {path_cost_val}",
            f"Execution Time: {exec_time_val:.2f}ms",
            "",
            f"Grid: {self.grid_rows}x{self.grid_cols}",
            f"State: {self.state.name}",
        ]
        
        if self.state == UIState.DYNAMIC_MODE:
            metrics_info.append(f"Agent Step: {self.agent_step_count}/{len(self.current_path)}")
        
        for i, info in enumerate(metrics_info):
            text = self.small_font.render(info, True, Colors.BLACK)
            self.screen.blit(text, (metrics_x, metrics_y + i * 20))
        
        # Draw legend
        legend_y = metrics_y + 220
        legend_info = [
            "Legend:",
            "Blue • : Start",
            "Orange • : Goal",
            "Green : Final Path",
            "Red : Visited",
            "Yellow : Frontier",
            "Black : Obstacle",
        ]
        
        for i, info in enumerate(legend_info):
            text = self.small_font.render(info, True, Colors.BLACK)
            self.screen.blit(text, (metrics_x, legend_y + i * 18))
    
    def _draw_instructions(self):
        """Draw instructions on the screen."""
        instructions = [
            "LEFT CLICK: Set Start",
            "RIGHT CLICK: Set Goal",
            "MIDDLE CLICK: Toggle Obstacle",
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, Colors.DARK_GRAY)
            self.screen.blit(text, (self.grid_x, self.grid_y - 20 - i * 15))
    
    def handle_events(self) -> bool:
        """Handle events. Return False if quit."""
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hovers
        for button in self.buttons.values():
            button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check buttons
                if self.buttons['start_search'].is_clicked(mouse_pos):
                    self._start_search()
                elif self.buttons['clear_obstacles'].is_clicked(mouse_pos):
                    self._clear_obstacles()
                elif self.buttons['generate_obstacles'].is_clicked(mouse_pos):
                    self._generate_obstacles()
                elif self.buttons['reset'].is_clicked(mouse_pos):
                    self._reset()
                elif self.buttons['toggle_dynamic'].is_clicked(mouse_pos):
                    self._toggle_dynamic_mode()
                else:
                    # Handle grid clicks
                    self._handle_grid_click(mouse_pos, event.button)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                # Press 's' to set start at current mouse position
                elif event.key == pygame.K_s:
                    x_offset = mouse_pos[0] - self.grid_x
                    y_offset = mouse_pos[1] - self.grid_y
                    if x_offset >= 0 and y_offset >= 0:
                        grid_x = x_offset // self.cell_size
                        grid_y = y_offset // self.cell_size
                        if 0 <= grid_x < self.grid_cols and 0 <= grid_y < self.grid_rows:
                            self.grid.set_start(grid_x, grid_y)
                # Press 'g' to set goal at current mouse position
                elif event.key == pygame.K_g:
                    x_offset = mouse_pos[0] - self.grid_x
                    y_offset = mouse_pos[1] - self.grid_y
                    if x_offset >= 0 and y_offset >= 0:
                        grid_x = x_offset // self.cell_size
                        grid_y = y_offset // self.cell_size
                        if 0 <= grid_x < self.grid_cols and 0 <= grid_y < self.grid_rows:
                            self.grid.set_goal(grid_x, grid_y)
        
        return True
    
    def update(self):
        """Update game logic."""
        # If executing a stepwise search, advance one step per frame
        if self.state == UIState.SEARCHING and self.search_generator is not None:
            try:
                next(self.search_generator)
            except StopIteration as stop:
                # Generator finished and may have returned a path
                result = stop.value
                self.current_path = result or []
                self.execution_time = self.path_finder.metrics.execution_time
                self.nodes_visited = self.path_finder.metrics.nodes_visited
                self.path_cost = self.path_finder.metrics.path_cost

                if self.current_path and self.dynamic_mode and len(self.current_path) > 1:
                    self.state = UIState.DYNAMIC_MODE
                    self.agent_position = self.current_path[0]
                    self.agent_step_count = 0
                else:
                    self.state = UIState.FINISHED
                self.search_generator = None
            return

        self._update_dynamic_mode()
    
    def draw(self):
        """Draw everything."""
        self.screen.fill(Colors.WHITE)
        
        self._draw_instructions()
        self._draw_grid()
        self._draw_ui()
        
        pygame.display.flip()
    
    def run(self):
        """Main loop."""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point."""
    gui = PathFindingGUI()
    gui.run()


if __name__ == "__main__":
    main()