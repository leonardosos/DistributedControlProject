import customtkinter

class WelcomeTab(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry()
        self.title("Welcome Message")

        self.grid_columnconfigure(0, weight=1)

        self.text = '''WELCOME to the mission control system.
        \n
        You can hover over the map for obtain information about each location.
        \n
        Click on a location for select the target and unlock the setting area.'''

        self.label = customtkinter.CTkLabel(self, text=self.text)
        self.label.grid(padx=20, pady=20, sticky="ew")

        # Keep the window on top
        self.attributes("-topmost", True)

        self.button = customtkinter.CTkButton(self, text="Okay", command=self.destroy)
        self.button.grid(pady=20, padx=20 ,sticky="ew")