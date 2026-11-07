import argparse
import hashlib
import logging
import os
import random
import string
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Optional
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileOrganizerGUI:
    """
    A class for maintaining GUI and UI elements.
    """

    def __init__(self, root: tk.Tk) -> None:
        """
        Initializes a GUI.
        """

        self.log = logging.getLogger("GUI")
        self.root = root
        self.root.title('File Organizer')
        self.directory_path: tk.StringVar = tk.StringVar()
        self.remove_metadata: tk.BooleanVar = tk.BooleanVar(value=False)
        self.random_rename: tk.BooleanVar = tk.BooleanVar(value=False)
        self.organize_folders: tk.BooleanVar = tk.BooleanVar(value=False)
        self.create_widgets()

    def create_widgets(self) -> None:
        """Generates the widgets on the GUI"""

        # create a frame to group the widgets
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack()

        # directory selection label and button
        tk.Label(
            frame, text="Select directory:", font=("Helvetica", 14)).grid(
                row=0, column=0, pady=5, sticky="w")
        tk.Button(
            frame,
            text="Browse",
            command=self.select_directory,
            font=("Helvetica", 14),
        ).grid(row=0, column=1, pady=5, sticky="e")
        tk.Label(
            frame, textvariable=self.directory_path, font=("Helvetica", 12)
        ).grid(row=0, column=2, padx=5)

        # Checkbuttons - remove metadata, random rename, and organize folders
        checkbuttons_frame = tk.Frame(frame)
        checkbuttons_frame.grid(row=2, columnspan=3, pady=5, sticky="w")
        tk.Checkbutton(
            checkbuttons_frame,
            text="Remove metadata",
            variable=self.remove_metadata,
            font=("Helvetica", 14),
            onvalue=True,
            offvalue=False,
            command=self.on_remove_metadata_changed,
        ).grid(row=0, column=0, padx=5, pady=5)
        tk.Checkbutton(
            checkbuttons_frame,
            text="Randomly rename files",
            variable=self.random_rename,
            font=("Helvetica", 14),
            onvalue=True,
            offvalue=False,
            command=self.on_random_rename_changed,
        ).grid(row=1, column=0, padx=5, pady=5)
        tk.Checkbutton(
            checkbuttons_frame,
            text="Organize files by extension",
            variable=self.organize_folders,
            font=("Helvetica", 14),
            onvalue=True,
            offvalue=False,
        ).grid(row=2, column=0, padx=5, pady=5)

        # Run button
        tk.Button(
            frame,
            text="Run",
            command=self.run_file_organizer,
            font=("Helvetica", 14),
        ).grid(row=3, columnspan=3)

    def select_directory(self) -> None:
        """
        Open file dialog to select directory.
        """

        self.directory_path.set(filedialog.askdirectory())

    def on_remove_metadata_changed(self) -> None:
        """
        Handle remove metadata checkbox change.
        """

        logger.info(f"Remove metadata: {self.remove_metadata.get()}")

    def on_random_rename_changed(self) -> None:
        """
        Handle random rename checkbox change.
        """

        logger.info(f"Random rename: {self.random_rename.get()}")

    def run_file_organizer(self) -> None:
        """
        Run the file organizer with the selected options and save files in a subdirectory.
        """

        directory_path = Path(self.directory_path.get()).resolve()
        if not directory_path.exists() or not directory_path.is_dir():
            messagebox.showerror(
                "Error", "Please select a valid directory."
            )
            return

        remove_metadata = self.remove_metadata.get()
        random_rename = self.random_rename.get()
        organize_folders = self.organize_folders.get()

        new_folder = directory_path / "New_Folder"
        if not new_folder.exists():
            new_folder.mkdir()

        organize_and_rename_files(
            directory_path, remove_metadata, random_rename,
            organize_folders, new_folder)

    def run(self) -> None:
        """
        Runs the GUI.
        """

        self.root.mainloop()

    def organize_files_by_extension(self, directory_path: Path) -> None:
        """
        Organize text files by extension into folders.
        """

        for file_path in directory_path.glob("*.*"):
            if not file_path.is_file() or file_path.suffix.lower() not in {".txt", ".md", ".py", ".java", ".c", ".cpp"}:
                continue

            extension_folder = directory_path / file_path.suffix.lstrip(".")
            try:
                extension_folder.mkdir()
            except FileExistsError:
                pass

            new_file_path = extension_folder / file_path.name
            try:
                file_path.rename(new_file_path)
                logger.info(f"Moved {file_path.name} to {extension_folder}")
            except FileNotFoundError:
                logger.error(f"Could not rename/move {file_path.name}.")

