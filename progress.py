import customtkinter as ctk
import requests
import threading
from progress_tracker import open_detail_window

class BuildPlannerFrame(ctk.CTkFrame):
    def __init__(self, master, soft_pink, btn_pink, back_command, user_checked_list, **kwargs):
        super().__init__(master, fg_color="#000000", **kwargs)
        self.ELDEN_GREEN = "#A8FFB5"
        self.SOFT_PINK = soft_pink
        self.user_checked = user_checked_list
        self.base_url = "https://raw.githubusercontent.com/deliton/eldenring-api/main/api/public/data/"
        self.categories = ["ammos", "armors", "ashes", "bosses", "incantations", "items", "locations", "npcs", "shields", "sorceries", "spirits", "talismans", "weapons"]
        self.master_dict = {}

        self.sidebar_width = 220
        self.sidebar_visible = False
        self.sidebar = ctk.CTkFrame(self, width=self.sidebar_width, fg_color="#0A0A0A", border_color=self.ELDEN_GREEN, border_width=2)
        self.sidebar.place(x=-self.sidebar_width, y=0, relheight=1)

        ctk.CTkLabel(self.sidebar, text="STRATEGY", font=("Times New Roman", 24, "bold"), text_color=self.ELDEN_GREEN).pack(pady=30)
        self.create_side_btn("✨ DISCOVER", self.show_discover_area)
        self.create_side_btn("📝 NOTES", self.show_notes_area)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.menu_btn = ctk.CTkButton(self.container, text="☰ MENU", width=90, fg_color=self.ELDEN_GREEN, text_color="black", font=("Arial", 12, "bold"), command=self.animate_sidebar)
        self.menu_btn.pack(anchor="nw", pady=10)

        self.back_btn = ctk.CTkButton(self, text="← BACK", fg_color=self.SOFT_PINK, text_color="black", command=back_command)
        self.back_btn.place(relx=0.98, rely=0.96, anchor="se")

        threading.Thread(target=self.load_all_data, daemon=True).start()
        self.show_discover_area()

    def load_all_data(self):
        for cat in self.categories:
            try:
                data = requests.get(f"{self.base_url}{cat}.json", timeout=10).json()
                self.master_dict[cat] = data
            except: pass

    def create_side_btn(self, text, cmd):
        ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", anchor="w", height=50, hover_color="#1A331D",
                      command=lambda: [cmd(), self.animate_sidebar()]).pack(fill="x", padx=15, pady=5)

    def animate_sidebar(self):
        dest = 0 if not self.sidebar_visible else -self.sidebar_width
        current = int(self.sidebar.place_info().get('x', -self.sidebar_width))
        step = 20 if dest == 0 else -20
        # Smooth motion
        for x in range(current, dest + (1 if step > 0 else -1), step):
            self.sidebar.place(x=x)
            self.sidebar.lift()
            self.update()
        self.sidebar_visible = not self.sidebar_visible

    def show_discover_area(self):
        for w in self.container.winfo_children():
            if w != self.menu_btn: w.destroy()
        ctk.CTkLabel(self.container, text="REMAINING CHALLENGES", font=("Times New Roman", 24, "bold"), text_color=self.ELDEN_GREEN).pack(anchor="w")
        cat_bar = ctk.CTkScrollableFrame(self.container, orientation="horizontal", height=65, fg_color="#0A0A0A")
        cat_bar.pack(fill="x", pady=10)
        for cat in self.categories:
            ctk.CTkButton(cat_bar, text=cat.upper(), width=110, fg_color="#1A331D", command=lambda c=cat: self.load_missing(c)).pack(side="left", padx=5)

        self.missing_list = ctk.CTkScrollableFrame(self.container, fg_color="#050505", border_color="#1A1A1A", border_width=1)
        self.missing_list.pack(fill="both", expand=True)
        self.load_missing("bosses")

    def load_missing(self, category):
        for w in self.missing_list.winfo_children(): w.destroy()
        items = self.master_dict.get(category, [])
        for item in items:
            if item['name'] not in self.user_checked:
                f = ctk.CTkFrame(self.missing_list, fg_color="transparent")
                f.pack(fill="x", pady=2)
                ctk.CTkButton(f, text=f"✦ {item['name']}", fg_color="transparent", anchor="w", text_color="white", hover_color="#111111",
                              command=lambda i=item: open_detail_window(i, self.SOFT_PINK, self.ELDEN_GREEN)).pack(fill="x")

    def show_notes_area(self):
        for w in self.container.winfo_children():
            if w != self.menu_btn: w.destroy()
        ctk.CTkLabel(self.container, text="ADVENTURE LOG", font=("Times New Roman", 24, "bold"), text_color=self.ELDEN_GREEN).pack(anchor="w")
        self.notes = ctk.CTkTextbox(self.container, fg_color="#050505", border_color=self.ELDEN_GREEN, border_width=1,
                                    text_color=self.SOFT_PINK, font=("Consolas", 15), padx=15, pady=15)
        self.notes.pack(fill="both", expand=True, pady=10)
        self.notes.insert("0.0", "• ")
