# Importing necessary libraries
import tkinter as tk
from tkinter import messagebox, filedialog, Menu
import os
import subprocess
import webbrowser

class App(tk.Tk):
    """Main Application for AI Copilot Assistant.

    This class represents the main window of the AI Copilot Assistant application.
    It initializes the application window and creates the necessary widgets.
    """
    
    def __init__(self):
        """Initialize the application with a title and geometry."""
        super().__init__()
        self.title('AI Copilot Assistant')
        self.geometry('600x400')
        self.resizable(True, True)
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create widgets for the application.

        This method sets up the greeting label, input entry, submit button, and a menu bar.
        """
        # Menu Bar
        self.menu_bar = Menu(self)
        
        # File Menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label='Open', command=self._open_file)
        self.file_menu.add_command(label='Save', command=self._save_file)
        self.file_menu.add_command(label='Generate VS Code Project', command=self._generate_vscode_project)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', command=self.quit)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        
        # Tools Menu
        self.tools_menu = Menu(self.menu_bar, tearoff=0)
        self.tools_menu.add_command(label='Run Python File', command=self._run_python_file)
        self.menu_bar.add_cascade(label='Tools', menu=self.tools_menu)
        
        # Help Menu
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label='Documentation', command=self._open_documentation)
        self.help_menu.add_command(label='About', command=self._show_about_info)
        self.menu_bar.add_cascade(label='Help', menu=self.help_menu)

        self.config(menu=self.menu_bar)

        # Greeting Label
        self.greeting_label = tk.Label(self, text='Welcome to AI Copilot Assistant!')
        self.greeting_label.pack(pady=20)

        # User Input Entry
        self.user_input_entry = tk.Entry(self)
        self.user_input_entry.pack(fill='x', padx=50)

        # Submit Button
        self.submit_button = tk.Button(self, text='Submit', command=self._process_user_input)
        self.submit_button.pack(pady=10)

    def _process_user_input(self) -> None:
        """Process the user input and display the result.

        This method retrieves the user's input from the entry widget, processes it,
        and then displays the result in a message box.
        """
        user_input = self.user_input_entry.get()
        result = f'You entered: {user_input}'
        messagebox.showinfo('Result', result)

    def _open_file(self) -> None:
        """Open a file dialog to select a file and display its contents."""
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                self.user_input_entry.delete(0, tk.END)
                self.user_input_entry.insert(0, content)

    def _save_file(self) -> None:
        """Open a file dialog to save the current entry content to a file."""
        file_path = filedialog.asksaveasfilename()
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.user_input_entry.get())

    def _generate_vscode_project(self) -> None:
        """Generate a Visual Studio Code project from selected directory."""
        folder_path = filedialog.askdirectory()
        if folder_path:
            # Create a .vscode folder if it doesn't exist
            vscode_folder = os.path.join(folder_path, '.vscode')
            if not os.path.exists(vscode_folder):
                os.makedirs(vscode_folder)
            
            # Generate settings.json inside .vscode folder
            settings_path = os.path.join(vscode_folder, 'settings.json')
            with open(settings_path, 'w') as settings_file:
                settings_file.write('{\n\t// Add your settings here\n}')
            
            # Open the folder in VS Code
            subprocess.run(['code', folder_path], check=True)

    def _run_python_file(self) -> None:
        """Run the current Python file in a separate terminal window."""
        file_path = self.user_input_entry.get()
        if file_path.endswith('.py'):
            subprocess.run(['python', file_path], check=True)
        else:
            messagebox.showerror('Error', 'Please enter a valid Python file path.')

    def _open_documentation(self) -> None:
        """Open the Python documentation in the default web browser."""
        webbrowser.open('https://docs.python.org/3/')

    def _show_about_info(self) -> None:
        """Show the about information of the application."""
        messagebox.showinfo('About', 'AI Copilot Assistant\nVersion 1.0\nCreated by OpenAI')

if __name__ == '__main__':
    app = App()
    app.mainloop()
