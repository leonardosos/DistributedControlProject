
import customtkinter

from left_frame import LeftFrame
from central_frame import CentralFrame
from right_frame import RightFrame
from welcome_tab import WelcomeTab
from menu_bar import MenuBar
from button_frame import ButtonFrame


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mission control")
        self.geometry("1600x930")
        customtkinter.set_appearance_mode("dark")
        #customtkinter.set_widget_scaling(1.2)  # widget dimensions and text size

        self.grid_columnconfigure((0,1,2), weight=1)
        self.grid_rowconfigure((0,1,2), weight=1)

        # Welcome Tab
        # self.welcome_tab = WelcomeTab(self)

        self.count_mission = 0
        self.ongoing_mission = 0
        self.vessel_available = 4
        self.garbage_collected = 0
        self.mission_info = dict()

        # Menu Bar
        self.menu_bar = MenuBar(self)
        self.menu_bar.grid(row=0, column=0, columnspan=3, sticky="new")
        self.menu_bar.update_vessel_availability(self.vessel_available)
        self.menu_bar.update_ongoing_mission(self.ongoing_mission)
        self.menu_bar.update_garbage(self.garbage_collected)
        
        # Left Frame 
        self.left_frame = LeftFrame(self)
        self.left_frame.grid(row=1, column=0, padx=(0,10), pady=10, sticky="nsew") 

        # Center Frame with a Matrix of Buttons
        self.central_frame = CentralFrame(self)
        self.central_frame.grid(row=1, column=1, padx=10, pady=10)

        # Right Frame
        self.right_frame = RightFrame(self)
        self.right_frame.grid(row=1, column=2, padx=(10,0), pady=10, sticky="nsew")

        # Button Frame
        self.button_frame = ButtonFrame(self)
        self.button_frame.grid(row=2, column=0, columnspan=3, sticky="nsew")


def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()