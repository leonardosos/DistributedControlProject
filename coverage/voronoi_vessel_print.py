'''
This script runs a simulation of a team of vessels using the Voronoi algorithm.

The robots are initialized in a circular formation around the motherboat.
The motherboat position is determined based on the map with the best position algorithm.

The robots update their positions based on the Voronoi algorithm with Gaussian weights 
centered at a target position.

The simulation is run for a maximum number of steps or until the convergence threshold is reached.

Some configuration parameters can be set at the beginning of the script:
- The initial formation of the robots can be plotted.
- The simulation animation can be plotted.
- The positions of the robots could saved to a JSON file.
- can be printed additional information about the simulation.
- The return coordinates can be offset to the center of the cell instead of the corner.
'''

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import scipy.spatial
import json
import sys
import os

# --- Import the required functions from the modules ---
# Add the path to the weighted_position module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from map_analysis.Weighted_Position import find_best_position  # Import the function
from map_analysis.parse_map import parse_map  # Import the function



# Choose the configuration for the simulation
PLOT_INITIAL = False     # Set to True to plot the initial formation
PLOT = False             # Set to True to plot the simulation
SAVE_TO_FILE = False     # Set to True to save the positions to a file
PRINT_STATS = False      # Set to True to print additional information
OFFSET_ZERO = True       # Set to True to offset the return coordinates
                            #to the center of (last row, first column) cell instead of the corner



# --- Function: Gaussian PDF ---
def gauss_pdf(x, y, sigma, mean):
    xt = mean[0]
    yt = mean[1]
    temp = ((x - xt) ** 2 + (y - yt) ** 2) / (2 * sigma ** 2)
    val = np.exp(-temp)
    return val

# --- Function: Compute centroid with Gaussian weight ---
def compute_centroid(vertices, sigma, mean, discretz_int):
    x_inf = np.min(vertices[:, 0])
    x_sup = np.max(vertices[:, 0])
    y_inf = np.min(vertices[:, 1])
    y_sup = np.max(vertices[:, 1])

    dx = (x_sup - x_inf) / discretz_int
    dy = (y_sup - y_inf) / discretz_int
    dA = dx * dy
    A = 0
    Cx = 0
    Cy = 0

    # Create grid points within the polygon
    x_vals = np.arange(x_inf, x_sup, dx)
    y_vals = np.arange(y_inf, y_sup, dy)
    xv, yv = np.meshgrid(x_vals, y_vals)
    xv = xv.flatten()
    yv = yv.flatten()
    points = np.vstack((xv, yv)).T

    # Check which points are inside the polygon
    p = Path(vertices)
    mask = p.contains_points(points)

    # Compute weighted centroid
    for i in range(len(points)):
        if mask[i]:
            x_i, y_i = points[i]
            weight = gauss_pdf(x_i, y_i, sigma, mean)
            A += dA * weight
            Cx += x_i * dA * weight
            Cy += y_i * dA * weight

    if A == 0:
        # If area is zero, return the centroid of the vertices
        return np.mean(vertices, axis=0)
    Cx /= A
    Cy /= A

    return np.array([Cx, Cy])

# --- Function: Generate bounded Voronoi diagram ---
def bounded_voronoi(points, bounding_box):
    points_center = points
    points_left = points_center.copy()
    points_left[:, 0] = bounding_box[0] - (points_left[:, 0] - bounding_box[0])
    points_right = points_center.copy()
    points_right[:, 0] = bounding_box[1] + (bounding_box[1] - points_right[:, 0])
    points_down = points_center.copy()
    points_down[:, 1] = bounding_box[2] - (points_down[:, 1] - bounding_box[2])
    points_up = points_center.copy()
    points_up[:, 1] = bounding_box[3] + (bounding_box[3] - points_up[:, 1])

    # Combine all points
    points_all = np.vstack([points_center, points_left, points_right, points_down, points_up])

    # Compute Voronoi diagram
    vor = scipy.spatial.Voronoi(points_all)

    # Filter regions to include only those for the original points
    regions = [vor.regions[vor.point_region[i]] for i in range(len(points_center))]
    vertices = vor.vertices

    return regions, vertices

