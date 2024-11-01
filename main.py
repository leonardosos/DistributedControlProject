import customtkinter


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.toplevel_window = ToplevelWindow(self)

        self.title("Mission control")
        self.geometry("800x650")
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0,1), weight=1)

        # Left Frame with Buttons
        self.left_frame = LeftFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Right Frame with a Matrix of Buttons
        self.right_frame = RightFrame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10)

        # Bottom Frame with a Launch Button
        self.button = customtkinter.CTkButton(self, text="Launch mission", command=self.button_callback)
        self.button.grid(row=1, column=0, padx=10, pady=10, sticky="ew", columnspan=2)



    def button_callback(self):
        print("Launch button pressed")

class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")

        self.things = "Object1, Object2, Object3"

        self.text = f"The drones have find the object: \n\n {self.things}"

        self.label = customtkinter.CTkLabel(self, text=self.text, fg_color="gray30", corner_radius=6)




        self.label.pack(padx=20, pady=20)
class LeftFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.title = "Settings"
        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.pack(padx=10, pady=10, fill="x")



        self.left_button1 = customtkinter.CTkButton(self, text="Button 1", command=self.button1_callback)
        self.left_button1.pack(pady=5)

        self.left_button2 = customtkinter.CTkButton(self, text="Button 2", command=self.button2_callback)
        self.left_button2.pack(pady=5)

        self.text = "Set the number of the vessel"
        self.text = customtkinter.CTkLabel(self, text=self.text, fg_color="gray30", corner_radius=6)
        self.text.pack(pady=5)

        self.spinbox_1 = FloatSpinbox(self, width=150, step_size=1)
        self.spinbox_1.pack(padx=10, pady=10, fill="x")

        self.spinbox_1.set(35)




    def button1_callback(self):
        print("Button 1 clicked")

    def button2_callback(self):
        print("Button 2 clicked")



class RightFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.title = "Map"
        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.matrix_button = MatrixButton(self)
        self.matrix_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

class MatrixButton(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.create_matrix_of_buttons(10, 10)

    def create_matrix_of_buttons(self, rows, cols):
        for i in range(rows):  # 3 rows
            for j in range(cols):  # 3 columns
                button = customtkinter.CTkButton(self,
                                                 text=f"({i},{j})",
                                                 command=lambda i_=i, j_=j: self.matrix_button_callback(i_, j_),
                                                 width=50,
                                                 height=50,
                                                 corner_radius=0)
                button.grid(row=i, column=j, padx=0, pady=0, )

    def matrix_button_callback(self, row, col):
        print(f"Matrix Button clicked at ({row}, {col})")

class FloatSpinbox(customtkinter.CTkFrame):
    def __init__(self, master, width=100, height=30, step_size=1, command=None):
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
        self.entry.insert(0, "0.0")

    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = float(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = float(self.entry.get()) - self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return


    def set(self, value: float):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(float(value)))

app = App()
app.mainloop()
