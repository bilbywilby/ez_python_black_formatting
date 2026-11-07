import os
import tkinter as tk
from tkinter import filedialog


class ProjectCreator:
    def __init__(self, master):
        self.master = master
        self.master.title('Project Creator')
        self.template_button = tk.Button(
            self.master, text='Select Template', command=self.select_template)
        self.template_button.pack()
        self.template_path_label = tk.Label(
            self.master, text='No template selected.')
        self.template_path_label.pack()
        self.project_button = tk.Button(
            self.master, text='Select Project Directory', command=self.select_project_directory)
        self.project_button.pack()
        self.project_path_label = tk.Label(
            self.master, text='No project directory selected.')
        self.project_path_label.pack()
        self.create_button = tk.Button(
            self.master, text='Create Project', command=self.create_project)
        self.create_button.pack()
        self.status_label = tk.Label(self.master, text='Ready')
        self.status_label.pack()

    def select_template(self):
        template_path = filedialog.askopenfilename(title='Select Template')
        self.template_path_label.config(text=template_path)

    def select_project_directory(self):
        project_path = filedialog.askdirectory(
            title='Select Project Directory')
        self.project_path_label.config(text=project_path)

    def create_project(self):
        template_path = self.template_path_label.cget('text')
        project_path = self.project_path_label.cget('text')

        if not template_path or not os.path.exists(template_path):
            self.status_label.config(text='Error: No template selected.')
            return

        if not project_path or not os.path.exists(project_path):
            self.status_label.config(
                text='Error: No project directory selected.')
            return

        # Read the template file structure
        with open(template_path, 'r') as f:
            template = f.read()

        # Remove the leading and trailing whitespace from the template
        template = template.strip()

        # Split the template into individual directory and file paths
        file_paths = template.split('\n')

        # Create each directory and file in the project directory
        for file_path in file_paths:
            # Replace placeholders with project name and project path
            file_path = file_path.replace('EZ_PIC', project_path)

            # Get the full directory path and create it if it doesn't exist
            directory_path = os.path.dirname(file_path)
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            # Create the file if it doesn't exist
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write('')
                    self.status_label.config(
                        text='Created file: {}'.format(file_path))

        self.status_label.config(text='Finished creating project directory.')


if __name__ == '__main__':
    root = tk.Tk()
    project_creator = ProjectCreator(root)
    root.mainloop()
