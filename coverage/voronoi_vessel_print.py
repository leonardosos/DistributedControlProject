
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import scipy.spatial
import json

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
    def __init__(self, x, y):
        self.position = np.array([float(x), float(y)])  # Ensure position is stored as floats

# --- Class: RobotTeam ---
class RobotTeam:
    def __init__(self, n_robots, bounding_box, sigma, mean, gain_speed, discretz_int):
        self.robots = [Robot(0.2 * i, 0.2 * i) for i in range(n_robots)]
        self.bounding_box = bounding_box
        self.sigma = sigma
        self.mean = mean
        self.gain_speed = gain_speed
        self.discretz_int = discretz_int

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
            centroid = compute_centroid(polygon, sigma=self.sigma, mean=self.mean, discretz_int=discretz_int)
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


# --- Function 1: Plot the simulation ---
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


# --- Function 2: Save robot positions to a JSON file ---
def save_positions_to_file(positions_over_time, filename='robot_positions.json'):
    data_to_save = []
    for timestep, positions in enumerate(positions_over_time):
        timestep_data = {'timestep': timestep, 'positions': positions.tolist()}  # Convert to serializable format
        data_to_save.append(timestep_data)

    with open(filename, 'w') as f:
        json.dump(data_to_save, f, indent=4)

    print(f"Robot positions saved to '{filename}'.")


# --- Main Script ---
n_robots = 5
sim_dimension = 100.0
number_of_cells = 10.0
cell_dimension = sim_dimension / number_of_cells
bounding_box = np.array([0., sim_dimension, 0., sim_dimension])
gain_speed = 0.5
tolerance = 0.025  # Convergence threshold
discretz_int=100 # Discretization for voronoi

# Gaussina Cell 
gaussian_row = 2
gaussian_column = 7

# Gaussian parameters
sigma = cell_dimension / 4
mean_x = gaussian_column * cell_dimension + cell_dimension / 2
mean_y = gaussian_row * cell_dimension + cell_dimension / 2
mean = [mean_x, mean_y]

# Initialize team and variables
team = RobotTeam(n_robots, bounding_box, sigma, mean, gain_speed, discretz_int)
positions_over_time = []
max_steps = 500

# Simulation loop
fig, ax1 = plt.subplots(figsize=(8, 8))
for step in range(max_steps):
    team.update_positions()
    positions = team.get_positions()
    positions_over_time.append(positions.copy())

    max_displacement = max(team.displacements)
    if max_displacement < tolerance:
        print(f"Convergence reached at step {step}. Maximum displacement: {max_displacement:.5f}")
        break

    # Call the plot function
    plot_simulation(ax1, team, bounding_box, positions, step, sim_dimension, number_of_cells)
    plt.pause(0.01)

# Save data to file
save_positions_to_file(positions_over_time, 'robot_positions.json')

# Show final plot
plt.show()
