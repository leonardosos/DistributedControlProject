'''
This module contains the ButtonFrame class that contains:
- LogFrame: a frame that contains a text box that can be updated with new lines of text with a related function. 
- StatusFrame: a frame that contains the list of the mission and a button to clear the completed missions.

The status frame initially empty, can be filled with the add_status method that creates 
a new SingleMissionFrame object, add it to the status frame and start the progress bar. 

The SingleMissionFrame object contains a label with the mission number, a progress bar and an info button.

At the start of the mission, the initial_refresh_counter method is called to update the ongoing mission and the vessel availability.
At the end of the mission:
 - the final_refresh_counter method is called to update the ongoing mission, the garbage collected, the vessel availability and the status of the mission.
 - matrix_button.clean_button method is called to clean the button value and color in the central frame matrix.

The fixed interface size are: 
- height of entry box of log 
- width of missions frame. 
- width of label mission progress bar

The progress bar is a custom progress bar that changes color based on the progress percentage and 
it is more general possible due to the use on left frame for the data upload.
'''

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
        self.grid_columnconfigure((0,1), weight=1)
        self.grid_columnconfigure(2, weight=0)

class LogFrame(customtkinter.CTkFrame):
    """Log entry box with own add method"""
    def __init__(self, master, font_size=16):
        super().__init__(master)

        # Label
        self.label = customtkinter.CTkLabel(self, text="Log:", font=(None, font_size))
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        # Text box
        self.text_box = customtkinter.CTkTextbox(self, height=120, border_width=1, border_color="black", font=(None, font_size))
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
        super().__init__(master, width=600)

        # hack to ordinate the mission status
        self.mission_order_counter = 10 

        # Set the font size for pass to the children widgets
        self.font_size = font_size

        # Label frame
        self.label_frame = LabelFrame(self, font_size)
        self.label_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.status_list = []

    def add_status(self, id_mission, max_time=10000, update_interval=50):
        """ Add a status progress bar to the status frame """

        self.grid_columnconfigure(0, weight=1)
        
        # Create a frame to hold the label and progress bar
        self.single_mission_frame = SingleMissionFrame(self, id_mission, max_time, update_interval, self.font_size)
        self.single_mission_frame.grid(row = self.mission_order_counter ,padx=10, pady=5)

        self.status_list.append(self.single_mission_frame)

        # Increase the counter for display the mission status in the correct order
        self.mission_order_counter -= 1

        # Call the initial_refresh_counter method
        self.initial_refresh_counter(id_mission)

        # Start and update the progress bar asynchonously
        self.single_mission_frame.start_progress() # at the end of the progression, call the final_refresh_counter method

    def initial_refresh_counter(self, id_mission):
        """Refresh the interface counter using the info from mission_info dictionary at the start of the mission""" 

        # Define the main master -> app of main.py
        main_master = self.master.master.master.master

        # Decrese the ongoing mission and update menu bar
        main_master.ongoing_mission += 1
        main_master.menu_bar.update_ongoing_mission(main_master.ongoing_mission)
        
        # Update vessel availability
        main_master.vessel_available -= main_master.mission_info[id_mission]["number_of_vessels"]
        main_master.menu_bar.update_vessel_availability(main_master.vessel_available)

    def clear_list(self):
        """Clear the list of missions"""

        # Log and print the clear list
        text_ = "Clear the list of missions"
        self.master.master.master.log_frame.add_text(text_)
        print(text_)

        try:
            for status in self.status_list:
                print(f"Checking status: {status}")
                print(f"Status value: {status.get_status()}")
                if status.get_status() == 1:
                    status.destroy()
                    self.status_list.remove(status)
        except AttributeError as e:
            print(f"AttributeError: {e}")

    def final_refresh_counter(self, id_mission):
        """Refresh the interface counter using the info from mission_info dictionary at the end of the mission""" 

        # Define the main master -> app of main.py
        main_master = self.master.master.master.master

        # Decrese the ongoing mission and update menu bar
        main_master.ongoing_mission -= 1
        main_master.menu_bar.update_ongoing_mission(main_master.ongoing_mission)

        # Update garbage
        main_master.garbage_collected += main_master.mission_info[id_mission]["value_of_map"]
        main_master.menu_bar.update_garbage(main_master.garbage_collected)
        
        # Update vessel availability
        main_master.vessel_available += main_master.mission_info[id_mission]["number_of_vessels"]
        main_master.menu_bar.update_vessel_availability(main_master.vessel_available)

        # Clean the button in the central frame matrix
        main_master.central_frame.matrix_button.clean_button(id_mission)

        # Update the status mission from the dictionary
        main_master.mission_info[id_mission]["status"] = "Completed"


