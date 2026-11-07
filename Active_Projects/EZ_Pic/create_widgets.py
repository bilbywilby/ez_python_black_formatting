import tkinter as tk
from tkinter import ttk


def create_widgets(self):
    """Create all of the GUI components"""

    # Directory entry and button
    self.dir_entry = ttk.Entry(self)

    dir_button = ttk.Button(self, text="Select Folder", command=self.select_folder)

    # Resize and enhance options UI
    self.resize_var = tk.BooleanVar(value=True)
    self.resize_check = ttk.Checkbutton(self, text="Resize Photos", variable=self.resize_var)

    self.enhance_var = tk.BooleanVar(value=False)
    self.enhance_check = ttk.Checkbutton(self, text="Enhance Photos", variable=self.enhance_var)

    # Progress bar UI
    self.progressbar = ttk.Progressbar(self, mode='indeterminate')

    # Process button UI
    proc_button = ttk.Button(self, text="Process Images", command=self.process_images)

    # Layout the widgets
    dir_button.grid(row=0, column=1, padx=5, pady=5)
    self.dir_entry.grid(row=0, column=0, padx=5, pady=5)

    self.resize_check.grid(row=1, column=0, padx=5, pady=5, sticky='W')
    self.enhance_check.grid(row=2, column=0, padx=5, pady=5, sticky='W')

    proc_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
    self.progressbar.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='we')

    # Set the window title
    self.master.title("Image Enhancer")