import os
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Dict, Tuple


class FileExplorer(tk.Tk):
    """
    Initializes a FileExplorer class with a GUI and necessary functionality.
    """

    def __init__(self) -> None:
        """
        Initializes the FileExplorer class, defines the properties of the GUI window and loads the saved executable list.
        """
        super().__init__()
        self.title('File Explorer')
        self.geometry('800x400')
        self.apps: List[str] = self._load_apps()
        self.create_widgets()
        self.create_menu_bar()

    def create_widgets(self) -> None:
        """Creates the GUI elements and places them at their required positions."""
        self.canvas = tk.Canvas(self, height=800, width=400, bg="#263D42")
        self.canvas.pack(side='left', fill='both', expand=True)

        self.frame = tk.Frame(self, bg="white")
        self.frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

        self.open_file_button = tk.Button(self, text="Open File", padx=10, pady=5, command=self._add_app)
        self.open_file_button.pack()

        self.run_apps_button = tk.Button(self, text="Run Apps", padx=10, pady=5, command=self.run_all_apps)
        self.run_apps_button.pack()

        self.create_project_button = tk.Button(self, text="Create Project", padx=10, pady=5, command=self.create_new_project)
        self.create_project_button.pack()

        self.listbox = tk.Listbox(self.frame)
        self.listbox.pack(fill='both', expand=True)

        self.refresh_app_list()

    def create_menu_bar(self) -> None:
        """Creates the menu bar for the user interface."""
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self._add_app)
        file_menu.add_command(label="Save", command=self._save_apps)
        file_menu.add_command(label="Create Project", command=self.create_new_project)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menu_bar)

    def _add_app(self) -> None:
        """Adds an executable to the list of stored apps."""
        filename = filedialog.askopenfilename(initialdir="/", title="Select File", filetypes=self.get_filetypes())

        if filename:
            arguments = self._get_arguments()
            app = f"{filename} {arguments}" if arguments else filename
            self.apps.append(app)
            self.refresh_app_list()

    def run_all_apps(self) -> None:
        """Runs all stored executables."""
        for app in self.apps:
            try:
                subprocess.Popen(app, shell=True, encoding='utf-8', errors='ignore')
            except OSError as error:
                messagebox.showerror("Error", f'Cannot run "{app}": {error}')

    def refresh_app_list(self) -> None:
        """Refreshes the list of executables in the GUI."""
        self.listbox.delete(0, tk.END)
        for app in self.apps:
            self.listbox.insert(tk.END, app)

    def _load_apps(self) -> List[str]:
        """Loads the list of executables."""
        try:
            with open('apps.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def _save_apps(self) -> None:
        """Saves the list of executables."""
        with open('apps.json', 'w') as f:
            json.dump(self.apps, f, indent=4)

    def create_new_project(self) -> None:
        """Creates a new project with a predefined structure and initial files."""
        project_name = self._get_project_name()
        if project_name:
            base_path = self._get_basepath()
            if base_path:
                self._create_project_structure(base_path, project_name)
                messagebox.showinfo("Success", f"Project '{project_name}' has been created.")

    @staticmethod
    def _create_project_structure(base_path: str, project_name: str) -> None:
        """Creates a new folder structure for a project."""
        project_folder = os.path.join(base_path, project_name)
        os.makedirs(project_folder, exist_ok=True)

        for folder, files in FileExplorer.PROJECT_STRUCTURE.items():
            folder_path = os.path.join(project_folder, folder.rstrip('/') if folder != 'root' else '')
            os.makedirs(folder_path, exist_ok=True)

            for file in files:
                file_path = os.path.join(folder_path, file)
                file_extension = os.path.splitext(file)[1]

                with open(file_path, 'w') as f:
                    f.write(FileExplorer.FILE_PLACEHOLDERS.get(file_extension, ''))

    @staticmethod
    def _get_arguments() -> str:
        """Gets optional command-line arguments from the user."""
        arguments = filedialog.askstring("Arguments", "Enter arguments (optional):")
        return arguments.strip() if arguments else ""

    @staticmethod
    def get_filetypes() -> List[Tuple[str]]:
        """Gets the filetypes that can be selected by the user for the file dialog."""
        return [("All files", "*.*")]

    @staticmethod
    def _get_project_name() -> str:
        """Gets the project name from the user."""
        project_name = filedialog.askstring("Project Name", "Enter the name of the new project:")
        return project_name.strip() if project_name else ""

    @staticmethod
    def _get_basepath() -> str:
        """Gets the base path where the new project will be created."""
        base_path = filedialog.askdirectory()
        return base_path.strip() if base_path else ""

    PROJECT_STRUCTURE: Dict[str, List[str]] = {
        'root': ['README.md', 'requirements.txt', '.gitignore'],
        'src': ['main.py', '__init__.py'],
        'docs': ['documentation.md'],
        'tests': ['test_main.py', '__init__.py']
    }

    FILE_PLACEHOLDERS: Dict[str, str] = {
        '.md': '# Project Title\n\nThis is a placeholder for documentation.',
        '.py': '#!/usr/bin/env python3\n\n"""Module docstring."""\n\ndef main() -> None:\n    pass\n\nif __name__ == "__main__":\n    main()',
        '.txt': '# Requirements or other text information',
        '.gitignore': '# Compiled python modules.\n*.pyc\n\n# Setuptools distribution folder.\ndist/'
    }


if __name__ == '__main__':
    app = FileExplorer()
    app.mainloop()