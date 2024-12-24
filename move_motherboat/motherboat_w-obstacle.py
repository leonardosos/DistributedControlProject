"""
This script computes the path for the motherboat to follow.

The path is computed using the A* algorithm with obstacle avoidance implemented.

The motherboat starts at the bottom-left corner of the map and moves to the center of mass of the map.

The path is then smoothed using spline interpolation to ensure a smooth trajectory.

A list of setting is provided at the beginning of the script for easy configuration of plot and print options.
"""


import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import os
from scipy.interpolate import splprep, splev

# --- Import the required functions from the modules ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from coverage.voronoi_vessel_print import save_positions_to_file
from map_analysis import center_of_mass
from map_analysis import conversion_map

# Import the pathfinding library classes
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

# Configuration
PRINT_STATS = False      # Set to True to print additional information
PLOT_TRAJECTORY = False  # Set to True to plot the trajectory
SAVE_TO_FILE = True      # Set to True to save the positions to a file
COPPELIA_OUTPUT = True   # Coppelia-like output


def simulation_revert_axis(positions_over_time, number_of_cells, cell_dimension, sim_dimension):
    """
    Apply a 180° rotation and a translation by (sim_dimension - cell_dimension) to each point at each timestep.
    
    Parameters:
    positions_over_time (list of lists): List of positions for each timestep.
    number_of_cells (int): Number of cells in the grid.
    cell_dimension (float): Dimension of each cell.
    sim_dimension (float): Dimension of the simulation area.
    
    Returns:
    list of lists: Transformed positions for each timestep.
    """
    transformed_positions = []

    for  x, y in positions_over_time:

        # Apply 180° rotation: (x, y) -> (-x, -y)
        x_rotated = -x
        y_rotated = -y

        # Apply translation: (x, y) -> (x, y + (sim_dimension - cell_dimension))
        x_transformed = x_rotated
        y_transformed = y_rotated + (sim_dimension - cell_dimension)

        transformed_positions.append([x_transformed, y_transformed])
    
    return transformed_positions

def smooth_path(path, spline_factor=2, path_point=200):
    """
    Smooths the given path using a spline interpolation.

    Parameters:
    path (list of tuples): The original path as a list of (x, y) tuples.
    spline_factor (int): The smoothing factor.
    path_point (int): The number of points to generate along the spline for smoothing.

    Returns:
    smoothed_path (list of tuples): The smoothed path as a list of (x, y) tuples.
    """
    # Extract x and y coordinates from the path
    x = [point[0] for point in path]
    y = [point[1] for point in path]

    # Create a spline representation of the path
    tck, u = splprep([x, y], s=spline_factor)

    # Generate new points along the spline
    u_new = np.linspace(0, 1, num=path_point)  # Increase the number of points for smoothing
    x_new, y_new = splev(u_new, tck)

    # Combine the new x and y coordinates into a list of tuples
    smoothed_path = list(zip(x_new, y_new))

    return smoothed_path

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

def plot_trajectory(robot_positions, number_of_cells, cell_dimension, sim_dimension, map_matrix):
    """
    Plots the trajectory of the robots over time with a simulation cell grid and
    marks the initial and ending positions.

    Parameters:
    robot_positions (list of lists): Positions for each robot over time.
    number_of_cells (int): Number of cells in the grid.
    cell_dimension (float): Dimension of each cell.
    sim_dimension (float): Dimension of the simulation area.
    map_matrix (list of lists): Matrix representing the map.
    """
    
    fig, ax = plt.subplots()

    # Display the map matrix
    ax.imshow(map_matrix, extent=[0, sim_dimension, 0, sim_dimension], origin='upper', cmap='gray', alpha=0.5)

    # Set the axis limits
    ax.set_xlim(0, sim_dimension)
    ax.set_ylim(0, sim_dimension)

    # Add a grid with a width and height of 3.5
    ax.set_xticks(np.arange(0, sim_dimension + cell_dimension, cell_dimension))
    ax.set_yticks(np.arange(0, sim_dimension + cell_dimension, cell_dimension))
    
    # Set the axis labels and title
    ax.set_title("Robot Trajectories with Grid and Start/End Points")
    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")

    # Unique colors for each robot using a colormap
    cmap = plt.get_cmap("viridis", len(robot_positions))

    # Plot robot trajectories, start, and end points
    for idx, robot_positions_over_time in enumerate(robot_positions):
        x = [pos[0]+cell_dimension/2 for pos in robot_positions_over_time]
        y = [pos[1]+cell_dimension/2 for pos in robot_positions_over_time]

        # Plot the trajectory
        ax.plot(x, y, label=f'Robot {idx+1}', color=cmap(idx))
        
        # Mark the starting position
        ax.plot(x[0], y[0], 'o', color=cmap(idx))  # Circle marker for start
        ax.text(x[0], y[0], "Start", color=cmap(idx), fontsize=10)

        # Mark the ending position
        ax.plot(x[-1], y[-1], 's', color=cmap(idx))  # Square marker for end
        ax.text(x[-1], y[-1], "End", color=cmap(idx), fontsize=10)

    # Add a grid, legend, and show the plot
    ax.grid(True, color="lightgray", linestyle="--", linewidth=0.5)
    ax.legend()

    plt.show()


def motherboat_path(path_point):
    """
    Computes the path for the motherboat to follow.

    This function sets environment parameters, loads the map data, defines the starting position (0, 0),
    and computes the goal position using the center of mass function on the map data. The path is computed
    using the A* algorithm and then smoothed using a spline interpolation.

    Parameters:
    path_point (int): The number of points to generate along the spline for smoothing.

    Returns:
    list of tuples: A list of (x, y) tuples representing the smoothed path.
    """

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
    index_path = astar_path(map, start_position, goal_position)

    if PRINT_STATS:
        # Print the path in indices
        print("Path in indices:")
        print(index_path)

    # Convert the path to coordinates
    coord_path = []
    for cell in index_path:
        coord_path.append(conversion_map.index2coord2offset(cell_dimension, number_of_cells, cell[0], cell[1]))

    if PRINT_STATS:
        # Print the path in coordinates
        print("Path in coordinates:")
        print(coord_path)

    # Smooth the path    
    spline_factor = 2 # Smoothing factor
    coord_path = smooth_path(coord_path, spline_factor, path_point)

    # Plot the trajectory
    if PLOT_TRAJECTORY: plot_trajectory([coord_path], number_of_cells, cell_dimension, sim_dimension, map)

    if COPPELIA_OUTPUT:
        # Convert the path to CoppeliaSim coordinates
        coord_path = simulation_revert_axis(coord_path, number_of_cells, cell_dimension, sim_dimension)

    if SAVE_TO_FILE: 
        # Save the positions to a file
        save_positions_to_file(coord_path, f'PATH_to_follow/motherboat_positions.json', single_position=True)

    return coord_path
    
# --- Run the simulation ---
if __name__ == '__main__':
    # Test 
    
    # Parameters for path, the number of points in the path
    path_point=200

    motherboat_path(path_point)
