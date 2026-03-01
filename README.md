# Dynamic-Pathfinding-Agent-Informed-Searches-
A dynamic grid-based pathfinding agent implementing A* and Greedy Best-First Search with real-time obstacle spawning and re-planning using heuristic evaluation.
# Dynamic Pathfinding Agent
A comprehensive Grid-based pathfinding application implementing informed search algorithms with dynamic obstacle spawning and re-planning capabilities.
## Features

### Environment Specifications
- **Dynamic Grid Sizing**: User-defined grid dimensions (rows × columns)
- **Fixed Start & Goal**: Clearly identified start and goal nodes
- **Random Map Generation**: Maze generation with configurable obstacle density
- **Interactive Map Editor**: Click-based obstacle placement and removal
- **Constraint**: No static map files - all maps generated dynamically

### Algorithmic Implementation
- **Greedy Best-First Search (GBFS)**: f(n) = h(n)
- **A* Search**: f(n) = g(n) + h(n)
- **Heuristic Functions**:
  - Manhattan Distance: $D_{manhattan} = |x_1 - x_2| + |y_1 - y_2|$
  - Euclidean Distance: $D_{euclidean} = \sqrt{(x_1 - x_2)^2 + (y_1 - y_2)^2}$

### Dynamic Obstacles & Re-planning
- **Obstacle Spawning**: Random obstacles spawn during agent motion
- **Path Re-planning**: Automatic re-calculation when path is blocked
- **Optimized**: Only re-plans when necessary, not on every step

### Visualization & Metrics
- **Interactive GUI**: Built with Pygame
- **Visual Elements**:
  - **Blue Circle**: Start node
  - **Orange Circle**: Goal node
  - **Green**: Final path
  - **Red**: Visited nodes
  - **Yellow**: Frontier nodes (in priority queue)
  - **Black**: Obstacles
  - **Cyan Circle**: Agent position (in dynamic mode)
- **Real-time Metrics Dashboard**:
  - Nodes Visited: Total count of expanded nodes
  - Path Cost: Total length of the final path
  - Execution Time: Computation time in milliseconds

## Installation

### Prerequisites
- Python 3.8+
- Pygame 2.5+

### Setup
```bash
# Navigate to the project directory
cd "g:\My projects\Dynamic PathFinding agent"

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

## Usage Guide

### Grid Interaction
- **Left Click**: Set the start node (blue circle)
- **Right Click**: Set the goal node (orange circle)
- **Middle Click**: Toggle obstacle placement/removal

### Controls
- **Find Path**: Execute pathfinding with current settings
- **Clear Map**: Remove all obstacles
- **Generate 30%**: Create random obstacles (30% density)
- **Reset**: Clear everything and reset to default state
- **A* ↔ GBFS**: Toggle between A* Search and Greedy Best-First Search
- **Manhattan**: Toggle between Manhattan and Euclidean distance heuristics
- **Dynamic ON/OFF**: Toggle dynamic mode (obstacles spawn while agent moves)

### Workflow Example
1. Draw a map using middle-click to place obstacles
2. Set a start node (left-click) and goal node (right-click)
3. Choose algorithm (A* or GBFS) and heuristic (Manhattan or Euclidean)
4. Optional: Enable Dynamic Mode to simulate real-time obstacle spawning
5. Click "Find Path" to run the algorithm
6. View results in the metrics dashboard

## Project Structure

```
Dynamic PathFinding agent/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── src/
    ├── grid.py            # Grid and Node classes
    ├── algorithms.py      # A* and GBFS implementations
    ├── heuristics.py      # Distance heuristics
    └── gui.py             # Pygame GUI and visualization
```

## Algorithm Details

### A* Search
- Evaluation: f(n) = g(n) + h(n)
- g(n): Actual path cost from start to node n
- h(n): Heuristic estimated cost from node n to goal
- Optimal path guaranteed with admissible heuristics
- More accurate than GBFS

### Greedy Best-First Search
- Evaluation: f(n) = h(n)
- Uses only heuristic estimate to goal
- Faster but may not find optimal path
- Good for large grids with good heuristics

### Heuristics
Both heuristics are admissible (never overestimate actual cost):
- **Manhattan Distance**: Better for grid-based movement
- **Euclidean Distance**: More accurate geometric estimate

### Dynamic Mode
When enabled:
1. Agent follows the calculated path
2. Obstacles randomly spawn each step
3. If path is blocked, automatic re-planning occurs
4. Re-planning starts from agent's current position
5. Process continues until goal is reached

## Performance Considerations

- Larger grids (50x50+) may take longer to process
- A* generally slower than GBFS but finds better paths
- Dynamic mode adds significant computation per step
- Euclidean distance slightly faster than Manhattan
- Re-planning efficiency depends on obstacle density

## Example Scenarios

### Static Pathfinding
1. Generate 30% obstacles
2. Select A* with Manhattan distance
3. Click "Find Path"
4. Observe optimal path from start to goal

### Dynamic Navigation
1. Create custom map with obstacles
2. Enable Dynamic Mode
3. Select GBFS for speed
4. Watch agent re-plan as new obstacles appear

## Technical Implementation

### Grid System
- 4-directional movement (up, down, left, right)
- Coordinate system: (0,0) at top-left
- Node states: Empty, Obstacle, Start, Goal

### Search State Tracking
- Open set (frontier): Nodes to be explored
- Closed set (visited): Already explored nodes
- Parent pointers for path reconstruction
- Priority queue using Python's heapq

### Re-planning Strategy
- Only re-plans if obstacle blocks current path
- Starts search from agent's current position
- Inherits remaining path if no blocking occurs

## Future Enhancements

- Diagonal movement option
- Bidirectional search
- JPS (Jump Point Search) algorithm
- Visualize search progress step-by-step
- Configurable grid generation patterns
- Performance profiling and comparison charts
- Save/load maps
- Network multiplayer pathfinding

## License
Educational project for AI/Algorithms course.

## Issues & Support
For issues or questions, please review the code comments and docstrings throughout the src/ directory.
rephrase it and cosise it
