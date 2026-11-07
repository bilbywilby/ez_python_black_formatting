import os
import subprocess
import json
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from functools import lru_cache
from typing import List, Dict

class FileExplorer:
    """This class implements file browsing and displaying placeholders for different file types."""

    FILE_PLACEHOLDERS = {
        ".py": 'print("Hello World!")\n',
        ".cpp": '#include <iostream>\n\nint main() {\n    std::cout << "Hello World!";\n    return 0;\n}',
        ".java": 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello World!");\n    }\n}',
        ".html": '<!DOCTYPE html>\n<html>\n<head>\n\t<title>Hello World</title>\n</head>\n<body>\n\t<h1>Hello World!</h1>\n</body>\n</html>\n',
        ".txt": '',
    }

    def __init__(self, project_builder: 'ProjectBuilder'):
        """Creates a FileExplorer instance with a project builder object."""
        self.project_builder = project_builder

    def open_file(self):
        """Opens the selected file using the default program on the system."""
        filename = self.project_builder.filename_listbox.get(tk.ACTIVE)
        if not filename:
            return

        try:
            subprocess.Popen(['start', filename], shell=True, encoding='utf-8', errors='ignore')
        except OSError as error:
            messagebox.showerror('Error', f'Error opening "{filename}": {error}')

    def delete_file(self):
        """Deletes the selected file from the system and from the project list."""
        filename = self.project_builder.filename_listbox.get(tk.ACTIVE)
        if not filename:
            return

        response = messagebox.askyesno('Delete File', f'Are you sure you want to delete "{filename}"?')
        if response == tk.NO:
            return

        try:
            os.remove(filename)
            self.project_builder.refresh_filename_list()
        except OSError as error:
            messagebox.showerror('Error', f'Error deleting "{filename}": {error}')


