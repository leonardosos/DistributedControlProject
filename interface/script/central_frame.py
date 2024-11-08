import os
import json
import customtkinter

class CentralFrame(customtkinter.CTkFrame):
    """Central Frame that contain the frame matrix of buttons"""

    def __init__(self, master):
        super().__init__(master)

        self.matrix_button = MatrixButton(self)
        self.matrix_button.grid(padx=10, pady=10)

class MatrixButton(customtkinter.CTkFrame):
    """Frame containing a matrix of buttons."""

    def __init__(self, master):
        super().__init__(master)

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
        rows = len(self.map_matrix)
        cols = len(self.map_matrix[0])

        self.buttons = []  # Store buttons to access them for hover effect

        # Iterate through the matrix to create buttons
        for i in range(rows):
            row_buttons = []
            for j in range(cols):
                value = self.map_matrix[i][j]
                bg_color = self.map_value_to_color(value)

                # Create button without any text initially, and configure border and colors
                button = customtkinter.CTkButton(self,
                                                 text='',
                                                 border_width=1,
                                                 border_color="black",
                                                 command=lambda i_=i, j_=j: self.matrix_button_callback(i_, j_),
                                                 width=60,
                                                 height=60,
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
        button.configure(text=str(value), fg_color="#00008B")  # Dark Blue for hovering

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
            button.configure(text=str(self.last_clicked_value), fg_color="red")
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
        """Map matrix values to colors."""
        # Return a color depending on the matrix value
        if value == 0:
            return "#4478C6"  # Blue for value 0
        else:
            # Convert value into grayscale, where higher values are darker
            gray_value = int(255 - (value / 100) * 255)
            return f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"

    def matrix_button_callback(self, row, col):
        """Handle button click events."""
        # If there is already a clicked button, reset it
        if self.last_clicked_button:
            last_row, last_col = self.last_clicked_button.grid_info()["row"], self.last_clicked_button.grid_info()["column"]
            original_color = self.map_value_to_color(self.map_matrix[last_row][last_col])
            self.last_clicked_button.configure(text='', fg_color=original_color)

        value = self.map_matrix[row][col]

        # Show the value and change background to red on the clicked button
        target_button = self.grid_slaves(row=row, column=col)[0]
        target_button.configure(text=str(value), fg_color="red")  # Red for selected state

        # Keep track of the currently clicked button
        self.last_clicked_button = target_button
        # Keep track of the garbage value
        self.last_clicked_value = self.map_matrix[row][col]

        # Print and log the selected coordinates
        text_ = f"Selected coordinates: ({row}, {col}), with {value} kg of garbage"
        self.master.master.button_frame.log_frame.add_text(text_)
        print(text_)


        # Update the coordinate box in the left frame
        self.master.master.left_frame.update_coordinate_box(row, col)
        
    def clean_button(self, row, col):
        """Clean the button by setting its value to 0 and changing its color to the default blue."""
        # Update the map matrix to set the value to 0
        self.map_matrix[row][col] = 0

        # Get the button at the specified row and column
        button = self.grid_slaves(row=row, column=col)[0]

        # Update the button's appearance
        button.configure(text='', fg_color="#4478C6")  # Blue for value 0

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
