'''
This script creates a welcome message window that poup-up when the user opens the application.
'''

from ast import arg
import customtkinter

class WelcomeTab(customtkinter.CTkToplevel):
    def __init__(self, font_size=16):
        super().__init__()

        # Set the window size and title
        self.geometry("700x500")
        self.title("Welcome Message")

        # Grid configuration for the window
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create the bold label on top
        self.label = customtkinter.CTkLabel(self, text="Welcome to the mission control interface", font=(None, font_size+3, "bold"))
        self.label.grid(padx=20, pady=20, sticky="ew")

        # Create the text below the label
        self.text = '''
        Here you can:\n
        • Obtain information about the garbage distribution\n
        • Launch a new mission\n
        • Get updates on the ongoing mission\n
        '''

        self.label = customtkinter.CTkLabel(self, text=self.text, anchor="w", justify="left", font=(None, font_size))
        self.label.grid(padx=20, pady=20, sticky="ew")

        # Keep the window on top
        self.attributes("-topmost", True)

        # Create the button to close the window
        self.button = customtkinter.CTkButton(self, text="Okay", command=self.destroy, font=(None, font_size))
        self.button.grid(pady=20, padx=20 ,sticky="ew")

if __name__ == "__main__":
    app = WelcomeTab()
    app.mainloop()