import matplotlib.pyplot as plt
import numpy as np


def index2coord(cell_dimension, number_of_cells, row, col):
    '''
    Converts a grid index (matrix-like) with origin at top-left
    to 2D Cartesian coordinates with origin in bottom-left -->
        --> ZERO ON THE CORNER OF THE CELL <-- .
    
    Parameters:
        cell_dimension (float): The size of one cell (length of one side of a square cell).
        number_of_cells (int): The number of cells along one grid dimension (assumes square grid).
        row (int): The row index (matrix-like, starting from 0 at the top).
        col (int): The column index (matrix-like, starting from 0 at the left).

    Returns:
        (x, y): A tuple of real-world Cartesian coordinates (center of the cell).
    '''
    # x-coordinate: col * cell_dimension + offset to the center of the cell
    x = col * cell_dimension + cell_dimension / 2

    # y-coordinate: flip y-axis by subtracting row from (number_of_cells - 1)
    step_cell = number_of_cells - 1  # Max matrix row index
    y = (step_cell - row) * cell_dimension + cell_dimension / 2

    return (x, y)

def index2coord2offset(cell_dimension, number_of_cells, row, col):
    '''
    Converts a grid index (matrix-like) with origin at top-left
    to 2D Cartesian coordinates with origin in bottom-left -->
        --> ZERO ON CENTER THE CELL <-- .
    
    Parameters:
        cell_dimension (float): The size of one cell (length of one side of a square cell).
        number_of_cells (int): The number of cells along one grid dimension (assumes square grid).
        row (int): The row index (matrix-like, starting from 0 at the top).
        col (int): The column index (matrix-like, starting from 0 at the left).

    Returns:
        (x, y): A tuple of real-world Cartesian coordinates (center of the cell).
    '''
    # x-coordinate: col * cell_dimension + offset to the center of the cell
    x = col * cell_dimension 

    # y-coordinate: flip y-axis by subtracting row from (number_of_cells - 1)
    step_cell = number_of_cells - 1  # Max matrix row index
    y = (step_cell - row) * cell_dimension 

    return (x, y)

def plot_grid_map(cell_dimension, number_of_cells, highlight_cell=None):
    '''Plots the grid map and highlights a specific cell if provided.'''
    fig, ax = plt.subplots()
    grid_size = cell_dimension * number_of_cells

    # Draw grid lines
    for i in range(number_of_cells + 1):
        ax.plot([i * cell_dimension, i * cell_dimension], [0, grid_size], color='black')
        ax.plot([0, grid_size], [i * cell_dimension, i * cell_dimension], color='black')

    # Highlight a specific cell if provided
    if highlight_cell:
        row, col = highlight_cell
        rect = plt.Rectangle((col * cell_dimension, (number_of_cells - 1 - row) * cell_dimension), 
                             cell_dimension, cell_dimension, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
        ax.text(col * cell_dimension + cell_dimension / 2, (number_of_cells - 1 - row) * cell_dimension + cell_dimension / 2, 
                f'({row}, {col})', ha='center', va='center', color='blue', fontsize=12)

    ax.set_aspect('equal')
    plt.xlim(0, grid_size)
    plt.ylim(0, grid_size)
    plt.show()

if __name__ == '__main__':
    cell_dimension = 10
    number_of_cells = 10
    index = [5, 4]
    print(index2coord(cell_dimension, number_of_cells, index[0], index[1]))
    plot_grid_map(cell_dimension, number_of_cells, highlight_cell=index)