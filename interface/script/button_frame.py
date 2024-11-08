import customtkinter


class ButtonFrame(customtkinter.CTkFrame):
    """Button frame that contain log and mission status"""
    def __init__(self, master):
        super().__init__(master)

        self.log_frame = LogFrame(self)
        self.log_frame.grid(row=0, column=0, padx=(0,20), sticky="nsew")

        self.status_frame = StatusFrame(self)
        self.status_frame.grid(row=0, column=2, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0,1), weight=1)



class LogFrame(customtkinter.CTkFrame):
    """Log entry box with add method"""
    def __init__(self, master):
        super().__init__(master)

        self.label = customtkinter.CTkLabel(self, text="Log:")
        self.label.grid(row=0, column=0, padx=10, pady=5, sticky="nw")

        self.text_box = customtkinter.CTkTextbox(self, width=1000 , height=300,border_width=1, border_color="black")#, font=(None, 15))
        self.text_box.grid(row=1, column=0, padx=(0,10), pady=(0,10), sticky="nsew")

        self.grid_columnconfigure(0, weight=1)

    def add_text(self, text):
        self.text_box.insert("1.0",">  " + text + "\n")
        self.text_box.yview_moveto(0)

class StatusFrame(customtkinter.CTkFrame):
    
    def __init__(self, master):
        super().__init__(master)

        self.label = customtkinter.CTkLabel(self, width=600 ,text="Status missions:")
        self.label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.status_list = []
        self.grid_columnconfigure(0, weight=1)

    def add_status(self, text, id_mission, max_time=10000, update_interval=50):
        """ Add a status progress bar to the status frame """

        # Create a frame to hold the label and progress bar
        frame = customtkinter.CTkFrame(self, fg_color="#2B2B2B")
        frame.grid(padx=10, pady=5)

        self.grid_columnconfigure(0, weight=1)

        # Add the label and progress bar to the frame
        label = customtkinter.CTkLabel(frame, text=text)
        label.grid(row=0, column=0, padx=5, pady=5)

        # Add the progress bar to the frame
        progress_bar = ProgressBar(frame, id_mission, max_time=max_time, update_interval=update_interval)
        progress_bar.grid(row=0, column=1, padx=5, pady=5)

        # Start the progress bar
        progress_bar.start_progress()

        # Add the frame to the status list
        self.status_list.append(frame)
    
    def update_and_remove_status(self, frame_bar, id_mission):
        """ Update the mission info, update the menu bar
        and destroy the progress frame"""

        # Destroy the progress frame
        self.after(2000, frame_bar.destroy)

        # Define the main master -> app of main.py
        main_master = self.master.master

        # Decrese the ongoing mission and update menu bar
        main_master.ongoing_mission -= 1
        main_master.menu_bar.update_ongoing_mission(main_master.ongoing_mission)

        # Update garbage
        #print(f'DEBOUG Actual garbage counter {main_master.garbage_collected}')
        #print(f'DEBOUG id mission {id_mission} con garbage value {main_master.mission_info[id_mission]["value_of_map"]}')
        main_master.garbage_collected += main_master.mission_info[id_mission]["value_of_map"]
        main_master.menu_bar.update_garbage(main_master.garbage_collected)
        
        # Update vessel availability
        #print(f'DEBOUG Actual vessel counter {main_master.vessel_available}')
        #print(f'DEBOUG id mission {id_mission} con vessel value {main_master.mission_info[id_mission]["number_of_vessels"]}')
        main_master.vessel_available += main_master.mission_info[id_mission]["number_of_vessels"]
        main_master.menu_bar.update_vessel_availability(main_master.vessel_available)

        print(f"Mission completed #{id_mission}")
        text_ = f"Mission completed #{id_mission}"
        self.master.log_frame.add_text(text_)



# Define a new ProgressBar
class ProgressBar(customtkinter.CTkProgressBar):
    def __init__(self, master,id_mission, max_time=5000, update_interval=50):
        super().__init__(master ,height=25, corner_radius=12, progress_color="green", border_color="black")
        self.progress = 0
        self.max_time = max_time
        self.update_interval = update_interval
        self.set(0)
        self.green = (0, 255, 0)
        self.yellow = (255, 255, 0)
        self.red = (255, 0, 0)

        # Correlate progress bar with mission id
        self.id_mission = id_mission

    def start_progress(self):
        self.update_progress()

    def update_progress(self):
        if self.progress < 1:
            self.progress += self.update_interval / self.max_time
            self.set(self.progress)
            # Dynamically calculate the color based on the progress percentage
            self.change_color_based_on_progress(self.progress * 100)

            self.after(self.update_interval, self.update_progress)
        else:
            self.set(1)
            self.change_color_based_on_progress(100)  # Set the final color at 100%

            # After finish the progression of the bar, call update and destroy function
            self.master.master.update_and_remove_status(self.master, self.id_mission) 
            #print(f"DEBOUG Mission {self.id_mission} passed to updater of end mission")

    
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
        