import PySimpleGUI as sg
import os
import sys
import subprocess
from typing import Tuple

class Application:
    """A PySimpleGUI application for creating a Windows executable file from a Python script file."""

    def __init__(self):
        sg.theme('SystemDefaultForReal')

        self.layout = [
            [sg.Text('Select Python Script:', pad=(10, 10)), sg.Input(key='script_path'), sg.FileBrowse()],
            [sg.Text('Select Output Directory:', pad=(10, 10)), sg.Input(key='output_dir'), sg.FolderBrowse()],
            [sg.Button('Create Executable', disabled=True, size=(20, 2), pad=(10, 10))],
            [sg.Output(size=(80, 20), key='-OUTPUT-', pad=(10, 10))],
            [sg.Button('Exit', size=(20, 2), pad=(10, 10))]
        ]

        self.window = sg.Window('PyInstaller GUI', self.layout, resizable=True)

    def _create_exe(self, source_file_path: str, destination_file_path: str) -> Tuple[bool, str]:
        """Creates a Windows executable for a Python script file.
        Args:
            source_file_path (str): The path of the Python script file.
            destination_file_path (str): The path to save the created executable.
        Returns:
            A tuple containing a boolean indicating if the executable file was created successfully and an output message.
        """
        if not os.path.isfile(source_file_path):
            return False, f"The file does not exist: {source_file_path}"

        if not source_file_path.endswith('.py'):
            return False, 'The file must have a .py extension.'

        try:
            # Run pyinstaller to create an executable
            subprocess.check_call(['pyinstaller', '--onefile', source_file_path])

            # Verify that the executable file was created successfully
            if not os.path.isfile(destination_file_path):
                return False, f"Could not find {destination_file_path}"

            return True, f"The executable file has been created successfully: {destination_file_path}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to create the .exe file: {str(e)}"
        except Exception as e:
            return False, f"An error occurred: {str(e)}"

    def run(self):
        while True:
            event, values = self.window.read()
            if event in (sg.WIN_CLOSED, 'Exit'):
                break
            elif event == 'Create Executable':
                script_path = values['script_path']
                output_dir = values['output_dir']

                if not script_path or not output_dir:
                    sg.popup_error("Please select a Python script file and an output directory.")
                    continue

                exe_path = os.path.join(output_dir, 'my_script.exe')

                if os.path.isfile(exe_path):
                    result = sg.popup_yes_no(f"A file named 'my_script.exe' already exists in {output_dir}. "
                                             "Overwrite it?", title='Confirm Overwrite')
                    if result == 'No':
                        continue

                self.window['Create Executable'].update(disabled=True)
                success, message = self._create_exe(script_path, exe_path)
                if success:
                    sg.popup_ok(message, title='Success')
                else:
                    sg.popup_error(message, title='Error')
                    self.window['-OUTPUT-'].update(message)
                self.window['Create Executable'].update(disabled=False)

            elif 'output_dir' in event or 'script_path' in event:
                if values['output_dir'] and values['script_path']:
                    self.window['Create Executable'].update(disabled=False)

        self.window.close()

if __name__ == "__main__":
    app = Application()
    app.run()