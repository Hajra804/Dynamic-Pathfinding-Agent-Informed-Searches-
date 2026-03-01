"""
Benchmarking and performance comparison script.
Compares A* and GBFS with different heuristics and obstacle densities.
"""

import sys
import os
import time
from typing import List, Tuple, Dict
import statistics

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from grid import Grid
from algorithms import PathFinder, AlgorithmType
from heuristics import HeuristicType


class BenchmarkResult:
    """Stores results of a single benchmark run."""
    
    def __init__(self, algorithm: str, heuristic: str, grid_size: int, 
                 obstacle_density: float):
        self.algorithm = algorithm
        self.heuristic = heuristic
        self.grid_size = grid_size
        self.obstacle_density = obstacle_density
        self.nodes_visited_list: List[int] = []
        self.execution_times: List[float] = []
        self.path_costs: List[float] = []
        self.path_found_count: int = 0
        self.trials: int = 0
    
    def add_result(self, nodes_visited: int, execution_time: float, 
                   path_cost: float, path_found: bool):
        """Add a trial result."""
        self.nodes_visited_list.append(nodes_visited)
        self.execution_times.append(execution_time)
        self.path_costs.append(path_cost)
        if path_found:
            self.path_found_count += 1
        self.trials += 1
    
    @property
    def avg_nodes_visited(self) -> float:
        """Average nodes visited."""
        if not self.nodes_visited_list:
            return 0
        return statistics.mean(self.nodes_visited_list)
    
    @property
    def avg_execution_time(self) -> float:
        """Average execution time in ms."""
        if not self.execution_times:
            return 0
        return statistics.mean(self.execution_times)
    
    @property
    def avg_path_cost(self) -> float:
        """Average path cost."""
        if not self.path_costs:
            return 0
        return statistics.mean(self.path_costs)
    
    @property
    def success_rate(self) -> float:
        """Percentage of successful pathfinds."""
        if self.trials == 0:
            return 0
        return (self.path_found_count / self.trials) * 100
    
    def __repr__(self) -> str:
        return (f"{self.algorithm:20} | {self.heuristic:15} | "
                f"{self.avg_execution_time:8.3f}ms | "
                f"Nodes: {self.avg_nodes_visited:6.1f} | "
                f"Path: {self.avg_path_cost:5.1f} | "
                f"Success: {self.success_rate:5.1f}%")