class SingleMissionFrame(customtkinter.CTkFrame):
    """Single mission frame that contain the label, progress bar and info button"""
    def __init__(self, master, id_mission, max_time, update_interval, font_size=16):
        super().__init__(master, 
                         fg_color="#2B2B2B", 
                         height=font_size*2, 
                         corner_radius=10, 
                         border_width=1, 
                         border_color="black",
                         )

        self.id_mission = id_mission
        self.font_size = font_size
        
        # Set central alignment
        self.grid_columnconfigure(0, weight=1)

        # Add the label to the frame
        self.label = customtkinter.CTkLabel(self, text=f'Mission {id_mission}', font=(None, font_size))
        self.label.grid(row=0, column=0, padx=10, pady=10)

        # Add the progress bar to the frame
        self.mission_progress_bar = MissionProgressBar(self, 
                                                       id_mission=id_mission, 
                                                       max_time=max_time, 
                                                       update_interval=update_interval, 
                                                       callback=self.end_progress)
        self.mission_progress_bar.grid(row=0, column=1, padx=5, pady=5)
        
        # Info button
        self.info_button = customtkinter.CTkButton(self,
                                                   text="Info", 
                                                   width=font_size*6,
                                                   font=(None, font_size),
                                                   command=self.show_info)
        self.info_button.grid(row=0, column=2, padx=10, pady=10)
        
    def show_info(self):
        """Show the info of the mission"""
        print(f"Info button pressed, mission {self.id_mission}")

        main_master = self.master.master.master.master.master # Get the main master -> app of main.py
        info = main_master.mission_info[self.id_mission]

        info_text = ""
        for key, value in info.items():
            info_text += f"{key}: {value}\n"

        top_view_info = TopViewInfo(f"Mission {self.id_mission} info", info_text, font_size=self.font_size)


    def start_progress(self):
        """Start the progress bar"""

        # log the start of the mission
        text_ = f"Mission #{self.id_mission} started"
        self.master.master.master.master.log_frame.add_text(text_)
        print(text_)

        self.mission_progress_bar.update_progress()

    def end_progress(self):
        """At the End of the progress bar call the final_refresh_counter method"""

        # log the end of the mission
        text_ = f"Mission #{self.id_mission} completed"
        self.master.master.master.master.log_frame.add_text(text_)
        print(text_)

        # Call the final_refresh_counter method
        self.master.final_refresh_counter(self.mission_progress_bar.id_mission)

    def get_status(self):
        """Get the status of the mission"""
        #print(f"DEBUG - Mission {self.id_mission} status: {self.mission_progress_bar.progress_value_bar}")
        return self.mission_progress_bar.progress_value_bar
    

class LabelFrame(customtkinter.CTkFrame):
    def __init__(self, master, font_size=16):
        super().__init__(master, fg_color="#333333")

        # Label
        self.label = customtkinter.CTkLabel(self,text="Missions:", font=(None, font_size), height=font_size*2, width=410, anchor="w")
        self.label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.clear_list_button = customtkinter.CTkButton(self, text="Clear list", font=(None, font_size), command=self.master.clear_list)
        self.clear_list_button.grid(row=0, column=2, padx=10, pady=5, sticky="e")


class MissionProgressBar(customtkinter.CTkProgressBar):
    """Custom progress bar for the mission status"""
    def __init__(self, master, id_mission, max_time, update_interval, callback, width=None):
        super().__init__(master , width= width, height=25, corner_radius=12, progress_color="green", border_color="black")
        # Set the variables
        self.progress_value_bar = 0
        self.max_time = max_time
        self.update_interval = update_interval
        self.callback = callback
        self.set(0)
        self.green = (0, 255, 0)
        self.yellow = (255, 255, 0)
        self.red = (255, 0, 0)

        # Correlate progress bar with mission id
        self.id_mission = id_mission

    def update_progress(self):
        """Update the progress bar and the color based on the progress."""
        if self.progress_value_bar < 0.99: 
            self.progress_value_bar += self.update_interval / self.max_time

            self.set(self.progress_value_bar) # Update the progress bar
            self.change_color_based_on_progress(self.progress_value_bar * 100) # Dynamically calculate the color based on the progress percentage

            # Schedule the next update and call the update_progress function recursively
            self.after(self.update_interval, self.update_progress)

        # When the progress is 100%
        else: 
            self.progress_value_bar = 1
            self.set(1) # Set the progress to 100% 
            self.change_color_based_on_progress(100)  # Set the final color at 100%

            self.callback()  # Call the callback function to end the progress bar

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

class TopViewInfo(customtkinter.CTkToplevel):
    def __init__(self, label, text, font_size=16, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x300")
        self.title("Mission info")

        # Keep the window on top
        self.attributes("-topmost", True)

        self.grid_columnconfigure(0, weight=1) # set button to bottom

        self.label = customtkinter.CTkLabel(self, text=label, font=(None, font_size+2, "bold"), justify="left")
        self.label.grid(row = 0, padx=20, pady=20, sticky="ew")

        self.info = customtkinter.CTkLabel(self, text=text, font=(None, font_size), justify="left")
        self.info.grid(row = 1, padx=20, pady=20, sticky="ew")

        self.button = customtkinter.CTkButton(self, text="Okay", command=self.destroy, font=(None, font_size))
        self.button.grid(row = 5,pady=20, padx=20 ,sticky="ew")

        self.grid_rowconfigure(4, weight=1)

if __name__ == "__main__":
    
    app = customtkinter.CTk()

    menu = ButtonFrame(app)
    menu.grid(row=2, column=0, columnspan=3, padx = 0 , pady=(20,0), sticky="nsew")

    # test the add_text method
    menu.log_frame.add_text("TEST mission controller")

    app.mainloop() 