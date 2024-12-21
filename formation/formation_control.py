'''
This script controls the formation of a team of robots.

The robots are controlled to maintain a specific formation while navigating through a given space.

The robot positions are updated and visualized in real-time using Matplotlib's FuncAnimation.

The script also includes options for saving the simulation output to a file and generating Coppelia-like output.
'''

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import networkx as nx
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from coverage.voronoi_vessel_print import SAVE_TO_FILE, apply_offset, decuple_robot_positions, save_positions_to_file, simulation_revert_axis
from map_analysis.conversion_map import index2coord


# Set the parameters for the simulation
PLOT_SIM = False
PLOT_TRAJECTORY = True
COPPELIA_OUTPUT = True  # Coppelia-like output
SAVE_TO_FILE = True


# Define the Robot class
class Robot:
    def __init__(self, x, y):
        self.position = np.array([x, y])

# Define the RobotTeam class
class RobotTeam:
    def __init__(self, n_robots, space_size, waypoints, rradius):
        self.n_robots = n_robots
        self.space_size = space_size
        self.waypoints = waypoints
        self.current_waypoint_index = 0
        self.rradius = rradius
        self.target_achieved = False

        # Laplacian Matrix for formation
        self.laplacian = self.create_laplacian()

        # Formation offsets (pentagon arrangement)
        angle = 2 * np.pi / n_robots
        self.target_offsets = [np.array([np.cos(i * angle), np.sin(i * angle)]) * rradius for i in range(n_robots)]

        # Initialize robots in a pentagonal formation with leader at origin
        self.robots = self.initialize_pentagonal_formation()

    def initialize_pentagonal_formation(self):
        """
        Initializes the robots in a pentagonal formation centered around the leader.
        """
        robots = []
        leader_start_pos = self.waypoints[0]
        for i, offset in enumerate(self.target_offsets):
            if i == 0:
                # Place the leader at the first waypoint
                robots.append(Robot(leader_start_pos[0], leader_start_pos[1]))
            else:
                # Followers in pentagonal formation relative to the leader
                follower_pos = leader_start_pos + offset
                robots.append(Robot(follower_pos[0], follower_pos[1]))
        return robots

    def create_laplacian(self):
        """
        Creates the Laplacian matrix for a fully connected graph.
        """
        # Fully connected graph adjacency matrix
        adjacency = np.ones((self.n_robots, self.n_robots)) - np.eye(self.n_robots)
        # Degree matrix
        degree = np.diag(np.sum(adjacency, axis=1))
        # Laplacian matrix
        return degree - adjacency

    def update_leader_position(self):
        """
        Updates the leader's position to move towards the next waypoint.
        """
        leader = self.robots[0]  # The leader is robot 0
        if self.current_waypoint_index < len(self.waypoints):
            target = self.waypoints[self.current_waypoint_index]
            direction = target - leader.position
            distance_to_target = np.linalg.norm(direction)

            # Move leader towards the waypoint
            if distance_to_target < 0.1:
                self.current_waypoint_index += 1  # Switch to the next waypoint
            else:
                direction_norm = direction / distance_to_target if distance_to_target > 0 else np.zeros(2)
                leader.position += 0.04 * direction_norm  # Leader moves with a small gain
        else:
            self.target_achieved = True
            
    def update_follower_formation(self):
        """
        Updates the positions of follower robots using Laplacian consensus 
        and the desired pentagonal formation control inputs.
        """
        # Get the current positions of all robots
        positions = np.array([robot.position for robot in self.robots])
        
        # Calculate the formation control input with Laplacian influence
        formation_input = np.zeros_like(positions)
        for i in range(self.n_robots):
            for j in range(self.n_robots):
                if i != j:
                    # Current position difference
                    current_diff = positions[j] - positions[i]
                    # Desired position difference based on pentagonal formation offsets
                    desired_diff = self.target_offsets[j] - self.target_offsets[i]
                    # Formation control contribution from j to i
                    formation_input[i] += current_diff - desired_diff

        # Scale down the control input for stability (gain adjustment)
        formation_input *= 0.6  # Reduce the influence scale to avoid overshooting

        # Update followers' positions using Laplacian-driven consensus
        new_positions = positions - 0.3 * (np.dot(self.laplacian, positions) + formation_input)
        
        # Assign updated positions back to the robots (followers only)
        for i in range(1, self.n_robots):  # Skip updating the leader at index 0
            self.robots[i].position = new_positions[i]

    def update_positions(self):
        """
        Updates positions of both the leader and follower robots.
        """
        self.update_leader_position()
        self.update_follower_formation()

    def get_positions(self):
        """
        Returns the positions of all robots as a numpy array.
        """
        return np.array([robot.position for robot in self.robots])

