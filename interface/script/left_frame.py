import customtkinter

class LeftFrame(customtkinter.CTkFrame):
    """Left frame with settings"""

    def __init__(self, master):
        super().__init__(master)

        self.text = "Settings"
        self.title = customtkinter.CTkLabel(self, text=self.text, fg_color="gray30", corner_radius=6)
        self.title.pack(padx=10, pady=10, fill="x")


        self.text = "Set the number of the vessel"
        self.text = customtkinter.CTkLabel(self, text=self.text, fg_color="gray30", corner_radius=6)
        self.text.pack(pady=5)

        self.spinbox_1 = FloatSpinbox(self, width=150, step_size=1)
        self.spinbox_1.pack(padx=10, pady=10)
        self.spinbox_1.set(1)

        
        # Bottom Frame with Button
        self.bottom_button = customtkinter.CTkButton(self,
                                                     text="Confirm selected terget", 
                                                     fg_color="green", 
                                                     hover_color="darkgreen",
                                                     command=self.button_callback)
        self.bottom_button.pack(padx=10, pady=10)


    def button_callback(self):
        print("Button pressed")
        #print(f"Selected target: {self.spinbox_1.get_spin_value()}")  


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

