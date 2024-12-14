import json

def parse_map(json_path):
    """
    Parse a JSON file containing a 2D array of integers.
    The JSON file should contain a 2D array of integers, where each integer represents a weight.
    The function returns a dictionary with the coordinates of the non-zero weights as keys and the weights as values.
    The function also returns the dimensions of the 2D array as a tuple (rows, columns).
    """
    
    with open(json_path, 'r') as file:
        data = json.load(file)
    
    result = {}
    for row_index, row in enumerate(data):
        for col_index, value in enumerate(row):
            if value != 0:
                result[(row_index, col_index)] = value
    
    dimensions = (len(data), len(data[0]) if data else 0)
    return result, dimensions


# test usage:
if __name__ == '__main__':
    import os
    import json

    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'map_generator', 'map.json'))
    parsed_data, dimensions = parse_map(json_path)
    print(parsed_data)
    print("Dimensions:", dimensions)

    # Extract coordinates and weights
    coordinates = list(parsed_data.keys())
    weights = list(parsed_data.values())

    print("Coordinates:", coordinates)
    print("Weights:", weights)