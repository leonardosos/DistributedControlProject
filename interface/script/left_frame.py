import customtkinter


class LeftFrame(customtkinter.CTkFrame):
    """Left frame with settings"""

    def __init__(self, master):
        super().__init__(master, fg_color="#4D4D4D")

        # Configuring the frame's grid layout to allow expansion of rows
        self.grid_rowconfigure(9, weight=3)  # Allow row 6 (before bottom_button) to expand
        self.grid_columnconfigure(0, weight=1)  # Allow the frame to expand horizontally

        # Label 
        self.title = customtkinter.CTkLabel(self, text="Mission Profile", corner_radius=6)
        self.title.grid(row=0, padx=10, pady=15, sticky="n")

        # Label for "Coordinate selected target"
        self.text = "To start a new mission, select a target cell on the map"
        self.text = customtkinter.CTkLabel(self, text=self.text, corner_radius=6)
        self.text.grid(row=1, pady=(50, 5))

        # Coordinate entry box
        self.coordinate_box = customtkinter.CTkEntry(self, width=150, height=30, border_width=0, justify="center")
        self.coordinate_box.grid(row=2, padx=10)

        # Label for "Select the number of boats"
        self.text = "Number of Vessels involved"
        self.text = customtkinter.CTkLabel(self, text=self.text, corner_radius=6)
        self.text.grid(row=3, pady=(50, 5))

        # Spinbox for selecting boats
        self.spinbox_1 = FloatSpinbox(self, width=150, step_size=1)
        self.spinbox_1.set(1)
        self.spinbox_1.grid(row=4, padx=10)

        # Creating an empty row that will expand to push the button down
        self.empty_space = customtkinter.CTkLabel(self, text="")#THIS FRAME IS LOCKED.\nSELECT A TARGET TO UNLOCK")  # An empty label creates space
        self.empty_space.grid(row=5, pady=(20, 5))  # Row 5 is a spacer

        # Button to confirm the selected target, positioned at the bottom
        self.launch_already_pressed = False
        self.uploading_data = False
        self.bottom_button = customtkinter.CTkButton(self,
                                                     text="LAUNCH MISSION", 
                                                     fg_color="gray", 
                                                     #width=250,
                                                     hover_color="gray",
                                                     command=self.launch_callback_deactive)
        self.bottom_button.grid(row=10, padx=30, pady=15, sticky="ew")  # Stick to bottom 

        # Lock the frame initially
        self.unlock = False  
        self.spinbox_1.entry.configure(state="disabled")
        #self.bottom_button.configure(state="disabled")
        self.coordinate_box.configure(state="disabled")

    def unlock_frame(self):
        """Unlock the frame to allow user interaction."""

        # Enable the widgets if the frame is unlocked only once
        if not self.unlock:
            print("Frame unlocked")  
            self.master.button_frame.log_frame.add_text("Frame unlocked")

            self.configure(fg_color="#2B2B2B")
            self.empty_space.configure(text="")  # Remove the text to make the row smaller
            self.coordinate_box.configure(state="normal")
            self.spinbox_1.entry.configure(state="normal")
            self.spinbox_1.subtract_button.configure(fg_color="blue")
            self.spinbox_1.subtract_button.configure(hover_color="darkblue")
            self.spinbox_1.add_button.configure(fg_color="blue")
            self.spinbox_1.add_button.configure(hover_color="darkblue")
            self.bottom_button.configure(command=self.launch_callback)
            self.bottom_button.configure(hover_color="darkblue")
            #self.bottom_button.configure(state="normal")
            self.bottom_button.configure(fg_color="blue")

        self.unlock = True

    def update_coordinate_box(self, row, col):
        """Update the coordinate box with the selected coordinates."""
        self.coordinate_box.delete(0, "end")
        self.coordinate_box.insert(0, f"({row}, {col})")

    def launch_callback_deactive(self):
        self.error_text = '''This option is blocked:\n
        please select a target cell to unlock it'''
        TopViewError(self.error_text)

    def launch_callback(self):
        # Catch the error if no target is selected
        try:
            # Check if the last clicked button has a value of garbage
            if self.master.central_frame.matrix_button.last_clicked_value:
                # Check if the number of boats is selected
                if int(self.spinbox_1.get_spin_value()) != 0:

                    print(f"Number of boats selected: {self.spinbox_1.get_spin_value()}")  
                    
                    text_ = f"Number of boats selected: {self.spinbox_1.get_spin_value()}"
                    self.master.button_frame.log_frame.add_text(text_)

                    print("Button launch pressed")

                    text_ = "Button launch pressed"
                    self.master.button_frame.log_frame.add_text(text_)
                    
                    # Check if the uploading process is already in progress
                    if not self.launch_already_pressed:

                        # Create a label to display the upload status
                        self.text = "Uploading data..."
                        self.upload_status = customtkinter.CTkLabel(self, text=self.text, corner_radius=6)
                        self.upload_status.grid(row=6 ,pady=(0, 5))
                        # Create a progress bar
                        self.progress_bar = ProgressBar(self) 
                        self.progress_bar.grid(row=7)

                        # CORE FUNCTIONALITY

                        # Save the mission data
                        self.save_mission_data()

                        # Update the number of vessels available  
                        self.master.vessel_available -= int(self.spinbox_1.get_spin_value())
                        self.master.menu_bar.update_vessel_availability(self.master.vessel_available)

                        # Start the progress and at the end handle the mission data updates
                        self.progress_bar.start_progress(self.master.count_mission)

                        print("Data uploading progress is started!")

                        # Set the uploading data flag to True to prevent multiple uploads
                        self.launch_already_pressed = True

                        # Clean the target area after a delay
                        self.after(900, self.clean_last_clicked_button)

                else:
                    print("You can't launch mission without select the number of boat")

                    text_ = "You can't launch mission without select the number of boat"
                    self.master.button_frame.log_frame.add_text(text_)
            else:
                self.text = "The mission target is empty!\n\nPlease select a valid target before launching the mission."
                # Puopup an error message if no target is selected
                TopViewError(self.text)

                self.text = "The mission target is empty! Please select a valid target before launching the mission."
                print(self.text)
                self.master.button_frame.log_frame.add_text(self.text)

        except AttributeError:
            print("You can't launch mission without selected target")

            text_ = "You can't launch mission without selected target"
            self.master.button_frame.log_frame.add_text(text_)

    
    def save_mission_data(self):
        """Save the mission data to the mission info dictionary."""
        # Get the current mission ID and increment it
        self.master.count_mission += 1

        # Get the selected coordinates
        coordinates = self.coordinate_box.get()

        # Get the number of vessels
        number_of_vessels = int(self.spinbox_1.get_spin_value())

        # Get the value of the map at the selected coordinates
        value_of_map = self.master.central_frame.matrix_button.last_clicked_value

        # Create the mission data dictionary
        mission_data = {
            "id": self.master.count_mission, # same as the key in the mission_info dictionary
            "coordinates": coordinates,
            "number_of_vessels": number_of_vessels,
            "value_of_map": value_of_map,
        }

        # Save the mission data to the mission info dictionary
        self.master.mission_info[self.master.count_mission] = mission_data

        print(f"Mission data saved: {self.master.mission_info[self.master.count_mission]}")

        text_ = f"Mission data saved: {self.master.mission_info[self.master.count_mission]}"
        self.master.button_frame.log_frame.add_text(text_)

        

    def clean_last_clicked_button(self):
        """Clean the last clicked button after a delay."""
        if self.master.central_frame.matrix_button.last_clicked_button:
            row = self.master.central_frame.matrix_button.last_clicked_button.grid_info()["row"]
            col = self.master.central_frame.matrix_button.last_clicked_button.grid_info()["column"]
            self.master.central_frame.matrix_button.clean_button(row, col)
            
    def mission_data_updates(self):
        """Update on going mission and destroy status bar"""
        print("Updating mission data...")
        self.master.button_frame.log_frame.add_text("Updating mission data...")

        # Clean up the left frame progress bar and status text
        self.upload_status.configure(text="Uploading complete!")

        # Update the number of ongoing missions
        self.master.ongoing_mission += 1
        self.master.menu_bar.update_ongoing_mission(self.master.ongoing_mission)

        # Update number of boat counter
        if self.master.vessel_available == 0:
            self.spinbox_1.set(0)
        else:
            self.spinbox_1.set(1)

        # Reset the launch button state
        self.launch_already_pressed = False

        print('Updated')
        self.master.button_frame.log_frame.add_text("Updated")

        self.after(5000, self.upload_status.destroy)
        self.after(5000, self.progress_bar.destroy)

    
