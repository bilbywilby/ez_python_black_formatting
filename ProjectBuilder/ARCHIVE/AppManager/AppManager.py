import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os


class AppManager(tk.Tk):

    SUPPORTED_APP_FILETYPES = [("Application Executable", "*.exe"), ("All Files", "*.*")]

    def __init__(self):
        super().__init__()
        self.title("App Manager")
        self.geometry("800x600")
        self.apps = []
        self.search_query = ''
        self.search_entry = None

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

        project_menu = tk.Menu(self.main_menu, tearoff=0)
        project_menu.add_command(label="Create Project", command=self.create_project_structure)
        self.main_menu.add_cascade(label="Project", menu=project_menu)

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

    def create_button(self):
        self.add_clear_button = tk.Button(self, text="Add/ Clear Apps", command=self.add_clear_applications)
        self.add_clear_button.pack(pady=10)

        self.label = tk.Label(self, text="No apps added")
        self.label.pack(pady=10)

        self.search_frame = tk.Frame(self)
        self.search_label = tk.Label(self.search_frame, text="Search Apps:")
        self.search_label.pack(side='left', padx=5, pady=5)
        self.search_entry = tk.Entry(self.search_frame, width=30)
        self.search_entry.pack(side='left', padx=5, pady=5)
        self.search_button = tk.Button(self.search_frame, text="Search", command=self.search_applications)
        self.search_button.pack(side='left', padx=5, pady=5)
        self.search_clear_button = tk.Button(self.search_frame, text="Clear", command=self.clear_search)
        self.search_clear_button.pack(side='left', padx=5, pady=5)
        self.search_frame.pack(pady=10)

    def add_application(self):
        app_path = filedialog.askopenfilename(initialdir="/", title="Select App", filetypes=self.SUPPORTED_APP_FILETYPES)

        if app_path:
            self.apps.append(app_path)

            # Load the app icon
            icon = Image.open(app_path)
            icon = icon.resize((32, 32))

            # Create a PhotoImage and add it to the listbox
            photo = ImageTk.PhotoImage(icon)
            self.listbox.insert('end', app_path, image=photo)
            self.listbox.image_list.append(photo)

            self.label.config(text=f"{len(self.apps)} apps added")

    def clear_applications(self):
        if len(self.apps) == 0:
            messagebox.showwarning("Warning", "No apps have been added.")
            return

        if messagebox.askyesno("Confirmation", "Are you sure you want to clear all added apps?"):
            self.apps.clear()
            self.listbox.delete(0, 'end')
            self.listbox.image_list.clear()
            self.label.config(text="No apps added")
        else:
            return

    def add_clear_applications(self):
        if len(self.apps) == 0:
            self.add_application()
        else:
            self.clear_applications()

    def app_selection(self, event):
        selected = self.listbox.curselection()
        if not selected:
            return

        app_path = self.listbox.get(selected[0])
        messagebox.showinfo("Selected Application", app_path)

    def save_apps(self):
        app_filetypes = [("Application Files", "*.txt")]

        filename = filedialog.asksaveasfilename(title="Save Apps",
                                                defaultextension=".txt",
                                                filetypes=app_filetypes)
        if not filename:
            return

        with open(filename, 'w') as f:
            f.write('\n'.join(self.apps))

        messagebox.showinfo("Success", f"Apps saved to '{filename}'")

    def load_apps(self):
        app_filetypes = [("Application Files", "*.txt")]

        filename = filedialog.askopenfilename(title="Load Apps",
                                              defaultextension=".txt",
                                              filetypes=app_filetypes)
        if not filename:
            return

        with open(filename, 'r') as f:
            self.clear_applications()
            for app_path in f.readlines():
                app_path = app_path.strip()
                self.apps.append(app_path)

                # Load the app icon
                icon = Image.open(app_path)
                icon = icon.resize((32, 32))

                # Create a PhotoImage and add it to the listbox
                photo = ImageTk.PhotoImage(icon)
                self.listbox.insert('end', app_path, image=photo)
                self.listbox.image_list.append(photo)

            self.label.config(text=f"{len(self.apps)} apps added")

        messagebox.showinfo("Success", f"Apps loaded from '{filename}'")

    def create_project_structure(self):
        self.withdraw()
        project_name = simpledialog.askstring(title="Create Project", prompt="Enter the name of the new project:")
        if project_name is None:
            self.deiconify()
            return

        base_path = filedialog.askdirectory(title="Choose project directory:")
        self.deiconify()

        if not base_path:
            return

        project_path = f"{base_path}/{project_name}"
        os.makedirs(project_path, exist_ok=True)
        messagebox.showinfo("Success", f"Project '{project_name}' has been created at {project_path}")

    def show_help(self):
        help_window = tk.Toplevel(self)
        help_window.title("Help")
        help_message = "Creating a New Project:\n\n1. Select 'Create Project' from the 'Project' menu.\n"
        help_message += "2. Enter the name of the new project and select the destination directory.\n"
        help_message += "3. Click 'Create Project' to complete the process."

        help_label = tk.Label(help_window, text=help_message, justify='left')
        help_label.pack(padx=10, pady=10)

    def search_applications(self):
        query = self.search_entry.get().lower().strip()

        if not query:
            self.clear_search()
            return

        filtered = [app_path for app_path in self.apps if query in app_path.lower()]
        self.update_listbox(filtered)

        if len(filtered) == 0:
            self.label.config(text="No apps found")
        else:
            self.label.config(text=f"{len(filtered)} apps found")

    def clear_search(self):
        self.search_entry.delete(0, 'end')
        self.search_query = ''
        self.refresh_listbox()

    def refresh_listbox(self):
        self.listbox.delete(0, 'end')
        for i, app_path in enumerate(self.apps):
            icon = Image.open(app_path)
            icon = icon.resize((32, 32))

            photo = ImageTk.PhotoImage(icon)
            self.listbox.insert(i, app_path, image=photo)
            self.listbox.image_list.append(photo)

        self.label.config(text=f"{len(self.apps)} apps added")

    def update_listbox(self, apps):
        self.listbox.delete(0, 'end')
        for app_path in apps:
            icon = Image.open(app_path)
            icon = icon.resize((32, 32))

            photo = ImageTk.PhotoImage(icon)
            self.listbox.insert('end', app_path, image=photo)
            self.listbox.image_list.append(photo)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

if __name__ == "__main__":
    app = AppManager()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)