import tkinter as tk
from tkinter import filedialog, ttk
import os
import concurrent.futures
from PIL import Image, ImageEnhance

class ImageEnhancementAlgorithm:
    """
    Base class for image enhancement algorithms.
    """
    def process(self, img: Image.Image, contrast: float, brightness: float) -> Image.Image:
        """
        Process the input image using the current settings.

        Args:
            img (PIL.Image): Input image to process.
            contrast (float): Value of contrast slider (default value is 1.0)
            brightness (float): Value of brightness slider (default value is 1.0)

        Returns:
            PIL.Image: Processed image.
        """
        raise NotImplementedError


class BrightnessEnhancementAlgorithm(ImageEnhancementAlgorithm):
    """
    Class for brightness enhancement algorithm.
    """
    def process(self, img: Image.Image, contrast: float, brightness: float) -> Image.Image:
        """
        Process the input image using the current settings.

        Args:
            img (PIL.Image): Input image to process.
            contrast (float): Value of contrast slider (default value is 1.0)
            brightness (float): Value of brightness slider (default value is 1.0)

        Returns:
            PIL.Image: Processed image.
        """
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness)
        return img


class ContrastEnhancementAlgorithm(ImageEnhancementAlgorithm):
    """
    Class for contrast enhancement algorithm.
    """
    def process(self, img: Image.Image, contrast: float, brightness: float) -> Image.Image:
        """
        Process the input image using the current settings.

        Args:
            img (PIL.Image): Input image to process.
            contrast (float): Value of contrast slider (default value is 1.0)
            brightness (float): Value of brightness slider (default value is 1.0)

        Returns:
            PIL.Image: Processed image.
        """
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)
        return img


