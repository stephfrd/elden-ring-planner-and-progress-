import customtkinter as ctk
from PIL import Image
import time
import threading
import requests
from io import BytesIO
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
try:
    from progress_tracker import ProgressTrackerFrame
    from planner import BuildPlannerFrame
except ImportError:
    # Dummy classes for testing if files are missing
    class ProgressTrackerFrame(ctk.CTkFrame):
        pass
    class BuildPlannerFrame(ctk.CTkFrame):
        pass
class EldenApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Elden Ring UwU")
        self.configure(fg_color="black")
        self.geometry("1200x800")
        self.bind("<F11>", lambda e: self.attributes("-fullscreen", not self.attributes("-fullscreen")))
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        self.SOFT_PINK = "#F2D1D1"
        self.BTN_PINK = "#E5B1B1"
        self.ELDEN_GREEN = "#A8FFB5"
        self.POPUP_GREEN_BG = "#0A2F0A"  # Dark green for boxes
        self.POPUP_BTN_GREEN = "#145214"  # Green for buttons
        self.START_IMG_URL = "https://image.api.playstation.com/vulcan/img/rnd/202111/0506/hcFeWRVGHYK72uOw6Mn6f4Ms.jpg"
        self.STORMVEIL_URL = "https://upload.wikimedia.org/wikipedia/en/f/f9/Elden_Ring_Stormveil_Castle.png"
        self.RANNI_IMG_URL = "https://static0.polygonimages.com/wordpress/wp-content/uploads/chorus/uploads/chorus_asset/file/23325398/Elden_Ring_Ranni_questline.png?w=1600&h=900&fit=crop"
        self.user_checked_list = set()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tracker_page = ProgressTrackerFrame(self, self.SOFT_PINK, self.BTN_PINK, self.show_main_menu)
        self.planner_page = BuildPlannerFrame(self, self.SOFT_PINK, self.BTN_PINK, self.show_main_menu,
                                              self.user_checked_list)
        self.menu_container = ctk.CTkFrame(self, fg_color="black")
        self.menu_container.grid(row=0, column=0, sticky="nsew")

        self.show_start_screen()

    def create_custom_popup(self, message, yes_text, no_text, yes_cmd):
        """Creates the green and pink styled pop-up windows."""
        popup = ctk.CTkToplevel(self)
        popup.title("Elden Ring")
        popup.geometry("450x220")
        popup.configure(fg_color=self.POPUP_GREEN_BG)
        popup.attributes("-topmost", True)
        popup.grab_set()  # Lock interaction to this window

        label = ctk.CTkLabel(popup, text=message, font=("Times New Roman", 24, "bold"),
                             text_color=self.SOFT_PINK)
        label.pack(pady=40)

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text=yes_text, width=150, height=45,
                      fg_color=self.POPUP_BTN_GREEN, text_color=self.SOFT_PINK,
                      border_color=self.SOFT_PINK, border_width=2,
                      font=("Arial", 14, "bold"),
                      command=lambda: [popup.destroy(), yes_cmd()]).pack(side="left", padx=15)
        ctk.CTkButton(btn_frame, text=no_text, width=150, height=45,
                      fg_color=self.POPUP_BTN_GREEN, text_color=self.SOFT_PINK,
                      border_color=self.SOFT_PINK, border_width=2,
                      font=("Arial", 14, "bold"),
                      command=popup.destroy).pack(side="left", padx=15)
    def step_1_quit(self):
        self.create_custom_popup("Do you really want to quit?", "Yes", "No", self.step_2_quit)
    def step_2_quit(self):
        self.create_custom_popup("Are you 100% sure?", "Yes", "No", self.step_3_quit)
    def step_3_quit(self):
        self.create_custom_popup("....fr?", "Leave me alone", "Fine", self.quit)
    def get_remote_image(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, timeout=10, verify=False, headers=headers)
            img_data = Image.open(BytesIO(response.content))
            return ctk.CTkImage(img_data, size=(1920, 1080))
        except:
            return None
    def clear_menu(self):
        for widget in self.menu_container.winfo_children(): widget.destroy()
    def show_start_screen(self):
        self.clear_menu()
        img = self.get_remote_image(self.START_IMG_URL)
        if img:
            bg = ctk.CTkLabel(self.menu_container, image=img, text="")
            bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        ctk.CTkButton(self.menu_container, text="START", width=300, height=80,
                      fg_color=self.SOFT_PINK, text_color="black",
                      font=("Times New Roman", 32, "bold"),
                      command=self.show_loading_screen).place(relx=0.5, rely=0.8, anchor="center")
    def show_loading_screen(self):
        self.clear_menu()
        img = self.get_remote_image(self.STORMVEIL_URL)
        if img:
            bg = ctk.CTkLabel(self.menu_container, image=img, text="")
            bg.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.load_msg_label = ctk.CTkLabel(self.menu_container, text="", font=("Times New Roman", 34, "italic"),
                                           text_color="white", fg_color="black")
        self.load_msg_label.place(relx=0.5, rely=0.6, anchor="center")

        self.progress = ctk.CTkProgressBar(self.menu_container, width=800, height=20, progress_color=self.ELDEN_GREEN,
                                           fg_color="#1A1A1A")
        self.progress.set(0)
        self.progress.place(relx=0.5, rely=0.75, anchor="center")

        self.percent_label = ctk.CTkLabel(self.menu_container, text="0%", font=("Consolas", 24, "bold"),
                                          text_color=self.ELDEN_GREEN, fg_color="black")
        self.percent_label.place(relx=0.5, rely=0.82, anchor="center")

        threading.Thread(target=self.run_loading_animation, daemon=True).start()
    def run_loading_animation(self):
        messages = {10: "not so long to go", 40: "patience is a virtue", 70: "almost there", 90: "isn't this exciting"}
        for i in range(1, 11):
            percent = i * 10
            self.progress.set(i / 10)
            self.percent_label.configure(text=f"{percent}%")
            self.load_msg_label.configure(text=f" {messages.get(percent, '')} " if percent in messages else "")
            time.sleep(4)
        self.after(0, self.show_main_menu)
    def show_main_menu(self):
        self.tracker_page.grid_forget()
        self.planner_page.grid_forget()
        self.menu_container.grid(row=0, column=0, sticky="nsew")
        self.clear_menu()
        img = self.get_remote_image(self.RANNI_IMG_URL)
        if img:
            bg = ctk.CTkLabel(self.menu_container, image=img, text="")
            bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        menu_frame = ctk.CTkFrame(self.menu_container, fg_color="transparent")
        menu_frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(menu_frame, text="CHOOSE YOUR PATH",
                     font=("Times New Roman", 50, "bold"), text_color=self.SOFT_PINK).pack(pady=30)
        ctk.CTkButton(menu_frame, text="PROGRESS TRACKER", width=380, height=75,
                      fg_color=self.BTN_PINK, text_color="black", font=("Arial", 20, "bold"),
                      command=self.show_tracker).pack(pady=15)
        ctk.CTkButton(menu_frame, text="BUILD PLANNER", width=380, height=75,
                      fg_color=self.ELDEN_GREEN, text_color="black", font=("Arial", 20, "bold"),
                      command=self.show_planner).pack(pady=15)
        ctk.CTkButton(menu_frame, text="QUIT", width=380, height=75,
                      fg_color="#333333", text_color="white", font=("Arial", 20, "bold"),
                      command=self.step_1_quit).pack(pady=15)
    def show_tracker(self):
        self.menu_container.grid_forget()
        self.tracker_page.grid(row=0, column=0, sticky="nsew")
    def show_planner(self):
        self.menu_container.grid_forget()
        self.planner_page.grid(row=0, column=0, sticky="nsew")
if __name__ == "__main__":
    app = EldenApp()
    app.mainloop()
