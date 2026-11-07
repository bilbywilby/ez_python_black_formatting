import os
import tkinter as tk
from tkinter import filedialog

class ProjectCreator:

    ''' 
    This class creates a graphical user interface for selecting a template and project directory,
    then proceeds to create a project based on the selected template.
    '''

    def __init__(self, master):

        ''' 
        Initializes the ProjectCreator class.

        :param master: The root window for the graphical user interface.
        '''

        self.master = master
        self.master.title('Project Creator')

        # Create the "Select Template" button.
        self.template_button = tk.Button(self.master, text='Select Template', command=self.select_template, font=("Helvetica", 12))
        self.template_button.pack(pady=10)

        # Display the selected template path.
        self.template_path_label = tk.Label(self.master, text='No template selected.', font=("Helvetica", 12))
        self.template_path_label.pack()

        # Create the "Select Project Directory" button.
        self.project_button = tk.Button(self.master, text='Select Project Directory', command=self.select_project_directory, font=("Helvetica", 12))
        self.project_button.pack(pady=10)

        # Display the selected project directory path.
        self.project_path_label = tk.Label(self.master, text='No project directory selected.', font=("Helvetica", 12))
        self.project_path_label.pack()

        # Create the "Create Project" button.
        self.create_button = tk.Button(self.master, text='Create Project', command=self.create_project, font=("Helvetica", 12, "bold"))
        self.create_button.pack(pady=10)

        # Display the current project status.
        self.status_label = tk.Label(self.master, text='Ready', font=("Helvetica", 12))
        self.status_label.pack()

        # Add progress bar for the project creation process
        self.progress_bar = tk.Progressbar(self.master, orient='horizontal', mode='indeterminate')
        self.progress_bar.pack(pady=10)

    def select_template(self):

        ''' 
        Opens a dialog box for the user to select a template and updates the template path label.
        '''

        template_path = filedialog.askopenfilename(title='Select Template')
        self.template_path_label.config(text=template_path)

    def select_project_directory(self):

        ''' 
        Opens a dialog box for the user to select a project directory and updates the project directory path label.
        '''

        project_path = filedialog.askdirectory(title='Select Project Directory')
        self.project_path_label.config(text=project_path)

    def create_project(self):

        ''' 
        Creates a project using the user-selected template and directory.
        '''

        template_path = self.template_path_label.cget('text')
        project_path = self.project_path_label.cget('text')

        # Check if a template and project directory have been selected.
        if not template_path or not os.path.exists(template_path):
            self.status_label.config(text='Error: No template selected.')
            return

        if not project_path or not os.path.exists(project_path):
            self.status_label.config(text='Error: No project directory selected.')
            return

        # Check if the template is a valid file.
        if not os.path.isfile(template_path):
            self.status_label.config(text='Error: Invalid template file.')
            return
        
        # Create the directory if it doesn't exist
        if not os.path.exists(project_path):
            os.makedirs(project_path)

        # Read the template file structure.
        with open(template_path, 'r') as file:
            template = file.read()

        # Remove leading and trailing whitespace from the template.
        template = template.strip()

        # Split the template into individual file and directory paths.
        file_paths = template.split('\n')

        # Display a preview of the template contents.
        self.preview_template_contents(file_paths)

        # Create each directory and file in the project directory.
        for file_path in file_paths:

            # Replace placeholders in the file path with the project path.
            file_path = file_path.replace('EZ_PIC', project_path)

            # Get the full directory path and create it if it doesn't exist.
            directory_path = os.path.dirname(file_path)
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            # Create the file if it doesn't exist.
            if not os.path.exists(file_path):
                with open(file_path, 'w') as file:
                    file.write('')

            # Check if the file already exists in the project directory and prompt the user to make a backup copy.
            else:
                selection = tk.messagebox.askyesno(title='File Already Exists', message=f'{file_path} already exists. Do you want to make a backup copy?')
                if selection:
                    backup_path = self.make_backup_copy(file_path)
                    os.rename(file_path, backup_path)
                    with open(file_path, 'w') as file:
                        file.write('')
                    self.status_label.config(text=f'Created file {file_path} and made backup copy {backup_path}.')
                else:
                    self.status_label.config(text=f'Skipped creating file {file_path}.')

        # Update the status with the project creation result.
        self.status_label.config(text='Project created successfully.')

    def preview_template_contents(self, file_paths):

        ''' 
        Displays a preview of the contents of the selected template.

        :param file_paths: The list of file paths in the template.
        '''

        preview_window = tk.Toplevel(self.master)
        preview_window.title('Preview Template Contents')

        preview_text = tk.Text(preview_window, height=20, width=80, font=("Helvetica", 12))
        preview_text.pack()

        preview_text.insert(tk.END, 'Template Contents:\n\n')
        for file_path in file_paths:
            preview_text.insert(tk.END, f'{file_path}\n')

    def make_backup_copy(self, file_path):

        ''' 
        Creates a backup copy of the file by appending the suffix "_backup" to the file name.

        :param file_path: The original file path.
        :return: The backup file path.
        '''

        backup_name = os.path.splitext(os.path.basename(file_path))[0] + '_backup' + os.path.splitext(file_path)[1]
        backup_path = os.path.join(os.path.dirname(file_path), backup_name)

        return backup_path