class ProgressBar(customtkinter.CTkProgressBar):
    def __init__(self, master, max_time=4000, update_interval=50):
        """Create a progress bar that completes and changes color smoothly over max_time milliseconds."""
        
        self.height = 25  # Progress bar height

        super().__init__(master,
                         width=150,
                         height=self.height,
                         corner_radius=self.height // 2,
                         progress_color="green",  # Start with green initially
                         border_color="black",
                         )

        # Progress bar state
        self.progress = 0  # Initial progress (0%)
        self.max_time = max_time  # Total time to complete progress bar in ms
        self.update_interval = update_interval  # How often to update the progress bar (in ms)

        # Set the initial value of the progress bar to 0
        self.set(0)

        # Define the gradient colors as RGB tuples
        self.green = (0, 255, 0)  # Green
        self.yellow = (255, 255, 0)  # Yellow
        self.red = (255, 0, 0)  # Red


    def start_progress(self, count_mission):
        """Increment the progress bar keeping the countmission parameter"""
        # Calculate how much progress to increment in each update
        increments = self.update_interval / self.max_time
        self.progress += increments  # Update the progress

        if self.progress <= 1:
            # Update the progress bar's visual display
            self.set(self.progress)
            
            # Dynamically calculate the color based on the progress percentage
            self.change_color_based_on_progress(self.progress * 100)

            # Re-run this function after `update_interval` milliseconds
            self.after(self.update_interval, lambda: self.start_progress(count_mission))
        else:
            # Ensure the progress is fully filled to 100%
            self.set(1)
            self.change_color_based_on_progress(100)  # Set the final color at 100%
            
            print("Progress complete!")
            self.master.master.button_frame.log_frame.add_text("Progress complete!")

            # Update mission on going on and destroy progress bar
            self.master.mission_data_updates()

            # Create status bar on bottom frame
            self.master.master.button_frame.status_frame.add_status(count_mission)
            print(f'A new mission has been added to the status list: {count_mission} with id {count_mission}')

            text_ = f'A new mission has been added to the status list: {count_mission} with id {count_mission}'
            self.master.master.button_frame.log_frame.add_text(text_)

            return
        
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

