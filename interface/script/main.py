
import customtkinter

from left_frame import LeftFrame
from central_frame import CentralFrame
from right_frame import RightFrame


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mission control")
        self.geometry("1600x800")
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_widget_scaling(1.2)  # widget dimensions and text size

        self.grid_columnconfigure((0,1,2), weight=1)
        self.grid_rowconfigure((0,1,2), weight=1)

        
        # Left Frame 
        self.left_frame = LeftFrame(self)
        self.left_frame.grid(row=1, column=0, padx=(0,10), pady=10, sticky="nsew") 

        # Center Frame with a Matrix of Buttons
        self.central_frame = CentralFrame(self)
        self.central_frame.grid(row=1, column=1, padx=10, pady=10)

        # Right Frame
        self.right_frame = RightFrame(self)
        self.right_frame.grid(row=1, column=2, padx=(0,10), pady=10, sticky="nsew")


def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()