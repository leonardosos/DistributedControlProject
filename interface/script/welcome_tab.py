import customtkinter

class WelcomeTab(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x370")
        self.title("Welcome Message")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self, text="Welcome to the mission control interface", font=(None, 15, "bold"))
        self.label.grid(padx=20, pady=20, sticky="ew")

        self.text = '''
        Here you can:\n
        • Obtain information about the garbage distribution\n
        • Launch a new mission\n
        • Get updates on the ongoing mission\n
        '''

        self.label = customtkinter.CTkLabel(self, text=self.text, anchor="w", justify="left", font=(None, 14))
        self.label.grid(padx=20, pady=20, sticky="ew")

        # Keep the window on top
        self.attributes("-topmost", True)

        self.button = customtkinter.CTkButton(self, text="Okay", command=self.destroy)
        self.button.grid(pady=20, padx=20 ,sticky="ew")

if __name__ == "__main__":
    app = WelcomeTab()
    app.mainloop()