# Distributed Control Interface Project

## Overview
This is a part of a project for the Distributed Control Systems course at the University of Modena and Reggio Emilia (UNIMORE). 
The goal is to create a custom interface to interact with an autonomous vessel float, which is controlled by a distributed control system. The interface allows the user to visualize the discrete map and send a group of agents to a specific location for a cleaning task. 

![Screenshot of the Interface](images/screenshot.png)

## Authors
This part of the project was developed by:
- [Leonardo Brighenti]

## Technical Skills
The project is developed using Python and leverages the `customtkinter` library to create custom widgets and the graphical user interface (GUI). (`customtkinter` is an enhanced version of the standard Tkinter library.)

The codebase follows the object-oriented programming (OOP) paradigm, ensuring modularity and scalability.

## Folder Structure

The repository contain two main components: the map generator and the custom interface.

### 1. `map_generator`
This folder contains the code to create a matrix that defines a map with a fixed seed. It generates both a plot and a JSON file that can be shared with other applications. The generated files are saved within this folder.

![Discretized map of the environment](images/map.png)

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
