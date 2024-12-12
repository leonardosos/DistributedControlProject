
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.path import Path
import scipy.spatial

# Function to compute Gaussian PDF
def gauss_pdf(x, y, sigma, mean):
    xt = mean[0]
    yt = mean[1]
    temp = ((x - xt) ** 2 + (y - yt) ** 2) / (2 * sigma ** 2)
    val = np.exp(-temp)
    return val

# Compute the centroid with a Gaussian weight
def compute_centroid(vertices, sigma=1.0, mean=[0.5, 0.5], discretz_int=20):
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

# Generate bounded Voronoi diagram
def bounded_voronoi(points, bounding_box):
    # Mirror points to create a finite Voronoi diagram
    points_center = points

    # Mirroring points
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

    # Filter regions to only include those corresponding to the original points
    regions = [vor.regions[vor.point_region[i]] for i in range(len(points_center))]
    vertices = vor.vertices

    return regions, vertices

# Function to plot Gaussian 2D distribution
def plot_gaussian_2d(mean, sigma, xlim, ylim, resolution=100, ax=None):
    # Create a grid of points
    x = np.linspace(xlim[0], xlim[1], resolution)
    y = np.linspace(ylim[0], ylim[1], resolution)
    X, Y = np.meshgrid(x, y)
    # Calculate Gaussian values over the grid
    Z = gauss_pdf(X, Y, sigma, mean)
    # Plot the Gaussian distribution as a heatmap
    if ax is None:
        ax = plt.gca()
    c = ax.contourf(X, Y, Z, levels=50, cmap='viridis')
    return c

# Define the Robot class
class Robot:
    def __init__(self, x, y):
        self.position = np.array([float(x), float(y)])  # Ensure position is stored as floats

# Define the RobotTeam class with coverage algorithm
class RobotTeam:
    def __init__(self, n_robots, bounding_box, sigma, mean):
        # Initialize robots at positions along the diagonal
        self.robots = [Robot(0.2 * i, 0.2 * i) for i in range(n_robots)]
        self.n_robots = n_robots
        self.bounding_box = bounding_box
        self.sigma = sigma
        self.mean = mean

    def update_positions(self):
        # Get current positions
        positions = self.get_positions()

        # Compute Voronoi diagram
        regions, vertices = bounded_voronoi(positions, self.bounding_box)

        centroids = []
        for region in regions:
            if -1 in region or len(region) == 0:
                # Skip open or empty regions
                centroids.append(None)
                continue
            polygon = vertices[region + [region[0]], :]

            # Compute weighted centroid using Gaussian distribution
            centroid = compute_centroid(polygon, sigma=self.sigma, mean=self.mean, discretz_int=20)
            centroids.append(centroid)

        # Update positions towards the centroids
        for i, robot in enumerate(self.robots):
            if centroids[i] is not None:
                displacement = (centroids[i] - robot.position) * 0.1  # Adjust step size as needed
                robot.position += displacement

                # Ensure robots stay within the bounding box
                robot.position[0] = np.clip(robot.position[0], self.bounding_box[0], self.bounding_box[1])
                robot.position[1] = np.clip(robot.position[1], self.bounding_box[2], self.bounding_box[3])

    def get_positions(self):
        return np.array([robot.position for robot in self.robots])

# Animation function
def animate(frame):
    ax1.clear()
    ax1.set_xlim(bounding_box[0], bounding_box[1])
    ax1.set_ylim(bounding_box[2], bounding_box[3])
    ax1.set_title("Robot Positions and Voronoi Diagram")

    # Update robot positions
    team.update_positions()
    positions = team.get_positions()

    #print(positions) # print the positions of the robots

    # Plot the Gaussian distribution
    plot_gaussian_2d(mean=team.mean, sigma=team.sigma,
                     xlim=bounding_box[0:2], ylim=bounding_box[2:], ax=ax1)

    # Plot Voronoi diagram
    regions, vertices = bounded_voronoi(positions, bounding_box)
    for region in regions:
        if -1 in region or len(region) == 0:
            continue
        polygon = vertices[region + [region[0]], :]
        ax1.plot(polygon[:, 0], polygon[:, 1], 'k-')

    # Plot robots
    ax1.plot(positions[:, 0], positions[:, 1], 'ro')

    # Add grid
    ax1.set_xticks(np.arange(bounding_box[0], bounding_box[1] + 1, 1))
    ax1.set_yticks(np.arange(bounding_box[2], bounding_box[3] + 1, 1))
    ax1.grid(True)

# Main script
n_robots = 5
bounding_box = np.array([0., 10., 0., 10.])  # [x_min, x_max, y_min, y_max]

# Parameters for Gaussian distribution
sigma = 0.5  # Set sigma to match the size of a grid cell

# Allow user to select the row and column for Gaussian center (0-indexed)
gaussian_row = 5  # Change to desired row (0 to 9)
gaussian_column = 5  # Change to desired column (0 to 9)

# Calculate the mean based on selected row and column
mean_x = gaussian_column + 0.5
mean_y = gaussian_row + 0.5
mean = [mean_x, mean_y]

team = RobotTeam(n_robots, bounding_box, sigma, mean)

# Set up the plot
fig, ax1 = plt.subplots(figsize=(8, 8))

# Create the animation
anim = FuncAnimation(fig, animate, frames=2200, interval=100, blit=False)

plt.tight_layout()
plt.show()