class ProjectBuilder(tk.Tk):
    """This class implements a graphical interface for project creation, management, and execution."""

    def __init__(self):
        """Initializes the ProjectBuilder class with a GUI and all of its necessary functionality."""
        super().__init__()
        self.title('Project Builder')
        self.geometry('800x400')
        self.filenames: List[str] = self.load_filenames()
        self.templates: Dict[str, List[str]] = self.load_templates()
        self.file_explorer = FileExplorer(self)
        self.create_widgets()
        self.create_menu_bar()

    def create_widgets(self):
        """Creates the main UI elements and places them in the window."""
        self.canvas = tk.Canvas(self, height=800, width=400, bg='#263D42')
        self.canvas.pack(side='left', fill='both', expand=True)

        self.frame = tk.Frame(self, bg='white')
        self.frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

        self.choose_file_button = ttk.Button(
            self.frame, text='Choose File', command=self.choose_file)
        self.choose_file_button.pack(side='top', pady=(10,0))

        self.create_project_button = ttk.Button(
            self.frame, text='Create Project', command=self.create_new_project)
        self.create_project_button.pack(side='top', pady=10)

        self.filename_listbox = tk.Listbox(self.frame, selectmode=tk.SINGLE)
        self.filename_listbox.pack(fill='both', expand=True)

        self.filename_listbox.bind(
            '<Double-1>', lambda event: self.file_explorer.open_file())

        self.refresh_filename_list()

    def create_menu_bar(self) -> None:
        """Creates the main menu bar with options like choosing file, saving, quitting, 
        and creating templates."""
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)

        file_menu.add_command(label='Choose file', command=self.choose_file)
        file_menu.add_command(label='Save', command=self.save_filenames)
        file_menu.add_command(label='Create Project', command=self.create_new_project)
        file_menu.add_separator()
        file_menu.add_command(label='Quit', command=self.quit)

        template_menu = tk.Menu(menu_bar, tearoff=0)
        for name in self.templates:
            template_menu.add_command(
                label=name, command=lambda name=name: self.create_new_project(template_name=name))

        template_menu.add_separator()
        template_menu.add_command(label='Manage Templates', command=self.manage_templates)

        menu_bar.add_cascade(label='File', menu=file_menu)
        menu_bar.add_cascade(label='Template', menu=template_menu)
        self.config(menu=menu_bar)

    def choose_file(self):
        """Prompts the user to choose a file and directory for the project."""
        filename = filedialog.askopenfilename(
            initialdir='/', title='Select File', filetypes=self.get_filetypes())
        if not filename:
            return

        dir_path = filedialog.askdirectory(title="Choose directory to save project")
        if not dir_path:
            return

        project_name = os.path.splitext(os.path.basename(filename))[0]
        ext = os.path.splitext(filename)[1]
        self.create_new_project(name=project_name, ext=ext, dir_path=dir_path)

    def run_all_filenames(self):
        """Runs all of the applications in the list of filenames."""
        for filename in self.filenames:
            try:
                subprocess.Popen(filename, shell=True, encoding='utf-8', errors='ignore')
            except OSError as error:
                messagebox.showerror('Error', f'Error running "{filename}": {error}')

    def refresh_filename_list(self):
        """Refreshes the listbox to updated the list of filenames."""
        self.filename_listbox.delete(0, tk.END)
        for filename in self.filenames:
            self.filename_listbox.insert(tk.END, filename)

    def load_filenames(self):
        """Loads the list of executables that have been saved from filenames.json."""
        try:
            with open('filenames.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def load_templates(self):
        """Loads the templates that can be used for project creation from templates.json."""
        try:
            with open('templates.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_filenames(self):
        """Saves the current list of executables to filenames.json."""
        with open('filenames.json', 'w') as f:
            json.dump(self.filenames, f, indent=4)

    def create_new_project(self, name='', ext='', template_name='', dir_path=''):
        """Creates a new project with the required directory structure and initial files."""
        if not dir_path:
            dir_path = os.getcwd()

        project_name = name or simpledialog.askstring('Input', 'Enter Project Name:', parent=self)
        if not project_name:
            return

        ext = ext or self.select_file_type()
        project_structure = {'root': []}
        response = 'Y'
        while response.upper() == 'Y':
            folder_name = simpledialog.askstring('Input', 'Enter Folder Name (blank if root):', parent=self)
            if folder_name and not re.match(r'^[A-Za-z0-9_-]*$', folder_name):
                messagebox.showwarning(
                    "Invalid Input", "Folder name can only contain alphanumeric characters, hyphens, and underscores.")
                continue

            if folder_name:
                project_structure[folder_name] = self.get_file_names(ext)
                response = simpledialog.askstring('Input', 'Add another folder? (Y/N)', parent=self).strip().upper()
            else:
                project_structure['root'] = self.get_file_names(ext)
                response = 'N'

        self.create_project_structure(dir_path, project_name, project_structure)
        messagebox.showinfo('Success', f"Project '{project_name}' has been created.")
        filename = os.path.join(dir_path, project_name)
        self.filenames.append(filename)
        self.refresh_filename_list()

        if template_name:
            if not self.templates.get(template_name):
                return

            template_structure = self.templates[template_name]
            self.create_project_structure(dir_path, project_name, template_structure)

            messagebox.showinfo('Success', f"Project '{project_name}' has been created using template '{template_name}'.")
            self.filenames.append(filename)
            self.refresh_filename_list()

    def get_file_names(self, ext=''):
        """Prompts the user to enter the names for the filenames to be created."""
        response = 'Y'
        filenames = []

        while response.upper() == 'Y':
            filename = simpledialog.askstring('Input', 'Enter Filename (without extension):', parent=self)
            if filename and not re.match(r'^[A-Za-z0-9_-]*$', filename):
                messagebox.showwarning(
                    "Invalid Input", "Filename can only contain alphanumeric characters, hyphens, and underscores.")
                continue

            if filename:
                filenames.append(f'{filename}.{ext}')
                response = simpledialog.askstring('Input', 'Add another file? (Y/N)', parent=self).strip().upper()
            else:
                response = 'N'

        return filenames

    @staticmethod
    def create_project_structure(base_path: str, project_name: str, project_structure: Dict[str, List[str]]):
        """Creates the file hierarchy and initial files for the new project."""
        project_folder = os.path.join(base_path, project_name)
        try:
            os.makedirs(project_folder, exist_ok=True)
        except OSError as error:
            messagebox.showerror('Error', f'Error creating directory "{project_folder}": {error}')

        for folder, filenames in project_structure.items():
            folder_path = os.path.join(project_folder, folder if folder != 'root' else '')
            try:
                os.makedirs(folder_path, exist_ok=True)
            except OSError as error:
                messagebox.showerror('Error', f'Error creating directory "{folder_path}": {error}')

            for filename in filenames:
                file_path = os.path.join(folder_path, filename)
                file_extension = os.path.splitext(filename)[1]

                try:
                    with open(file_path, 'w') as f:
                        f.write(FileExplorer.FILE_PLACEHOLDERS.get(file_extension, ''))
                except OSError as error:
                    messagebox.showerror('Error', f'Error creating file "{file_path}": {error}')

    @staticmethod
    def get_filetypes():
        """Returns the filetypes that can be selected by the user for the file dialog."""
        filetypes = [('Python files', '*.py'), ('Java files', '*.java'), ('C++ files', '*.cpp'),
                     ('HTML files', '*.html'), ('Text files', '*.txt'), ('All files', '*.*')]
        return filetypes

    def select_file_type(self):
        """Prompts the user to select a file type for the project files."""
        file_type = ''
        while file_type not in FileExplorer.FILE_PLACEHOLDERS:
            file_type = simpledialog.askstring(
                'Input', f'Select file type from list ({", ".join(FileExplorer.FILE_PLACEHOLDERS.keys())}):', parent=self).strip().lower()
        return file_type

    def manage_templates(self):
        """Provides the option to edit, add, or remove templates."""
        manage_templates_window = tk.Toplevel(self)
        manage_templates_window.title("Manage Templates")

        template_settings_frame = ttk.Frame(manage_templates_window)
        template_settings_frame.pack(fill="both", expand=True)

        template_listbox_frame = ttk.Frame(template_settings_frame)
        template_listbox_frame.pack(side="left", fill="both", expand=True)

        template_listbox_scrollbar = ttk.Scrollbar(template_listbox_frame, orient="vertical")
        template_listbox_scrollbar.pack(side="right", fill="y")

        template_listbox = tk.Listbox(template_listbox_frame, yscrollcommand=template_listbox_scrollbar.set)
        template_listbox.pack(side="left", fill="both", expand=True)

        template_listbox_scrollbar.config(command=template_listbox.yview)

        name_label = ttk.Label(template_settings_frame, text="Name:")
        name_entry = ttk.Entry(template_settings_frame)

        files_label = ttk.Label(template_settings_frame, text="Files:")
        files_textarea = tk.Text(template_settings_frame)

        name_label.grid(row=0, column=0, padx=5, pady=5)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        files_label.grid(row=1, column=0, padx=5, pady=5)
        files_textarea.grid(row=1, column=1, padx=5, pady=5)

        button_frame = ttk.Frame(manage_templates_window)
        button_frame.pack(fill="x", expand=False)

        add_button = ttk.Button(
            button_frame, text="Add", command=lambda: self.add_template(template_listbox, name_entry, files_textarea))
        edit_button = ttk.Button(
            button_frame, text="Edit", command=lambda: self.edit_template(template_listbox, name_entry, files_textarea))
        delete_button = ttk.Button(
            button_frame, text="Delete", command=lambda: self.delete_template(template_listbox))

        add_button.pack(side="left", padx=5, pady=5, fill="both")
        edit_button.pack(side="left", padx=5, pady=5, fill="both")
        delete_button.pack(side="left", padx=5, pady=5, fill="both")

        for name in self.templates:
            template_listbox.insert(tk.END, name)

        def on_select_template(event):
            selected_template = template_listbox.get(template_listbox.curselection())
            name_entry.delete(0, "end")
            name_entry.insert(0, selected_template)
            files_textarea.delete(1.0, "end")
            files_textarea.insert(1.0, "\n".join(self.templates[selected_template]))

        template_listbox.bind("<<ListboxSelect>>", on_select_template)

    def add_template(self, template_listbox: tk.Listbox, name_entry: tk.Entry, files_textarea: tk.Text):
        """Adds a new template with the specified name and files to the templates dictionary and listbox."""
        name = name_entry.get().strip()
        files = files_textarea.get("1.0", "end-1c").strip().split("\n")

        if name and files:
            self.templates[name] = files
            template_listbox.insert(tk.END, name)
            messagebox.showinfo("Template Added", f"Template '{name}' has been added.")
        else:
            messagebox.showwarning("Invalid Input", "Name and files cannot be empty.")

    def edit_template(self, template_listbox: tk.Listbox, name_entry: tk.Entry, files_textarea: tk.Text):
        """Edits an existing template with the specified name and files in the templates dictionary and listbox."""
        selected_template = template_listbox.get(template_listbox.curselection())
        if selected_template:
            name = name_entry.get().strip()
            files = files_textarea.get("1.0", "end-1c").strip().split("\n")
            if name and files:
                self.templates[name] = files
                old_name = template_listbox.get(template_listbox.curselection())
                if old_name != name:
                    index = template_listbox.curselection()
                    template_listbox.delete(index)
                    template_listbox.insert(index, name)
                    del self.templates[old_name]
                messagebox.showinfo("Template Edited", f"Template '{name}' has been edited.")
            else:
                messagebox.showwarning("Invalid Input", "Name and files cannot be empty.")
        else :
            messagebox.showerror("No Template Selected","Please select a template first.")</s>   
            #include <stdio.h> 
  
/* Function to print all elements of an array */
void printArray(int arr[], int n) {  
    for (int i=0; i<n; ++i)
        printf("%d ", arr[i]); 
}  
  
// This function returns minimum number of swaps required to sort an array using selection sort algorithm.
int minSwaps(int arr[], int n)  {  
    // Initialize result  
    int res = 0;  
  
    /* One by one move boundary of unsorted subarray */
    for (int i = 0; i < n - 1; i++) { 
        /* Find the minimum element in remaining  
           unsorted array */
        int minIdx = i;      
        for (int j = i +  1; j < n; j++)  
          if (arr[j] < arr[minIdx])   
              minIdx = j;  
  
        /* Swap the found minimum element with the first      
           element */
        int temp = arr[minIdx];  
        arr[minIdx] = arr[i];    
        arr[i] = temp;  
        
        /* increment the swap counter */
        res++;          
    }    
    return res;  
}     
  import os
import subprocess
import json
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from functools import lru_cache
from typing import List, Dict


class FileExplorer:
    """This class implements file browsing and displaying placeholders for different file types."""

    FILE_PLACEHOLDERS = {
        ".py": 'print("Hello, World!")\n',
        ".cpp": '#include <iostream>\n\nint main() {\n    std::cout << "Hello, World!";\n    return 0;\n}',
        ".java": 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
        ".html": '<!DOCTYPE html>\n<html>\n<head>\n\t<title>Hello, World</title>\n</head>\n<body>\n\t<h1>Hello, World!</h1>\n</body>\n</html>\n',
        ".txt": '',
    }

    def __init__(self, project_builder: 'ProjectBuilder'):
        """Creates a FileExplorer instance with a project builder object."""
        self.project_builder = project_builder

    def open_file(self):
        """Opens the selected file using the default program on the system."""
        filename = self.project_builder.filename_listbox.get(tk.ACTIVE)
        if not filename:
            return

        try:
            subprocess.Popen(['start', filename], shell=True, encoding='utf-8', errors='ignore')
        except OSError as error:
            messagebox.showerror('Error', f'Error opening "{filename}": {error}')

    def delete_file(self):
        """Deletes the selected file from the system and from the project list."""
        filename = self.project_builder.filename_listbox.get(tk.ACTIVE)
        if not filename:
            return

        response = messagebox.askyesno('Delete File', f'Are you sure you want to delete "{filename}"?')
        if response == tk.NO:
            return

        try:
            os.remove(filename)
            self.project_builder.refresh_filename_list()
        except OSError as error:
            messagebox.showerror('Error', f'Error deleting "{filename}": {error}')


class ProjectBuilder(tk.Tk):
    """This class implements a graphical interface for project creation, management, and execution."""

    def __init__(self):
        """Initializes the ProjectBuilder class with a GUI and all of its necessary functionality."""
        super().__init__()
        self.title('Project Builder')
        self.geometry('800x400')
        self.filenames: List[str] = self.load_filenames()
        self.templates: Dict[str, List[str]] = self.load_templates()
        self.file_explorer = FileExplorer(self)
        self.create_widgets()
        self.create_menu_bar()

    def create_widgets(self):
        """Creates the main UI elements and places them in the window."""
        self.canvas = tk.Canvas(self, height=800, width=400, bg='#263D42')
        self.canvas.pack(side='left', fill='both', expand=True)

        self.frame = tk.Frame(self, bg='white')
        self.frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

        self.choose_file_button = ttk.Button(
            self.frame, text='Choose File', command=self.choose_file)
        self.choose_file_button.pack(side='top', pady=(10,0))

        self.create_project_button = ttk.Button(
            self.frame, text='Create Project', command=self.create_new_project)
        self.create_project_button.pack(side='top', pady=10)

        self.filename_listbox = tk.Listbox(self.frame, selectmode=tk.SINGLE)
        self.filename_listbox.pack(fill='both', expand=True)

        self.filename_listbox.bind(
            '<Double-1>', lambda event: self.file_explorer.open_file())

        self.refresh_filename_list()

    def create_menu_bar(self) -> None:
        """Creates the main menu bar with options like choosing file, saving, quitting,
        and creating templates."""
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)

        file_menu.add_command(label='Choose file', command=self.choose_file)
        file_menu.add_command(label='Save', command=self.save_filenames)
        file_menu.add_command(label='Create Project', command=self.create_new_project)
        file_menu.add_separator()
        file_menu.add_command(label='Quit', command=self.quit)

        template_menu = tk.Menu(menu_bar, tearoff=0)
        for name in self.templates:
            template_menu.add_command(
                label=name, command=lambda name=name: self.create_new_project(template_name=name))

        template_menu.add_separator()
        template_menu.add_command(label='Manage Templates', command=self.manage_templates)

        menu_bar.add_cascade(label='File', menu=file_menu)
        menu_bar.add_cascade(label='Template', menu=template_menu)
        self.config(menu=menu_bar)

    def choose_file(self) -> None:
        """Prompts the user to choose a file and directory for the project."""
        filename = filedialog.askopenfilename(
            initialdir='/', title='Select File', filetypes=self.get_filetypes())
        if not filename:
            return

        dir_path = filedialog.askdirectory(title="Choose directory to save project")
        if not dir_path:
            return

        project_name = os.path.splitext(os.path.basename(filename))[0]
        ext = os.path.splitext(filename)[1]
        self.create_new_project(name=project_name, ext=ext, dir_path=dir_path)

    def run_all_filenames(self) -> None:
        """Runs all of the applications in the list of filenames."""
        for filename in self.filenames:
            try:
                subprocess.Popen(filename, shell=True, encoding='utf-8', errors='ignore')
            except OSError as error:
                messagebox.showerror('Error', f'Error running "{filename}": {error}')

    def refresh_filename_list(self) -> None:
        """Refreshes the listbox to updated the list of filenames."""
        self.filename_listbox.delete(0, tk.END)
        for filename in self.filenames:
            self.filename_listbox.insert(tk.END, filename)

    def load_filenames(self) -> List[str]:
        """Loads the list of executables that have been saved from filenames.json."""
        try:
            with open('filenames.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def load_templates(self) -> Dict[str, List[str]]:
        """Loads the templates that can be used for project creation from templates.json."""
        try:
            with open('templates.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_filenames(self) -> None:
        """Saves the current list of executables to filenames.json."""
        with open('filenames.json', 'w') as f:
            json.dump(self.filenames, f, indent=4)

    def create_new_project(self, name='', ext='', template_name='', dir_path='') -> None:
        """Creates a new project with the required directory structure and initial files."""
        if not dir_path:
            dir_path = os.getcwd()

        project_name = name or simpledialog.askstring('Input', 'Enter Project Name:', parent=self)
        if not project_name:
            return

        ext = ext or self.select_file_type()
        project_structure = {'root': []}
        response = 'Y'
        while response.upper() == 'Y':
            folder_name = simpledialog.askstring('Input', 'Enter Folder Name (blank if root):', parent=self)
            if folder_name and not re.match(r'^[A-Za-z0-9_-]*$', folder_name):
                messagebox.showwarning(
                    "Invalid Input", "Folder name can only contain alphanumeric characters, hyphens, and underscores.")
                continue

            if folder_name:
                project_structure[folder_name] = self.get_file_names(ext)
                response = simpledialog.askstring('Input', 'Add another folder? (Y/N)', parent=self).strip().upper()
            else:
                project_structure['root'] = self.get_file_names(ext)
                response = 'N'

        self.create_project_structure(dir_path, project_name, project_structure)
        messagebox.showinfo('Success', f"Project '{project_name}' has been created.")
        filename = os.path.join(dir_path, project_name)
        self.filenames.append(filename)
        self.refresh_filename_list()

        if template_name:
            if not self.templates.get(template_name):
                return

            template_structure = self.templates[template_name]
            self.create_project_structure(dir_path, project_name, template_structure)

            messagebox.showinfo('Success', f"Project '{project_name}' has been created using template '{template_name}'.")
            self.filenames.append(filename)
            self.refresh_filename_list()

    def get_file_names(self, ext='') -> List[str]:
        """Prompts the user to enter the names for the filenames to be created."""
        response = 'Y'
        filenames = []

        while response.upper() == 'Y':
            filename = simpledialog.askstring('Input', 'Enter Filename (without extension):', parent=self)
            if filename and not re.match(r'^[A-Za-z0-9_-]*$', filename):
                messagebox.showwarning(
                    "Invalid Input", "Filename can only contain alphanumeric characters, hyphens, and underscores.")
                continue

            if filename:
                filenames.append(f'{filename}.{ext}')
                response = simpledialog.askstring('Input', 'Add another file? (Y/N)', parent=self).strip().upper()
            else:
                response = 'N'

        return filenames

    @staticmethod
    def create_project_structure(base_path: str, project_name: str, project_structure: Dict[str, List[str]]) -> None:
        """Creates the file hierarchy and initial files for the new project."""
        project_folder = os.path.join(base_path, project_name)
        try:
            os.makedirs(project_folder, exist_ok=True)
        except OSError as error:
            messagebox.showerror('Error', f'Error creating directory "{project_folder}": {error}')

        for folder, filenames in project_structure.items():
            folder_path = os.path.join(project_folder, folder if folder != 'root' else '')
            try:
                os.makedirs(folder_path, exist_ok=True)
            except OSError as error:
                messagebox.showerror('Error', f'Error creating directory "{folder_path}": {error}')

            for filename in filenames:
                file_path = os.path.join(folder_path, filename)
                file_extension = os.path.splitext(filename)[1]

                try:
                    with open(file_path, 'w') as f:
                        f.write(FileExplorer.FILE_PLACEHOLDERS.get(file_extension, ''))
                except OSError as error:
                    messagebox.showerror('Error', f'Error creating file "{file_path}": {error}')

    @staticmethod
    def get_filetypes() -> List[tuple]:
        """Returns the filetypes that can be selected by the user for the file dialog."""
        return [('Python files', '*.py'), ('Java files', '*.java'), ('C++ files', '*.cpp'),
                ('HTML files', '*.html'), ('Text files', '*.txt'), ('All files', '*.*')]

    def select_file_type(self) -> str:
        """Prompts the user to select a file type for the project files."""
        file_type = ''
        while file_type not in FileExplorer.FILE_PLACEHOLDERS:
            file_type = simpledialog.askstring(
                'Input', f'Select file type from list ({", ".join(FileExplorer.FILE_PLACEHOLDERS.keys())}):', parent=self).strip().lower()
        return file_type

    def manage_templates(self) -> None:
        """Provides the option to edit, add, or remove templates."""
        manage_templates_window = tk.Toplevel(self)
        manage_templates_window.title("Manage Templates")

        template_settings_frame = ttk.Frame(manage_templates_window)
        template_settings_frame.pack(fill="both", expand=True)

        template_listbox_frame = ttk.Frame(template_settings_frame)
        template_listbox_frame.pack(side="left", fill="both", expand=True)

        template_listbox_scrollbar = ttk.Scrollbar(template_listbox_frame, orient="vertical")
        template_listbox_scrollbar.pack(side="right", fill="y")

        template_listbox = tk.Listbox(template_listbox_frame, yscrollcommand=template_listbox_scrollbar.set)
        template_listbox.pack(side="left", fill="both", expand=True)

        template_listbox_scrollbar.config(command=template_listbox.yview)

        name_label = ttk.Label(template_settings_frame, text="Name:")
        name_entry = ttk.Entry(template_settings_frame)

        files_label = ttk.Label(template_settings_frame, text="Files:")
        files_textarea = tk.Text(template_settings_frame)

        name_label.grid(row=0, column=0, padx=5, pady=5)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        files_label.grid(row=1, column=0, padx=5, pady=5)
        files_textarea.grid(row=1, column=1, padx=5, pady=5)

        button_frame = ttk.Frame(manage_templates_window)
        button_frame.pack(fill="x", expand=False)

        add_button = ttk.Button(
            button_frame, text="Add", command=lambda: self.add_template(template_listbox, name_entry, files_textarea))
        edit_button = ttk.Button(
            button_frame, text="Edit", command=lambda: self.edit_template(template_listbox, name_entry, files_textarea))
        delete_button = ttk.Button(
            button_frame, text="Delete", command=lambda: self.delete_template(template_listbox))

        add_button.pack(side="left", padx=5, pady=5, fill="both")
        edit_button.pack(side="left", padx=5, pady=5, fill="both")
        delete_button.pack(side="left", padx=5, pady=5, fill="both")

        for name in self.templates:
            template_listbox.insert(tk.END, name)

        def on_select_template(event):
            selected_template = template_listbox.get(template_listbox.curselection())
            name_entry.delete(0, "end")
            name_entry.insert(0, selected_template)
            files_textarea.delete(1.0, "end")
            files_textarea.insert(1.0, "\n".join(self.templates[selected_template]))

        template_listbox.bind("<<ListboxSelect>>", on_select_template)

    def add_template(self, template_listbox: tk.Listbox, name_entry: tk.Entry, files_textarea: tk.Text) -> None:
        """Adds a new
class TemplateEditor : public T