# --- Function: Plot Gaussian distribution ---
def plot_gaussian_2d(mean, sigma, xlim, ylim, resolution=100, ax=None):
    x = np.linspace(xlim[0], xlim[1], resolution)
    y = np.linspace(ylim[0], ylim[1], resolution)
    X, Y = np.meshgrid(x, y)
    Z = gauss_pdf(X, Y, sigma, mean)
    if ax is None:
        ax = plt.gca()
    return ax.contourf(X, Y, Z, levels=50, cmap='viridis')

# --- Class: Robot ---
class Robot:
    '''
    This class represents a robot in the simulation.
    Each robot has a position in the 2D space.
    '''
    def __init__(self, x, y):
        self.position = np.array([float(x), float(y)])  # Ensure position is stored as floats


# --- Class: RobotTeam ---
class RobotTeam:
    '''
    This class represents a team of robots in the simulation.
    The team has a number of robots.
    The robots are initialized in a circular formation around the motherboat.

    The team update the positions of the robots based on the Voronoi algorithm.

    The team has the following attributes:
    - n_robots: Number of robots in the team
    - bounding_box: Bounding box of the simulation area
    - sigma: Standard deviation of the Gaussian distribution
    - mean: Mean of the Gaussian distribution
    - gain_speed: Gain speed for updating the positions
    - discretz_int: Discretization interval for computing the centroid
    - motherboat_position: Position of the motherboat
    - cell_dimension: Dimension of the cell
    
    - robots: List of robots in the team
    - displacements: List of displacements of the robots

    The team has the following methods:
    - plot_formation: Plot the initial formation of the robots
    - initialize_robots_positions: Initialize the positions of the robots
    - update_positions: Update the positions of the robots based on the Voronoi algorithm
    - get_positions: Get the positions of the robots
    '''
    def __init__(self, 
                 n_robots, 
                 bounding_box, 
                 sigma, mean, 
                 gain_speed, 
                 discretz_int, 
                 motherboat_position,
                 cell_dimension,
                 PLOT_INITIAL):
        
        self.n_robots = n_robots
        self.bounding_box = bounding_box
        self.sigma = sigma
        self.mean = mean
        self.gain_speed = gain_speed
        self.discretz_int = discretz_int
        self.cell_dimension = cell_dimension
        self.motherboat_position = ((motherboat_position[0] * cell_dimension) + cell_dimension/2 , 
                                    (motherboat_position[1] * cell_dimension) + cell_dimension/2)
        if PRINT_STATS: print(f'Motherboat position {motherboat_position} -> {self.motherboat_position}')
        
        self.robots = list()
        self.initialize_robots_positions()

        if PLOT_INITIAL: self.plot_formation()

    def plot_formation(self):
        # Plotting the positions using Matplotlib
        plt.figure()
        ax = plt.gca()

        plt.plot(self.motherboat_position[0], self.motherboat_position[1], 'bo', label='Motherboat')
        
        for i, robot in enumerate(self.robots):
            x, y = robot.position  # Assuming Robot object has a 'position' attribute
            plt.plot(x, y, 'ro', label=f'Vessel {i+1}')
            plt.text(x, y, f'R{i+1}')
        
        # Plot the cell as a square
        cell_x = self.motherboat_position[0] - self.cell_dimension / 2
        cell_y = self.motherboat_position[1] - self.cell_dimension / 2
        cell = patches.Rectangle((cell_x, cell_y), self.cell_dimension, self.cell_dimension, linewidth=1, edgecolor='r', facecolor='none', label='Cell')
        ax.add_patch(cell)

        plt.xlabel('X Position')
        plt.ylabel('Y Position')
        plt.title('Robot Positions')
        plt.legend()
        plt.grid(True)
        plt.axis('equal')
        plt.show()

    def initialize_robots_positions(self):
        if PRINT_STATS:  print(f"Initializing {self.n_robots} robots...")

        # Dispose robots in a circular way around the motherboat_position
        radius = (self.cell_dimension/2)/2  # Radius of the circle
        angle_increment = 2 * np.pi / self.n_robots

        if PRINT_STATS:  print(f'Radius = {radius}, angle increment = {round(np.degrees(angle_increment),1)}, cell dimension = {self.cell_dimension} ')

        for i in range(n_robots):
            angle = i * angle_increment
            x = self.motherboat_position[0] + radius * np.cos(angle)
            y = self.motherboat_position[1] + radius * np.sin(angle)
            self.robots.append(Robot(x, y))

    def update_positions(self):
        positions = self.get_positions()
        regions, vertices = bounded_voronoi(positions, self.bounding_box)
        centroids = []
        self.displacements = []

        for region in regions:
            if region is None or -1 in region or len(region) == 0:
                centroids.append(None)
                continue
            polygon = vertices[region + [region[0]], :]
            centroid = compute_centroid(polygon, sigma=self.sigma, mean=self.mean, discretz_int=self.discretz_int)
            centroids.append(centroid)

        # Update positions
        for i, robot in enumerate(self.robots):
            if centroids[i] is not None:
                displacement = (centroids[i] - robot.position) * self.gain_speed
                robot.position += displacement
                # Store displacement magnitude for convergence check
                self.displacements.append(np.linalg.norm(displacement))
                # Ensure robots stay within the bounding box
                robot.position[0] = np.clip(robot.position[0], self.bounding_box[0], self.bounding_box[1])
                robot.position[1] = np.clip(robot.position[1], self.bounding_box[2], self.bounding_box[3])

            else:
                self.displacements.append(0.0)

    def get_positions(self):
        return np.array([robot.position for robot in self.robots])


