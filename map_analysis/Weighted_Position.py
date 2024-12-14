'''
This module contains the function find_best_position(grid_size, areas, weights)
that finds the best position in a grid for be closer to the areas with garbage,
this is compute using the Manhattan distance and weighting the distance with the
weights of the areas.
'''


def find_best_position(grid_size, areas, weights):
    """
    Find the best position in a grid to be close to the specified areas.

    Args:
        grid_size (int): Size of the grid (e.g., 10 for 10x10).
        areas (list of tuple): List of coordinates of the areas with a weight value [(x1, y1), (x2, y2), ...].
        weights (list of int): List of weights associated with the areas.

    Returns:
        tuple: The best position (i, j) and the minimum total distance.
    """

    best_position = None
    min_distance = float('inf')

    for i in range(grid_size):
        for j in range(grid_size):
            # Calcola la distanza totale (Manhattan) pesata
            total_distance = sum(weights[k] * (abs(i - x) + abs(j - y)) for k, (x, y) in enumerate(areas))

            # Trova la posizione con distanza minima
            if total_distance < min_distance:
                min_distance = total_distance
                best_position = (i, j)

    return best_position, min_distance


if __name__ == '__main__':
    # Test of find_best_position
    grid_size = 10
    areas = [(0, 0), (2, 3), (5, 7)]
    weights = [1, 2, 3]

    best_position, min_distance = find_best_position(grid_size, areas, weights)
    print(f"Best Position: {best_position}, Min Distance: {min_distance}")