class ImageEnhancer(ttk.Frame):
    """
    Application that recursively finds all images in a directory and enhances them.
    """

    def __init__(self, master: tk.Tk = None) -> None:
        """
        Creates a new ImageEnhancer instance with the given master Tk widget.

        Args:
            master (tk.Tk, optional): Parent Tk widget. Defaults to None.
        """
        super().__init__(master)
        self.master = master
        self.pack()

        # Create all GUI components
        self.create_widgets()

    def create_widgets(self) -> None:
        """
        Creates all of the GUI components.
        """

        # Directory entry and button
        self.directory_entry = ttk.Entry(self)

        directory_button = ttk.Button(self, text="Select Folder", command=self.select_directory)

        # Resize and enhance options UI
        self.directory_entry.insert(0, "Select a directory")

        # Progress bar
        self.progress_bar = ttk.Progressbar(self, mode="indeterminate")

        # Layout the widgets
        directory_button.grid(row=0, column=1, padx=5, pady=5)
        self.directory_entry.grid(row=0, column=0, padx=5, pady=5)
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        # Set the window title
        self.master.title("Image Enhancer")

    def select_directory(self) -> None:
        """
        Prompts the user for a directory and calls `process_image_file` on the selected directory.
        """

        selected_directory = filedialog.askdirectory()

        if not selected_directory:
            return

        self.show_progress_bar()

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            filenames = [
                os.path.join(selected_directory, filename) for filename in os.listdir(selected_directory) if self.is_image_file(filename)
            ]
            results = list(executor.map(self.process_image_file, filenames))

        self.hide_progress_bar(results)

    def is_image_file(self, filename: str) -> bool:
        """
        Returns True if the given filename points to an image file, otherwise False.

        Args:
            filename (str): Name of the file to check.

        Returns:
            bool: True if the filename points to an image file, False otherwise.
        """

        return filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif"))

    def show_progress_bar(self) -> None:
        """
        Makes the progress bar visible and starts it spinning.
        """

        self.progress_bar.start()
        self.progress_bar["state"] = "normal"

    def hide_progress_bar(self, results: list) -> None:
        """
        Hides the progress bar when all processing is done and logs the number of processed images.

        Args:
            results (list): The list of success flags for the processed images.
        """

        self.progress_bar.stop()
        self.progress_bar["state"] = "disabled"

        success_count = sum(results)
        print(f"Processing complete - {success_count} images processed!")

    def process_image_file(self, filename: str) -> int:
        """
        Process a single image file by enhancing it, using the current enhancement algorithm, then returns a success flag.

        Args:
            filename (str): The name of the image file to process.

        Returns:
            int: 1 if the image was successfully processed, 0 if there were errors during processing.
        """

        try:
            # Load the input image
            img = Image.open(filename).convert("RGB")

            # Process the image using the current settings
            enhancement = self.current_enhancement_algorithm
            result_image = enhancement.process(img, self.contrast_slider.get(), self.brightness_slider.get())

            # Save the resulting image
            result_filename = os.path.splitext(filename)[0] + "_enhanced.jpg"
            result_image.save(result_filename)

            return 1

        except Exception as e:
            print(f"An error occurred while processing '{filename}': {e}")
            return 0

    def create_enhancement_options_ui(self) -> None:
        """
        Creates the UI components for selecting the enhancement algorithm and the enhacement options.
        """

        # Enhancement algorithm selector
        self.current_enhancement_algorithm = BrightnessEnhancementAlgorithm()
        self.algorithm_choice = tk.StringVar()
        algorithm_label = ttk.Label(self, text="Enhancement algorithm:")
        algorithm_selector = ttk.OptionMenu(self, self.algorithm_choice, "Brightness", "Brightness", "Contrast", command=self.set_enhancement_algorithm)

        algorithm_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        algorithm_selector.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Brightness slider
        self.brightness_slider = ttk.Scale(self, from_=0.0, to=2.0, orient=tk.HORIZONTAL, length=150, command=self.process_all_images)
        self.brightness_slider.set(1.0)
        brightness_label = ttk.Label(self, text="Brightness:")

        brightness_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.brightness_slider.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Contrast slider
        self.contrast_slider = ttk.Scale(self, from_=0.0, to=2.0, orient=tk.HORIZONTAL, length=150, command=self.process_all_images)
        self.contrast_slider.set(1.0)
        contrast_label = ttk.Label(self, text="Contrast:")

        contrast_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.contrast_slider.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

    def set_enhancement_algorithm(self, algorithm_name: str) -> None:
        """
        Changes the current enhancement algorithm based on the user's selection.

        Args:
            algorithm_name (str): Name of the selected enhancement algorithm.
        """

        if algorithm_name == "Brightness":
            self.current_enhancement_algorithm = BrightnessEnhancementAlgorithm()
        elif algorithm_name == "Contrast":
            self.current_enhancement_algorithm = ContrastEnhancementAlgorithm()

        self.process_all_images()

    def process_all_images(self, *args) -> None:
        """
        Processes all images in the selected directory using the current enhancement algorithm and enhacement options.
        """

        self.show_progress_bar()

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            filenames = [
                os.path.join(self.selected_directory, filename) for filename in os.listdir(self.selected_directory) if self.is_image_file(filename)
            ]
            results = list(executor.map(self.process_image_file, filenames))

        self.hide_progress_bar(results)

    def create_image_preview_ui(self) -> None:
        """
        Creates the UI components for displaying the original and processed images preview.
        """

        self.main_window = ttk.Label(self, padding=10)
        self.preview_window = ttk.Label(self, padding=10)

        self.main_window.grid(row=0, column=2, rowspan=5, padx=5, pady=5)
        self.preview_window.grid(row=0, column=3, rowspan=5, padx=5, pady=5)

    def create_widgets(self) -> None:
        """
        Creates all of the GUI components.
        """

        # Directory entry and button
        self.directory_entry = ttk.Entry(self)

        directory_button = ttk.Button(self, text="Select Folder", command=self.select_directory)

        # Resize and enhance options UI
        self.create_enhancement_options_ui()
        self.directory_entry.insert(0, "Select a directory")

        # Progress bar
        self.progress_bar = ttk.Progressbar(self, mode="indeterminate")

        # Main and preview windows
        self.create_image_preview_ui()

        # Layout the widgets
        directory_button.grid(row=0, column=1, padx=5, pady=5)
        self.directory_entry.grid(row=0, column=0, padx=5, pady=5)
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        # Set the window title
        self.master.title("Image Enhancer")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEnhancer(master=root)
    app.mainloop()