import PySimpleGUI as sg
import os
import sys
import subprocess
import logging
from typing import Tuple
from collections import namedtuple

CreateExeResult = namedtuple('CreateExeResult', ['success', 'message'])

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
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.handler = logging.StreamHandler(sys.stdout)
        self.handler.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def _create_exe(self, source_file_path: str, destination_file_path: str) -> CreateExeResult:
        """Creates a Windows executable for a Python script file.

        Args:
            source_file_path (str): The path of the Python script file.
            destination_file_path (str): The path to save the created executable.

        Returns:
            A named tuple containing a boolean indicating if the executable file was created successfully
            and an output message.
        """
        try:
            if not os.path.isfile(source_file_path):
                raise FileNotFoundError(f"The file does not exist: {source_file_path}")

            if not source_file_path.endswith('.py'):
                raise ValueError('The file must have a .py extension.')

            # Run pyinstaller to create an executable
            subprocess.check_call(['pyinstaller', '--onefile', source_file_path])

            # Verify that the executable file was created successfully
            if not os.path.isfile(destination_file_path):
                raise Exception(f"Could not find {destination_file_path}")

            message = f"The executable file has been created successfully: {destination_file_path}"
            self.logger.info(message)
            return CreateExeResult(True, message)
        except FileNotFoundError as e:
            message = f"Failed to create the .exe file: {str(e)}."
            self.logger.exception(message)
            return CreateExeResult(False, message)
        except ValueError as e:
            message = f"Failed to create the .exe file: {str(e)}."
            self.logger.exception(message)
            return CreateExeResult(False, message)
        except subprocess.CalledProcessError as e:
            message = f"Failed to create the .exe file: {str(e)}."
            self.logger.exception(message)
            return CreateExeResult(False, message)
        except Exception as e:
            message = f"An error occurred: {str(e)}."
            self.logger.exception(message)
            return CreateExeResult(False, message)

    def run(self):
        while True:
            event, values = self.window.read()
            if event in (sg.WIN_CLOSED, 'Exit'):
                break
            elif event == 'Create Executable':
                script_path = values['script_path']
                output_dir = values['output_dir']

                if not script_path or not output_dir:
                    message = "Please select a Python script file and an output directory."
                    sg.popup_error(message)
                    self.logger.error(message)
                    continue

                exe_path = os.path.join(output_dir, 'my_script.exe')

                if os.path.isfile(exe_path):
                    confirm_message = f"A file named 'my_script.exe' already exists in {output_dir}. Overwrite it?"
                    result = sg.popup_yes_no(confirm_message, title='Confirm Overwrite')
                    if result == 'No':
                        continue

                self.window['Create Executable'].update(disabled=True)
                result = self._create_exe(script_path, exe_path)
                if result.success:
                    sg.popup_ok(result.message, title='Success')
                else:
                    sg.popup_error(result.message, title='Error')
                    self.window['-OUTPUT-'].update(result.message)
                self.window['Create Executable'].update(disabled=False)

            elif 'output_dir' in event or 'script_path' in event:
                if values['output_dir'] and values['script_path']:
                    self.window['Create Executable'].update(disabled=False)

        self.logger.info("Exiting the application.")
        self.window.close()

if __name__ == "__main__":
    app = Application()
    app.run()