# --- Function: Plot the simulation ---
def plot_simulation(ax, team, bounding_box, positions, step, sim_dimension, number_of_cells):
    ax.clear()
    ax.set_xlim(bounding_box[0], bounding_box[1])
    ax.set_ylim(bounding_box[2], bounding_box[3])
    ax.set_title(f"Step {step}: Robot Positions and Voronoi Diagram")

    # Plot Gaussian distribution
    plot_gaussian_2d(mean=team.mean, sigma=team.sigma, xlim=bounding_box[0:2], ylim=bounding_box[2:], ax=ax)

    # Plot Voronoi diagram
    regions, vertices = bounded_voronoi(positions, bounding_box)
    for region in regions:
        if region is None or -1 in region or len(region) == 0:
            continue
        polygon = vertices[region + [region[0]], :]
        ax.plot(polygon[:, 0], polygon[:, 1], 'k-')

    # Plot robots
    ax.plot(positions[:, 0], positions[:, 1], 'ro')

    # Add grid
    ax.set_xticks(np.arange(bounding_box[0], bounding_box[1] + 1, sim_dimension / number_of_cells))
    ax.set_yticks(np.arange(bounding_box[2], bounding_box[3] + 1, sim_dimension / number_of_cells))
    ax.grid(True)


# --- Function: Save robot positions to a JSON file ---
def save_positions_to_file(positions_over_time, file_path):
    '''
    This function saves the positions of the robots over time to a JSON file.
    The file is saved in the specified file path.
    '''

    # Create directory if it does not exist
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    data_to_save = []
    for timestep, positions in enumerate(positions_over_time):
        timestep_data = {'timestep': timestep, 'positions': positions.tolist()}  # Convert to serializable format
        data_to_save.append(timestep_data)

    with open(file_path, 'w') as f:
        json.dump(data_to_save, f, indent=4)

    print(f"Robot positions saved to '{file_path}'.")


# --- Function: Compute start position ---
def compute_start_position(number_of_cells, map_name):  
    '''
    This function computes the start position of the motherboat based on the map.
    The motherboat is placed in the cell with the highest weight.
    '''

    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'map_generator', map_name))
    
    parsed_data, dimensions = parse_map(json_path)

    if PRINT_STATS:  print(f'Garbage at {parsed_data}')
    
    coordinates = list(parsed_data.keys())
    weights = list(parsed_data.values())
    
    start_position = find_best_position(number_of_cells, coordinates, weights)[0]
    
    if number_of_cells != dimensions[0] or number_of_cells != dimensions[1]:
        raise ValueError("The number of cells must match the dimensions of the map.")

    if PRINT_STATS:  print(f"Start position: {start_position}")
    if PRINT_STATS:  print(f"Coordinates: {coordinates}")
    
    return start_position 

