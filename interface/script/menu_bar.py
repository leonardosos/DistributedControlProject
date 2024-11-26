# import doctest to test the functions standalone
from doctest import master

import customtkinter 
import json


class MenuBar(customtkinter.CTkFrame):
    def __init__(self, master, font_size=16):
        super().__init__(master)

        # Set the font size for pass to the children widgets (topview menu setting)
        self.font_size = font_size
        self.width_entry = int(font_size*4.3) # 70

        # Set weight for row and column
        self.rowconfigure(0, weight=1)      # keep the info counters on the right corner
        self.columnconfigure(2, weight=1)   # avoiding bar collapsing when resizing

        # Menu button
        self.menu_button = customtkinter.CTkButton(self, height=font_size*2, width=font_size*6, font=(None, font_size) ,text="Menu", fg_color="#444444", command=self.open_menu_window_callback)
        self.menu_button.grid(row=0, column=0, padx=20, pady=10)

        # Vessel availability
        # Label
        self.vessel_label = customtkinter.CTkLabel(self, height=font_size*2, font=(None, font_size) ,text="Vessel Available:")
        self.vessel_label.grid(row=0, column=2, pady=10, sticky="e")
        # Entry field
        self.vessel_entry = customtkinter.CTkEntry(self, height=font_size*2, font=(None, font_size) ,width=self.width_entry ,justify="center")
        self.vessel_entry.grid(row=0, column=3, padx=(5,50), pady=10, sticky="e")
        self.vessel_entry.insert(0, "--")  # Empty initial value
        self.vessel_entry.configure(state="readonly")

        # Ongoing mission
        # Label
        self.mission_label = customtkinter.CTkLabel(self, height=font_size*2, font=(None, font_size), text="Ongoing Mission:")
        self.mission_label.grid(row=0, column=4, pady=10, sticky="e")
        # Entry field
        self.mission_entry = customtkinter.CTkEntry(self, width=self.width_entry, height=font_size*2, font=(None, font_size), justify="center")
        self.mission_entry.grid(row=0, column=5, padx=(5,50), pady=10, sticky="e")
        self.mission_entry.insert(0, "# 0")  # Initial value
        self.mission_entry.configure(state="readonly")

        # Garbage status
        # Label
        self.garbage_label = customtkinter.CTkLabel(self, height=font_size*2, font=(None, font_size), text="Garbage collected:")
        self.garbage_label.grid(row=0, column=6, pady=10, sticky="e")
        # Entry field
        self.garbage_entry = customtkinter.CTkEntry(self, width=self.width_entry, height=font_size*2, font=(None, font_size), justify="center")
        self.garbage_entry.grid(row=0, column=7, padx=(5,20), pady=10, sticky="e")
        self.garbage_entry.insert(0, "0")  # Initial value
        self.garbage_entry.configure(state="readonly")

    # Callback function for opening the menu window
    def open_menu_window_callback(self):
        menu_setting_top_view = MenuSettingTopView(self, self.font_size)

    # Callback function for update the menu 
    def update_vessel_availability(self, value):
        """Update the vessel availability entry with the given value."""
        self.vessel_entry.configure(state="normal")
        self.vessel_entry.delete(0, "end")
        self.vessel_entry.insert(0, str(value))
        self.vessel_entry.configure(state="readonly")

    def update_ongoing_mission(self, mission):
        """Update the ongoing mission entry with the given mission."""
        self.mission_entry.configure(state="normal")
        self.mission_entry.delete(0, "end")
        self.mission_entry.insert(0, f'# {mission}')
        self.mission_entry.configure(state="readonly")
        
    def update_garbage(self,total_garbage):
        """Update the garbage entry with the given value."""
        self.garbage_entry.configure(state="normal")
        self.garbage_entry.delete(0, "end")
        self.garbage_entry.insert(0, f"{str(total_garbage)} kg")
        self.garbage_entry.configure(state="readonly")


class MenuSettingTopView(customtkinter.CTkToplevel):
    """Top view of the menu settings."""
    def __init__(self, master, font_size):
        super().__init__(master)

        self.geometry("400x300")
        self.title("Menu")

        self.columnconfigure(0, weight=1)     # Set weight for center alignment
        self.rowconfigure(2, weight=1)        # Set weight for spacing between buttons and last button

        # Buttons in the TopView
        self.button1 = customtkinter.CTkButton(self, text="Import mission", height=font_size*2, width=220 ,font=(None, font_size),command=self.import_mission)
        self.button1.grid(row=0, padx=10, pady=(30,0))

        self.button2 = customtkinter.CTkButton(self, text="Export mission", height=font_size*2, width=220 ,font=(None, font_size), command=self.export_mission)
        self.button2.grid(row=1, padx=10, pady=30)

        self.button3 = customtkinter.CTkButton(self, text="Save and close", height=font_size*2, width=220 ,font=(None, font_size), command=self.destroy)
        self.button3.grid(row=3, padx=10, pady=30)

        # Keep the window on top
        self.attributes("-topmost", True)
    
    def export_mission(self):
        # Start exporting message
        print("Exporting missions...")
        self.master.master.button_frame.log_frame.add_text("Exporting missions data...")

        # Dump the mission info to file 
        with open("mission_info.log", "w") as file:
            json.dump(self.master.master.mission_info, file, indent=4)

        # Print the mission info to the log frame and console
        for key, value in self.master.master.mission_info.items():
            text = f"{key}: {value}"
            print(text)  # Print also in the console
            self.master.master.button_frame.log_frame.add_text(text)

    # Fake function to simulate the import mission
    def import_mission(self):
        print("Importing missions...")
        self.master.master.button_frame.log_frame.add_text("Importing missions data...")


if __name__ == "__main__":
    app = customtkinter.CTk()
    menu = MenuBar(app)
    menu.grid(row=0, column=0, columnspan=3, sticky="nswe")

    # test the update functions
    menu.update_vessel_availability(10)
    menu.update_garbage(20)
    menu.update_ongoing_mission(30)

    app.mainloop()