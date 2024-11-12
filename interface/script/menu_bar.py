import customtkinter 
import pprint


class MenuBar(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)

        # Menu button to open TopView
        self.menu_button = customtkinter.CTkButton(self, height=25, width=100 ,text="Menu", fg_color="#444444", command=self.open_top_view)
        self.menu_button.grid(row=0, column=0, padx=20, pady=10)

        # Vessel availability
        self.vessel_label = customtkinter.CTkLabel(self, text="Vessel Available:")
        self.vessel_label.grid(row=0, column=2, padx=5, pady=10, sticky="e")

        self.vessel_entry = customtkinter.CTkEntry(self, width=50, justify="center")
        self.vessel_entry.grid(row=0, column=3, padx=(0,50), pady=10, sticky="e")
        self.vessel_entry.insert(0, "-")  # Initial value

        # Ongoing mission
        self.mission_label = customtkinter.CTkLabel(self, text="Ongoing Mission:")
        self.mission_label.grid(row=0, column=4, padx=5, pady=10, sticky="e")

        self.mission_entry = customtkinter.CTkEntry(self, width=50, justify="center")
        self.mission_entry.grid(row=0, column=5, padx=(10,50), pady=10, sticky="e")
        self.mission_entry.insert(0, "# 0")  # Initial value

        # Garbage status
        self.garbage_label = customtkinter.CTkLabel(self, text="Garbage collected:")
        self.garbage_label.grid(row=0, column=6, padx=5, pady=10, sticky="e")

        self.garbage_entry = customtkinter.CTkEntry(self, width=50, justify="center")
        self.garbage_entry.grid(row=0, column=7, padx=(10,20), pady=10, sticky="e")
        self.garbage_entry.insert(0, "0")  # Initial value

    def open_top_view(self):
        top_view = TopView(self)

    def update_vessel_availability(self, value):
        """Update the vessel availability entry with the given value."""
        self.vessel_entry.delete(0, "end")
        self.vessel_entry.insert(0, str(value))

    def update_ongoing_mission(self, mission):
        """Update the ongoing mission entry with the given mission."""
        self.mission_entry.delete(0, "end")
        self.mission_entry.insert(0, f'# {mission}')

    def update_garbage(self,total_garbage):
        """Update garbage counter"""
        self.garbage_entry.delete(0, "end")
        self.garbage_entry.insert(0, f"{str(total_garbage)} kg")


class TopView(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")
        self.title("Menu")

        self.columnconfigure(0, weight=1)

        # Buttons in the TopView
        self.button1 = customtkinter.CTkButton(self, text="Button TODO")
        self.button1.grid(row=0, padx=10, pady=(30,10))

        self.button2 = customtkinter.CTkButton(self, text="Export mission", command=self.export_mission)
        self.button2.grid(row=1, padx=10, pady=10)

        self.button3 = customtkinter.CTkButton(self, text="Save and close", command=self.destroy)
        self.button3.grid(row=2, padx=10, pady=(50,20))

        # Keep the window on top
        self.attributes("-topmost", True)
    
    def export_mission(self):
        print("Exporting missions...")

        self.master.master.button_frame.log_frame.add_text("Exporting missions data...")

        pprint.pprint(self.master.master.mission_info)

        self.master.master.button_frame.log_frame.add_text("Missions data exported")
