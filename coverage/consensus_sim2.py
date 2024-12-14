'''





PROF EXAMPLE





'''


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import networkx as nx

# Define a class for a single robot
class Robot:
    def __init__(self, x, y):
        # Initialize the robot's position
        self.position = np.array([x, y])

# Define a class for a team of robots
class RobotTeam:
    def __init__(self, n_robots, space_size):
        # Initialize the robots with random positions within the given space size
        self.robots = [Robot(np.random.uniform(0, space_size), np.random.uniform(0, space_size)) 
                       for _ in range(n_robots)]
        self.n_robots = n_robots
        self.space_size = space_size
        # Create the Laplacian matrix for the robot team
        self.laplacian = self.create_laplacian()

    def create_laplacian(self):
        # Create a fully connected graph adjacency matrix
        adjacency = np.ones((self.n_robots, self.n_robots)) - np.eye(self.n_robots)
        # Create the degree matrix
        degree = np.diag(np.sum(adjacency, axis=1))
        # Return the Laplacian matrix
        return degree - adjacency

    def update_positions(self):
        # Get the current positions of all robots
        positions = np.array([robot.position for robot in self.robots])
        # Update positions based on the Laplacian matrix
        #This line is the core of the consensus algorithm. It implements the equation: x(t+1) = x(t) - ε * L * x(t)
        new_positions = positions - 0.01 * np.dot(self.laplacian, positions)
        # Assign the new positions back to the robots
        for i, robot in enumerate(self.robots):
            robot.position = new_positions[i]

    def get_positions(self):
        # Return the current positions of all robots
        return np.array([robot.position for robot in self.robots])

# Function to animate the robot positions and connectivity graph
def animate(frame):
    # Update the positions of the robots
    team.update_positions()
    # Get the updated positions
    positions = team.get_positions()
    # Update the scatter plot with new positions
    scatter.set_offsets(positions)
    
    # Update graph node positions
    pos = {i: position for i, position in enumerate(positions)}
    nx.draw(G, pos, ax=ax2, node_color='lightblue', with_labels=True, node_size=300)
    ax2.set_title("Robot Connectivity Graph")
    return scatter,

# Set up the simulation parameters
n_robots = 5
space_size = 10
# Create a team of robots
team = RobotTeam(n_robots, space_size)

# Set up the plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
# Initialize the scatter plot for robot positions
scatter = ax1.scatter([], [], s=100)
ax1.set_xlim(0, space_size)
ax1.set_ylim(0, space_size)
ax1.set_title("Robot Positions")

# Create a complete graph for the robot connectivity
G = nx.complete_graph(n_robots)
nx.draw(G, ax=ax2, node_color='lightblue', with_labels=True, node_size=300)

# Create the animation
anim = FuncAnimation(fig, animate, frames=200, interval=50, blit=False)

# Adjust layout and display the plots
plt.tight_layout()
plt.show()