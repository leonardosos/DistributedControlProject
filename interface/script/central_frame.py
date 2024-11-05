import os
import json
import customtkinter




class CentralFrame(customtkinter.CTkFrame):
    """Central Frame with matrix of button"""

    def __init__(self, master):
        super().__init__(master)

        self.matrix_button = MatrixButton(self)
        self.matrix_button.grid(row=0, column=0,padx=10, pady=(10,0), sticky="ew")

'''
        self.textbox = customtkinter.CTkTextbox(master=self, height=20)
        self.textbox.insert("0.0", "Legenda: black - occupied, white - free, grey - percentage of gargabe, red - selected")
        self.textbox.configure(state="disabled")
        self.textbox.grid(row=1, column=0, padx=10, pady=(5,10), sticky="ew")
'''


class MatrixButton(customtkinter.CTkFrame):
    """Matrix of buttons"""
    
    def __init__(self, master):
        super().__init__(master)

        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Build the path to map.json
        map_json_path = os.path.join(current_dir, '../../map_generator/map.json')

        # Read the map from file
        with open(map_json_path, 'r') as file:
            self.map_matrix = json.load(file)

        # Create the matrix of buttons based on the loaded matrix
        self.create_matrix_of_buttons()

    def create_matrix_of_buttons(self):
        rows = len(self.map_matrix)
        cols = len(self.map_matrix[0]) if rows > 0 else 0

        # Print the size of the matrix
        print(f"Matrix size: {rows}x{cols}")

        for i in range(rows):
            for j in range(cols):
                value = self.map_matrix[i][j]
                bg_color = self.map_value_to_color(value)

                button = customtkinter.CTkButton(self,
                                                 text='',#f"({i},{j})",
                                                 border_width=1,
                                                 border_color="black",
                                                 command=lambda i_=i, j_=j: self.matrix_button_callback(i_, j_),
                                                 width=50,
                                                 height=50,
                                                 corner_radius=0,
                                                 fg_color=bg_color)  # Set background color
                button.grid(row=i, column=j, padx=0, pady=0)

    def map_value_to_color(self, value):
        if value == 0:
            return "#4478C6"  # White for 0
        else:
            # Calculate grayscale based on the value (1 to 100)
            gray_value = int(255 - (value / 100) * 255)  # Scale 0-100 to 255-0
            return f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"  # Convert to hex

    def matrix_button_callback(self, row, col):
        print(f"Matrix Button clicked at ({row}, {col})")

