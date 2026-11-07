import os
from typing import List, Tuple

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageEnhance
import concurrent.futures
from tqdm import tqdm


class ProgressBarHandler:
    """Used to handle progressbar updates."""

    def __init__(self, progressbar: ttk.Progressbar):
        self.progressbar = progressbar

    def show_progress(self) -> None:
        """Make progress bar visible and start it rotating."""
        self.progressbar.start()

    def hide_progress(self, result: str) -> None:
        """Stop progress bar rotation."""
        self.progressbar.stop()


class ImageEnhancerGUI(ttk.Frame):
    """Main GUI class."""

    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.master = master
        self.progress_bar_handler = ProgressBarHandler(self.progress_bar)
        self.pack()

        # Create all GUI components
        self.create_ui()

    def create_ui(self) -> None:
        """Create all of the GUI components."""
        self.create_select_folder_ui()
        self.resize_var = tk.BooleanVar(value=True)
        self.resize_check = ttk.Checkbutton(self, text="Resize Photos", variable=self.resize_var)
        self.enhance_var = tk.BooleanVar(value=False)
        self.enhance_check = ttk.Checkbutton(self, text="Enhance Photos", variable=self.enhance_var)
        self.create_progress_bar_ui()

        # Create the process button UI
        proc_button = ttk.Button(self, text="Process Images", command=self.process_files)

        # Layout the widgets
        self.dir_button.grid(row=0, column=1, padx=5, pady=5)
        self.dir_entry.grid(row=0, column=0, padx=5, pady=5)
        self.resize_check.grid(row=1, column=0, padx=5, pady=5, sticky='W')
        self.enhance_check.grid(row=2, column=0, padx=5, pady=5, sticky='W')
        proc_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # Set the window title
        self.master.title("Image Enhancer")

    def create_select_folder_ui(self) -> None:
        """Setup the select folder UI components."""
        self.dir_entry = ttk.Entry(self)
        self.dir_button = ttk.Button(self, text="Select Folder", command=self.select_folder)

        self.dir_entry.insert(0, "Select a folder")

    def create_progress_bar_ui(self) -> None:
        """Setup the progress bar UI components."""
        self.progress_bar = ttk.Progressbar(self, mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='we')

    def is_valid_folder(self, directory: str) -> bool:
        """Check if directory selected and exit if empty."""
        if not directory:
            messagebox.showerror("Error", "Please select a folder.")
            return False
        return True

    def process_files(self) -> None:
        """Start processing selected folder's images."""
        directory = self.dir_entry.get()
        if not self.is_valid_folder(directory):
            return

        # Gather filenames
        file_paths = [os.path.join(directory, filename) for filename in os.listdir(directory)]
        successful_count = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self._process_file, file_path) for file_path in file_paths]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(file_paths)):
                successful_count += future.result()

        # Show success message with success count
        messagebox.showinfo("Success", f"Processed {successful_count}/{len(file_paths)} files.")

    def _process_file(self, file_path: str) -> int:
        """Process a single image file by calling the main function and returning its success status."""
        try:
            with Image.open(file_path) as img:
                if self.resize_var.get():
                    img.thumbnail((800, 800), Image.ANTIALIAS)

                if self.enhance_var.get():
                    img = self.enhance_image(img)

                img.save(f"{file_path}_processed")
            # If successful return 1
            return 1
        except Exception as e:
            # If unsuccessful return 0
            return 0

    def enhance_image(self, img: Image.Image) -> Image.Image:
        """Enhance image using Pillow."""
        sharpness_enhancer = ImageEnhance.Sharpness(img)
        return sharpness_enhancer.enhance(1.5)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEnhancerGUI(root)
    root.mainloop()