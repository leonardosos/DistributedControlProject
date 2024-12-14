'''





PROF EXAMPLE





'''


import matplotlib.pyplot as plt
from matplotlib.path import Path
import numpy as np
import scipy as sp
from math import exp
import sys
from numpy import arange

eps = sys.float_info.epsilon

def in_box(towers, bounding_box):
    return np.logical_and(np.logical_and(bounding_box[0] <= towers[:, 0],
                                         towers[:, 0] <= bounding_box[1]),
                          np.logical_and(bounding_box[2] <= towers[:, 1],
                                         towers[:, 1] <= bounding_box[3]))

def gauss_pdf(x, y, sigma, mean):
    xt = mean[0]
    yt = mean[1]
    temp = ((x-xt)**2+(y-yt)**2)/(2*sigma**2)
    val = exp(-temp)
    return val


# Compute the centroid with a Gaussian weight
def compute_centroid(vertices, sigma=0.2, mean=[0.8,0.8], discretz_int = 20):
    x_inf = np.min(vertices[:,0])
    x_sup = np.max(vertices[:,0])
    y_inf = np.min(vertices[:,1])
    y_sup = np.max(vertices[:,1])

    # Discretization step, discretz_int define the square of of poligon to aproximate, usually: [20,100]
    t_discretize = 1.0/discretz_int

    dx = (x_sup - x_inf)/2.0 * t_discretize
    dy = (y_sup - y_inf)/2.0 * t_discretize
    dA = dx*dy
    A = 0
    Cx = 0
    Cy = 0

    bool_val = 0

    for i in arange(x_inf, x_sup, dx):
        for j in arange(y_inf, y_sup, dy):
            p = Path(vertices)
            bool_val = p.contains_points([(i+dx, j+dy)])[0]
            if bool_val:
                A = A + dA*gauss_pdf(i, j, sigma, mean)
                Cx = Cx + i*dA*gauss_pdf(i, j, sigma, mean)
                Cy = Cy + j*dA*gauss_pdf(i, j, sigma, mean)

    Cx = Cx/A
    Cy = Cy/A

    return np.array([[Cx, Cy]])

# Generates a bounded Voronoi diagram with finite regions
def bounded_voronoi(towers, bounding_box):
    # Select towers inside the bounding box
    i = in_box(towers, bounding_box)
    
    # Mirror points left, right, above, and below to provide finite regions for the edge regions
    points_center = towers[i, :]

    points_left = np.copy(points_center)
    points_left[:, 0] = bounding_box[0] - (points_left[:, 0] - bounding_box[0])

    points_right = np.copy(points_center)
    points_right[:, 0] = bounding_box[1] + (bounding_box[1] - points_right[:, 0])

    points_down = np.copy(points_center)
    points_down[:, 1] = bounding_box[2] - (points_down[:, 1] - bounding_box[2])

    points_up = np.copy(points_center)
    points_up[:, 1] = bounding_box[3] + (bounding_box[3] - points_up[:, 1])

    points = np.concatenate((points_center, points_left, points_right, points_down, points_up), axis=0)

    # Compute Voronoi
    vor = sp.spatial.Voronoi(points)

    # Store the original regions corresponding to `points_center`
    original_region_indices = vor.point_region[:len(points_center)]
    filtered_regions = [vor.regions[idx] for idx in original_region_indices if -1 not in vor.regions[idx]]

    # Assign filtered regions and points to the vor object
    vor.filtered_points = points_center
    vor.filtered_regions = filtered_regions  # This is now a list of lists

    return vor


def centroid_region(vertices):
    # Polygon's signed area
    A = 0
    # Centroid's x
    C_x = 0
    # Centroid's y
    C_y = 0
    for i in range(0, len(vertices) - 1):
        s = (vertices[i, 0] * vertices[i + 1, 1] - vertices[i + 1, 0] * vertices[i, 1])
        A = A + s
        C_x = C_x + (vertices[i, 0] + vertices[i + 1, 0]) * s
        C_y = C_y + (vertices[i, 1] + vertices[i + 1, 1]) * s
    A = 0.5 * A
    C_x = (1.0 / (6.0 * A)) * C_x
    C_y = (1.0 / (6.0 * A)) * C_y
    
    return np.array([[C_x, C_y]])