# Function to animate the robot positions and connectivity graph
def animate(frame):
    ax1.clear()
    ax2.clear()

    # Add grid
    ax1.set_xticks(np.arange(0, team.space_size + 1, team.space_size / number_of_cells))
    ax1.set_yticks(np.arange(0, team.space_size + 1, team.space_size / number_of_cells))
    ax1.grid(True)

    # Update the positions of the robots
    team.update_positions()
    # Get the updated positions
    positions = team.get_positions()
    # Plot the robots
    ax1.set_xlim(0, team.space_size)
    ax1.set_ylim(0, team.space_size)
    ax1.set_title("Robot Positions")
    ax1.plot(waypoints[:, 0], waypoints[:, 1], 'k--', label='Waypoints')  # Plot the waypoints
    ax1.scatter(positions[:, 0], positions[:, 1], c='blue', s=50)
    ax1.scatter(positions[0, 0], positions[0, 1], c='red', s=50, label='Leader')  # Leader in red
    ax1.legend()

    # Draw connectivity graph
    G = nx.Graph()
    G.add_nodes_from(range(team.n_robots))
    pos_dict = {i: positions[i] for i in range(team.n_robots)}
    node_colors = ['red'] + ['blue'] * (team.n_robots - 1)
    G.add_edges_from([(i, j) for i in range(team.n_robots) for j in range(i + 1, team.n_robots)])
    nx.draw(G, pos=pos_dict, ax=ax2, node_color=node_colors, with_labels=True, node_size=300)
    ax2.set_title("Robot Connectivity Graph")
    ax2.set_xlim(pos_dict[0][0] - 3, pos_dict[0][0] + 3)
    ax2.set_ylim(pos_dict[0][1] - 3, pos_dict[0][1] + 3)


def generate_zigzag(rows, cols):
    """
    Generates a zigzag path for the leader to follow in a grid.
    """
    zigzag_path = []
    for col in range(cols):
        if col % 2 == 0:  # Even column: top-to-bottom
            for row in range(rows):
                zigzag_path.append([row, col])
        else:  # Odd column: bottom-to-top
            for row in range(rows - 1, -1, -1):
                zigzag_path.append([row, col])
    return zigzag_path

def plot_trajectory(positions_over_time):
    """
    Plots the trajectory of the robots over time with waypoints.
    """

    positions_over_time = np.array(positions_over_time)
    plt.figure(figsize=(8, 8))
    plt.plot(waypoints[:, 0], waypoints[:, 1], 'k--', label='Waypoints')  # Plot the waypoints
    plt.scatter(positions_over_time[:, 0, 0], positions_over_time[:, 0, 1], c='red', s=50, label='Leader')  # Leader in red
    for i in range(1, n_robots):
        plt.plot(positions_over_time[:, i, 0], positions_over_time[:, i, 1], label=f'Robot {i+1}')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Robot Trajectories')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

# Set up the simulation parameters
n_robots = 5  # Number of robots (pentagon has 5 vertices)
sim_dimensions = 35.0
number_of_cells = 10
cell_dimension = 3.5
radius = cell_dimension / 5

# Generate a zigzag path for the leader to follow
index_path = generate_zigzag(number_of_cells, number_of_cells)

# Generate a zigzag path for the leader to follow
index_path = generate_zigzag(number_of_cells, number_of_cells)

# Convert the zigzag path to coordinates
coord_path = list()
for index in index_path:
    coord = index2coord(cell_dimension, number_of_cells, index[0], index[1])
    coord_shift = np.zeros(2)
    coord_shift[0] = - cell_dimension/4 + coord[0]
    coord_shift[1] = coord[1]
    coord_path.append(coord_shift)

# Define waypoints for the leader to follow
waypoints = np.array(coord_path)

# Create a team of robots
team = RobotTeam(n_robots, sim_dimensions, waypoints, radius)

# Animation of the simulation
if PLOT_SIM:
    # Set up the plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    ax1.set_aspect('equal')
    ax2.set_aspect('equal')

    # Create the animation
    anim = FuncAnimation(fig, animate, frames=500, interval=50)

    # Show the animation
    plt.tight_layout()
    plt.show()

# Run the simulation and store the positions over time
positions_over_time = []
positions_over_time.append(team.get_positions().copy())

for i in range(50000):
    # Update the positions of the robots
    team.update_positions()
    # Get the updated positions
    positions = team.get_positions()
    positions_over_time.append(positions.copy())  

    if team.target_achieved:
        print("Target achieved!")
        break  

if PLOT_TRAJECTORY: plot_trajectory(positions_over_time)

if COPPELIA_OUTPUT: 
    # Apply offset to the positions for coppelia zero
    positions_over_time = apply_offset(positions_over_time, offset=[cell_dimension/2, cell_dimension/2])

    # Revert the axis and plot the trajectory of the robots over time
    positions_over_time = simulation_revert_axis(positions_over_time, number_of_cells, cell_dimension, sim_dimensions)

if SAVE_TO_FILE: 
    list_of_positions = decuple_robot_positions(positions_over_time)  

    # Save the positions to a JSON file for each vessel
    count = 0
    for i in list_of_positions:
        count += 1  
        save_positions_to_file(i, f'PATH_to_follow/drone_{count}_positions.json', single_position=True)
