import tkinter as tk
from tkinter import ttk
import os
import logging
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import os
import logging
from PIL import Image, ImageFilter, ImageEnhance
import concurrent.futures
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class App(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        # Create all GUI components
        self.create_widgets()

    def create_widgets(self):
        """Create all of the GUI components"""
        # Directory entry and button
        self.dir_entry = ttk.Entry(self, width=50, state="readonly")
        self.dir_entry.grid(column=0, row=0)
        self.dir_btn = ttk.Button(self, text="Browse...", command=self.browse_directory)
        self.dir_btn.grid(column=1, row=0)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.grid(column=0, row=1, columnspan=2, pady=(10, 0))

        # Checkbox to enable/disable progress bar
        self.pb_var = tk.BooleanVar()
        self.pb_checkbox = ttk.Checkbutton(self, text="Show progress bar", variable=self.pb_var, onvalue=True, offvalue=False, command=self.toggle_progress_bar)
        self.pb_checkbox.grid(column=0, row=2, columnspan=2, pady=(5, 0))

        # Button to start processing
        self.process_btn = ttk.Button(self, text="Process Images", command=self.process_images)
        self.process_btn.grid(column=0, row=3, columnspan=2, pady=(5, 0))

    def browse_directory(self):
        """Open a file dialog to select a directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.config(state="normal")
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
            self.dir_entry.config(state="readonly")

    def toggle_progress_bar(self):
        """Enable or disable the progress bar based on the checkbox state"""
        if self.pb_var.get():
            self.progress_bar.config(state="normal")
        else:
            self.progress_bar.config(state="hidden")

    def process_images(self):
        """Process the images in the selected directory"""
        directory = self.dir_entry.get()
        if not directory:
            messagebox.showerror("Error", "Please select a directory first.")
            return

        self.progress_bar.config(maximum=len(os.listdir(directory)))
        self.progress_bar.config(value=0)

        # Clear any existing thumbnails
        for widget in self.master.winfo_children():
            if isinstance(widget, tk.Label) and "thumbnail" in widget.config()["text"]:
                widget.destroy()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.process_image, os.path.join(directory, filename)): filename for filename in tqdm(os.listdir(directory))}
            for future in concurrent.futures.as_completed(futures):
                filename = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    logger.error(f"{filename} generated an exception: {exc}")
                else:
                    thumbnail = tk.Label(self.master, image=result, text=f"thumbnail {
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import os
import logging
from PIL import Image, ImageFilter, ImageEnhance
import concurrent.futures
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class App(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        # Create all GUI components
        self.create_widgets()

    def create_widgets(self):
        """Create all of the GUI components"""
        # Directory entry and button
        self.dir_entry = ttk.Entry(self, width=50, state="readonly")
        self.dir_entry.grid(column=0, row=0)
        self.dir_btn = ttk.Button(self, text="Browse...", command=self.browse_directory)
        self.dir_btn.grid(column=1, row=0)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.grid(column=0, row=1, columnspan=2, pady=(10, 0))

        # Checkbox to enable/disable progress bar
        self.pb_var = tk.BooleanVar()
        self.pb_checkbox = ttk.Checkbutton(self, text="Show progress bar", variable=self.pb_var, onvalue=True, offvalue=False, command=self.toggle_progress_bar)
        self.pb_checkbox.grid(column=0, row=2, columnspan=2, pady=(5, 0))

        # Button to start processing
        self.process_btn = ttk.Button(self, text="Process Images", command=self.process_images)
        self.process_btn.grid(column=0, row=3, columnspan=2, pady=(5, 0))

    def browse_directory(self):
        """Open a file dialog to select a directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.config(state="normal")
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
            self.dir_entry.config(state="readonly")

    def toggle_progress_bar(self):
        """Enable or disable the progress bar based on the checkbox state"""
        if self.pb_var.get():
            self.progress_bar.config(state="normal")
        else:
            self.progress_bar.config(state="hidden")

    def process_images(self):
        """Process all images in the selected directory"""
        directory = self.dir_entry.get()
        if not directory:
            messagebox.showerror("Error", "Please select a directory first.")
            return

        self.progress_bar.config(maximum=len(os.listdir(directory)))
        self.progress_bar.config(value=0)

        self.process_images_in_directory(directory)

    def process_images_in_directory(self, directory):
        """Process all images in the given directory using multiple threads"""
        images = [f for f in os.listdir(directory) if f.endswith((".png", ".jpg", ".jpeg"))]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.process_image, os.path.join(directory, image)): image for image in images}
            for future in tqdm(futures, total=len(futures)):
                future.result()

        messagebox.showinfo("Success", "All images have been processed.")

    def process_image(self, image_path):
        """Apply filters and enhancements to a single image"""
        try:
            image = Image.open(image_path)
       # Convert to RGB if it's grayscale (assuming that grayscale is always used for thumbnails).
            if image.mode == "L":
# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class EZPicApp:
    def __init__(self, root):
        self.root = root
        # Updated the title to a more elegant version
        self.root.title("EZ Pic App")

        # initialize other attributes and widgets here

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = EZPicApp(root)
    app.run()

# Configuration parameters
# Renamed and changed the parameter for better readability
SUPPORTED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
DEFAULT_IMAGE_SIZE = (800, 600)
THUMBNAIL_SIZE = (100, 100)

# Utility functions


def get_file_extension(filename):
    # Changed the variable name for clarity
    _, file_ext = os.path.splitext(filename)
    return file_ext.lower()


def is_supported_image_file(filename):
    return get_file_extension(filename) in SUPPORTED_IMAGE_FORMATS

# Image processing functions


def resize_image(image_path, output_path, size):
    with Image.open(image_path) as img:
        img = img.resize(size, Image.ANTIALIAS)
        img.save(output_path)


def apply_filter(image_path, output_path, filter_type):
    with Image.open(image_path) as img:
        if filter_type == 'BLUR':
            img = img.filter(ImageFilter.BLUR)
        elif filter_type == 'CONTOUR':
            img = img.filter(ImageFilter.CONTOUR)
        # Add more filters as needed
        img.save(output_path)

# GUI functions


def create_main_window():
    window = tk.Tk()
    window.title("EZ_PIC Image Processor")

    # Add GUI components here
    # For example, buttons for selecting images, applying filters, etc.

    return window


# Main function to run the application
if __name__ == "__main__":
    main_window = create_main_window()
    main_window.mainloop()

# EZ_PIC.py
# A script to organize and process images in a user-friendly manner.


class EZPicApp:
    def __init__(self, master):
        self.master = master
        master.title("EZ_PIC - Photo Organizer")

        # Load or initialize configuration
        self.config = self.load_config()

        # UI Elements
        self.create_widgets()

    def create_widgets(self):
        # Folder selection UI
        self.folder_label = ttk.Label(self.master, text="Select Folder:")
        self.folder_label.grid(row=0, column=0, sticky="w")
        self.folder_entry = ttk.Entry(self.master, width=50)
        self.folder_entry.grid(row=0, column=1, sticky="ew")
        self.browse_button = ttk.Button(
            self.master, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=0, column=2, sticky="ew")

        # Resize and enhance options UI
        self.resize_var = tk.BooleanVar(value=self.config.get('resize', True))
        self.resize_check = ttk.Checkbutton(
            self.master, text="Resize Photos", variable=self.resize_var)
        self.resize_check.grid(row=1, column=0, columnspan=3, sticky="w")
        self.enhance_var = tk.BooleanVar(
            value=self.config.get('enhance', False))
        self.enhance_check = ttk.Checkbutton(
            self.master, text="Enhance Photos", variable=self.enhance_var)
        self.enhance_check.grid(row=2, column=0, columnspan=3, sticky="w")

        # Process button UI
        self.process_button = ttk.Button(
            self.master, text="Process Images", command=self.process_images)
        self.process_button.grid(row=3, column=0, columnspan=3, sticky="ew")

        # Progress bar UI
        self.progress = ttk.Progressbar(
            self.master, orient="horizontal", length=100, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=3, sticky="ew")

    def load_config(self):
        # Load configuration from a JSON file
        # ...

    def save_config(self):
        # Save current settings to a JSON file
        # ...

    def browse_folder(self):
        # Open a dialog for folder selection
        # ...

    def process_images(self):
        # Start the photo processing with the current settings
        # ...

    def update_progress(self, value):
        # Update the progress bar and status label
        # ...


def process_image(file, config):
    # Process a single image, resizing and enhancing it
    # ...


def batch_process_images(files, config):
    # Process images in batches using multiple threads
    # ...

    # Main function to run the application


def main():
    root = tk.Tk()
    app = EZPicApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