class FloatSpinbox(customtkinter.CTkFrame):
    """Spinbox class with buttons to increase and decrease the value"""
    def __init__(self, master, width=40, height=30, step_size=1, command=None):
        super().__init__(master, width=width, height=height)

        self.step_size = step_size
        self.command = command

        self.configure(fg_color=("gray78", "gray28"))  # set frame color

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.subtract_button = customtkinter.CTkButton(self, text="-", width=height-6, height=height-6,
                                                       command=self.subtract_button_callback,
                                                       fg_color="gray",
                                                       hover_color="gray")  
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = customtkinter.CTkEntry(self, width=width-(2*height), height=height-6, border_width=0, justify="center")
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=height-6, height=height-6,
                                                  command=self.add_button_callback,
                                                  fg_color="gray",
                                                  hover_color="gray")
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        # default value
        self.entry.insert(0, "0")

    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            if int(self.entry.get()) < int(self.master.master.vessel_available):
                value = int(self.entry.get()) + self.step_size
                self.entry.delete(0, "end")
                self.entry.insert(0, value)
            else:
                # Display error
                self.text = f'''Current number of vessels: {self.master.master.vessel_available}
                Vessel requested: {int(self.entry.get())}\n\nNo more vessels available!
                '''
                TopViewError(self.text)
                
                self.text = f"No more vessels available! Max number of vessels: {self.master.master.vessel_available}"
                self.master.master.button_frame.log_frame.add_text(self.text)
                print(self.text)
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            if int(self.entry.get()) > 0:
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

class TopViewError(customtkinter.CTkToplevel):
    def __init__(self, text ,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry()
        self.title("Error message")

        self.grid_columnconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self, text=text)
        self.label.grid(padx=20, pady=20, sticky="ew")

        # Keep the window on top
        self.attributes("-topmost", True)

        self.button = customtkinter.CTkButton(self, text="Okay", command=self.destroy)
        self.button.grid(pady=20, padx=20 ,sticky="ew")