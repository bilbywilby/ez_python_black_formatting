import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk


class AppManager(tk.Tk):
    SUPPORTED_APP_FILETYPES = [("Application Executable", "*.exe"), ("All Files", "*.*")]

    def __init__(self):
        super().__init__()
        self.title("App Manager")
        self.geometry("800x600")
        self.apps = []

        self.create_widgets()
        self.mainloop()

    def create_widgets(self):
        self.create_menu()
        self.create_listbox()
        self.create_button()

    def create_menu(self):
        self.main_menu = tk.Menu(self)

        file_menu = tk.Menu(self.main_menu, tearoff=0)

        file_menu.add_command(label="Save Configuration", command=self.save_apps)
        file_menu.add_command(label="Load Configuration", command=self.load_apps)

        self.main_menu.add_cascade(label="File", menu=file_menu)

        self.main_menu.add_command(label="Create Project", command=self.create_project_structure)

        help_menu = tk.Menu(self.main_menu, tearoff=0)
        help_menu.add_command(label="How to Create a Project", command=self.show_help)
        self.main_menu.add_cascade(label="Help", menu=help_menu)

        self.config(menu=self.main_menu)

    def create_listbox(self):
        self.list_frame = tk.Frame(self)
        self.list_frame.pack(side='left', padx=10, pady=10, fill='both', expand=True)

        self.listbox = tk.Listbox(self.list_frame, width=60, height=20)
        self.listbox.pack(side='top', padx=10, pady=10, fill='both', expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.app_selection)
        self.listbox.image_list = []

    def create_button(self):
        self.add_clear_button = tk.Button(self, text="Add/ Clear Applications", command=self.add_clear_applications)
        self.add_clear_button.pack(pady=10)

        self.label = tk.Label(self, text="0 applications added")
        self.label.pack(pady=10)

        self.search_frame = tk.Frame(self)
        self.search_label = tk.Label(self.search_frame, text="Search Applications:")
        self.search_label.pack(side='left', padx=5, pady=5)
        self.search_entry = tk.Entry(self.search_frame, width=30)
        self.search_entry.pack(side='left', padx=5, pady=5)
        self.search_button = tk.Button(self.search_frame, text="Search", command=self.search_applications)
        self.search_button.pack(side='left', padx=5, pady=5)
        self.search_frame.pack(pady=10)

    def add_application(self):
        app_path = filedialog.askopenfilename(initialdir="/", title="Select Application", filetypes=self.SUPPORTED_APP_FILETYPES)

        if app_path:
            self.apps.append(app_path)

            # Load the application icon
            icon = Image.open(app_path)
            icon = icon.resize((32, 32))

            # Create a PhotoImage and add it to the listbox
            photo = ImageTk.PhotoImage(icon)
            self.listbox.insert('end', app_path, image=photo)
            self.listbox.image_list.append(photo)

            self.label.config(text=f"{len(self.apps)} applications added")

    def clear_applications(self):
        self.apps.clear()
        self.listbox.delete(0, 'end')
        self.listbox.image_list.clear()
        self.label.config(text="0 applications added")

    def add_clear_applications(self):
        if len(self.apps) == 0:
            messagebox.showwarning("Warning", "No applications have been added.")
        elif messagebox.askyesno("Confirmation", "Are you sure you want to clear all added applications?"):
            self.clear_applications()
        else:
            return

    def app_selection(self, event) -> None:
        selected = self.listbox.curselection()
        if len(selected) != 0:
            index = selected[0]
            item = self.listbox.get(index)
            print(item)

    def save_apps(self):
        app_filetypes = [("Application Files", "*.txt")]

        filename = filedialog.asksaveasfilename(title="Save Applications",
                                                defaultextension=".txt",
                                                filetypes=app_filetypes)

        with open(filename, 'w') as f:
            for app_path in self.apps:
                f.write(app_path + '\n')

    def load_apps(self):
        app_filetypes = [("Application Files", "*.txt")]

        filename = filedialog.askopenfilename(title="Load Applications",
                                              defaultextension=".txt",
                                              filetypes=app_filetypes)

        with open(filename, 'r') as f:
            self.clear_applications()
            for app_path in f.readlines():
                app_path = app_path.strip()
                self.apps.append(app_path)

                # Load the application icon
                icon = Image.open(app_path)
                icon = icon.resize((32, 32))

                # Create a PhotoImage and add it to the listbox
                photo = ImageTk.PhotoImage(icon)
                self.listbox.insert('end', app_path, image=photo)
                self.listbox.image_list.append(photo)

                self.label.config(text=f"{len(self.apps)} applications added")

    def create_project_structure(self):
        project_name = tk.simpledialog.askstring(title="Project Name", prompt="Enter the name of the new project:")
        if project_name is not None:
            base_path = filedialog.askdirectory(title="Choose a directory for your project:")
            if base_path:
                project_path = base_path + "\\" + project_name
                os.makedirs(project_path, exist_ok=True)
                messagebox.showinfo("Success", f"Project '{project_name}' has been created at {project_path}")

    def show_help(self):
        help_text = "To create a new project:\n\n1. Click 'Create Project' in the 'File' menu.\n"
        help_text += "2. Enter the name of the new project when prompted.\n"
        help_text += "3. Choose the destination folder for the new project.\n"
        help_text += "4. Click 'Create Project' to complete the process.\n"

        help_window = tk.Toplevel(self)
        help_window.title("Help")
        help_label = tk.Label(help_window, text=help_text, justify='left')
        help_label.pack(padx=10, pady=10)

    def search_applications(self):
        query = self.search_entry.get()
        if query != '':
            self.listbox.delete(0, 'end')
            for app_path in self.apps:
                if query.lower() in app_path.lower():
                    icon = Image.open(app_path)
                    icon = icon.resize((32, 32))

                    photo = ImageTk.PhotoImage(icon)
                    self.listbox.insert('end', app_path, image=photo)
                    self.listbox.image_list.append(photo)
        else:
            self.listbox.delete(0, 'end')
            for i, app_path in enumerate(self.apps):
                icon = Image.open(app_path)
                icon = icon.resize((32, 32))

                photo = ImageTk.PhotoImage(icon)
                self.listbox.insert(i, app_path, image=photo)
                self.listbox.image_list.append(photo)
        self.label.config(text=f"{len(self.apps)} applications added")


if __name__ == "__main__":
    AppManager()