def generate_random_filename(length: int = 10, existing_names=None) -> str:
    """
    Generate a randomly named file.
    """
    letters = string.ascii_lowercase
    filename = "".join(random.choice(letters) for _ in range(length))
    if existing_names is None:
        return filename
    # Check if filename already exists
    while filename in existing_names:
        filename = "".join(random.choice(letters) for _ in range(length))
    return filename

def hash_file_content(file_path: Path) -> Optional[str]:
    """
    Generate a SHA-1 hash of the file's contents.
    """

    BUF_SIZE = 65536  # 64kb chunk
    sha1 = hashlib.sha1()
    try:
        with open(file_path, "rb") as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()
    except FileNotFoundError:
        logger.error(f"File {file_path} not found.")
        return None

def organize_and_rename_files(
    directory_path: Path,
    remove_metadata: bool = False,
    random_rename: bool = False,
    organize_folders: bool = False,
    new_folder: Path = None
) -> None:
    """
    Organize and/or rename all text files in a directory and its subdirectories.
    """
    existing_names = set()

    if organize_folders:
        FileOrganizerGUI("").organize_files_by_extension(directory_path)

    # Collect existing filenames to avoid duplicates
    for file_path in directory_path.glob("**/*.*"):
        if not file_path.is_file() or file_path.suffix.lower() not in {".txt", ".md", ".py", ".java", ".c", ".cpp"}:
            continue
        existing_names.add(file_path.name)

    for file_path in tqdm(
        directory_path.glob("**/*.*"), desc="Processing files", unit="file"
    ):
        if not file_path.is_file() or file_path.suffix.lower() not in {".txt", ".md", ".py", ".java", ".c", ".cpp"}:
            continue

        if remove_metadata:
            pass  # Remove metadata here

        content_hash = hash_file_content(file_path)
        if content_hash is None:
            continue

        if random_rename:
            new_filename = generate_random_filename(existing_names=existing_names) + file_path.suffix
        else:
            new_filename = f"{content_hash}{file_path.suffix}"

        if new_folder:
            new_file_path = new_folder / new_filename
        else:
            new_file_path = file_path.with_name(new_filename)

        if new_file_path.exists():
            logger.error(f"File {new_file_path} already exists. Skipping renaming.")
            continue

        try:
            file_path.rename(new_file_path)
            existing_names.remove(file_path.name)
            existing_names.add(new_file_path.name)
            logger.info(f"{file_path.name} renamed to {new_filename}.")
        except OSError:
            logger.error(f"Could not rename {file_path.name}.")

def main() -> None:
    """
    Main function to run the Organize and Rename tool.
    """

    parser = argparse.ArgumentParser(
        description="Organize and rename text files in a directory and its subdirectories."
    )
    parser.add_argument(
        "directory_path",
        type=str,
        help="Path to directory to organize",
    )
    parser.add_argument(
        "-r",
        "--remove-metadata",
        action="store_true",
        help="Remove metadata from files",
    )
    parser.add_argument(
        "-n",
        "--random-rename",
        action="store_true",
        help="Rename text files randomly",
    )
    parser.add_argument(
        "-o",
        "--organize-folders",
        action="store_true",
        help="Organize files by extension into folders",
    )
    args = parser.parse_args()

    directory_path = Path(args.directory_path).resolve()

    if not directory_path.exists() or not directory_path.is_dir():
        raise ValueError(f"The given path '{directory_path}' does not exist or is not a directory.")

    remove_metadata = args.remove_metadata
    random_rename = args.random_rename
    organize_folders = args.organize_folders

    new_folder = directory_path / "New_Folder"
    if not new_folder.exists():
        new_folder.mkdir()

    organize_and_rename_files(
        directory_path, remove_metadata, random_rename, organize_folders, new_folder
    )

if __name__ == "__main__":
    main()
    