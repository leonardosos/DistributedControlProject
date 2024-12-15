'''
This script computes the path for the motherboat to follow. 

The path is computed using the A* algorithm (obstacle avoidance is implemented).

The path is given in grid indices.

The motherboat starts at the bottom-left corner of the map and moves to the center of mass of the map.
'''


import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import os

# --- Import the required functions from the modules ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from map_analysis import center_of_mass
from map_analysis import conversion_map

# Import the pathfinding library classes
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

# Configuration
PRINT_STATS = True      # Set to True to print additional information


# --- Function: A* Pathfinding using pathfinding library ---
def astar_path(map_grid, start, goal):
    """
    Find path using the pathfinding library.
    map_grid: 2D numpy array where 0 is walkable, 1 is obstacle
    start, goal: (row, col) coordinates
    Returns a list of (row, col) tuples representing the path
    """
    # Convert map_grid to a NumPy array if it is not already
    map_grid = np.array(map_grid)
    # Adjust map_grid to match library expectations (0: walkable, 1: obstacle)
    map_grid_for_pathfinding = np.where(map_grid > 1, 1, map_grid)
    map_grid_for_pathfinding = np.where(map_grid_for_pathfinding == 1, 0, 1)
    
    grid = Grid(matrix=map_grid_for_pathfinding.tolist())

    # Convert (row, col) to (x, y) for the library
    start_node = grid.node(start[1], start[0])  # (x, y)
    end_node = grid.node(goal[1], goal[0])

    finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
    path, runs = finder.find_path(start_node, end_node, grid)

    if PRINT_STATS:
        print('operations:', runs, 'path length:', len(path))
        print(grid.grid_str(path=path, start=start_node, end=end_node))

    if path:
        # Convert the path back to (row, col)
        path_converted = [(y, x) for x, y in path] 
        return path_converted
    else:
        return None

def motherboat_path():
    '''
    This function computes the path for the motherboat to follow.

    It set environment parameters, load the map data, define the starting position (0, 0),
        compute the goal position using the center of mass function on the map data.

    The path is computed using the A* algorithm.

    Returns:
        coordinate_list (list): A list of (row, col) tuples representing the path in grid indices.
    '''

    # --- Environment parameters ---
    sim_dimension = 35.0    # Physical dimension
    number_of_cells = 10
    cell_dimension = sim_dimension / number_of_cells  # Size of each cell

    # --- Map parameters ---
    map_folder = "map_generator"
    map_name = "map.json"

    # Load the map data
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', map_folder, map_name))
    with open(json_path, 'r') as file:
        map = json.load(file)

    # Starting position (0, 0)
    start_position = (0, 0)

    # Compute best position (goal position)
    goal_position = center_of_mass.compute_center_position(number_of_cells, map_folder, map_name)

    if PRINT_STATS:
        print(f"Start position: {start_position}")
        print(f"Goal position: {goal_position}")
    
        #print("Map Grid:")
        #print(map)

    # Use the pathfinding library to find the path
    path = astar_path(map, start_position, goal_position)

    if path:
        if PRINT_STATS:
            print("Path found!")
            print(path)
        
        return path
    
    else:
        raise ValueError("No path found!")
    
# --- Run the simulation ---
if __name__ == '__main__':
    motherboat_path()
