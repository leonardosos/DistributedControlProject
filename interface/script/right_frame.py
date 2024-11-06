from pydoc import text
from selectors import SelectorKey
import customtkinter

class RightFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)  # Allow the frame to expand horizontally

        self.text = '''Info Menù\n(keep the cursor on the cell to know the info)'''
        self.title = customtkinter.CTkLabel(self, text=self.text, corner_radius=6, width=250)
        self.title.grid(row=0, padx=10, pady=15, sticky="n")

        # Label for "Coordinate selected target"
        self.coordinate_label = customtkinter.CTkLabel(self, text="Coordinate hovered", corner_radius=6)
        self.coordinate_label.grid(row=1, pady=(20, 5))

        # Coordinate entry box
        self.coordinate_box = customtkinter.CTkEntry(self, width=150, height=30, border_width=0, justify="center")
        self.coordinate_box.grid(row=2, padx=10)

        # Label for displaying the quantity 
        self.value_label = customtkinter.CTkLabel(self, text="Quantity of garbage found:", corner_radius=6)
        self.value_label.grid(row=3, pady=(50, 5))

        self.vertical_progressbar = VerticalProgressBar(self)
        self.vertical_progressbar.grid(row=4, padx=10)

        # Advice from systems 
        self.advice_label = customtkinter.CTkLabel(self, text="For cleaning this area you should sent:", corner_radius=6)
        self.advice_label.grid(row=5, pady=(50, 5))

        self.advice_box = customtkinter.CTkEntry(self, width=150, height=30, border_width=0, justify="center")
        self.advice_box.grid(row=6, padx=10)


    def update_info(self, row, col, value):
        """Update the coordinate box and value label with the hovered coordinates and value."""
        self.coordinate_box.delete(0, "end")
        self.coordinate_box.insert(0, f"({row}, {col})")

        self.advice_box.delete(0, "end")
        self.advice_box.insert(0, f"{value//20} boats and {value%20} people")

        self.vertical_progressbar.set_progress(value)



class VerticalProgressBar(customtkinter.CTkFrame):
    def __init__(self, master, width=50, height=170):
        """Create a vertical progress bar with a method to set its value."""
        super().__init__(master, width=width, height=height)

        # Define the vertical progress bar layout and options
        self.progress_bar = customtkinter.CTkProgressBar(self, orientation="vertical", width=20, height=height)
        self.progress_bar.grid(row=0, column=0, padx=10, pady=10)
        self.progress_bar.set(0)  # Initial progress value as 0%

        # Label to display percentage (initially 0%)
        self.value_label = customtkinter.CTkLabel(self, text="0%", width=width)
        self.value_label.grid(row=1, column=0, pady=(10, 0))

    def set_progress(self, value):
        """Set the progress bar to a specific value between 0 and 100.

        Args:
            value (int/float): The progress percentage from 0 to 100.
        """
        if 0 <= value <= 100:
            percentage = value / 100.0  # Normalize the value for the progress bar (0 to 1).
            self.progress_bar.set(percentage)  # Update the visual progress bar.
            self.value_label.configure(text=f"{int(value)}%")  # Update the label to show the percentage.