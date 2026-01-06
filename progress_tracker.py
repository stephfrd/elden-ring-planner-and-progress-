import customtkinter as ctk
import requests
from PIL import Image
from io import BytesIO
import threading
import webbrowser
def open_detail_window(item_data, soft_pink, elden_green):
    detail_win = ctk.CTkToplevel()
    detail_win.title(f"Archives: {item_data.get('name')}")
    detail_win.geometry("550x750")
    detail_win.configure(fg_color="#050505")
    detail_win.attributes("-topmost", True)
    if item_data.get('image'):
        img_label = ctk.CTkLabel(detail_win, text="Loading Image...", text_color=elden_green)
        img_label.pack(pady=20)
        def load_img():
            try:
                res = requests.get(item_data['image'], timeout=5)
                img = Image.open(BytesIO(res.content))
                ctk_img = ctk.CTkImage(img, size=(250, 250))
                img_label.configure(image=ctk_img, text="")
            except:
                img_label.configure(text="Image Unavailable")
        threading.Thread(target=load_img, daemon=True).start()
    ctk.CTkLabel(detail_win, text=item_data.get('name', '').upper(), font=("Times New Roman", 26, "bold"),
                 text_color=soft_pink).pack()
    info_scroll = ctk.CTkScrollableFrame(detail_win, fg_color="transparent", border_color=elden_green, border_width=1)
    info_scroll.pack(fill="both", expand=True, padx=20, pady=20)
    wiki_name = item_data.get('name').replace(" ", "+")
    wiki_url = f"https://eldenring.wiki.fextralife.com/{wiki_name}"
    ctk.CTkButton(detail_win, text="🔗 VIEW ON FEXTRALIFE WIKI", fg_color=elden_green, text_color="black",
                  font=("Arial", 12, "bold"), hover_color=soft_pink, command=lambda: webbrowser.open(wiki_url)).pack(
        pady=10)
    skip_keys = ['id', 'name', 'image', 'category_type']
    for key, value in item_data.items():
        if key in skip_keys or not value or value == "-": continue
        display_key = key.replace('_', ' ').upper()
        ctk.CTkLabel(info_scroll, text=f"[{display_key}]", text_color=soft_pink, font=("Arial", 12, "bold")).pack(
            anchor="w", pady=(15, 0))
        if isinstance(value, list):
            for sub_val in value:
                clean_val = str(sub_val).replace('{', '').replace('}', '').replace("'", "")
                ctk.CTkLabel(info_scroll, text=f" > {clean_val}", wraplength=450, justify="left", font=("Consolas", 13),
                             text_color=elden_green).pack(anchor="w", padx=15)
        else:
            ctk.CTkLabel(info_scroll, text=str(value), wraplength=450, justify="left", font=("Consolas", 13),
                         text_color=elden_green).pack(anchor="w", padx=15)
class ProgressTrackerFrame(ctk.CTkFrame):
    def __init__(self, master, soft_pink, btn_pink, back_command, **kwargs):
        super().__init__(master, fg_color="#000000", **kwargs)
        self.soft_pink = soft_pink
        self.ELDEN_GREEN = "#A8FFB5"
        self.base_url = "https://raw.githubusercontent.com/deliton/eldenring-api/main/api/public/data/"
        self.categories = ["ammos", "armors", "ashes", "bosses", "classes", "creatures", "incantations", "items",
                           "locations", "npcs", "shields", "sorceries", "spirits", "talismans", "weapons"]
        self.master_data = {}

        # Header & Search Bar
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=30, pady=20)
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.update_autofill)
        self.search_entry = ctk.CTkEntry(
            self.header, placeholder_text="Type at least one letter...",
            textvariable=self.search_var, width=450, height=45,
            fg_color=self.ELDEN_GREEN, text_color="black",
            placeholder_text_color="#333333", border_color=self.soft_pink
        )
        self.search_entry.pack(side="left")
        self.display_container = ctk.CTkFrame(self, fg_color="transparent")
        self.display_container.pack(fill="both", expand=True, padx=30)
        self.autofill_frame = ctk.CTkScrollableFrame(
            self, fg_color=self.ELDEN_GREEN, border_color=self.soft_pink,
            border_width=2, width=435, height=250
        )
        self.back_btn = ctk.CTkButton(self, text="← BACK", fg_color=self.soft_pink, text_color="black",
                                      command=back_command)
        self.back_btn.place(relx=0.98, rely=0.96, anchor="se")
        threading.Thread(target=self.pre_fetch, daemon=True).start()
        self.show_category_hub()
    def pre_fetch(self):
        for cat in self.categories:
            try:
                data = requests.get(f"{self.base_url}{cat}.json", timeout=10).json()
                for item in data:
                    item['category_type'] = cat
                    self.master_data[item['name']] = item
            except:
                pass

    def update_autofill(self, *args):
        query = self.search_var.get().strip().lower()
        for w in self.autofill_frame.winfo_children():
            w.destroy()
            if len(query) < 1:
            self.autofill_frame.place_forget()
            return
        matches = [n for n in self.master_data.keys() if query in n.lower()]

        if matches:
            # Re-place and Lift every time text changes to keep it on top
            self.autofill_frame.place(x=40, y=70)
            self.autofill_frame.lift()
            for m in matches[:15]:
                item_info = self.master_data[m]
                ctk.CTkButton(
                    self.autofill_frame,
                    text=f"{m} ({item_info['category_type'].upper()})",
                    fg_color=self.ELDEN_GREEN,
                    text_color="black",
                    anchor="w",
                    hover_color="#88E695",
                    command=lambda i=item_info: self.open_info(i)
                ).pack(fill="x", pady=1)
        else:
            self.autofill_frame.place_forget()

    def open_info(self, item):
        self.autofill_frame.place_forget()
        self.search_var.set("")
        open_detail_window(item, self.soft_pink, self.ELDEN_GREEN)

    def show_category_hub(self):
        for w in self.display_container.winfo_children(): w.destroy()
        grid = ctk.CTkScrollableFrame(self.display_container, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        for i, cat in enumerate(self.categories):
            ctk.CTkButton(grid, text=cat.upper(), width=200, height=80, fg_color="#111111", border_color=self.soft_pink,
                          border_width=1, hover_color=self.soft_pink,
                          command=lambda c=cat: self.load_category_view(c)).grid(row=i // 3, column=i % 3, padx=20,
                                                                                 pady=15)
    def load_category_view(self, category):
        for w in self.display_container.winfo_children(): w.destroy()
        nav = ctk.CTkFrame(self.display_container, fg_color="transparent")
        nav.pack(fill="x", pady=10)
        ctk.CTkButton(nav, text="← LIBRARY HUB", width=120, fg_color="#333333", command=self.show_category_hub).pack(
            side="left")
        scroll = ctk.CTkScrollableFrame(self.display_container, fg_color="#050505", border_color="#1A1A1A",
                                        border_width=1)
        scroll.pack(fill="both", expand=True)
        items = [v for k, v in self.master_data.items() if v['category_type'] == category]
        for item in sorted(items, key=lambda x: x['name']):
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.pack(fill="x", pady=2)
            ctk.CTkCheckBox(f, text="", width=20, fg_color=self.soft_pink).pack(side="left", padx=10)
            ctk.CTkButton(f, text=item['name'], fg_color="transparent", anchor="w", text_color="white",
                          hover_color="#1A1A1A",
                          command=lambda i=item: open_detail_window(i, self.soft_pink, self.ELDEN_GREEN)).pack(
                side="left", fill="x", expand=True)
