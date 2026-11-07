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

        # Read the template file structure.
        with open(template_path, 'r') as file:
            template = file.read()

        # Remove leading and trailing whitespace from the template.
        template = template.strip()

        # Split the template into individual file and directory paths.
        file_paths = template.split('\n')

        # Create each directory and file in the project directory.
        for file_path in file_paths:

            # Replace placeholders in the file path with the project name and path.
            file_path = file_path.replace('EZ_PIC', project_path)

            # Get the full directory path and create it if it doesn't exist.
            directory_path = os.path.dirname(file_path)
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            # Create the file if it doesn't exist.
            if not os.path.exists(file_path):
                with open(file_path, 'w') as file:
                    file.write('')

        self.status_label.config(text='Project created successfully.')