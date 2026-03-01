"""
Test script to verify core functionality without GUI.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from grid import Grid, NodeType
from algorithms import PathFinder, AlgorithmType
from heuristics import HeuristicType


def test_basic_pathfinding():
    """Test basic pathfinding on a simple grid."""
    print("=" * 60)
    print("TEST 1: Basic Pathfinding (5x5 grid, no obstacles)")
    print("=" * 60)
    
    grid = Grid(5, 5)
    grid.set_start(0, 0)
    grid.set_goal(4, 4)
    
    print("\nInitial Grid:")
    print(grid.display())
    
    # Test A* with Manhattan
    pathfinder = PathFinder(grid, AlgorithmType.A_STAR, HeuristicType.MANHATTAN)
    path = pathfinder.find_path()
    
    print(f"\nA* with Manhattan Distance:")
    print(f"  Path found: {path is not None}")
    print(f"  Path length: {len(path) if path else 0}")
    print(f"  Path cost: {pathfinder.metrics.path_cost}")
    print(f"  Nodes visited: {pathfinder.metrics.nodes_visited}")
    print(f"  Execution time: {pathfinder.metrics.execution_time:.2f}ms")
    print(f"  Metrics: {pathfinder.metrics}")
    
    assert path is not None, "Path should be found on empty grid"
    assert len(path) == 9, f"Expected path length 9, got {len(path)}"
    print("✓ Test 1 PASSED")


def test_pathfinding_with_obstacles():
    """Test pathfinding with obstacles."""
    print("\n" + "=" * 60)
    print("TEST 2: Pathfinding with Obstacles (8x8 grid)")
    print("=" * 60)
    
    grid = Grid(8, 8)
    grid.set_start(0, 0)
    grid.set_goal(7, 7)
    
    # Create a wall
    for x in range(1, 6):
        grid.set_obstacle(x, 3, True)
    
    print("\nGrid with obstacles:")
    print(grid.display())
    
    # Test A* with Euclidean
    pathfinder = PathFinder(grid, AlgorithmType.A_STAR, HeuristicType.EUCLIDEAN)
    path = pathfinder.find_path()
    
    print(f"\nA* with Euclidean Distance:")
    print(f"  Path found: {path is not None}")
    print(f"  Path length: {len(path) if path else 0}")
    print(f"  Path cost: {pathfinder.metrics.path_cost}")
    print(f"  Nodes visited: {pathfinder.metrics.nodes_visited}")
    print(f"  Execution time: {pathfinder.metrics.execution_time:.2f}ms")
    
    assert path is not None, "Path should be found around obstacles"
    print("✓ Test 2 PASSED")


def test_gbfs():
    """Test Greedy Best-First Search."""
    print("\n" + "=" * 60)
    print("TEST 3: Greedy Best-First Search")
    print("=" * 60)
    
    grid = Grid(10, 10)
    grid.set_start(0, 0)
    grid.set_goal(9, 9)
    grid.generate_random_obstacles(0.25)
    
    print("\nGrid with 25% random obstacles")
    
    # Test GBFS
    pathfinder = PathFinder(grid, AlgorithmType.GBFS, HeuristicType.MANHATTAN)
    path = pathfinder.find_path()
    
    print(f"\nGBFS with Manhattan Distance:")
    print(f"  Path found: {path is not None}")
    print(f"  Path length: {len(path) if path else 0}")
    print(f"  Path cost: {pathfinder.metrics.path_cost}")
    print(f"  Nodes visited: {pathfinder.metrics.nodes_visited}")
    print(f"  Execution time: {pathfinder.metrics.execution_time:.2f}ms")
    
    # Test A* for comparison
    grid2 = Grid(10, 10)
    grid2.set_start(0, 0)
    grid2.set_goal(9, 9)
    
    # Copy obstacles
    for y in range(10):
        for x in range(10):
            if grid.get_node(x, y).node_type == NodeType.OBSTACLE:
                grid2.set_obstacle(x, y, True)
    
    pathfinder_astar = PathFinder(grid2, AlgorithmType.A_STAR, HeuristicType.MANHATTAN)
    path_astar = pathfinder_astar.find_path()
    
    print(f"\nA* with Manhattan Distance (same grid):")
    print(f"  Path found: {path_astar is not None}")
    print(f"  Path length: {len(path_astar) if path_astar else 0}")
    print(f"  Path cost: {pathfinder_astar.metrics.path_cost}")
    print(f"  Nodes visited: {pathfinder_astar.metrics.nodes_visited}")
    print(f"  Execution time: {pathfinder_astar.metrics.execution_time:.2f}ms")
    
    print("✓ Test 3 PASSED")


def test_dynamic_replanning():
    """Test dynamic re-planning."""
    print("\n" + "=" * 60)
    print("TEST 4: Dynamic Re-planning")
    print("=" * 60)
    
    grid = Grid(10, 10)
    grid.set_start(0, 0)
    grid.set_goal(9, 9)
    
    # Create initial path
    pathfinder = PathFinder(grid, AlgorithmType.A_STAR, HeuristicType.MANHATTAN)
    initial_path = pathfinder.find_path()
    
    print(f"\nInitial path found with cost: {pathfinder.metrics.path_cost}")
    print(f"Initial nodes visited: {pathfinder.metrics.nodes_visited}")
    
    # Simulate moving along the path and blocking it
    if initial_path and len(initial_path) > 3:
        current_pos = initial_path[2]
        print(f"\nAgent at position {current_pos}")
        
        # Block the path ahead
        if len(initial_path) > 3:
            next_node = initial_path[3]
            grid.set_obstacle(next_node[0], next_node[1], True)
            print(f"Obstacle placed at {next_node}")
        
        # Replan from current position
        new_pathfinder = PathFinder(grid, AlgorithmType.A_STAR, HeuristicType.MANHATTAN)
        new_path = new_pathfinder.replan_from_position(current_pos[0], current_pos[1])
        
        print(f"\nReplanned path found: {new_path is not None}")
        if new_path:
            print(f"New path length: {len(new_path)}")
            print(f"New path cost: {new_pathfinder.metrics.path_cost}")
            print(f"Nodes visited in replanning: {new_pathfinder.metrics.nodes_visited}")
        
        print("✓ Test 4 PASSED")


def test_no_path():
    """Test when no path exists."""
    print("\n" + "=" * 60)
    print("TEST 5: No Path Available")
    print("=" * 60)
    
    grid = Grid(5, 5)
    grid.set_start(0, 0)
    grid.set_goal(4, 4)
    
    # Create a complete wall around goal
    for x in range(3, 5):
        for y in range(3, 5):
            if not (x == 4 and y == 4):
                grid.set_obstacle(x, y, True)
    
    print("\nGrid layout:")
    print(grid.display())
    
    pathfinder = PathFinder(grid, AlgorithmType.A_STAR, HeuristicType.MANHATTAN)
    path = pathfinder.find_path()
    
    print(f"\nA* Search Result:")
    print(f"  Path found: {path is not None}")
    print(f"  Nodes visited: {pathfinder.metrics.nodes_visited}")
    
    assert path is None, "No path should be found when goal is surrounded"
    print("✓ Test 5 PASSED")


def main():
    """Run all tests."""
    print("\n" + "█" * 60)
    print("DYNAMIC PATHFINDING AGENT - TEST SUITE")
    print("█" * 60)
    
    try:
        test_basic_pathfinding()
        test_pathfinding_with_obstacles()
        test_gbfs()
        test_dynamic_replanning()
        test_no_path()
        
        print("\n" + "█" * 60)
        print("ALL TESTS PASSED ✓")
        print("█" * 60 + "\n")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())