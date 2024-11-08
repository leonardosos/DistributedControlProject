# Distributed Control Project

This project is designed to facilitate distributed control systems. It consists of two main components: the map generator and the custom interface.

## Folder Structure

### 1. `map_generator`
This folder contains the code to create a matrix that defines a map with a fixed seed. It generates both a plot and a JSON file that can be shared with other applications. The generated files are saved within this folder.

#### Requirements
To install the necessary dependencies for the `map_generator`, run:
```bash
pip install -r map_generator/requirements.txt
```

### 2. `interface`
This folder contains the custom interface built using `customtkinter`. It provides a user-friendly interface to interact with the distributed control system.

#### Requirements
To install the necessary dependencies for the `interface`, run:
```bash
pip install -r interface/requirements.txt
```

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DistributedControlProject.git
cd DistributedControlProject
```

2. Install the requirements for each component as described above.

3. Run the map generator:
```bash
python map_generator/generate_map.py
```
or use the map.json already present in the folder

4. Launch the interface:
```bash
python interface/main.py
```
