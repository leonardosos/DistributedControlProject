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

from matplotlib.cbook import pts_to_midstep
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import scipy.spatial
import json
import sys
import os

# --- Import the required functions from the modules ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from map_analysis import center_of_mass
from map_analysis import conversion_map


# Choose the configuration for the simulation
PLOT_INITIAL = False     # Set to True to plot the initial formation
PLOT = False             # Set to True to plot the simulation
PLOT_REVERT = False       # Set to True to plot the trajectory reverted + non reverted
SAVE_TO_FILE = True     # Set to True to save the positions to a file
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
        self.motherboat_position = motherboat_position

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
def save_positions_to_file(positions_over_time, file_path, single_position):
    '''
    This function saves the positions of the robots over time to a JSON file.
    The file is saved in the specified file path.

    if the single_position=True the json dump handle single vessel path
    if the single_position=False the json dump do for all the vessel for each time frame
    '''

    # Create directory if it does not exist
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    data_to_save = []

    if not single_position:
        for timestep, positions in enumerate(positions_over_time):
            timestep_data = {'timestep': timestep, 'positions': positions.tolist()}  # Convert to serializable format
            data_to_save.append(timestep_data)
    else:
        for position in positions_over_time:
            data_to_save.append(position)

    with open(file_path, 'w') as f:
        json.dump(data_to_save, f, indent=4)

    print(f"Robot positions saved to '{file_path}'.")

def decuple_robot_positions(positions):
    '''
    This function takes the positions of the robots at each timestep and returns n list of positions
    where n is the number of robots. Each list contains the positions of the robot over time. 
    '''

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

    for timestep in positions_over_time:
        transformed_timestep = []
        for x, y in timestep:
            # Apply 180° rotation: (x, y) -> (-x, -y)
            x_rotated = -x
            y_rotated = -y

            # Apply translation: (x, y) -> (x, y + (sim_dimension - cell_dimension))
            x_transformed = x_rotated
            y_transformed = y_rotated + (sim_dimension - cell_dimension)

            transformed_timestep.append((x_transformed, y_transformed))
        transformed_positions.append(transformed_timestep)
    
    return transformed_positions

def plot_trajectory(robot_positions, number_of_cells, cell_dimension, sim_dimension):
    """
    Plots the trajectory of the robots over time with a simulation cell grid and
    marks the initial and ending positions.

    Parameters:
    robot_positions (list of lists): Positions for each robot over time.
    number_of_cells (int): Number of cells in the grid.
    cell_dimension (float): Dimension of each cell.
    sim_dimension (float): Dimension of the simulation area.
    """
    fig, ax = plt.subplots()

    # Set the axis limits
    ax.set_xlim(-sim_dimension, sim_dimension)
    ax.set_ylim(0, sim_dimension)

    # Add a grid with a width and height of 3.5
    ax.set_xticks(np.arange(-sim_dimension + cell_dimension / 2, sim_dimension - cell_dimension / 2 + 3.5, 3.5))
    ax.set_yticks(np.arange(-sim_dimension + cell_dimension / 2, sim_dimension - cell_dimension / 2 + 3.5, 3.5))
    
    # Set the axis labels and title
    ax.set_title("Robot Trajectories with Grid and Start/End Points")
    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")

    # Unique colors for each robot
    cmap = plt.get_cmap("hsv", len(robot_positions))

    # Plot robot trajectories, start, and end points
    for idx, robot_positions_over_time in enumerate(robot_positions):
        x = [pos[0] for pos in robot_positions_over_time]
        y = [pos[1] for pos in robot_positions_over_time]

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
    motherboat_index_position = center_of_mass.compute_center_position(number_of_cells, map_folder='map_generator' ,map_name='map.json')
    motherboat_position = conversion_map.index2coord(cell_dimension, number_of_cells, motherboat_index_position[0], motherboat_index_position[1])

    # Gaussian parameters for the target position
    sigma = cell_dimension / 5
    mean = conversion_map.index2coord(cell_dimension, number_of_cells, gaussian_row, gaussian_column)

    if PRINT_STATS:
        print(f"Motherboat idex: {motherboat_index_position} with position: {motherboat_position}")
        print(f"Target index ({gaussian_row},{gaussian_column}) with position: {mean}")

    # Voronoi Parameters
    gain_speed = 0.1
    tolerance = 0.005  # Convergence threshold
    discretz_int=100   # Discretization for voronoi
    max_steps = 500    # Maximum number of steps

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
            print(f"Voronoi Convergence reached at step {step}. Maximum displacement: {max_displacement:.5f}")
            break

        # Call the plot function
        if PLOT: plot_simulation(ax1, team, bounding_box, positions, step, sim_dimension, number_of_cells)
        if PLOT: plt.pause(0.01)

    # Show final plot
    if PLOT: plt.show()

    # Apply offset to the positions
    if OFFSET_ZERO: 
        positions_over_time = apply_offset(positions_over_time, offset=[cell_dimension/2, cell_dimension/2])
    
    # Plot the trajectory of the robots over time - not reverted
    if PLOT_REVERT: plot_trajectory(decuple_robot_positions(positions_over_time), number_of_cells, cell_dimension, sim_dimension)

    # Revert the axis and plot the trajectory of the robots over time
    positions_over_time = simulation_revert_axis(positions_over_time, number_of_cells, cell_dimension, sim_dimension)

    # Plot the trajectory of the robots over time - reverted
    if PLOT_REVERT: plot_trajectory(decuple_robot_positions(positions_over_time), number_of_cells, cell_dimension, sim_dimension)

    if SAVE_TO_FILE: 

        list_of_positions = decuple_robot_positions(positions_over_time)  

        count = 0

        for i in list_of_positions:
            name = f'PATH_to_follow/vessel_{count}_positions.json'
            count += 1  

            save_positions_to_file(i, f'PATH_to_follow/vessel_{count}_positions.json', single_position=True)

    # Return the positions of the robots over time
    return decuple_robot_positions(positions_over_time)


# test the simulation
if __name__ == '__main__':
    # Simulation parameters
    n_robots = 5

    # Target position - Gaussina Cell 
    row = 1
    column = 0

    #simulation(n_robots, gaussian_row, gaussian_column)
    simulation(n_robots, row, column)
