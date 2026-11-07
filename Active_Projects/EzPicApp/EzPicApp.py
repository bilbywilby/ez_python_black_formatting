import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageOps, ExifTags
from typing import List, Tuple
from pathlib import Path
from datetime import datetime
import logging
import os

class EZPicApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('EZPic')
        self.geometry('700x350')
        self.images_dir = Path.cwd()
        self.logger = self._set_up_logger()

        self._org_option = tk.StringVar(value='date')
        self._rename_option = tk.StringVar(value='timestamp')
        self._image_filter_option = tk.StringVar(value='all')
        self._max_size = tk.IntVar(value=0)

        self.images = []
        self.filtered_images = []

        self.init_ui()

    def init_ui(self) -> None:
        self.create_widgets()
        self.create_menu_bar()
        self.bind("<Configure>", self.on_resize)

    def create_widgets(self) -> None:
        self.canvas = tk.Canvas(self, height=700, width=350, bg="#263D42")
        self.canvas.pack(side='left', fill='both', expand=True)

        self.frame = tk.Frame(self, bg="white")
        self.frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

        open_button = tk.Button(self, text="Open", command=self.load_images)
        open_button.pack(side="left", padx=10, pady=10)

        options_button = tk.Button(self, text="Options", command=self.display_options_dialog)
        options_button.pack(side="left", padx=10, pady=10)

        process_button = tk.Button(self, text="Process", command=self.process_images)
        process_button.pack(side="left", padx=10, pady=10)

        self.image_canvas = tk.Canvas(self.canvas)
        self.scrollbar = tk.Scrollbar(self.canvas, orient="vertical", command=self.image_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.image_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.image_canvas.configure(
                scrollregion=self.image_canvas.bbox("all")
            )
        )

        self.image_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.image_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.image_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def create_menu_bar(self) -> None:
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menu_bar)

    def load_images(self) -> None:
        """
        Loads images from the selected directory/folder into the GUI or all supported images files found.
        """
        dir_path = filedialog.askdirectory(initialdir="/", title="Select Images Directory") or self.images_dir
        self.images_dir = Path(dir_path)
        self.logger.info(f"Selected Images Directory: {self.images_dir}")
        self.images = []
        for item in os.listdir(self.images_dir):
            item_path = self.images_dir / item
            if item_path.is_file() and item_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.bmp']:
                self.images.append(item_path)
        self.filter_images()
        self.display_filtered_images()

    def on_resize(self, event) -> None:
        """
        Resizes the canvas.
        """
        self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))

    def filter_images(self) -> None:
        """
        Filters the loaded images based on the selected filter option.
        """
        self.filtered_images = []
        for img_path in self.images:
            if self._image_filter_option.get() == "landscape" and not self._is_landscape(img_path):
                continue
            elif self._image_filter_option.get() == "portrait" and not self._is_portrait(img_path):
                continue
            elif self._image_filter_option.get() == "square" and not self._is_square(img_path):
                continue
            self.filtered_images.append(img_path)

    def display_filtered_images(self) -> None:
        """
        Displays the filtered images on the GUI.
        """
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for image_path in self.filtered_images:
            image = tk.PhotoImage(file=image_path)
            image_label = tk.Label(self.scrollable_frame, image=image)
            image_label.image = image
            image_label.pack(padx=5, pady=5)

        self.image_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_frame.update_idletasks()
        canvas_height = self.scrollable_frame.winfo_reqheight()
        canvas_width = self.scrollable_frame.winfo_reqwidth()
        self.image_canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))

    def process_images(self) -> None:
        """
        Processes the filtered images and saves them according to the selected options.
        """
        output_dir_init = self.images_dir/'EZPic Output'
        output_dir = filedialog.askdirectory(initialdir=output_dir_init, title="Select Images Save Folder")
        if output_dir:
            output_dir_path = Path(output_dir)
            try:
                output_dir_path.mkdir(parents=True, exist_ok=True)
                for img_path in self.filtered_images:
                    img = Image.open(img_path)
                    img = self._remove_metadata(img)
                    img = self._auto_crop_image(img)
                    img = self._resize_image(img, self._max_size.get())
                    self._save_and_organize_image(img, img_path, output_dir_path)
                    del img
                messagebox.showinfo("Processing Complete", "Processing complete. Images saved to chosen folder!")
            except Exception as e:
                self.logger.error(f"Error processing images: {str(e)}")
                messagebox.showerror("Error", "An error occurred while processing the images. Please check your settings and try again.")

    def _is_landscape(self, img_path: Path) -> bool:
        """
        Return True if the image is in landscape orientation.
        """
        img = Image.open(img_path)
        width, height = img.size
        return width > height

    def _is_portrait(self, img_path: Path) -> bool:
        """
        Return True if the image is in portrait orientation.
        """
        img = Image.open(img_path)
        width, height = img.size
        return width < height

    def _is_square(self, img_path: Path) -> bool:
        """
        Return True if the image is square.
        """
        img = Image.open(img_path)
        width, height = img.size
        return width == height

    def _resize_image(self, img: Image, max_size: int) -> Image:
        """
        Resize the image to fit within the max size constraint while maintaining the aspect ratio.
        """
        if max_size == 0:
            return img
        width, height = img.size
        if width > max_size or height > max_size:
            if width > height:
                ratio = width / max_size
                new_width = max_size
                new_height = height / ratio
            else:
                ratio = height / max_size
                new_width = width / ratio
                new_height = max_size
            img = img.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
        return img

    def _remove_metadata(self, img: Image) -> Image:
        """
        Remove all metadata from the image.
        """
        data = list(img.getdata())
        exif_data = img.info.get("exif")
        if exif_data:
            for tag, _ in exif_data.items():
                if tag in ExifTags.TAGS:
                    img.info["exif"][ExifTags.TAGS[tag]] = None
        new_img = Image.new(img.mode, img.size)
        new_img.putdata(data)
        return new_img

    def _auto_crop_image(self, img: Image) -> Image:
        """
        Automatically crop the image to remove excess whitespace.
        """
        inverted_image = ImageOps.invert(img)
        bbox = inverted_image.getbbox()
        if bbox:
            cropped_img = img.crop(bbox)
            return cropped_img
        return img

    def _save_and_organize_image(self, img: Image, img_path: str, output_dir: Path) -> None:
        """
        Save the image and move it to the appropriate subdirectory based on the selected organization option.
        """
        output_filename = self._get_output_filename(img_path)
        output_path = output_dir / output_filename
        output_dir.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path))
        self.logger.info(f"Saved image to {output_path}")

        if self._org_option.get() == "date":
            date_dir = output_dir / self._get_creation_date(img_path)
            date_dir.mkdir(parents=True, exist_ok=True)
            output_path.replace(date_dir / output_path.name)
            self.logger.info(f"Moved image to {date_dir}")
        elif self._org_option.get() == "size":
            size_dir = output_dir / self._get_size_dirname(img.size)
            size_dir.mkdir(parents=True, exist_ok=True)
            output_path.replace(size_dir / output_path.name)
            self.logger.info(f"Moved image to {size_dir}")
        elif self._org_option.get() == "type":
            ext_dir = output_dir / img.format.lower()
            ext_dir.mkdir(parents=True, exist_ok=True)
            output_path.replace(ext_dir / output_path.name)
            self.logger.info(f"Moved image to {ext_dir}")

    def _get_output_filename(self, img_path: str) -> str:
        """
        Generate a new filename for the image based on the selected renaming option.
        """
        filename = Path(img_path).name
        if self._rename_option.get() == "timestamp":
            new_name = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + filename
        elif self._rename_option.get() == "prefix":
            new_name = "IMG_" + filename
        elif self._rename_option.get() == "suffix":
            new_name = filename + "_final"
        return new_name

    def _get_creation_date(self, img_path: str) -> str:
        """
        Return the creation date of the image as a string in the format 'YYYY-MM-DD'.
        """
        return datetime.fromtimestamp(Path(img_path).stat().st_birthtime).strftime('%Y-%m-%d')

    def _get_size_dirname(self, size: Tuple[int, int]) -> str:
        """
        Return the size of the image as a string in the format 'WxH'.
        """
        return f"{size[0]}x{size[1]}"

    def display_options_dialog(self) -> None:
        """
        Display the options dialog.
        """
        options_dialog = tk.Toplevel(self)
        options_dialog.title("Options")

        tk.Label(options_dialog, text="Organization Option:").grid(row=0, column=0)
        org_option_menu = tk.OptionMenu(options_dialog, self._org_option, "date", "size", "type", "general")
        org_option_menu.grid(row=0, column=1)

        tk.Label(options_dialog, text="Renaming Option:").grid(row=1, column=0)
        rename_option_menu = tk.OptionMenu(options_dialog, self._rename_option, "timestamp", "prefix", "suffix")
        rename_option_menu.grid(row=1, column=1)

        tk.Label(options_dialog, text="Filter Option:").grid(row=2, column=0)
        filter_option_menu = tk.OptionMenu(options_dialog, self._image_filter_option, "all", "landscape", "portrait", "square")
        filter_option_menu.grid(row=2, column=1)

        tk.Label(options_dialog, text="Max Size (pixels):").grid(row=3, column=0)
        max_size_scale = tk.Scale(options_dialog, from_=0, to=5000, orient="horizontal")
        max_size_scale.set(self._max_size.get())
        max_size_scale.grid(row=3, column=1)

        tk.Button(options_dialog, text="Apply",
                  command=lambda: self._apply_options(org_option_menu, rename_option_menu, filter_option_menu,
                                                       max_size_scale)).grid(row=4, column=0, columnspan=2)

    def _apply_options(self, org_option_menu: tk.OptionMenu, rename_option_menu: tk.OptionMenu,
                       filter_option_menu: tk.OptionMenu, max_size_scale: tk.Scale) -> None:
        """
        Apply the selected options and close the options dialog.
        """
        self._org_option.set(org_option_menu.get())
        self._rename_option.set(rename_option_menu.get())
        self._image_filter_option.set(filter_option_menu.get())
        self._max_size.set(max_size_scale.get())
        self._set_options_in_interface(org_option_menu.get(), rename_option_menu.get(), filter_option_menu.get(),
                                        max_size_scale.get())
        tk.Toplevel.wm_withdraw(org_option_menu)

    def _set_options_in_interface(self, org_option: str, rename_option: str, filter_option: str, max_size: int) -> None:
        """
        Set the selected options in the interface components.
        """
        self._org_option.set(org_option)
        self._rename_option.set(rename_option)
        self._image_filter_option.set(filter_option)
        self._max_size.set(max_size)

    def _set_up_logger(self):
        """
        Set up the logger.
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler("ezpic.log")
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger


if __name__ == '__main__':
    app = EZPicApp()
    app.mainloop()
    



import logging
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from tkinter import (BooleanVar, Button, Checkbutton, Label, OptionMenu,
                     StringVar, Scale, Tk, Toplevel, filedialog, messagebox, ttk)
from typing import List, Tuple

from PIL import ExifTags, Image, ImageOps


class EZPicApp(Tk):
    """
    Advanced photo management suite application with image processing capabilities.
    """
    def __init__(self) -> None:
        super().__init__()
        self.title("EZ Pic - Advanced Photo Management Suite")
        self.geometry("800x600")
        self._logger = self._set_up_logger()
        self._construct_interface()

    def _construct_interface(self) -> None:
        """
        Construct the main interface of the app.
        """
        self._create_menu_bar()
        self._add_image_processing_frame()

    def _create_menu_bar(self) -> None:
        """
        Create the menu bar and all its submenus.
        """
        menu_bar = Label(self, text="Menu Bar")
        menu_bar.pack()

        org_option_var = StringVar(self)
        org_option_var.set("date")
        org_menu = OptionMenu(self, org_option_var, "date", "size", "type", "general")
        org_menu.pack()

        rename_option_var = StringVar(self)
        rename_option_var.set("timestamp")
        rename_menu = OptionMenu(self, rename_option_var, "timestamp", "prefix", "suffix")
        rename_menu.pack()

        filter_option_var = StringVar(self)
        filter_option_var.set("all")
        filter_menu = OptionMenu(self, filter_option_var, "all", "landscape", "portrait", "square")
        filter_menu.pack()

        options_button = Button(self, text="Options", command=self._display_options_dialog)
        options_button.pack()

        self._org_option = org_option_var
        self._rename_option = rename_option_var
        self._image_filter_option = filter_option_var

    def _add_image_processing_frame(self) -> None:
        """
        Add the image processing frame to the main interface.
        """
        frame = Label(self, text="Image Processing Frame")
        frame.pack()

        max_size_scale = Scale(frame, from_=0, to=5000, label="Max Size (pixels):")
        max_size_scale.pack()

        auto_crop_var = BooleanVar()
        auto_crop_var.set(False)
        auto_crop_checkbox = Checkbutton(frame, text="Auto Crop", variable=auto_crop_var)
        auto_crop_checkbox.pack()

        batch_resize_button = Button(frame, text="Batch Resize",
                                     command=lambda: self._process_button_click(auto_crop_var, max_size_scale.get(), True))
        batch_resize_button.pack()

        preview_button = Button(frame, text="Preview", command=lambda: self._process_button_click(auto_crop_var, max_size_scale.get()))
        preview_button.pack()

        process_button = Button(frame, text="Process", command=lambda: self._process_button_click(auto_crop_var, max_size_scale.get()))
        process_button.pack()

        self.progress_bar = ttk.Progressbar(frame, mode="determinate")
        self.progress_bar.pack(fill="x", padx=10, pady=10)

        self._max_size = max_size_scale
        self._auto_crop_var = auto_crop_var

    def _process_button_click(self, auto_crop_var: BooleanVar, max_size: int, is_batch: bool = False) -> None:
        """
        Handle button click event and execute image processing.
        """
        img_dir = filedialog.askdirectory(title="Select Image Directory")
        if img_dir:
            output_dir = Path(img_dir) / "EZPic Output"
            output_dir.mkdir(parents=True, exist_ok=True)
            image_filter = self._image_filter_option.get()

            if is_batch:
                t = threading.Thread(target=self._execute_batch_processing, args=(img_dir, output_dir, max_size, auto_crop_var, image_filter))
                t.start()
            else:
                self._execute_image_processing(img_dir, output_dir, max_size, auto_crop_var, image_filter)

    def _execute_batch_processing(self, img_dir: str, output_dir: Path, max_size: int, auto_crop_var: BooleanVar, image_filter: str) -> None:
        """
        Execute the batch image processing for images in the specified image directory.
        """
        image_paths = self._get_images(img_dir, image_filter)
        num_images = len(image_paths)
        self.progress_bar["maximum"] = num_images

        for index, img_path in enumerate(image_paths):
            try:
                img = Image.open(img_path).convert("RGB")
                img = self._resize_image(img, max_size)
                img = self._remove_metadata(img)
                if auto_crop_var.get():
                    img = self._auto_crop_image(img)
                self._save_and_organize_image(img, img_path, output_dir)
                self.progress_bar["value"] = index + 1
            except Exception as e:
                self._logger.exception(e)

        self.progress_bar["value"] = 0
        self._logger.info("Batch processing completed successfully")

    def _execute_image_processing(self, img_dir: str, output_dir: Path, max_size: int, auto_crop_var: BooleanVar, image_filter: str) -> None:
        """
        Execute the image processing for images in the specified image directory.
        """
        for img_path in self._get_images(img_dir, image_filter):
            try:
                img = Image.open(img_path).convert("RGB")
                img = self._resize_image(img, max_size)
                img = self._remove_metadata(img)
                if auto_crop_var.get():
                    img = self._auto_crop_image(img)
                self._save_and_organize_image(img, img_path, output_dir)
            except Exception as e:
                messagebox.showerror("Error",
                                     f"Error processing image: {img_path}. Error message: {str(e)}")

    def _get_images(self, img_dir: str, filter_option: str) -> List[str]:
        """
        Return a list of image file paths that match the given subdirectory and filter criteria.
        """
        image_paths = []
        for file_path in Path(img_dir).rglob("*.*"):
            if file_path.is_file() and file_path.suffix.lower() in (".jpg", ".jpeg", ".png"):
                if not self._include_image(file_path, filter_option):
                    continue
                image_paths.append(str(file_path))
        return image_paths

    def _include_image(self, img_path: Path, filter_option: str) -> bool:
        """
        Return True if the image file path matches the given filter criteria.
        """
        if filter_option == "all":
            return True
        elif filter_option == "landscape":
            return self._is_landscape(img_path)
        elif filter_option == "portrait":
            return self._is_portrait(img_path)
        elif filter_option == "square":
            return self._is_square(img_path)
        return False

    def _is_landscape(self, img_path: Path) -> bool:
        """
        Return True if the image is in landscape orientation.
        """
        img = Image.open(img_path)
        width, height = img.size
        return width > height

    def _is_portrait(self, img_path: Path) -> bool:
        """
        Return True if the image is in portrait orientation.
        """
        img = Image.open(img_path)
        width, height = img.size
        return height > width

    def _is_square(self, img_path: Path) -> bool:
        """
        Return True if the image is square.
        """
        img = Image.open(img_path)
        width, height = img.size
        return width == height

    def _resize_image(self, img: Image, max_size: int = 1920) -> Image:
        """
        Return the resized image to fit the specified maximum size, maintaining the aspect ratio.
        """
        width, height = img.size
        ratio = min(max_size / width, max_size / height)
        return img.resize((int(width * ratio), int(height * ratio)), Image.ANTIALIAS)

    def _remove_metadata(self, img: Image) -> Image:
        """
        Remove EXIF metadata from the image.
        """
        data = list(img.getdata())

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == "Orientation":
                break

        try:
            exif = dict(img.getexif().items())
            if exif[orientation] == 3:
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            pass

        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)
        return image_without_exif

    def _save_and_organize_image(self, img: Image, img_path: str, output_folder: Path) -> None:
        """
        Save the image in the specified output folder and subfolder, with the specified new name.
        """
        subfolder = self._determine_subfolder(img, self._org_option.get())
        new_name = self._determine_new_name(img, img_path, self._rename_option.get())
        save_path = output_folder / subfolder / new_name

        save_path.parent.mkdir(parents=True, exist_ok=True)

        img.save(save_path)

    def _determine_subfolder(self, img: Image, org_criteria: str) -> str:
        """
        Determine the subfolder based on the organization criteria.
        """
        if org_criteria == "date":
            return datetime.now().strftime("%Y-%m-%d")
        elif org_criteria == "size":
            return f"{img.size[0]}x{img.size[1]}"
        elif org_criteria == "type":
            file_type = img.format
            return file_type if file_type else "Unknown"
        return "General"

    def _determine_new_name(self, img: Image, img_path: str, rename_criteria: str) -> str:
        """
        Determine the new name of the image based on the renaming criteria.
        """
        base, ext = Path(img_path).stem, Path(img_path).suffix
        if rename_criteria == "timestamp":
            return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        elif rename_criteria == "prefix":
            return f"Edited_{base}{ext}"
        elif rename_criteria == "suffix":
            return f"{base}_Edited{ext}"
        return Path(img_path).name

    def _auto_crop_image(self, img: Image) -> Image:
        """
        Automatically crop the image to remove extra whitespace.
        """
        img = ImageOps.autocontrast(img)
        img = ImageOps.crop(img, img.getbbox())
        return img

    def _display_options_dialog(self) -> None:
        """
        Display the options dialog for the user to customize processing settings.
        """
        options_dialog = OptionsDialog(self)
        options_dialog.grab_set()

    def _set_up_logger(self) -> logging.Logger:
        """
        Set up the application logger for error and debugging messages.
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.FileHandler("ezpic.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger


class OptionsDialog(Toplevel):
    """
    A dialog for setting options that affect image processing.
    """
    def __init__(self, parent: EZPicApp) -> None:
        super().__init__(parent)
        self.title("Options")
        self.geometry("250x200")

        Label(self, text="Output Format").pack(pady=5)
        ttk.Combobox(self, values=["JPEG", "PNG"], state="readonly").pack()

        Label(self, text="Compression").pack(pady=5)
        ttk.Combobox(self, values=["High", "Medium", "Low"], state="readonly").pack()

        Button(self, text="OK", command=self.destroy).pack(pady=5)


if __name__ == "__main__":
    app = EZPicApp()
    app.mainloop()
    
    import os
import shutil
from tkinter import (
    Tk, Label, Button, Checkbutton, BooleanVar, OptionMenu, StringVar, Scale,
    filedialog, messagebox, ttk
)
from typing import List, Tuple
from PIL import Image, ExifTags, ImageOps
from datetime import datetime
import logging
import threading
import os
import shutil
from tkinter import (
    Tk, Label, Button, Checkbutton, BooleanVar, OptionMenu, StringVar, Scale,
    filedialog, messagebox, ttk
)
from typing import List, Tuple
from PIL import Image, ExifTags, ImageOps
from datetime import datetime
import logging
import threading


class EZPicApp(Tk):
    """
    Advanced photo management suite application with image processing capabilities.
    """
    def __init__(self) -> None:
        super().__init__()
        self.title('EZ Pic - Advanced Photo Management Suite')
        self.geometry('800x600')
        self._logger = self._set_up_logger()
        self._construct_interface()

    def _construct_interface(self) -> None:
        """
        Construct the main interface of the app.
        """
        self._create_menu_bar()
        self._add_image_processing_frame()

    def _create_menu_bar(self) -> None:
        """
        Create the menu bar and all its submenus.
        """
        menu_bar = Label(self, text="Menu Bar")
        menu_bar.pack()

        org_option_var = StringVar(self)
        org_option_var.set("date")
        org_menu = OptionMenu(self, org_option_var, "date", "size", "type", "general")
        org_menu.pack()

        rename_option_var = StringVar(self)
        rename_option_var.set("timestamp")
        rename_menu = OptionMenu(self, rename_option_var, "timestamp", "prefix", "suffix")
        rename_menu.pack()

        filter_option_var = StringVar(self)
        filter_option_var.set("all")
        filter_menu = OptionMenu(self, filter_option_var, "all", "landscape", "portrait", "square")
        filter_menu.pack()

        options_button = Button(self, text="Options", command=self._display_options_dialog)
        options_button.pack()

        self._org_option = org_option_var
        self._rename_option = rename_option_var
        self._image_filter_option = filter_option_var

    def _add_image_processing_frame(self) -> None:
        """
        Add the image processing frame to the main interface.
        """
        frame = Label(self, text="Image Processing Frame")
        frame.pack()

        max_size_scale = Scale(frame, from_=0, to=5000, label="Max Size (pixels):")
        max_size_scale.pack()

        auto_crop_var = BooleanVar()
        auto_crop_var.set(False)
        auto_crop_checkbox = Checkbutton(frame, text="Auto Crop", variable=auto_crop_var)
        auto_crop_checkbox.pack()

        batch_resize_button = Button(frame, text="Batch Resize",
                                     command=lambda: self._process_button_click(auto_crop_var, max_size_scale.get(), True))
        batch_resize_button.pack()

        preview_button = Button(frame, text="Preview", command=lambda: self._process_button_click(auto_crop_var, max_size_scale.get()))
        preview_button.pack()

        process_button = Button(frame, text="Process", command=lambda: self._process_button_click(auto_crop_var, max_size_scale.get()))
        process_button.pack()

        self.progress_bar = ttk.Progressbar(frame, mode='determinate')
        self.progress_bar.pack(fill='x', padx=10, pady=10)

        self._max_size = max_size_scale
        self._auto_crop_var = auto_crop_var

    def _process_button_click(self, auto_crop_var: BooleanVar, max_size: int, is_batch: bool = False) -> None:
        """
        Handle button click event and execute image processing.
        """
        img_dir = filedialog.askdirectory()

        if img_dir:
            output_dir = os.path.join(img_dir, "EZPic Output")
            os.makedirs(output_dir, exist_ok=True)
            image_filter = self._image_filter_option.get()

            if is_batch:
                t = threading.Thread(target=self._execute_batch_processing, args=(img_dir, output_dir, max_size, auto_crop_var, image_filter))
                t.start()
            else:
                self._execute_image_processing(img_dir, output_dir, max_size, auto_crop_var, image_filter)

    def _execute_batch_processing(self, img_dir: str, output_dir: str, max_size: int, auto_crop_var: BooleanVar, image_filter: str) -> None:
        """
        Execute the batch image processing for images in the specified image directory.
        """
        image_paths = self._get_images(img_dir, image_filter)
        num_images = len(image_paths)
        self.progress_bar['maximum'] = num_images

        for index, img_path in enumerate(image_paths):
            try:
                img = Image.open(img_path).convert('RGB')
                img = self._resize_image(img, max_size)
                img = self._remove_metadata(img)
                if auto_crop_var.get():
                    img = self._auto_crop_image(img)
                self._save_and_organize_image(img, img_path, output_dir)
                self.progress_bar['value'] = index + 1
            except Exception as e:
                self._logger.exception(e)

        self.progress_bar['value'] = 0
        self._logger.info("Batch processing completed successfully")

    def _execute_image_processing(self, img_dir: str, output_dir: str, max_size: int, auto_crop_var: BooleanVar, image_filter: str) -> None:
        """
        Execute the image processing for images in the specified image directory.
        """
        for img_path in self._get_images(img_dir, image_filter):
            try:
                img = Image.open(img_path).convert('RGB')
                img = self._resize_image(img, max_size)
                img = self._remove_metadata(img)
                if auto_crop_var.get():
                    img = self._auto_crop_image(img)
                self._save_and_organize_image(img, img_path, output_dir)
            except Exception as e:
                messagebox.showerror("Error",
                                     f"Error processing image: {img_path}. Error message: {str(e)}")

    def _get_images(self, img_dir: str, filter_option: str) -> List[str]:
        """
        Return a list of image file paths that match the given subdirectory and filter criteria.
        """
        image_paths = []

        for root, _, files in os.walk(img_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(root, file)

                    if not self._include_image(img_path, filter_option):
                        continue

                    image_paths.append(img_path)

        return image_paths

    def _include_image(self, img_path: str, filter_option: str) -> bool:
        """
        Return True if the image file path matches the given filter criteria.
        """
        if filter_option == "all":
            return True
        elif filter_option == "landscape":
            return self._is_landscape(img_path)
        elif filter_option == "portrait":
            return self._is_portrait(img_path)
        elif filter_option == "square":
            return self._is_square(img_path)
        return False

    def _is_landscape(self, img_path: str) -> bool:
        """
        Return True if the image is in landscape orientation.
        """
        img = Image.open(img_path)
        width, height = img.size
        return width > height

    def _is_portrait(self, img_path: str) -> bool:
        """
        Return True if the image is in portrait orientation.
        """
        img = Image.open(img_path)
        width, height = img.size
        return height > width

    def _is_square(self, img_path: str) -> bool:
        """
        Return True if the image is square.
        """
        img = Image.open(img_path)
        width, height = img.size
        return width == height

    def _resize_image(self, img: Image, max_size: int = 1920) -> Image:
        """
        Return the resized image to fit the specified maximum size, maintaining the aspect ratio.
        """
        width, height = img.size
        ratio = min(max_size / width, max_size / height)
        return img.resize((int(width * ratio), int(height * ratio)), Image.ANTIALIAS)

    def _remove_metadata(self, img: Image) -> Image:
        """
        Remove EXIF metadata from the image.
        """
        data = list(img.getdata())

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        try:
            exif = dict(img.getexif().items())
            if exif[orientation] == 3:
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img = img.rotate(90, expand=True)
        except:
            pass

        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)
        return image_without_exif

    def _save_and_organize_image(self, img: Image, img_path: str, output_folder: str) -> None:
        """
        Save the image in the specified output folder and subfolder, with the specified new name.
        """
        subfolder = self._determine_subfolder(img, self._org_option.get())
        new_name = self._determine_new_name(img, img_path, self._rename_option.get())
        save_path = os.path.join(output_folder, subfolder, new_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path)

    def _determine_subfolder(self, img: Image, org_criteria: str) -> str:
        """
        Determine the subfolder based on the organization criteria.
        """
        if org_criteria == "date":
            return datetime.now().strftime("%Y-%m-%d")
        elif org_criteria == "size":
            return f"{img.size[0]}x{img.size[1]}"
        elif org_criteria == "type":
            file_type = img.format
            return file_type if file_type else "Unknown"
        return "General"

    def _determine_new_name(self, img: Image, img_path: str, rename_criteria: str) -> str:
        """
        Determine the new name of the image based on the renaming criteria.
        """
        base, ext = os.path.splitext(os.path.basename(img_path))
        if rename_criteria == "timestamp":
            return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        elif rename_criteria == "prefix":
            return f"Edited_{base}{ext}"
        elif rename_criteria == "suffix":
            return f"{base}_Edited{ext}"
        return os.path.basename(img_path)

    def _auto_crop_image(self, img: Image) -> Image:
        """
        Automatically crop the image to remove extra whitespace.
        """
        img = ImageOps.autocontrast(img)
        img = ImageOps.crop(img, img.getbbox())
        return img

    def _display_options_dialog(self) -> None:
        """
        Display the options dialog for the user to customize processing settings.
        """
        options_dialog = OptionsDialog(self)
        options_dialog.grab_set()

    def _set_up_logger(self) -> logging.Logger:
        """
        Set up the application logger for error and debugging messages.
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.FileHandler("ezpic.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger


class OptionsDialog(Toplevel):
    """
    A dialog for setting options that affect image processing.
    """
    def __init__(self, parent: EZPicApp) -> None:
        super().__init__(parent)
        self.title("Options")
        self.geometry("250x200")

        Label(self, text="Output Format").pack(pady=5)
        ttk.Combobox(self, values=["JPEG", "PNG"], state="readonly").pack()

        Label(self, text="Compression").pack(pady=5)
        ttk.Combobox(self, values=["High", "Medium", "Low"], state="readonly").pack()

        Button(self, text="OK", command=self.destroy).pack(pady=5)


if __name__ == "__main__":
    app = EZPicApp()
    app.mainloop()
    
    

class EZPicApp(Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('EZ Pic - Advanced Photo Management Suite')
        self.geometry('800x600')
        self.logger = self.set_up_logger()
        self.construct_interface()

    def construct_interface(self) -> None:
        self.create_menu_bar()
        self.add_image_processing_frame()

    def create_menu_bar(self) -> None:
        menu_bar = Label(self, text="Menu Bar")
        menu_bar.pack()

        org_menu = OptionMenu(self, self.org_option, "date", "size", "type", "general")
        org_menu.pack()

        rename_menu = OptionMenu(self, self.rename_option, "timestamp", "prefix", "suffix")
        rename_menu.pack()

        filter_menu = OptionMenu(self, self.image_filter_option, "all", "landscape", "portrait", "square")
        filter_menu.pack()

        options_button = Button(self, text="Options", command=self.display_options_dialog)
        options_button.pack()

    def add_image_processing_frame(self) -> None:
        frame = Label(self, text="Image Processing Frame")
        frame.pack()

        batch_resize_button = Button(frame, text="Batch Resize",
                                     command=self.process_batch_resize_button_click)
        batch_resize_button.pack()

        auto_crop_checkbox = Checkbutton(frame, text="Auto Crop", variable=self.auto_crop_var)
        auto_crop_checkbox.pack()

        preview_button = Button(frame, text="Preview", command=self.process_preview_button_click)
        preview_button.pack()

        process_button = Button(frame, text="Process", command=self.execute_image_processing)
        process_button.pack()

        self.progress_bar = ttk.Progressbar(frame, mode='determinate')
        self.progress_bar.pack(fill='x', padx=10, pady=10)

    def process_batch_resize_button_click(self) -> None:
        self.logger.info("Starting batch processing")
        t = threading.Thread(target=self.execute_batch_processing)
        t.start()

    def execute_batch_processing(self) -> None:
        img_dir = filedialog.askdirectory()

        if img_dir:
            output_dir = os.path.join(img_dir, "EZPic Output")
            os.makedirs(output_dir, exist_ok=True)
            max_size = self.max_size.get()
            auto_crop = self.auto_crop_var.get()
            image_filter = self.image_filter_option.get()
            image_paths = []

            for root, _, files in os.walk(img_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(root, file)

                        if not self.include_image(img_path, image_filter):
                            continue

                        image_paths.append(img_path)

            num_images = len(image_paths)
            self.progress_bar['maximum'] = num_images

            for index, img_path in enumerate(image_paths):
                try:
                    img = Image.open(img_path).convert('RGB')
                    img = self.resize_image(img, max_size)
                    img = self.remove_metadata(img)
                    if auto_crop:
                        img = self.auto_crop_image(img)
                    self.save_and_organize_image(img, img_path, output_dir)
                    self.progress_bar['value'] = index + 1
                except Exception as e:
                    self.logger.exception(e)

            self.progress_bar['value'] = 0
            self.logger.info("Batch processing completed successfully")

    def process_preview_button_click(self) -> None:
        pass  # Placeholder for future implementation

    def execute_image_processing(self) -> None:
        img_dir = filedialog.askdirectory()

        if img_dir:
            output_dir = os.path.join(img_dir, "EZPic Output")
            os.makedirs(output_dir, exist_ok=True)
            max_size = self.max_size.get()
            auto_crop = self.auto_crop_var.get()
            image_filter = self.image_filter_option.get()

            for root, _, files in os.walk(img_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(root, file)

                        if not self.include_image(img_path, image_filter):
                            continue

                        try:
                            img = Image.open(img_path).convert('RGB')
                            img = self.resize_image(img, max_size)
                            img = self.remove_metadata(img)
                            if auto_crop:
                                img = self.auto_crop_image(img)
                            self.save_and_organize_image(img, img_path, output_dir)
                        except Exception as e:
                            messagebox.showerror("Error",
                                                 f"Error processing image: {img_path}. Error message: {str(e)}")

    def include_image(self, img_path: str, filter_option: str) -> bool:
        if filter_option == "all":
            return True
        elif filter_option == "landscape":
            return self.is_landscape(img_path)
        elif filter_option == "portrait":
            return self.is_portrait(img_path)
        elif filter_option == "square":
            return self.is_square(img_path)
        return False

    def is_landscape(self, img_path: str) -> bool:
        img = Image.open(img_path)
        width, height = img.size
        return width > height

    def is_portrait(self, img_path: str) -> bool:
        img = Image.open(img_path)
        width, height = img.size
        return height > width

    def is_square(self, img_path: str) -> bool:
        img = Image.open(img_path)
        width, height = img.size
        return width == height

    def resize_image(self, img: Image, max_size: int = 1920) -> Image:
        """
        This method resizes the image to fit the specified maximum size, maintaining the aspect ratio.
        """
        width, height = img.size
        ratio = min(max_size / width, max_size / height)
        return img.resize((int(width * ratio), int(height * ratio)), Image.ANTIALIAS)

    def remove_metadata(self, img: Image) -> Image:
        """
        This method removes EXIF metadata from the image.
        """
        data = list(img.getdata())

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        try:
            exif = dict(img.getexif().items())
            if exif[orientation] == 3:
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img = img.rotate(90, expand=True)
        except:
            pass

        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)
        return image_without_exif

    def save_and_organize_image(self, img: Image, img_path: str, output_folder: str) -> None:
        """
        This method saves the image in the specified output folder and subfolder, with the specified new name.
        """
        subfolder = self.determine_subfolder(img, self.org_option.get())
        new_name = self.determine_new_name(img, img_path, self.rename_option.get())
        save_path = os.path.join(output_folder, subfolder, new_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path)

    def determine_subfolder(self, img: Image, org_criteria: str) -> str:
        """
        This method determines the subfolder based on the organization criteria.
        """
        if org_criteria == "date":
            return datetime.now().strftime("%Y-%m-%d")
        elif org_criteria == "size":
            return f"{img.size[0]}x{img.size[1]}"
        elif org_criteria == "type":
            file_type = img.format
            return file_type if file_type else "Unknown"
        return "General"

    def determine_new_name(self, img: Image, img_path: str, rename_criteria: str) -> str:
        """
        This method determines the new name of the image based on the renaming criteria.
        """
        base, ext = os.path.splitext(os.path.basename(img_path))
        if rename_criteria == "timestamp":
            return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        elif rename_criteria == "prefix":
            return f"Edited_{base}{ext}"
        elif rename_criteria == "suffix":
            return f"{base}_Edited{ext}"
        return os.path.basename(img_path)

    def auto_crop_image(self, img: Image) -> Image:
        img = ImageOps.autocontrast(img)
        img = ImageOps.crop(img, img.getbbox())
        return img

    def display_options_dialog(self) -> None:
        options_dialog = OptionsDialog(self)
        options_dialog.grab_set()

    def set_up_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.FileHandler("ezpic.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger


class OptionsDialog(Toplevel):
    def __init__(self, parent: EZPicApp) -> None:
        super().__init__(parent)
        self.title("Options")
        self.geometry("250x200")

        Label(self, text="Output Format").pack(pady=5)
        ttk.Combobox(self, values=["JPEG", "PNG"], state="readonly").pack()

        Label(self, text="Compression").pack(pady=5)
        ttk.Combobox(self, values=["High", "Medium", "Low"], state="readonly").pack()

        Button(self, text="OK", command=self.destroy).pack(pady=5)


if __name__ == "__main__":
    app = EZPicApp()
    app.mainloop()

import os
import shutil
from tkinter import (
    Tk, Label, Button, Checkbutton, BooleanVar, OptionMenu, StringVar, Scale,
    filedialog, image_names, messagebox
)
from typing import List
from PIL import Image, ExifTags
from datetime import datetime
import os
import shutil
from tkinter import (
    Tk, Label, Button, Checkbutton, BooleanVar, OptionMenu, StringVar, Scale,
    filedialog, messagebox
)
from typing import List, Tuple
from PIL import Image, ExifTags
from datetime import datetime

from Active_Projects.EZ_Pic.init import ImageEnhancerGUI

import os
import shutil
from tkinter import (
    Tk, Label, Button, Checkbutton, BooleanVar, OptionMenu, StringVar, Scale,
    filedialog, messagebox, ttk
)
from typing import List, Tuple
from PIL import Image, ExifTags, ImageOps
from datetime import datetime
import logging
import threading


class EZPicApp(Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('EZ Pic - Advanced Photo Management Suite')
        self.geometry('800x600')
        self.logger = self.set_up_logger()
        self.construct_interface()

    def construct_interface(self) -> None:
        self.create_menu_bar()
        self.add_image_processing_frame()

    def create_menu_bar(self) -> None:
        menu_bar = Label(self, text="Menu Bar")
        menu_bar.pack()

        org_menu = OptionMenu(self, self.org_option, "date", "size", "type", "general")
        org_menu.pack()

        rename_menu = OptionMenu(self, self.rename_option, "timestamp", "prefix", "suffix")
        rename_menu.pack()

        filter_menu = OptionMenu(self, self.image_filter_option, "all", "landscape", "portrait", "square")
        filter_menu.pack()

        options_button = Button(self, text="Options", command=self.display_options_dialog)
        options_button.pack()

    def add_image_processing_frame(self) -> None:
        frame = Label(self, text="Image Processing Frame")
        frame.pack()

        batch_resize_button = Button(frame, text="Batch Resize",
                                     command=self.process_batch_resize_button_click)
        batch_resize_button.pack()

        auto_crop_checkbox = Checkbutton(frame, text="Auto Crop", variable=self.auto_crop_var)
        auto_crop_checkbox.pack()

        preview_button = Button(frame, text="Preview", command=self.process_preview_button_click)
        preview_button.pack()

        process_button = Button(frame, text="Process", command=self.execute_image_processing)
        process_button.pack()

        self.progress_bar = ttk.Progressbar(frame, mode='determinate')
        self.progress_bar.pack(fill='x', padx=10, pady=10)

    def process_batch_resize_button_click(self) -> None:
        self.logger.info("Starting batch processing")
        t = threading.Thread(target=self.execute_batch_processing)
        t.start()

    def execute_batch_processing(self) -> None:
        img_dir = filedialog.askdirectory()
        if img_dir:
            output_dir = os.path.join(img_dir, "EZPic Output")
            os.makedirs(output_dir, exist_ok=True)
            max_size = self.max_size.get()
            auto_crop = self.auto_crop_var.get()
            image_filter = self.image_filter_option.get()
            image_paths = []

            for root, _, files in os.walk(img_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(root, file)

                        if not self.include_image(img_path, image_filter):
                            continue

                        image_paths.append(img_path)

            num_images = len(image_paths)
            self.progress_bar['maximum'] = num_images

            for index, img_path in enumerate(image_paths):
                try:
                    img = Image.open(img_path).convert('RGB')
                    img = self.resize_image(img, max_size)
                    img = self.remove_metadata(img)
                    if auto_crop:
                        img = self.auto_crop_image(img)
                    self.save_and_organize_image(img, img_path, output_dir)
                    self.progress_bar['value'] = index + 1
                except Exception as e:
                    self.logger.exception(e)

            self.progress_bar['value'] = 0
            self.logger.info("Batch processing completed successfully")

    def process_preview_button_click(self) -> None:
        pass  # Placeholder for future implementation

    def execute_image_processing(self) -> None:
        img_dir = filedialog.askdirectory()
        if img_dir:
            output_dir = os.path.join(img_dir, "EZPic Output")
            os.makedirs(output_dir, exist_ok=True)
            max_size = self.max_size.get()
            auto_crop = self.auto_crop_var.get()
            image_filter = self.image_filter_option.get()

            for root, _, files in os.walk(img_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(root, file)

                        if not self.include_image(img_path, image_filter):
                            continue

                        try:
                            img = Image.open(img_path).convert('RGB')
                            img = self.resize_image(img, max_size)
                            img = self.remove_metadata(img)
                            if auto_crop:
                                img = self.auto_crop_image(img)
                            self.save_and_organize_image(img, img_path, output_dir)
                        except Exception as e:
                            messagebox.showerror("Error",
                                                 f"Error processing image: {img_path}. Error message: {str(e)}")

    def include_image(self, img_path: str, filter_option: str) -> bool:
        if filter_option == "all":
            return True
        elif filter_option == "landscape":
            return self.is_landscape(img_path)
        elif filter_option == "portrait":
            return self.is_portrait(img_path)
        elif filter_option == "square":
            return self.is_square(img_path)
        return False

    def is_landscape(self, img_path: str) -> bool:
        img = Image.open(img_path)
        width, height = img.size
        return width > height

    def is_portrait(self, img_path: str) -> bool:
        img = Image.open(img_path)
        width, height = img.size
        return height > width

    def is_square(self, img_path: str) -> bool:
        img = Image.open(img_path)
        width, height = img.size
        return width == height

    def resize_image(self, img: Image, max_size: int = 1920) -> Image:
        """
        This method resizes the image to fit the specified maximum size, maintaining the aspect ratio.
        """
        width, height = img.size
        ratio = min(max_size / width, max_size / height)
        return img.resize((int(width * ratio), int(height * ratio)), Image.ANTIALIAS)

    def remove_metadata(self, img: Image) -> Image:
        """
        This method removes EXIF metadata from the image.
        """
        data = list(img.getdata())

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        try:
            exif = dict(img.getexif().items())
            if exif[orientation] == 3:
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img = img.rotate(90, expand=True)
        except:
            pass

        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)
        return image_without_exif

    def save_and_organize_image(self, img: Image, img_path: str, output_folder: str) -> None:
        """
        This method saves the image in the specified output folder and subfolder, with the specified new name.
        """
        subfolder = self.determine_subfolder(img, self.org_option.get())
        new_name = self.determine_new_name(img, img_path, self.rename_option.get())
        save_path = os.path.join(output_folder, subfolder, new_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path)

    def determine_subfolder(self, img: Image, org_criteria: str) -> str:
        """
        This method determines the subfolder based on the organization criteria.
        """
        if org_criteria == "date":
            return datetime.now().strftime("%Y-%m-%d")
        elif org_criteria == "size":
            return f"{img.size[0]}x{img.size[1]}"
        elif org_criteria == "type":
            file_type = img.format
            return file_type if file_type else "Unknown"
        return "General"

    def determine_new_name(self, img: Image, img_path: str, rename_criteria: str) -> str:
        """
        This method determines the new name of the image based on the renaming criteria.
        """
        base, ext = os.path.splitext(os.path.basename(img_path))
        if rename_criteria == "timestamp":
            return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        elif rename_criteria == "prefix":
            return f"Edited_{base}{ext}"
        elif rename_criteria == "suffix":
            return f"{base}_Edited{ext}"
        return os.path.basename(img_path)

    def auto_crop_image(self, img: Image) -> Image:
        img = ImageOps.autocontrast(img)
        img = ImageOps.crop(img, img.getbbox())
        return img

    def display_options_dialog(self) -> None:
        options_dialog = OptionsDialog(self)
        options_dialog.grab_set()

    def set_up_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.FileHandler("ezpic.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger


class OptionsDialog(Toplevel):
    def __init__(self, parent: EZPicApp) -> None:
        super().__init__(parent)
        self.title("Options")
        self.geometry("250x200")

        Label(self, text="Output Format").pack(pady=5)
        ttk.Combobox(self, values=["JPEG", "PNG"], state="readonly").pack()

        Label(self, text="Compression").pack(pady=5)
        ttk.Combobox(self, values=["High", "Medium", "Low"], state="readonly").pack()

        Button(self, text="OK", command=self.destroy).pack(pady=5)


if __name__ == "__main__":
    app = EZPicApp()
    app.mainloop()
class EZPicApp(Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('EZ Pic - Advanced Photo Management Suite')
        self.geometry('800x600')
        self.construct_interface()

    def construct_interface(self) -> None:
        self.create_menu_bar()
        self.add_image_processing_frame()

    def create_menu_bar(self) -> None:
        menu_bar = Label(self, text="Menu Bar")
        menu_bar.pack()

        org_menu = OptionMenu(self, self.org_option, "date", "size", "type", "general")
        org_menu.pack()

        rename_menu = OptionMenu(self, self.rename_option, "timestamp", "prefix", "suffix")
        rename_menu.pack()

        filter_menu = OptionMenu(self, self.image_filter_option, "all", "landscape", "portrait", "square")
        filter_menu.pack()

    def add_image_processing_frame(self) -> None:
        frame = Label(self, text="Image Processing Frame")
        frame.pack()

        batch_resize_button = Button(frame, text="Batch Resize",
                                     command=self.process_batch_resize_button_click)
        batch_resize_button.pack()

        auto_crop_checkbox = Checkbutton(frame, text="Auto Crop", variable=self.auto_crop_var)
        auto_crop_checkbox.pack()

        preview_button = Button(frame, text="Preview", command=self.process_preview_button_click)
        preview_button.pack()

        process_button = Button(frame, text="Process", command=self.execute_image_processing)
        process_button.pack()

    def process_batch_resize_button_click(self) -> None:
        pass  # Placeholder for future implementation

    def process_preview_button_click(self) -> None:
        pass  # Placeholder for future implementation

    def execute_image_processing(self) -> None:
        img_dir = filedialog.askdirectory()
        if img_dir:
            output_dir = os.path.join(img_dir, "EZPic Output")
            os.makedirs(output_dir, exist_ok=True)
            max_size = self.max_size.get()
            auto_crop = self.auto_crop_var.get()
            image_filter = self.image_filter_option.get()

            for root, _, files in os.walk(img_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(root, file)

                        if not self.include_image(img_path, image_filter):
                            continue

                        try:
                            img = Image.open(img_path).convert('RGB')
                            img = self.resize_image(img, max_size)
                            img = self.remove_metadata(img)
                            if auto_crop:
                                img = self.auto_crop_image(img)
                            self.save_and_organize_image(img, file, output_dir)
                        except Exception as e:
                            messagebox.showerror("Error",
                                                 f"Error processing image: {img_path}. Error message: {str(e)}")

    def include_image(self, img_path: str, filter_option: str) -> bool:
        if filter_option == "all":
            return True
        elif filter_option == "landscape":
            return self.is_landscape(img_path)
        elif filter_option == "portrait":
            return self.is_portrait(img_path)
        elif filter_option == "square":
            return self.is_square(img_path)
        return False

    def is_landscape(self, img_path: str) -> bool:
        img = Image.open(img_path)
        width, height = img.size
        return width > height

    def is_portrait(self, img_path: str) -> bool:
        img = Image.open(img_path)
        width, height = img.size
        return height > width

    def is_square(self, img_path: str) -> bool:
        img = Image.open(img_path)
        width, height = img.size
        return width == height

    def resize_image(self, img: Image, max_size: int = 1920) -> Image:
        """
        This method resizes the image to fit the specified maximum size, maintaining the aspect ratio.
        """
        width, height = img.size
        ratio = min(max_size / width, max_size / height)
        return img.resize((int(width * ratio), int(height * ratio)), Image.ANTIALIAS)

    def remove_metadata(self, img: Image) -> Image:
        """
        This method removes EXIF metadata from the image.
        """
        data = list(img.getdata())

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        try:
            exif = dict(img.getexif().items())
            if exif[orientation] == 3:
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img = img.rotate(90, expand=True)
        except:
            pass

        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)
        return image_without_exif

    def save_and_organize_image(self, img: Image, image_name: str, output_folder: str) -> None:
        """
        This method saves the image in the specified output folder and subfolder, with the specified new name.
        """
        subfolder = self.determine_subfolder(img, self.org_option.get())
        new_name = self.determine_new_name(img, image_name, self.rename_option.get())
        save_path = os.path.join(output_folder, subfolder, new_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path)

    def determine_subfolder(self, img: Image, org_criteria: str) -> str:
        """
        This method determines the subfolder based on the organization criteria.
        """
        if org_criteria == "date":
            return datetime.now().strftime("%Y-%m-%d")
        elif org_criteria == "size":
            return f"{img.size[0]}x{img.size[1]}"
        elif org_criteria == "type":
            file_type = img.format
            return file_type if file_type else "Unknown"
        return "General"

    def determine_new_name(self, img: Image, image_name: str, rename_criteria: str) -> str:
        """
        This method determines the new name of the image based on the renaming criteria.
        """
        base, ext = os.path.splitext(image_name)
        if rename_criteria == "timestamp":
            return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        elif rename_criteria == "prefix":
            return f"Edited_{base}{ext}"
        elif rename_criteria == "suffix":
            return f"{base}_Edited{ext}"
        return image_name

    def auto_crop_image(self, img: Image) -> Image:
        pass  # Placeholder for future implementation

    # Additional methods for new features

    # Setting parameters for the app
    org_option = StringVar()  # for organization
    rename_option = StringVar()  # for renaming rules
    max_size = Scale(from_=100, to=1920, orient="horizontal")  # for resizing by max size of images
    auto_crop_var = BooleanVar()  # to trigger auto-cropping
    image_filter_option = StringVar()  # filter options

    # Rest of the existing code...


if __name__ == "__main__":
    app = EZPicApp()
    app.mainloop()

class EZPicApp(Tk):
    def __init__(self):
        super().__init__()
        self.title('EZ Pic - Advanced Photo Management Suite')
        self.geometry('800x600')
        self.construct_interface()

    def construct_interface(self):
        self.add_organization_options()
        self.add_renaming_options()
        self.add_batch_resize_options()
        self.add_auto_crop_feature()
        self.add_image_filter_options()
        self.add_preview_button()
        self.add_error_handling()
        self.add_progress_bar()
        self.add_batch_edit_options()

    def execute_image_processing(self):
        img_dir = filedialog.askdirectory()
        if img_dir:
            output_dir = os.path.join(img_dir, "EZPic Output")
            os.makedirs(output_dir, exist_ok=True)
            max_size = self.max_size.get()
            auto_crop = self.auto_crop_var.get()
            image_filter = self.image_filter_option.get()

            for root, _, files in os.walk(img_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(root, file)

                        if not self.include_image(img_path, image_filter):
                            continue

                        try:
                            img = Image.open(img_path).convert('RGB')
                            img = self.resize_image(img, max_size)
                            img = self.remove_metadata(img)
                            if auto_crop:
                                img = self.auto_crop_image(img)
                            self.save_and_organize_image(img, file, output_dir)
                        except Exception as e:
                            self.progress_bar["value"] = 0
                            messagebox.showerror("Error",
                                                 f"Error processing image: {img_path}. Error message: {str(e)}")

    def resize_image(self, img: Image, max_size: int = 1920) -> Image:
        """
        This method resizes the image to fit the specified maximum size, maintaining the aspect ratio.
        """
        width, height = img.size
        ratio = min(max_size/width, max_size/height)
        return img.resize((int(width * ratio), int(height * ratio)), Image.ANTIALIAS)

    def remove_metadata(self, img: Image) -> Image:
        """
        This method removes EXIF metadata from the image.
        """
        data = list(img.getdata())

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        try:
            exif = dict(img.getexif().items())
            if exif[orientation] == 3:
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img = img.rotate(90, expand=True)
        except:
            pass

        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)
        return image_without_exif

    def save_and_organize_image(self, img: Image, image_name: str,
                                output_folder: str) -> None:
        """
        This method saves the image in the specified output folder and subfolder, with the specified new name.
        """
        subfolder = self.determine_subfolder(img, self.org_option.get())
        new_name = self.determine_new_name(img, image_name,
                                           self.rename_option.get())
        save_path = os.path.join(output_folder, subfolder, new_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path)

    def determine_subfolder(self, img: Image, org_criteria: str) -> str:
        """
        This method determines the subfolder based on the specified organization criteria.
        """
        if org_criteria == "date":
            return datetime.now().strftime("%Y-%m-%d")
        elif org_criteria == "size":
            return f"{img.size[0]}x{img.size[1]}"
        elif org_criteria == "type":
            return os.path.splitext(image_names)[1][1:].upper()
        return "General"

    def determine_new_name(self, img: Image, image_name: str,
                            rename_criteria: str) -> str:
        """
        This method determines the new name of the image based on the specified renaming criteria.
        """
        base, ext = os.path.splitext(image_name)
        if rename_criteria == "timestamp":
            return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        elif rename_criteria == "prefix":
            return f"Edited_{base}{ext}"
        elif rename_criteria == "suffix":
            return f"{base}_Edited{ext}"
        elif rename_criteria == "original":
            return image_name

    def add_image_filter_options(self):
        """
        This method adds the image filter options to the UI.
        """
        self.filter_label = Label(
            self, text="Filter images by:", anchor="w"
        )
        self.filter_label.grid(row=9, column=0, sticky="w")
        self.filter_options = ["None", "Black & White", "Sepia", "Negative"]
        self.image_filter_option = StringVar(value=self.filter_options[0])
        self.filter_menu = OptionMenu(
            self, self.image_filter_option, *self.filter_options
        )
        self.filter_menu.grid(row=9, column=1, sticky="ew")

    def add_preview_button(self):
        """
        This method adds the preview button to the UI.
        """
        self.preview_button = Button(
            self, text="Preview", command=self.preview_image
        )
        self.preview_button.grid(row=10, column=0, columnspan=2)

    def add_error_handling(self):
        """
        This method adds error handling to the program.
        """
        # Placeholder for future error handling implementation
        pass

    def add_progress_bar(self):
        """
        This method adds a progress bar to the program.
        """
        # Placeholder for future progress bar implementation
        pass

    def add_batch_edit_options(self):
        """
        This method adds batch edit options to the program.
        """
        # Placeholder for future batch edit implementation
        pass

    def include_image(self, img_path: str, image_filter: str) -> bool:
        """
        This method determines if the image should be included based on the specified filter.
        """
        if image_filter == "None":
            return True
        elif image_filter == "Black & White":
            img = Image.open(img_path).convert('L')
            img_enhancer = ImageEnhancerGUI.Color(img)
            img_colored = img_enhancer.enhance(0)
            return img == img_colored
        elif image_filter == "Sepia":
            img = Image.open(img_path).convert('L')
            img_sepia = Image.new('L', img.size, '#704214')
            img = Image.blend(img, img_sepia, 0.4)
            return True
        elif image_filter == "Negative":
            img = Image.open(img_path).convert('L')
            img_negative = ImageOps.invert(img)
            return True
        else:
            return False

    def auto_crop_image(self, img: Image) -> Image:
        """
        This method automatically crops the image to remove any blank space.
        """
        bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
        diff = ImageChops.difference(img, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return img.crop(bbox)
        else:
            return img

    def preview_image(self):
        """
        This method previews the image with the selected filter applied.
        """
        # Placeholder for future preview image implementation
        pass


if __name__ == "__main__":
    app = EZPicApp()
    app.mainloop()
    
    import os
import shutil
from tkinter import (
    Tk, Label, Button, Checkbutton, BooleanVar, OptionMenu, StringVar, Scale,
    filedialog, messagebox
)
from typing import List
from PIL import Image, ExifTags
from datetime import datetime


class EZPicApp(Tk):
    def __init__(self):
        super().__init__()
        self.title('EZ Pic - Advanced Photo Management Suite')
        self.geometry('800x600')
        self.construct_interface()

    def construct_interface(self):
        self.add_organization_options()
        self.add_renaming_options()
        self.add_batch_resize_options()
        self.add_auto_crop_feature()
        self.add_image_filter_options()
        self.add_preview_button()
        self.add_error_handling()
        self.add_progress_bar()
        self.add_batch_edit_options()

    def execute_image_processing(self):
        img_dir = filedialog.askdirectory()
        if img_dir:
            output_dir = os.path.join(img_dir, "EZPic Output")
            os.makedirs(output_dir, exist_ok=True)
            max_size = self.max_size.get()
            auto_crop = self.auto_crop_var.get()
            image_filter = self.image_filter_option.get()

            for root, _, files in os.walk(img_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(root, file)

                        if not self.include_image(img_path, image_filter):
                            continue

                        try:
                            img = Image.open(img_path).convert('RGB')
                            img = self.resize_image(img, max_size)
                            img = self.remove_metadata(img)
                            if auto_crop:
                                img = self.auto_crop_image(img)
                            self.save_and_organize_image(img, file, output_dir)
                        except Exception as e:
                            self.progress_bar["value"] = 0
                            messagebox.showerror("Error",
                                                 f"Error processing image: {img_path}. Error message: {str(e)}")

    def resize_image(self, img: Image, max_size: int = 1920) -> Image:
        """
        This method resizes the image to fit the specified maximum size, maintaining the aspect ratio.
        """
        width, height = img.size
        ratio = min(max_size/width, max_size/height)
        return img.resize((int(width * ratio), int(height * ratio)), Image.ANTIALIAS)

    def remove_metadata(self, img: Image) -> Image:
        """
        This method removes EXIF metadata from the image.
        """
        data = list(img.getdata())

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        try:
            exif = dict(img.getexif().items())
            if exif[orientation] == 3:
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img = img.rotate(90, expand=True)
        except:
            pass

        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)
        return image_without_exif

    def save_and_organize_image(self, img: Image, image_name: str,
                                output_folder: str) -> None:
        """
        This method saves the image in the specified output folder and subfolder, with the specified new name.
        """
        subfolder = self.determine_subfolder(img, self.org_option.get())
        new_name = self.determine_new_name(img, image_name,
                                           self.rename_option.get())
        save_path = os.path.join(output_folder, subfolder, new_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path.save(save_path), "JPEG").close()

    def determine_subfolder(self, img: Image, org_criteria: str) -> str:
        """
        This method determines the subfolder based on the organization criteria.
        """
        if org_criteria == "date":
            return datetime.now().strftime("%Y-%m-%d")
        elif org_criteria == "size":
            return f"{img.size[0]}x{img.size[1]}"
        elif org_criteria == "type":
            file_type = img.format
            return file_type if file_type else "Unknown"
        return "General"

    def determine_new_name(self, img: Image, image_name: str, rename_criteria: str) -> str:
        """
        This method determines the new name of the image based on the renaming criteria.
        """
        base, ext = os.path.splitext(image_name)
        if rename_criteria == "timestamp":
            return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        elif rename_criteria == "prefix":
            return f"Edited_{base}{ext}"
        elif rename_criteria == "suffix":
            return f"{base}_Edited{ext}"
        return image_name

    # Additional methods for new features
    def add_organization_options(self):
        # Organization options code here...
        # Placeholder for future organization options implementation

    def add_renaming_options(self):
        # Renaming options code here...
        # Placeholder for future renaming options implementation

    def add_batch_resize_options(self):
        # Batch resize options code here...
        # Placeholder for future batch resize options implementation

    def add_auto_crop_feature(self):
        # Auto crop feature code here...
        # Placeholder for future auto crop implementation

    def add_image_filter_options(self):
        # Image filter options code here...
        # Placeholder for future image filter options implementation

    def add_preview_button(self):
        # Preview button code here...
        # Placeholder for future preview button implementation

    def add_error_handling(self):
        # Error handling code here...
        # Placeholder for future error handling implementation

    def add_progress_bar(self):
        # Progress bar code here...
        # Placeholder for future progress bar implementation

    def add_batch_edit_options(self):
        # Batch edit options code here...
        # Placeholder for future batch edit options implementation

    # Rest of the existing code...
    # ... (implement as needed)

if __name__ == "__main__":
    app = EZPicApp()
    app.mainloop()
