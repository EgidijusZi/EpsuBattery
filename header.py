import tkinter as tk
from PIL import Image, ImageTk

class Header:
    def __init__(self, root):
        self.root = root
        self.setup_header()

    def setup_header(self):
        self.header_frame = tk.Frame(self.root)
        self.header_frame.pack(fill=tk.X, pady=10)
        self.logo_image = Image.open("C:\\Users\\sto\\PycharmProjects\\aut\\DAT_logo_FN.jpg")
        self.logo_image = self.logo_image.resize((100, 100), Image.Resampling.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        tk.Label(self.header_frame, image=self.logo_photo).grid(row=0, column=0, padx=10)
        tk.Label(self.header_frame, text="DAT Battery Maintenance System", font=("Helvetica", 16, "bold")).grid(row=0, column=1, padx=10)