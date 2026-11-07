import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageOps, ExifTags
from typing import List, Tuple
from pathlib import Path
from datetime import datetime
import logging


class EZPicApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('EZPic')
        self.geometry('700x350')
        self.images_dir = Path.cwd() / 'Images'
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
        Loads images from the selected directory into the GUI.
        """
        dir_path = filedialog.askdirectory(initialdir="/", title="Select Images Directory")
        if dir_path:
            self.images_dir = Path(dir_path)
            self.logger.info(f"Selected Images Directory: {self.images_dir}")
            self.images = [img for img in self.images_dir.iterdir() if img.is_file() and img.suffix.lower() in ['.jpg', '.jpeg', '.png']]
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
            del image
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
        output_dir = self.images_dir / 'EZPic Output'
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            for img_path in self.filtered_images:
                img = Image.open(img_path)
                img = self._remove_metadata(img)
                img = self._auto_crop_image(img)
                img = self._resize_image(img, self._max_size.get())
                self._save_and_organize_image(img, img_path, output_dir)
                del img
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