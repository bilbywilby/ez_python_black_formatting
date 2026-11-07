import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageEnhance
import concurrent.futures
from tqdm import tqdm

class ProgressBarHandler:
    def __init__(self, progressbar):
        self.progressbar = progressbar

    def show_progress(self):
        """Make progress bar visible and start it rotating"""
        self.progressbar.start()

    def hide_progress(self, future_result):
        """Stop progress bar rotation"""
        self.progressbar.stop()

class ImageEnhancerGUI(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        # Create all GUI components
        self.setupUI()
        self.progressBarHandler = ProgressBarHandler(self.progressbar)

    def setupUI(self):
        """Create all of the GUI components"""
        self.setupSelectFolderUI()
        self.resize_var = tk.BooleanVar(value=True)
        self.resize_check = ttk.Checkbutton(self, text="Resize Photos", variable=self.resize_var)
        self.enhance_var = tk.BooleanVar(value=False)
        self.enhance_check = ttk.Checkbutton(self, text="Enhance Photos", variable=self.enhance_var)
        self.setupProgressBarUI()

        # Create the process button UI
        proc_button = ttk.Button(self, text="Process Images", command=self.processFiles)

        # Layout the widgets
        self.dir_button.grid(row=0, column=1, padx=5, pady=5)
        self.dir_entry.grid(row=0, column=0, padx=5, pady=5)
        self.resize_check.grid(row=1, column=0, padx=5, pady=5, sticky='W')
        self.enhance_check.grid(row=2, column=0, padx=5, pady=5, sticky='W')
        proc_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # Set the window title
        self.master.title("Image Enhancer")

    def setupSelectFolderUI(self):
        """Setup the select folder UI components"""
        self.dir_entry = ttk.Entry(self)
        self.dir_button = ttk.Button(self, text="Select Folder", command=self.selectFolder)

        self.dir_entry.insert(0, "Select a folder")

    def setupProgressBarUI(self):
        """Setup the progress bar UI components"""
        self.progressbar = ttk.Progressbar(self, mode='indeterminate')
        self.progressbar.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='we')

    def selectFolder(self):
        """Prompt user for directory then call processFiles on selected directory."""
        try:
            selected_directory = filedialog.askdirectory()

            if not selected_directory:
                return

            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, selected_directory)
            self.progressBarHandler.show_progress()
            process_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)
            process_pool.submit(self.processFiles, selected_directory).add_done_callback(self.progressBarHandler.hide_progress)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while trying to access your files:\n{e}")

    def processFiles(self, directory):
        """Start processing selected folder's images."""
        try:
            if not directory:
                messagebox.showerror("Error", "Please select a folder.")
                return

            # Gather filenames
            filenames = [os.path.join(directory, filename) for filename in os.listdir(directory)]
            # Process files and count up successes
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(tqdm(executor.map(self._processFile, filenames), total=len(filenames)))

            success_count = sum(result[0] for result in results)

            # Show success message with success count
            messagebox.showinfo("Success", f"Processed {success_count}/{len(filenames)} files.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while trying to access your files:\n{e}")

    def _processFile(self, filename):
        """Process a single image file by calling the main function and returning its success status."""
        try:
            with Image.open(filename) as img:
                # Resize
                if self.resize_var.get():
                    img.thumbnail((800, 800), Image.ANTIALIAS)

                # Enhance
                if self.enhance_var.get():
                    sharpness_enhancer = ImageEnhance.Sharpness(img)
                    img = sharpness_enhancer.enhance(1.5)

                # Save processed image
                img.save(f"{filename}_processed")

            # If successful return `(1, "")`
            return 1, ""

        except Exception as e:
            # If unsuccessful return `(0, error message)`
            return 0, str(e)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEnhancerGUI(root)
    root.mainloop()