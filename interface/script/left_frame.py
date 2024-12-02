'''
This module contains the LeftFrame class, which is a custom tkinter frame that contains the settings for the mission profile.



The width of first label is fixed and is equal to the width of right_frame in order to have a simmetry.

'''

import customtkinter
from button_frame import MissionProgressBar
import ast # To convert string to tuple


class LeftFrame(customtkinter.CTkFrame):
    """Left Frame that contains the settings for the mission profile."""

    def __init__(self, master, font_size=16, side_panel_width=300):
        super().__init__(master, fg_color="#4D4D4D") # Set the frame color to match the background in order to hide it

        # Set the font size for child widgets
        self.font_size = font_size

        # Set the padding and spacing between widgets
        self.upper_down_space = 15
        self.label_box_space = 5
        self.inter_widget_space = 50

        # Configuring the frame's grid layout 
        self.grid_rowconfigure(19, weight=3)  # Allow the widgets to expand vertically and occupy all the bar space
        self.grid_columnconfigure(0, weight=1) 

        # Label 
        self.title = customtkinter.CTkLabel(self, text="Mission Profile", width=side_panel_width, font=(None, font_size), corner_radius=6)
        self.title.grid(row=0, padx=10, pady=(self.upper_down_space, self.inter_widget_space), sticky="n")

        # Coordinates
        # Label for coordinate
        self.coordinate_label = customtkinter.CTkLabel(self, text="Coordinate selected", font=(None, font_size), corner_radius=6)
        self.coordinate_label.grid(row=1, pady=(0, self.label_box_space))
        # Coordinate entry box
        self.coordinate_box = customtkinter.CTkEntry(self, width=font_size*5, height=font_size*2, font=(None, font_size), border_width=0, justify="center")
        self.coordinate_box.grid(row=2, padx=10, pady=(0, self.inter_widget_space))

        # Boat selection
        # Label for "Select the number of boats"
        self.vessel_label = customtkinter.CTkLabel(self, text="Number of Vessels involved", font=(None, font_size), corner_radius=6)
        self.vessel_label.grid(row=3, pady=(0, self.label_box_space))
        # Spinbox for selecting boats
        self.spinbox_1 = FloatSpinbox(self, font_size=font_size)
        self.spinbox_1.set(1)
        self.spinbox_1.grid(row=4, padx=10, pady=(0, self.inter_widget_space))

        # Label advice from systems 
        self.advice_label = customtkinter.CTkLabel(self, text="Suggested vessels", font=(None, font_size), corner_radius=6)
        self.advice_label.grid(row=5, pady=(0, 0))
        self.advice_info_label = customtkinter.CTkLabel(self, text="for optimal cleaning of the area:", font=(None, font_size), corner_radius=6)
        self.advice_info_label.grid(row=6, pady=(0, self.label_box_space))
        # Entry box for the suggested number of vessels
        self.advice_box = customtkinter.CTkEntry(self, width=font_size*3, height=font_size*2, font=(None, font_size), border_width=0, justify="center")
        self.advice_box.configure(state="disabled")
        self.advice_box.grid(row=7, padx=10, pady=(0, self.inter_widget_space))

        # Info text to display when the frame is locked
        self.tutorial_info = customtkinter.CTkLabel(self, 
                                                  text="To start a new mission,\nselect a target cell on the map", 
                                                  font=(None, font_size, "underline"),)
        self.tutorial_info.grid(row=8, pady=(0, 0)) #self.inter_widget_space))  # Will be replaced by the upload status 
                                                    # so add a space to avoid overlapping
        # Button to launch the mission
        # Keep track of the button state
        self.launch_already_pressed = False
        self.uploading_data = False
        self.bottom_button = customtkinter.CTkButton(self,
                                                     text="LAUNCH MISSION",
                                                     font=(None, font_size), 
                                                     fg_color="gray", 
                                                     hover_color="gray",
                                                     command=self.launch_callback_deactive)
        self.bottom_button.grid(row=20, padx=30, pady=(0, self.upper_down_space), sticky="ew")  # Stick to bottom 

        # Lock the frame initially
        self.unlock = False  
        self.spinbox_1.entry.configure(state="disabled")
        self.coordinate_box.configure(state="disabled")

    def unlock_frame(self):
        """Unlock the frame to allow user interaction."""

        # Enable the widgets if the frame is unlocked only once
        if not self.unlock:
            print("Frame unlocked")  
            self.master.button_frame.log_frame.add_text("Frame unlocked")

            self.configure(fg_color="#2B2B2B")
            self.tutorial_info.configure(text="")  # Remove the text to make the row smaller
            self.coordinate_box.configure(state="normal")
            self.spinbox_1.entry.configure(state="normal")
            self.spinbox_1.subtract_button.configure(fg_color="blue")
            self.spinbox_1.subtract_button.configure(hover_color="darkblue")
            self.spinbox_1.add_button.configure(fg_color="blue")
            self.spinbox_1.add_button.configure(hover_color="darkblue")
            self.spinbox_1.configure(fg_color="#2B2B2B")
            self.advice_box.configure(state="normal")
            self.bottom_button.configure(command=self.launch_callback)
            self.bottom_button.configure(hover_color="darkblue")
            self.bottom_button.configure(fg_color="blue")

        self.unlock = True

    def update_coordinate_box(self, row, col):
        """Update the coordinate box with the selected coordinates."""
        self.coordinate_box.delete(0, "end")
        self.coordinate_box.insert(0, f"({row}, {col})")

    def launch_callback_deactive(self):
        """Display an error message if the frame is locked and try to click the button."""
        self.error_text = '''This option is blocked:\n
        please select a target cell to unlock it'''
        TopViewError(self.error_text, self.font_size)

    def launch_callback(self):
        """Launch the mission and update the mission data."""
        # Catch the error if no target is selected
        try:
            # Check if the last clicked button has a value of garbage
            if self.master.central_frame.matrix_button.last_clicked_value:
                # Check if the number of boats is selected
                if int(self.spinbox_1.get_spin_value()) != 0:
                    # Check if the uploading process is already in progress
                    if not self.launch_already_pressed:

                        # log and print the button launch pressed
                        print("Button launch pressed")
                        text_ = "Button launch pressed"
                        self.master.button_frame.log_frame.add_text(text_)
                        
                        print(f'DEBUG {self.master.count_mission} missions launched')

                        # GET SELECTED INFO
                        # Get the current mission ID
                        self.master.count_mission += 1
                        self.id_mission = self.master.count_mission
                        # Get the selected coordinates
                        self.coordinates = self.coordinate_box.get()
                        # Get the number of vessels
                        self.number_of_vessels = int(self.spinbox_1.get_spin_value())
                        # Get the value of the map at the selected coordinates
                        self.value_of_map = self.master.central_frame.matrix_button.last_clicked_value

                        print(f"DEBUG: Mission ID: {self.id_mission}")

                        # Save the mission data
                        self.save_mission_data(id_mission=self.id_mission, 
                                               coordinates=self.coordinates,
                                               number_of_vessels=self.number_of_vessels,
                                               value_of_map=self.value_of_map)


                        # Create a label to display the upload status
                        self.upload_status = customtkinter.CTkLabel(self, text="Uploading data...", font=(None, self.font_size), corner_radius=6)
                        self.upload_status.grid(row=8, pady=(0, self.label_box_space))  # Rewrite the tutorial info
                        # Create a progress bar
                        self.progress_bar = MissionProgressBar(self,
                                                               id_mission=self.id_mission,
                                                               max_time=4000,
                                                               update_interval=50,
                                                               callback=self.end_progress,
                                                               width=150)
                        self.progress_bar.grid(row=9, pady=(0, self.inter_widget_space))

                        # Start the progression bar and call the callback at the end
                        self.progress_bar.update_progress()

                        # Set the uploading data flag to prevent multiple uploads
                        self.launch_already_pressed = True


        # HANDLE ERRORS
                else:
                    # log and print the error message
                    print("You can't launch mission without select the number of boat")
                    text_ = "You can't launch mission without select the number of boat"
                    self.master.button_frame.log_frame.add_text(text_)
            else:
                # popup an error message if no target is selected
                self.text = "The mission target is empty!\n\nPlease select a valid target before launching the mission."
                # Puopup an error message if no target is selected
                TopViewError(self.text, self.font_size)

                # log and print the error message
                self.text = "The mission target is empty! Please select a valid target before launching the mission."
                print(self.text)
                self.master.button_frame.log_frame.add_text(self.text)

        except AttributeError:
            # log and print the error message
            print("You can't launch mission without selected target")
            text_ = "You can't launch mission without selected target"
            self.master.button_frame.log_frame.add_text(text_)

    
    def end_progress(self):
        '''At the end of the progress bar:
          add the mission to the mission frame, 
          update the number of boat counter on the spinbox, 
          clean the value and color on cell (on the matrix map) and label after a delay,
        '''

        # Print and log the upploaded data
        print('Data uploaded successfully, mission started')
        self.master.button_frame.log_frame.add_text('Data uploaded successfully, mission started')

        # Add the mission to the mission frame
        self.master.button_frame.status_frame.add_status(self.id_mission)

        # Update the number of boat counter on the spinbox
        self.update_spinbox_vessel_counter()

        # Update the upload status label
        self.upload_status.configure(text="") # Prevent glitch
        self.upload_status.configure(text="Uploading complete!")
        # Delete the upload status and progress bar after a delay
        self.after(5000, self.upload_status.destroy)
        self.after(5000, self.progress_bar.destroy)

        # Clean the value and color on cell (on the matrix map) after a delay
        self.clean_last_mission_cell(self.id_mission)

        # Reset the launch button state
        self.launch_already_pressed = False

    def update_spinbox_vessel_counter(self):
        '''Update the number of boat counter on the spinbox, using the available vessels and adviced number of vessels'''
        
        if self.master.vessel_available == 0:
            self.spinbox_1.set(0)
        elif self.master.vessel_available >= self.master.central_frame.matrix_button.last_clicked_value//20:
            self.spinbox_1.set(self.master.central_frame.matrix_button.last_clicked_value//20)
        else:
            self.spinbox_1.set(1)

    def save_mission_data(self, id_mission, coordinates, number_of_vessels, value_of_map):
        """Save the mission data to the mission info dictionary."""

        # Create the mission data dictionary
        mission_data = {
            "id": id_mission,                    
            "coordinates": coordinates,
            "number_of_vessels": number_of_vessels,
            "value_of_map": value_of_map,
        }

        # Save the mission data to the mission info dictionary
        self.master.mission_info[id_mission] = mission_data

        print(f"Mission data saved: {self.master.mission_info[id_mission]}")  



    def clean_last_mission_cell(self, id_mission):
        """Clean the last clicked button after a delay."""
        
        coordinates_tuple = ast.literal_eval(self.master.mission_info[id_mission]["coordinates"])
        
        self.master.central_frame.matrix_button.clean_button(coordinates_tuple[0], coordinates_tuple[1])
            

   
class FloatSpinbox(customtkinter.CTkFrame):
    """Spinbox class with buttons to increase and decrease the value"""
    def __init__(self, master, font_size=16):
        super().__init__(master, width=40, corner_radius=0)

        self.command = None

        # Set the font size for child widgets
        self.font_size = font_size

        # Set the step size when the buttons are pressed
        self.step_size = 1

        # Set dimensions rateo
        self.height_text = font_size*2
        self.width_stepper = font_size*2

        # Set the frame color to match the background in order to hide it
        self.configure(fg_color="#4D4D4D")  

        # Configuring the grid layout
        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        # COMPONENTS of spinbox
        # minus button
        self.subtract_button = customtkinter.CTkButton(self, 
                                                       text="-", 
                                                       font=(None, font_size),
                                                       width=self.width_stepper, 
                                                       height=self.height_text,
                                                       command=self.subtract_button_callback,
                                                       fg_color="gray",
                                                       hover_color="gray",
                                                       corner_radius=9)  
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        # text entry
        self.entry = customtkinter.CTkEntry(self, 
                                            font=(None, font_size),
                                            width=font_size*5, 
                                            height=self.height_text,
                                            border_width=0, 
                                            justify="center")
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        # plus button
        self.add_button = customtkinter.CTkButton(self, 
                                                  text="+", 
                                                  font=(None, font_size),
                                                  width=self.width_stepper, 
                                                  height=self.height_text,
                                                  command=self.add_button_callback,
                                                  fg_color="gray",
                                                  hover_color="gray",
                                                  corner_radius=9)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        # Set default value
        self.entry.insert(0, "0")

    def add_button_callback(self):
        '''Increase the value of the spinbox.
        If the value is greater than the available vessels, display an error message.'''

        if self.command is not None:
            self.command()
        try:
            if int(self.entry.get()) < int(self.master.master.vessel_available):
                value = int(self.entry.get()) + self.step_size
                self.entry.delete(0, "end")
                self.entry.insert(0, value)

            else: 
                # Vessels requested is greater than the available vessels

                # Popup an error message
                self.text = f'''Current number of vessels: {self.master.master.vessel_available}
                Vessel requested: {int(self.entry.get())}\n\nNo more vessels available!
                '''
                TopViewError(self.text, self.font_size)
                
                # Print anf Log the error message
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
    def __init__(self, text, font_size=16 ):
        super().__init__()
        self.geometry()
        self.title("Error message")

        # Keep the window on top
        self.attributes("-topmost", True)

        self.grid_columnconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self, text=text, font=(None, font_size))
        self.label.grid(padx=20, pady=20, sticky="ew")

        self.button = customtkinter.CTkButton(self, text="Okay", font=(None, font_size), command=self.destroy)
        self.button.grid(pady=20, padx=20 ,sticky="ew")




# Test the left frame class
if __name__ == "__main__":
    app = customtkinter.CTk()

    left_frame = LeftFrame(app)
    left_frame.grid(row=1, column=0, padx=(0,10), sticky="nsew")

    app.mainloop()