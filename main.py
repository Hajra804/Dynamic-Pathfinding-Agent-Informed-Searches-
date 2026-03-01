"""
Main entry point for the Dynamic Pathfinding Agent.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui import PathFindingGUI 
from algorithms import AlgorithmType
from heuristics import HeuristicType 


def prompt_selection() -> (AlgorithmType, HeuristicType): 
    print("Select algorithm:")
    print("1) A* Search")
    print("2) Greedy Best-First Search (GBFS)")
    alg_choice = input("Enter 1 or 2 (default 1): ").strip() or "1"

    algorithm = AlgorithmType.A_STAR if alg_choice == "1" else AlgorithmType.GBFS

    print("\nSelect heuristic:")
    print("1) Manhattan Distance")
    print("2) Euclidean Distance")
    heur_choice = input("Enter 1 or 2 (default 1): ").strip() or "1"

    heuristic = HeuristicType.MANHATTAN if heur_choice == "1" else HeuristicType.EUCLIDEAN

    print(f"\nSelected: {algorithm.value} with {heuristic.value}\n")
    return algorithm, heuristic


if __name__ == "__main__":
    algorithm, heuristic = prompt_selection()
    gui = PathFindingGUI(algorithm=algorithm, heuristic=heuristic)
    gui.run()