def decuple_robot_positions(positions):
    '''
    This function takes the positions of the robots at each timestep and returns n list of positions
    where n is the number of robots. Each list contains the positions of the robot over time. 
    '''
    # Assuming positions is a list of lists where each inner list contains the positions of all robots at a given timestep
    num_robots = len(positions[0])
    robot_positions = [[] for _ in range(num_robots)]
    
    for timestep in positions:
        for i, position in enumerate(timestep):
            robot_positions[i].append(position)
    
    return robot_positions

def apply_offset(positions, offset):
    '''
    This function applies an offset to the positions of the robots. 
    The offset is applied to the x and y coordinates of each position.
    '''

    offset_positions = []
    for timestep in positions:
        offset_timestep = []
        for position in timestep:
            offset_position = position - offset
            offset_timestep.append(offset_position)
        offset_positions.append(offset_timestep)
        
    return offset_positions


# --- Function: Simulation ---
def simulation(n_robots, gaussian_row, gaussian_column):
    '''
    This is the simulation function that runs the Voronoi algorithm to compute the path of the robots.

    Parameters:
    - n_robots: Number of robots in the simulation
    - Target position - Gaussina Cell position
        - gaussian_row: Row of the Gaussian cell
        - gaussian_column: Column of the Gaussian cell

    Returns:
    - List of lists containing the positions of the robots over time
    '''

    # --- Enviroment parameters ---
    sim_dimension = 35.0
    number_of_cells = 10
    cell_dimension = sim_dimension / number_of_cells # float propagation
    bounding_box = np.array([0., sim_dimension, 0., sim_dimension])

    # Start position
    motherboat_position = compute_start_position(number_of_cells, map_name='map.json')

    # Voronoi Parameters
    gain_speed = 0.1
    tolerance = 0.005  # Convergence threshold
    discretz_int=100   # Discretization for voronoi
    max_steps = 500    # Maximum number of steps

    # Gaussian parameters
    sigma = cell_dimension / 5
    mean_x = gaussian_column * cell_dimension + cell_dimension / 2
    mean_y = gaussian_row * cell_dimension + cell_dimension / 2
    mean = [mean_x, mean_y]

    # Initialize team and variables
    team = RobotTeam(n_robots, 
                    bounding_box, 
                    sigma, 
                    mean, 
                    gain_speed, 
                    discretz_int, 
                    motherboat_position,
                    cell_dimension,
                    PLOT_INITIAL)
    
    positions_over_time = []

    # Initialize plot
    if PLOT: fig, ax1 = plt.subplots(figsize=(8, 8))

    # Simulation loop
    for step in range(max_steps):
        team.update_positions()
        positions = team.get_positions()
        positions_over_time.append(positions.copy())

        max_displacement = max(team.displacements)
        if max_displacement < tolerance:
            print(f"Convergence reached at step {step}. Maximum displacement: {max_displacement:.5f}")
            break

        # Call the plot function
        if PLOT: plot_simulation(ax1, team, bounding_box, positions, step, sim_dimension, number_of_cells)

        if PLOT: plt.pause(0.01)

    if SAVE_TO_FILE: save_positions_to_file(positions_over_time, 'PATH_to_follow/vessel_positions.json')

    # Show final plot
    if PLOT: plt.show()

    if OFFSET_ZERO: 
        positions_over_time = apply_offset(positions_over_time, offset=[cell_dimension/2, cell_dimension/2])
    
    return decuple_robot_positions(positions_over_time)



# test the simulation
if __name__ == '__main__':
    # Simulation parameters
    n_robots = 4

    # Target position - Gaussina Cell 
    gaussian_row = 2
    gaussian_column = 7

    #simulation(n_robots, gaussian_row, gaussian_column)
    simulation(n_robots, gaussian_row, gaussian_column)
