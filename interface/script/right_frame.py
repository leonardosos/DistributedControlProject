'''
This module contains the RightFrame class, which is a custom tkinter frame that displays information about the hovered cell.
The RightFrame class contains:
- a coordinate label and entry box to display the hover cell's coordinates,
- a value label to display the estimated garbage quantity in the hover cell,
- a vertical progress bar to visually represent the garbage quantity,
- an advice label and entry box to suggest the number of vessels needed for optimal cleaning.

The width of first label is fixed and is equal to the width of right_frame in order to have a simmetry.

'''

import customtkinter

class RightFrame(customtkinter.CTkFrame):
    def __init__(self, master, font_size=16, side_panel_width=300):
        super().__init__(master)

        # Set the font size for child widgets
        self.font_size = font_size

        # Set the padding and spacing between widgets
        self.upper_down_space = 15
        self.label_box_space = 5
        self.inter_widget_space = 35

        self.grid_columnconfigure(0, weight=1)  # Allow the frame to expand horizontally
        self.grid_rowconfigure((2, 5, 8, 12), weight=1)  # Allow the widgets to expand vertically and occupy all the bar space

        # Label for the title
        self.title = customtkinter.CTkLabel(self, text="Cell Analysis", font=(None, font_size), corner_radius=6, width=side_panel_width)
        self.title.grid(row=0, padx=10, pady=(self.upper_down_space, 0), sticky="n")
        # info label
        self.info = customtkinter.CTkLabel(self, text="Select a cell by placing the cursor over it", font=(None, font_size, "underline"),corner_radius=6, width=250)
        self.info.grid(row=1, padx=10, pady=(self.label_box_space, self.inter_widget_space), sticky="n")

        # Label for "Coordinate selected target"
        self.coordinate_label = customtkinter.CTkLabel(self, text="Cell Coordinates", font=(None, font_size), corner_radius=6)
        self.coordinate_label.grid(row=3, pady=(0, self.label_box_space))
        # Coordinate entry box
        self.coordinate_box = customtkinter.CTkEntry(self, width=font_size*5, height=font_size*2, font=(None, font_size), border_width=0, justify="center")
        self.coordinate_box.grid(row=4, padx=10, pady=(0, self.inter_widget_space))

        # Label for displaying the quantity 
        self.value_label = customtkinter.CTkLabel(self, text="Estimated garbage quantity:", font=(None, font_size), corner_radius=6)
        self.value_label.grid(row=6, pady=(0, self.label_box_space))
        # Vertical progress bar to represent the garbage quantity
        self.vertical_progressbar = VerticalProgressBar(self, width=50, height=170, font_size=self.font_size)
        self.vertical_progressbar.grid(row=7, padx=10, pady=(0, self.inter_widget_space))

        # Label advice from systems 
        self.advice_label = customtkinter.CTkLabel(self, text="Suggested vessels", font=(None, font_size), corner_radius=6)
        self.advice_label.grid(row=9, pady=(0, 0))
        self.advice_info_label = customtkinter.CTkLabel(self, text="for optimal cleaning of the area:", font=(None, font_size), corner_radius=6)
        self.advice_info_label.grid(row=10, pady=(0, self.label_box_space))
        # Entry box for the suggested number of vessels
        self.advice_box = customtkinter.CTkEntry(self, width=font_size*3, height=font_size*2, font=(None, font_size), border_width=0, justify="center")
        self.advice_box.grid(row=11, padx=10, pady=(0, self.upper_down_space))


    def update_info(self, row, col, value):
        """Update the coordinate box and value label with the hovered coordinates and value."""

        # Update the coordinate box with the hovered cell's coordinates
        self.coordinate_box.delete(0, "end")
        self.coordinate_box.insert(0, f"({row}, {col})")

        if value >= 0:
            # Update the value box with the advised number of vessels
            self.advice_box.delete(0, "end")
            self.advice_box.insert(0, f"{value//20}")

            # Update the vertical progress bar with the hovered cell's value
            self.vertical_progressbar.set_progress(value)
        else:
            # Update the value box with the advised number of vessels
            self.advice_box.delete(0, "end")
            self.advice_box.insert(0, "0")

            # Update the vertical progress bar with the hovered cell's value
            self.vertical_progressbar.set_progress(0)



class VerticalProgressBar(customtkinter.CTkFrame):
    '''Vertical progress bar widget with a method to set its value.'''

    def __init__(self, master, width=50, height=170, font_size=16):
        """Create a vertical progress bar with a method to set its value."""
        super().__init__(master, width=width, height=height, fg_color="#2B2B2B")

        # Define the vertical progress bar layout and options
        self.progress_bar = customtkinter.CTkProgressBar(self, orientation="vertical", width=width/2, height=height)
        self.progress_bar.grid(row=0, column=0, padx=10, pady=10)
        self.progress_bar.set(0)  # Initial progress value as 0%

        # Label to display percentage value
        self.value_label = customtkinter.CTkLabel(self, text="0 %", font=(None, font_size),width=font_size*3) # initial value as 0%
        self.value_label.grid(row=1, column=0, pady=(10, 0))

    def set_progress(self, value):
        """Set the progress bar to a specific value between 0 and 100.

        Args:
            value (int/float): The progress percentage from 0 to 100.
        """
        if 0 <= value <= 100:
            percentage = value / 100.0  # Normalize the value for the progress bar (0 to 1).
            self.progress_bar.set(percentage)  # Update the visual progress bar.
            self.value_label.configure(text=f"{int(value)} %")  # Update the label to show the percentage.


# Test the RightFrame class
if __name__ == "__main__":
    app = customtkinter.CTk()
    right_frame = RightFrame(app)

    right_frame.grid(row=1, column=2, padx=(10,0), pady=10, sticky="nsew")

    right_frame.update_info(3, 5, 40)

    app.mainloop()