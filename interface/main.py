import customtkinter
import json
import os

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mission control")
        self.geometry("800x650")
        customtkinter.set_appearance_mode("dark")
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0,1), weight=1)

        # Right Frame with a Matrix of Buttons
        self.right_frame = RightFrame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10)

        self.bottom_button_already_pressed = False

        # Left Frame with Settings
        self.left_frame = LeftFrameEmpty(self)
        self.left_frame.grid(row=0, column=0, padx=(0,10), pady=10, sticky="nsew") #need to be equal to left_frame_empty
               
        # Bottom Frame with Button
        self.bottom_button = customtkinter.CTkButton(self,
                                                     text="Confirm selected terget", 
                                                     fg_color="green", 
                                                     hover_color="darkgreen",
                                                     command=self.button_callback)
        self.bottom_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew", columnspan=2)


    def button_callback(self):

        if not self.bottom_button_already_pressed:
            print("Select clicked")

            self.bottom_button_already_pressed = True
            
            # overwrites Left Frame with Settings
            self.left_frame = LeftFrame(self)
            self.left_frame.grid(row=0, column=0, padx=(0,10), pady=10, sticky="nsew") #need to be equal to left_frame_empty

            # change the button botton
            self.bottom_button.configure(text="Launch mission", fg_color="green", hover_color="darkgreen")

        else:
            print("Launch mission clicked")
            print(f'Selected {self.left_frame.spinbox_1.get_spin_value()} boats')
            

''' PROGRESS BAR EXAMPLE

        self.progressbar = customtkinter.CTkProgressBar(self, width=200, height=20, mode="indeterminate")
        self.progressbar.start()
        self.progressbar.pack(pady=20)

        # Schedule the stop_progressbar method to be called after 5000 milliseconds (5 seconds)
        self.after(5000, self.stop_progressbar)

    def stop_progressbar(self):
        self.progressbar.stop()
        self.success_label = customtkinter.CTkLabel(self, text="Successful", fg_color="green", corner_radius=6)
        self.success_label.pack(pady=20)

'''

class LeftFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.text = "Settings"
        self.title = customtkinter.CTkLabel(self, text=self.text, fg_color="gray30", corner_radius=6)
        self.title.pack(padx=10, pady=10, fill="x")

        self.left_button1 = customtkinter.CTkButton(self, text="Button 1", command=self.button1_callback)
        self.left_button1.pack(pady=5)

        self.left_button2 = customtkinter.CTkButton(self, text="Button 2", command=self.button2_callback)
        self.left_button2.pack(pady=5)

        self.text = "Set the number of the vessel"
        self.text = customtkinter.CTkLabel(self, text=self.text, fg_color="gray30", corner_radius=6)
        self.text.pack(pady=5)

        self.spinbox_1 = FloatSpinbox(self, width=150, step_size=1)
        self.spinbox_1.pack(padx=10, pady=10)
        self.spinbox_1.set(1)


    def button1_callback(self):
        print("Button 1 clicked")

    def button2_callback(self):
        print("Button 2 clicked")

class LeftFrameEmpty(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.text = "Select the target area on the map"
        self.title = customtkinter.CTkLabel(self, text=self.text)

        self.title.pack(padx=10, pady=10, fill="x",expand=True) 


class RightFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.matrix_button = MatrixButton(self)
        self.matrix_button.grid(row=0, column=0,padx=10, pady=(10,0), sticky="ew")

        self.textbox = customtkinter.CTkTextbox(master=self, height=20)
        self.textbox.insert("0.0", "Legenda: black - occupied, white - free, grey - percentage of gargabe, red - selected")
        self.textbox.configure(state="disabled")
        self.textbox.grid(row=1, column=0, padx=10, pady=(5,10), sticky="ew")


class MatrixButton(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Build the path to map.json
        map_json_path = os.path.join(current_dir, '../map_generator/map.json')

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


class FloatSpinbox(customtkinter.CTkFrame):
    def __init__(self, master, width=40, height=30, step_size=1, command=None):
        super().__init__(master, width=width, height=height)

        self.step_size = step_size
        self.command = command

        self.configure(fg_color=("gray78", "gray28"))  # set frame color

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.subtract_button = customtkinter.CTkButton(self, text="-", width=height-6, height=height-6,
                                                       command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = customtkinter.CTkEntry(self, width=width-(2*height), height=height-6, border_width=0)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=height-6, height=height-6,
                                                  command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        # default value
        self.entry.insert(0, "0")

    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = int(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = int(self.entry.get()) - self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return


    def set(self, value: int):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(int(value)))

    def get_spin_value(self):
        return self.entry.get()

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()