class Benchmarker:
    """Runs benchmark tests on pathfinding algorithms."""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
    
    def benchmark_single_run(self, grid_size: int, obstacle_density: float,
                            algorithm: AlgorithmType, 
                            heuristic: HeuristicType) -> BenchmarkResult:
        """Run a single benchmark test."""
        result = BenchmarkResult(
            algorithm.name,
            heuristic.name,
            grid_size,
            obstacle_density
        )
        
        # Create grid with random obstacles
        grid = Grid(grid_size, grid_size)
        grid.set_start(0, 0)
        grid.set_goal(grid_size - 1, grid_size - 1)
        grid.generate_random_obstacles(obstacle_density)
        
        # Run pathfinding
        pathfinder = PathFinder(grid, algorithm, heuristic)
        path = pathfinder.find_path()
        
        # Record result
        result.add_result(
            pathfinder.metrics.nodes_visited,
            pathfinder.metrics.execution_time,
            pathfinder.metrics.path_cost if path else 0,
            path is not None
        )
        
        return result
    
    def benchmark_configuration(self, grid_size: int, obstacle_density: float,
                                algorithm: AlgorithmType,
                                heuristic: HeuristicType,
                                trials: int = 5) -> BenchmarkResult:
        """Run multiple trials for a configuration."""
        cumulative = BenchmarkResult(
            algorithm.name,
            heuristic.name,
            grid_size,
            obstacle_density
        )
        
        print(f"  Running {trials} trials: {algorithm.name} + {heuristic.name}...", end='')
        sys.stdout.flush()
        
        for _ in range(trials):
            result = self.benchmark_single_run(grid_size, obstacle_density, 
                                               algorithm, heuristic)
            cumulative.nodes_visited_list.extend(result.nodes_visited_list)
            cumulative.execution_times.extend(result.execution_times)
            cumulative.path_costs.extend(result.path_costs)
            cumulative.path_found_count += result.path_found_count
            cumulative.trials += 1
        
        print(" Done!")
        self.results.append(cumulative)
        return cumulative
    
    def run_comprehensive_benchmark(self, grid_sizes: List[int] = None,
                                   obstacle_densities: List[float] = None,
                                   trials_per_config: int = 5):
        """Run comprehensive benchmark suite."""
        if grid_sizes is None:
            grid_sizes = [10, 20, 30]
        if obstacle_densities is None:
            obstacle_densities = [0.1, 0.3, 0.5]
        
        algorithms = [AlgorithmType.A_STAR, AlgorithmType.GBFS]
        heuristics = [HeuristicType.MANHATTAN, HeuristicType.EUCLIDEAN]
        
        total_configs = len(grid_sizes) * len(obstacle_densities) * len(algorithms) * len(heuristics)
        current = 0
        
        print("=" * 80)
        print("COMPREHENSIVE PATHFINDING BENCHMARK")
        print("=" * 80)
        print(f"Grid Sizes: {grid_sizes}")
        print(f"Obstacle Densities: {obstacle_densities}")
        print(f"Total Configurations: {total_configs}")
        print(f"Trials per Config: {trials_per_config}")
        print("=" * 80 + "\n")
        
        for grid_size in grid_sizes:
            for density in obstacle_densities:
                print(f"Grid: {grid_size}x{grid_size}, Obstacles: {density*100:.0f}%")
                
                for algorithm in algorithms:
                    for heuristic in heuristics:
                        current += 1
                        self.benchmark_configuration(grid_size, density, algorithm,
                                                    heuristic, trials_per_config)
                
                print()
        
        self.print_results_summary()
    
    def run_algorithm_comparison(self, grid_size: int = 20, 
                                obstacle_density: float = 0.3,
                                trials: int = 10):
        """Compare algorithms on single configuration."""
        print("=" * 80)
        print("ALGORITHM COMPARISON")
        print("=" * 80)
        print(f"Grid Size: {grid_size}x{grid_size}")
        print(f"Obstacle Density: {obstacle_density*100:.0f}%")
        print(f"Trials per Algorithm: {trials}")
        print("=" * 80 + "\n")
        
        algorithms = [AlgorithmType.A_STAR, AlgorithmType.GBFS]
        heuristics = [HeuristicType.MANHATTAN, HeuristicType.EUCLIDEAN]
        
        results_dict: Dict[str, BenchmarkResult] = {}
        
        for algorithm in algorithms:
            for heuristic in heuristics:
                result = self.benchmark_configuration(grid_size, obstacle_density,
                                                     algorithm, heuristic, trials)
                key = f"{algorithm.name} + {heuristic.name}"
                results_dict[key] = result
        
        print("\n" + "=" * 80)
        print("RESULTS SUMMARY")
        print("=" * 80)
        print(f"{'Algorithm':<20} | {'Heuristic':<15} | "
              f"{'Exec Time':<10} | {'Nodes':<10} | "
              f"{'Path Cost':<10} | {'Success':<10}")
        print("-" * 80)
        
        for key, result in results_dict.items():
            print(result)
        
        self.analyze_results(results_dict)
    
    def run_heuristic_comparison(self, grid_size: int = 20,
                                obstacle_density: float = 0.3,
                                trials: int = 10):
        """Compare heuristics with same algorithm."""
        print("=" * 80)
        print("HEURISTIC COMPARISON")
        print("=" * 80)
        print(f"Algorithm: A*")
        print(f"Grid Size: {grid_size}x{grid_size}")
        print(f"Obstacle Density: {obstacle_density*100:.0f}%")
        print(f"Trials per Heuristic: {trials}")
        print("=" * 80 + "\n")
        
        heuristics = [HeuristicType.MANHATTAN, HeuristicType.EUCLIDEAN]
        results_dict: Dict[str, BenchmarkResult] = {}
        
        for heuristic in heuristics:
            result = self.benchmark_configuration(grid_size, obstacle_density,
                                                 AlgorithmType.A_STAR, 
                                                 heuristic, trials)
            results_dict[f"A* + {heuristic.name}"] = result
        
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"{'Heuristic':<20} | "
              f"{'Exec Time':<10} | {'Nodes':<10} | "
              f"{'Path Cost':<10} | {'Success':<10}")
        print("-" * 80)
        
        for key, result in results_dict.items():
            heur = key.split("+")[1].strip()
            print(f"{heur:<20} | "
                  f"{result.avg_execution_time:8.3f}ms | "
                  f"{result.avg_nodes_visited:8.1f} | "
                  f"{result.avg_path_cost:8.1f} | "
                  f"{result.success_rate:8.1f}%")
    
    def run_scaling_benchmark(self, grid_sizes: List[int] = None,
                             obstacle_density: float = 0.3,
                             trials: int = 3):
        """Test how algorithms scale with grid size."""
        if grid_sizes is None:
            grid_sizes = [10, 15, 20, 25, 30, 40, 50]
        
        print("=" * 80)
        print("SCALING ANALYSIS")
        print("=" * 80)
        print(f"Obstacle Density: {obstacle_density*100:.0f}%")
        print(f"Trials per Grid Size: {trials}")
        print("=" * 80 + "\n")
        
        algorithms = [AlgorithmType.A_STAR, AlgorithmType.GBFS]
        heuristic = HeuristicType.MANHATTAN
        
        print(f"{'Grid':<8} | {'Algorithm':<6} | {'Exec (ms)':<12} | "
              f"{'Nodes':<10} | {'Growth':<10}")
        print("-" * 70)
        
        prev_nodes = {}
        
        for grid_size in grid_sizes:
            for algorithm in algorithms:
                result = self.benchmark_configuration(grid_size, obstacle_density,
                                                     algorithm, heuristic, trials)
                
                algo_name = "A*" if algorithm == AlgorithmType.A_STAR else "GBFS"
                key = algo_name
                
                growth = ""
                if key in prev_nodes and prev_nodes[key] > 0:
                    ratio = result.avg_nodes_visited / prev_nodes[key]
                    growth = f"{ratio:.2f}x"
                
                prev_nodes[key] = result.avg_nodes_visited
                
                print(f"{grid_size:<8} | {algo_name:<6} | "
                      f"{result.avg_execution_time:10.3f}ms | "
                      f"{result.avg_nodes_visited:8.1f} | "
                      f"{growth:<10}")
            print()
    
    def analyze_results(self, results_dict: Dict[str, BenchmarkResult]):
        """Analyze and provide insights on results."""
        print("\n" + "=" * 80)
        print("ANALYSIS")
        print("=" * 80)
        
        # Find fastest
        fastest = min(results_dict.values(), 
                     key=lambda r: r.avg_execution_time)
        print(f"\n✓ Fastest: {fastest.algorithm} + {fastest.heuristic} "
              f"({fastest.avg_execution_time:.3f}ms)")
        
        # Find least nodes
        least_nodes = min(results_dict.values(),
                         key=lambda r: r.avg_nodes_visited)
        print(f"✓ Least Nodes: {least_nodes.algorithm} + {least_nodes.heuristic} "
              f"({least_nodes.avg_nodes_visited:.1f} nodes)")
        
        # Find best success
        best_success = max(results_dict.values(),
                          key=lambda r: r.success_rate)
        print(f"✓ Best Success: {best_success.algorithm} + {best_success.heuristic} "
              f"({best_success.success_rate:.1f}%)")
        
        # A* vs GBFS
        print("\n--- Algorithm Comparison ---")
        astar_results = [r for r in results_dict.values() 
                        if "A_STAR" in r.algorithm]
        gbfs_results = [r for r in results_dict.values() 
                       if "GBFS" in r.algorithm]
        
        if astar_results and gbfs_results:
            astar_time = statistics.mean([r.avg_execution_time for r in astar_results])
            gbfs_time = statistics.mean([r.avg_execution_time for r in gbfs_results])
            ratio = astar_time / gbfs_time if gbfs_time > 0 else 1
            
            astar_nodes = statistics.mean([r.avg_nodes_visited for r in astar_results])
            gbfs_nodes = statistics.mean([r.avg_nodes_visited for r in gbfs_results])
            node_ratio = gbfs_nodes / astar_nodes if astar_nodes > 0 else 1
            
            print(f"A* is {ratio:.2f}x slower but explores {node_ratio:.2f}x fewer nodes")
            print(f"Trade-off: Optimality vs Speed")
        
        # Manhattan vs Euclidean
        print("\n--- Heuristic Comparison ---")
        manhattan = [r for r in results_dict.values() if "MANHATTAN" in r.heuristic]
        euclidean = [r for r in results_dict.values() if "EUCLIDEAN" in r.heuristic]
        
        if manhattan and euclidean:
            m_time = statistics.mean([r.avg_execution_time for r in manhattan])
            e_time = statistics.mean([r.avg_execution_time for r in euclidean])
            ratio = e_time / m_time if m_time > 0 else 1
            print(f"Manhattan is {ratio:.2f}x faster than Euclidean")
            print(f"Reason: Better admissibility for grid-based movement")
    
    def print_results_summary(self):
        """Print summary of all benchmark results."""
        if not self.results:
            return
        
        print("\n" + "=" * 80)
        print("COMPREHENSIVE RESULTS SUMMARY")
        print("=" * 80)
        print(f"{'Algorithm':<20} | {'Heuristic':<15} | "
              f"{'Size':<8} | {'Density':<8} | "
              f"{'Time (ms)':<10} | {'Nodes':<8} | {'Success':<8}")
        print("-" * 100)
        
        for result in self.results:
            print(f"{result.algorithm:<20} | {result.heuristic:<15} | "
                  f"{result.grid_size:<8} | {result.obstacle_density:<8.1%} | "
                  f"{result.avg_execution_time:8.3f}ms | "
                  f"{result.avg_nodes_visited:6.1f} | "
                  f"{result.success_rate:6.1f}%")


def main():
    """Run benchmarks."""
    benchmarker = Benchmarker()
    
    # Run different benchmark types
    print("\n🔬 PATHFINDING ALGORITHM BENCHMARKS\n")
    
    # 1. Algorithm comparison
    benchmarker.run_algorithm_comparison(grid_size=20, obstacle_density=0.3, trials=10)
    
    # 2. Heuristic comparison
    print("\n" * 2)
    benchmarker.run_heuristic_comparison(grid_size=20, obstacle_density=0.3, trials=10)
    
    # 3. Scaling analysis
    print("\n" * 2)
    benchmarker.run_scaling_benchmark(grid_sizes=[10, 15, 20, 25, 30], 
                                     obstacle_density=0.3, trials=5)
    
    print("\n✓ Benchmarking complete!\n")


if __name__ == "__main__":
    main()