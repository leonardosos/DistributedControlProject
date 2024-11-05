import customtkinter
import json
import os

from left_frame import LeftFrame
from central_frame import CentralFrame



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mission control")
        self.geometry("800x650")
        customtkinter.set_appearance_mode("dark")
        #self.grid_columnconfigure((0, 1), weight=1)
        #self.grid_rowconfigure((0,1), weight=1)


        # Center Frame with a Matrix of Buttons
        self.central_frame = CentralFrame(self)
        self.central_frame.grid(row=0, column=1, padx=10, pady=10)

        #self.bottom_button_already_pressed = False

        # Left Frame 
        self.left_frame = LeftFrame(self)
        self.left_frame.grid(row=0, column=0, padx=(0,10), pady=10, sticky="nsew") #need to be equal to left_frame_empty
        

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()