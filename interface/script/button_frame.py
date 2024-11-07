import customtkinter

class LogFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.label = customtkinter.CTkLabel(self, text="Log:")
        self.label.grid(row=0, column=0, padx=10, pady=5, sticky="nw")

        self.text_box = customtkinter.CTkTextbox(self, width=1000 ,border_width=1, border_color="black")
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
        self.id_mission = id_mission

        frame = customtkinter.CTkFrame(self, fg_color="#2B2B2B")
        frame.grid(padx=10, pady=5)

        self.grid_columnconfigure(0, weight=1)


        label = customtkinter.CTkLabel(frame, text=text)
        label.grid(row=0, column=0, padx=5, pady=5)

        progress_bar = ProgressBar(frame, max_time=max_time, update_interval=update_interval)
        progress_bar.grid(row=0, column=1, padx=5, pady=5)

        progress_bar.start_progress()

        self.status_list.append(frame)
    
    def update_and_remove_status(self, frame_bar):
        #destroy frame
        self.after(2000, frame_bar.destroy)

        main_master = self.master.master

        #update ongoing mission
        main_master.ongoing_mission -= 1
        main_master.menu_bar.update_ongoing_mission(main_master.ongoing_mission)

        # Update garbage
        main_master.garbage_collected += main_master.mission_info[self.id_mission]["value_of_map"]
        main_master.menu_bar.update_garbage(main_master.garbage_collected)
        
        # Update vessel availability
        main_master.vessel_available += main_master.mission_info[self.id_mission]["number_of_vessels"]
        main_master.menu_bar.update_vessel_availability(main_master.vessel_available)

        print(f"Mission completed #{main_master.ongoing_mission}")

class ButtonFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.log_frame = LogFrame(self)
        self.log_frame.grid(row=0, column=0, padx=(0,20), sticky="nsew")

        self.status_frame = StatusFrame(self)
        self.status_frame.grid(row=0, column=2, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0,1), weight=1)

# Assuming ProgressBar is defined as in left_frame.py
class ProgressBar(customtkinter.CTkProgressBar):
    def __init__(self, master, max_time=5000, update_interval=50):
        super().__init__(master ,height=25, corner_radius=12, progress_color="green", border_color="black")
        self.progress = 0
        self.max_time = max_time
        self.update_interval = update_interval
        self.set(0)
        self.green = (0, 255, 0)
        self.yellow = (255, 255, 0)
        self.red = (255, 0, 0)

    def start_progress(self):
        self.update_progress()

    def update_progress(self):
        if self.progress < 1:
            self.progress += self.update_interval / self.max_time
            self.set(self.progress)
            self.after(self.update_interval, self.update_progress)
        else:
            self.set(1)
            self.configure(progress_color="red")

            self.master.master.update_and_remove_status(self.master)