def plot_gaussian_2d(mean, sigma, xlim=(-1, 2), ylim=(-1, 2), resolution=100):
    """
    Plots a 2D Gaussian distribution over a specified range.
    
    Parameters:
    - mean: The mean of the Gaussian distribution (x, y).
    - sigma: The standard deviation of the Gaussian distribution.
    - xlim: Tuple specifying the x-axis limits (xmin, xmax).
    - ylim: Tuple specifying the y-axis limits (ymin, ymax).
    - resolution: The number of points in each axis direction for the grid (higher means smoother).
    """
    
    # Create a grid of points
    x = np.linspace(xlim[0], xlim[1], resolution)
    y = np.linspace(ylim[0], ylim[1], resolution)
    X, Y = np.meshgrid(x, y)
    
    # Calculate Gaussian values over the grid
    Z = np.array([gauss_pdf(x, y, sigma, mean) for x, y in zip(np.ravel(X), np.ravel(Y))])
    Z = Z.reshape(X.shape)
    
    # Plot the Gaussian distribution as a heatmap
    plt.contourf(X, Y, Z, levels=50, cmap='viridis')
    plt.colorbar(label='Gaussian Value')

def main():
    K_gain = 1
    PERIOD = 10
    dt = 0.1
    SENSING_TOLERANCE = 0.01


    towers = np.array([[0.8,0.9],
                        [0.6,0.75],
                        [0.1,0.5],
                        [0.6,0.25],
                        [0.5,0.3]
                    ])
    bounding_box = np.array([0., 1., 0., 1.]) # [x_min, x_max, y_min, y_max]

    plt.plot(towers[:, 0], towers[:, 1], 'b.')

    for t in np.arange(0,10,0.1):
        print(t)

        vor = bounded_voronoi(towers, bounding_box)

        # Compute and plot centroids
        plt.clf()
        centroids = []
        for region in vor.filtered_regions:
            vertices = vor.vertices[region + [region[0]], :]
            #centroid = centroid_region(vertices)  #without gaussian
            centroid = compute_centroid(vertices, 0.1, [0.6,0.6]) #with gaussian
            centroids.append(list(centroid[0, :]))
            plt.plot(centroid[:, 0], centroid[:, 1], 'r.')

        # Plot initial points
        plt.plot(vor.filtered_points[:, 0], vor.filtered_points[:, 1], 'b.')

        for region in vor.filtered_regions:
            vertices = vor.vertices[region + [region[0]], :]
            plt.plot(vertices[:, 0], vertices[:, 1], 'k-')

        plt.xlim(-0.1, 1.1)
        plt.ylim(-0.1, 1.1)

        plot_gaussian_2d(mean=(0.6,0.6), sigma=0.1, xlim=(-0.1,1.1), ylim=(-0.1,1.1))
        
        plt.pause(0.05)
        towers = vor.filtered_points

        for i in range(towers.shape[0]):
            #compute velocities
            vxy_i = -K_gain*(towers[i] - np.array(centroids[i]))
            xy_i = towers[i] + vxy_i*dt
            towers[i] = xy_i
            #towers[i] = centroids[i]


    plt.show()

def example():
    n_towers = 5
    towers = np.random.rand(n_towers, 2)
    bounding_box = np.array([0., 1., 0., 1.]) # [x_min, x_max, y_min, y_max]
    vor = bounded_voronoi(towers, bounding_box)

    fig = plt.figure()
    ax = fig.gca()
    # Plot initial points
    ax.plot(vor.filtered_points[:, 0], vor.filtered_points[:, 1], 'b.')
    # Plot ridges points
    #for region in vor.filtered_regions:
    #    vertices = vor.vertices[region, :]
    #    ax.plot(vertices[:, 0], vertices[:, 1], 'go')
    # Plot ridges
    for region in vor.filtered_regions:
        vertices = vor.vertices[region + [region[0]], :]
        ax.plot(vertices[:, 0], vertices[:, 1], 'k-')
    # Compute and plot centroids
    centroids = []
    for region in vor.filtered_regions:
        vertices = vor.vertices[region + [region[0]], :]
        centroid = centroid_region(vertices)
        centroids.append(list(centroid[0, :]))
        ax.plot(centroid[:, 0], centroid[:, 1], 'r.')

    ax.set_xlim([-0.1, 1.1])
    ax.set_ylim([-0.1, 1.1])
    plt.savefig("bounded_voronoi.png")

    #sp.spatial.voronoi_plot_2d(vor)
    #plt.savefig("voronoi.png")

if __name__ == "__main__":
    main()