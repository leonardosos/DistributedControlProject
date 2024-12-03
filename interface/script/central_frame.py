'''
This module contains the CentralFrame class, which is a custom tkinter frame that contains the MatrixButton class.



'''

from math import e
import os
import json
from turtle import color
import customtkinter
import ast # To convert string to tuple


class CentralFrame(customtkinter.CTkFrame):
    """Central Frame that contain the frame matrix of buttons with the related padding"""

    def __init__(self, master, font_size=16):
        super().__init__(master)

        self.matrix_button = MatrixButton(self, font_size)
        self.matrix_button.grid(padx=10, pady=10)


class MatrixButton(customtkinter.CTkFrame):
    """Frame containing a matrix of buttons."""

    def __init__(self, master, font_size):
        super().__init__(master)

        # Set the font size for the button funcionality
        self.font_size = font_size

        # Load the map matrix from JSON
        current_dir = os.path.dirname(os.path.abspath(__file__))
        map_json_path = os.path.join(current_dir, '../../map_generator/map.json')
        with open(map_json_path, 'r') as file:
            self.map_matrix = json.load(file)

        # Track the currently hovered button and clicked button
        self.current_hovered_button = None
        self.last_clicked_button = None
        self.hide_text_timer = None  # For tracking the delay

        # Create the matrix of buttons
        self.create_matrix_of_buttons()

    def create_matrix_of_buttons(self):
        """Create the matrix of buttons based on loaded data."""

        # Find the dimensions of the matrix loaded
        rows = len(self.map_matrix)
        cols = len(self.map_matrix[0])

        # Store buttons to access them for hover effects
        self.buttons = []  

        # Iterate through the matrix to create buttons
        for i in range(rows):
            row_buttons = []
            for j in range(cols):
                
                # FOR EACH BUTTON
                # Retrieve the value from the matrix 
                value = self.map_matrix[i][j]

                # Map the value to a color 
                bg_color = self.map_value_to_color(value)

                # Create button 
                button = customtkinter.CTkButton(self,
                                                 text='',  #f'{i},{j}', # Show the coordinates on the button
                                                 font=(None, self.font_size),
                                                 border_width=1,
                                                 border_color="black",
                                                 command=lambda i_=i, j_=j: self.matrix_button_callback(i_, j_),
                                                 width=70,  # Keep multiple of 10 otherwise apper a line between buttons
                                                 height=70,  # Keep multiple of 10 otherwise apper a line between buttons
                                                 corner_radius=0,
                                                 fg_color=bg_color,
                                                 hover=False)
                button.grid(row=i, column=j, padx=0, pady=0)

                # Bind hover events: showing value on enter and hiding with a delay
                button.bind("<Enter>", lambda event, btn=button: self.hover_enter(btn))

                row_buttons.append(button)
            self.buttons.append(row_buttons)

    def hover_enter(self, button):
        """Called when the mouse enters a new button."""

        # Get the matrix value and coordinates of the button
        row, col = button.grid_info()["row"], button.grid_info()["column"]
        value = self.map_matrix[row][col]

        # Hide the value of the previously hovered button, if any
        if self.current_hovered_button and self.current_hovered_button != button:
            self.hide_value(self.current_hovered_button)

        # Show the value for the currently hovered button
        if value >= 0:
            button.configure(text=str(value), fg_color="#00008B")  # Dark Blue for hovering
        else:
            button.configure(text="ON", fg_color="#00008B")  # mission in progress

        # Update the right frame with the hovered coordinates and value
        row, col = button.grid_info()["row"], button.grid_info()["column"]
        self.master.master.right_frame.update_info(row, col, value)

        # Update the current hovered button
        self.current_hovered_button = button

        # Cancel any previous scheduled value hiding due to timeout
        if self.hide_text_timer:
            self.after_cancel(self.hide_text_timer)

        # Schedule to hide the value after 1 second of inactivity
        self.hide_text_timer = self.after(1500, lambda: self.hide_value(button))

    def hide_value(self, button):
        """Hide the value on the button after timeout or hover loss."""
        # Don't hide the value if the button is the one currently selected/clicked
        if button == self.last_clicked_button:
            if self.last_clicked_value >= 0:
                button.configure(text=str(self.last_clicked_value), fg_color="red")
            else:
                button.configure(text="ON", fg_color="red")
            return

        # Reset value and background color when the hover ends or timeout happens
        row, col = button.grid_info()["row"], button.grid_info()["column"]
        original_color = self.map_value_to_color(self.map_matrix[row][col])
        button.configure(text='', fg_color=original_color)

        # No button is hovered anymore if it's hidden due to timeout
        if button == self.current_hovered_button:
            self.current_hovered_button = None
            self.hide_text_timer = None

    def map_value_to_color(self, value):
        """Return a color depending on the matrix value."""

        if value == 0:
            return "#4478C6"  # Blue for value 0
        elif value == -1:
            return "yellow"
        else:
            # Convert value into grayscale, where higher values are darker
            gray_value = int(255 - (value / 100) * 255)
            return f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"

    def matrix_button_callback(self, row, col):
        """Handle button click events. 
        This update the left frame with the selected coordinates and value, and reset the previous button's appearance."""

        # Unlock the left frame when a button is clicked
        self.master.master.left_frame.unlock_frame()

        # If there is already a clicked button, reset the previous button's appearance
        if self.last_clicked_button:
            last_row, last_col = self.last_clicked_button.grid_info()["row"], self.last_clicked_button.grid_info()["column"]
            original_color = self.map_value_to_color(self.map_matrix[last_row][last_col])
            self.last_clicked_button.configure(text='', fg_color=original_color)

        # Show the value and change background to red on the clicked button
        target_button = self.grid_slaves(row=row, column=col)[0]
        value = self.map_matrix[row][col]
        if value >= 0:
            target_button.configure(text=str(value), fg_color="red")  # Red for selected state
        else:
            target_button.configure(text="ON", fg_color="red")  # mission in progress

        # Keep track of the currently clicked button
        self.last_clicked_button = target_button
        # Keep track of the garbage value
        self.last_clicked_value = self.map_matrix[row][col]

        # Print and log the selected coordinates
        if value >= 0:
            text_ = f"Selected coordinates: ({row}, {col}), with {value} % of garbage"
            self.master.master.button_frame.log_frame.add_text(text_)
            print(text_)
        else:
            text_ = f"Selected coordinates: ({row}, {col}) is a mission in progress"
            self.master.master.button_frame.log_frame.add_text(text_)
            print(text_)

        # Update the coordinate box in the left frame
        self.master.master.left_frame.update_coordinate_box(row, col)

        # Update the spinbox in the left frame with the adviced value of vessel
        self.master.master.left_frame.update_spinbox_vessel_counter()

        # Update the advice box in the right frame with the adviced value of vessel
        self.master.master.left_frame.advice_box.delete(0, "end")
        if value >= 0:
            self.master.master.left_frame.advice_box.insert(0, f"{value//20}")
        else:          
            self.master.master.left_frame.advice_box.insert(0, "0")
        
    def clean_button(self, id_mission):
        """Clean the button by setting its value to 0 and changing its color to the default blue."""
        
        coordinates_tuple = ast.literal_eval(self.master.master.mission_info[id_mission]["coordinates"])        
        row,col = coordinates_tuple[0], coordinates_tuple[1]

        # Update the map matrix to set the value to 0
        self.map_matrix[row][col] = 0

        # Get the button at the specified row and column
        button = self.grid_slaves(row=row, column=col)[0]

        # Update the button's appearance
        button.configure(text='')  # Remove the text
        button.configure(fg_color="#4478C6")  # Blue for value 0

        # Reset tracking variables and cancel any pending hover timeout
        if button == self.current_hovered_button:
            self.current_hovered_button = None
        if button == self.last_clicked_button:
            self.last_clicked_button = None
        if self.hide_text_timer:
            self.after_cancel(self.hide_text_timer)
            self.hide_text_timer = None

        # Re-bind the hover events for the cleaned button
        button.bind("<Enter>", lambda event, btn=button: self.hover_enter(btn))

        # Print and log the updated matrix value for debugging
        text_ = f"Updated matrix value at ({row}, {col}): {self.map_matrix[row][col]} after cleaning"
        self.master.master.button_frame.log_frame.add_text(text_)
        print(text_)

    def color_mission_in_progress(self, id_mission):
        """Color the button by setting its value to -1 and changing its color to yellow."""

        coordinates_tuple = ast.literal_eval(self.master.master.mission_info[id_mission]["coordinates"])        
        row,col = coordinates_tuple[0], coordinates_tuple[1]

        # Update the map matrix to set the value to 0
        self.map_matrix[row][col] = -1

        # Get the button at the specified row and column
        button = self.grid_slaves(row=row, column=col)[0]

        # Update the button's appearance
        button.configure(text='')  # Remove the text
        button.configure(fg_color="yellow")  # Blue for value 0

        # Reset tracking variables and cancel any pending hover timeout
        if button == self.current_hovered_button:
            self.current_hovered_button = None
        if button == self.last_clicked_button:
            self.last_clicked_button = None
        if self.hide_text_timer:
            self.after_cancel(self.hide_text_timer)
            self.hide_text_timer = None

        # Re-bind the hover events for the cleaned button
        button.bind("<Enter>", lambda event, btn=button: self.hover_enter(btn))        

# Test the central frame class
if __name__ == "__main__":
    app = customtkinter.CTk()
    central_frame = CentralFrame(app)

    central_frame.grid(row=1, column=1, padx=10, pady=10)


    app.mainloop()