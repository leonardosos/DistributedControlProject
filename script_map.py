import random
import json
import matplotlib.pyplot as plt
import numpy as np

map_seed = 91901 # Seed for reproducibility
random.seed(map_seed)

def generate_random_value(min_val=10, max_val=100):
    """Generates a random integer between min_val and max_val."""
    return random.randint(min_val, max_val)

def create_matrix(rows, cols, num_values, seed=map_seed):
    """Creates a matrix of size rows x cols filled with zeros and populates it with num_values random integers at random unique positions."""
    matrix = [[0 for _ in range(cols)] for _ in range(rows)]
    
    total_cells = rows * cols
    if num_values > total_cells:
        raise ValueError("Number of random values exceeds total number of cells in the matrix.")
    
    positions = set()
    while len(positions) < num_values:
        x, y = random.randint(0, rows - 1), random.randint(0, cols - 1)
        positions.add((x, y))
    
    for (x, y) in positions:
        matrix[x][y] = generate_random_value()
    
    return matrix

def save_matrix_to_json(matrix, filename='map.json'):
    """Saves the matrix to a JSON file with each row on a single line."""
    with open(filename, 'w') as file:
        formatted_matrix = "[\n" + ",\n".join("    " + str(row) for row in matrix) + "\n]"
        file.write(formatted_matrix)
    print(f"Matrix saved to {filename} in compact row format")

def plot_matrix(matrix):
    """Plots the matrix as a heatmap using matplotlib."""
    # Convert the matrix to a numpy array for easier plotting
    matrix_np = np.array(matrix)
    
    plt.figure(figsize=(8, 8))
    plt.imshow(matrix_np, cmap="Blues", interpolation="none")
    plt.colorbar(label="Value")
    plt.title("Matrix Visualization")
    plt.xlabel("Columns")
    plt.ylabel("Rows")
    
    # Display the plot
    plt.show()

def main():
    rows, cols, num_values = 10, 10, 5  # Example values for customization
    matrix = create_matrix(rows, cols, num_values)
    save_matrix_to_json(matrix)
    plot_matrix(matrix)

if __name__ == "__main__":
    main()
