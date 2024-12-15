import numpy as np
import os
import json

# --- Function: Compute start position ---
def compute_center_position(number_of_cells ,map_folder, map_name):  
    '''
    This function computes the center of mass based on the map.
    '''

    # Load the map data
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', map_folder, map_name))
    with open(json_path, 'r') as file:
        data = json.load(file)

    if number_of_cells != len(data) or number_of_cells != len(data[0]):
        raise ValueError("The number of cells must match the dimensions of the map.")

    # Convert to a NumPy array for easier computations
    grid = np.array(data)

    # Get the number of rows and columns
    rows, cols = grid.shape

    # Initialize variables
    sum_mass = 0  # Total mass
    sum_x = 0  # Weighted sum of row indices
    sum_y = 0  # Weighted sum of column indices

    # Loop through each cell in the grid
    for x in range(rows):
        for y in range(cols):
            mass = grid[x][y]
            if mass != 0:  # Only account for non-zero masses
                sum_mass += mass
                sum_x += mass * x
                sum_y += mass * y

    # Check if there's any mass at all (to avoid division by zero)
    if sum_mass == 0:
        print("No mass found in the grid.")
    else:
        # Calculate the center of mass as floating-point values
        com_x = sum_x / sum_mass  # Center of mass (row)
        com_y = sum_y / sum_mass  # Center of mass (column)

        # Round to the nearest integer to get discrete row and column indices
        discrete_row = round(com_x)
        discrete_col = round(com_y)

    return (discrete_row, discrete_col)




# Test the function
if __name__ == '__main__':
    # Test the function with example data
    number_of_cells = 10

    map_folder = 'map_generator'
    map_name = 'map.json'
    print(compute_center_position(number_of_cells, map_folder, map_name))