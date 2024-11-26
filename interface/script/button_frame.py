# import doctest to test the functions standalone
from doctest import master

import customtkinter


class ButtonFrame(customtkinter.CTkFrame):
    """Button frame that contain log and mission status"""
    def __init__(self, master, font_size=16):
        super().__init__(master)

        # Set the font size for pass to the children widgets
        self.font_size = font_size

        # Log frame
        self.log_frame = LogFrame(self, font_size)
        self.log_frame.grid(row=0, column=0, columnspan=2,  padx=(0,20), sticky="nsew")

        # Status frame
        self.status_frame = StatusFrame(self, font_size)
        self.status_frame.grid(row=0, column=2, sticky="nsew")

        # Set the weight for the row and column basic configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0,1,2), weight=1)

class LogFrame(customtkinter.CTkFrame):
    """Log entry box with own add method"""
    def __init__(self, master, font_size=16):
        super().__init__(master)

        # Label
        self.label = customtkinter.CTkLabel(self, text="Log:", font=(None, font_size))
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        # Text box
        self.text_box = customtkinter.CTkTextbox(self, width=1000, height=200 , border_width=1, border_color="black", font=(None, font_size))
        self.text_box.grid(row=1, column=0, padx=10, pady=(0,10), sticky="nsew")
        self.text_box.configure(state="disabled")

        # Set the weight for the row and column basic configuration
        self.grid_columnconfigure(0, weight=1)

    def add_text(self, text):
        """Add a new line of text to the log entry box."""
        self.text_box.configure(state="normal")
        self.text_box.insert("1.0",">  " + text + "\n")
        self.text_box.yview_moveto(0)
        self.text_box.configure(state="disabled")

class StatusFrame(customtkinter.CTkScrollableFrame):
    """Frame that contains the mission status"""
    def __init__(self, master, font_size=16):
        super().__init__(master, width=500)

        # hack to ordinate the mission status
        self.counter = 10 

        # Set the font size for pass to the children widgets
        self.font_size = font_size

        # Label
        self.label = customtkinter.CTkLabel(self, width=600 ,text="Missions:", font=(None, font_size))
        self.label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Set the weight for the row and column basic configuration
        self.grid_columnconfigure(0, weight=1)


    def add_status(self, text, id_mission, max_time=10000, update_interval=50):
        """ Add a status progress bar to the status frame """

        # Create a frame to hold the label and progress bar
        single_mission_frame = customtkinter.CTkFrame(self, fg_color="#2B2B2B")
        single_mission_frame.grid(row = self.counter ,padx=10, pady=5)

        # Increase the counter  
        self.counter -= 1

        # Set the weight for the row and column basic configuration
        self.grid_columnconfigure(0, weight=1)

        # COMPONETS OF THE SINGLE MISSION FRAME
        # Add the label to the frame
        label = customtkinter.CTkLabel(single_mission_frame, text=text, font=(None, self.font_size))
        label.grid(row=0, column=0, padx=5, pady=5)
        # Add the progress bar to the frame
        mission_progress_bar = MissionProgressBar(single_mission_frame, id_mission, max_time=max_time, update_interval=update_interval)
        mission_progress_bar.grid(row=0, column=1, padx=5, pady=5)

        # Start and update the progress bar asynchonously
        mission_progress_bar.update_progress() # at the end of the progression, call the refresh_counter method

    
    def refresh_counter(self, frame_bar, id_mission):
        """Refresh the counter using the info from mission_info"""

        # Define the main master -> app of main.py
        main_master = self.master.master

        # Decrese the ongoing mission and update menu bar
        main_master.ongoing_mission -= 1
        main_master.menu_bar.update_ongoing_mission(main_master.ongoing_mission)

        # Update garbage
        main_master.garbage_collected += main_master.mission_info[id_mission]["value_of_map"]
        main_master.menu_bar.update_garbage(main_master.garbage_collected)
        
        # Update vessel availability
        main_master.vessel_available += main_master.mission_info[id_mission]["number_of_vessels"]
        main_master.menu_bar.update_vessel_availability(main_master.vessel_available)

        # Print the mission completed also in the log frame
        print(f"Mission completed #{id_mission}")
        text_ = f"Mission completed #{id_mission}"
        self.master.log_frame.add_text(text_)



# Define a new ProgressBar
class MissionProgressBar(customtkinter.CTkProgressBar):
    """Custom progress bar for the mission status"""
    def __init__(self, master, id_mission, max_time=7000, update_interval=50):
        super().__init__(master ,height=25, corner_radius=12, progress_color="green", border_color="black")
        # Set the variables
        self.progress = 0
        self.max_time = max_time
        self.update_interval = update_interval
        self.set(0)
        self.green = (0, 255, 0)
        self.yellow = (255, 255, 0)
        self.red = (255, 0, 0)

        # Correlate progress bar with mission id
        self.id_mission = id_mission

    # PROGRESS BAR FUNCTION
    def update_progress(self):
        """Update the progress bar and the color based on the progress."""
        if self.progress < 1: 
            self.progress += self.update_interval / self.max_time

            self.set(self.progress) # Update the progress bar
            self.change_color_based_on_progress(self.progress * 100) # Dynamically calculate the color based on the progress percentage

            # Schedule the next update and call the update_progress function recursively
            self.after(self.update_interval, self.update_progress)

        # When the progress is 100%
        else: 
            self.set(1) # Set the progress to 100% 
            self.change_color_based_on_progress(100)  # Set the final color at 100%

            # Refresh the interface counter
            self.master.master.refresh_counter(self.master, self.id_mission) 

            #self.after(3000, self.destroy) # Destroy the progress bar after n second

    # COLOR FUNCTION
    def change_color_based_on_progress(self, percentage):
        """Smooth color gradient transition from green to yellow to red."""
        if percentage <= 50:
            # From green (0%) to yellow (50%)
            factor = percentage / 50  # Normalize between 0 and 1
            r, g, b = self.interpolate_color(self.red, self.yellow, factor)
        else:
            # From yellow (50%) to red (100%)
            factor = (percentage - 50) / 50  # Normalize between 0 and 1
            r, g, b = self.interpolate_color(self.yellow, self.green, factor)

        # Convert the RGB color to a hex format and apply it
        hex_color = self.rgb_to_hex(r, g, b)
        self.configure(progress_color=hex_color)  # Apply the calculated color
    def rgb_to_hex(self, r, g, b):
        """Convert an RGB color to a hex color string."""
        return f'#{r:02x}{g:02x}{b:02x}'
    def interpolate_color(self, color1, color2, factor):
        """Linearly interpolate between two RGB colors."""
        r1, g1, b1 = color1
        r2, g2, b2 = color2

        r = int(r1 + factor * (r2 - r1))
        g = int(g1 + factor * (g2 - g1))
        b = int(b1 + factor * (b2 - b1))

        return r, g, b
        
if __name__ == "__main__":
    
    app = customtkinter.CTk()

    menu = ButtonFrame(app)
    menu.grid(row=2, column=0, columnspan=3, padx = 0 , pady=(20,0), sticky="nsew")

    # test the add_text method
    menu.log_frame.add_text("Start mission controller")

    # test the add_status method
    menu.status_frame.add_status("Mission 1", 1)
    menu.status_frame.add_status("Mission 2", 2)
    menu.status_frame.add_status("Mission 3", 3)
    menu.status_frame.add_status("Mission 4", 4)
    menu.status_frame.add_status("Mission 5", 5)

    app.mainloop() 