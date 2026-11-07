import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import os
import logging
from PIL import Image, ImageEnhance
import concurrent.futures
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class EZPicApp(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.config = self.load_config()  # Load or initialize configuration

        self.create_widgets()

    def create_widgets(self):
        # Directory entry and button
        self.dir_entry = ttk.Entry(self)

        dir_button = ttk.Button(self, text="Select Folder", command=self.select_folder)

        self.dir_entry.insert(0, "Select a folder")

        # Resize and enhance options
        self.resize_var = tk.BooleanVar(value=self.config.get('resize', True))
        self.resize_check = ttk.Checkbutton(self, text="Resize Photos", variable=self.resize_var)

        self.enhance_var = tk.BooleanVar(value=self.config.get('enhance', False))
        self.enhance_check = ttk.Checkbutton(self, text="Enhance Photos", variable=self.enhance_var)

        # Process button
        self.process_button = ttk.Button(self, text="Process Images", command=self.process_images)

        # Progress bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")

        # Layout the widgets
        dir_button.grid(row=0, column=1, padx=5, pady=5)
        self.dir_entry.grid(row=0, column=0, padx=5, pady=5)
        self.resize_check.grid(row=1, column=0, padx=5, pady=5)
        self.enhance_check.grid(row=2, column=0, padx=5, pady=5)
        self.process_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        self.progress.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        self.master.title("EZ_PIC")

    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_config(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f)

    def select_folder(self):
        self.directory = filedialog.askdirectory()
        if self.directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, self.directory)

    def process_images(self):
        if not self.directory:
            messagebox.showerror("Error", "Please select a folder.")
            return

        self.config['resize'] = self.resize_var.get()
        self.config['enhance'] = self.enhance_var.get()
        self.save_config()

        files = [os.path.join(self.directory, f) for f in os.listdir(self.directory) if
                 os.path.isfile(os.path.join(self.directory, f)) and self.is_supported_image_file(f)]

        if not files:
            messagebox.showerror("Error", "No supported image files found in the selected folder.")
            return

        self.progress["maximum"] = len(files)
        self.progress["value"] = 0
        self.progress.start()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self._process_file, file): file for file in files}

            for future in concurrent.futures.as_completed(futures):
                file = futures[future]
                try:
                    success, error_msg = future.result()
                    if success:
                        status_message = f"Processed {os.path.basename(file)}"
                    else:
                        status_message = f"Error processing {os.path.basename(file)}: {error_msg}"

                except Exception as e:
                    logging.error(f"Processing file {os.path.basename(file)} failed with {e}")
                    status_message = f"Error processing {os.path.basename(file)}"

                self.update_progress(status_message)

        self.progress.stop()

    def is_supported_image_file(self, filename):
        return filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))

    def _process_file(self, filename):
        try:
            with Image.open(filename) as img:
                if self.resize_var.get():
                    img.thumbnail((800, 800), Image.ANTIALIAS)

                if self.enhance_var.get():
                    sharpness_enhancer = ImageEnhance.Sharpness(img)
                    img = sharpness_enhancer.enhance(1.5)

                filename_no_ext, extension = os.path.splitext(filename)
                output_file = f"{filename_no_ext}_processed{extension}"
                img.save(output_file)

            return (True, "")

        except Exception as e:
            return (False, str(e))

    def update_progress(self, status_message):
        self.progress["value"] += 1
        self.master.update()
        logging.info(status_message)


if __name__ == "__main__":
    root = tk.Tk()
    app = EZPicApp(root)
    root.mainloop()