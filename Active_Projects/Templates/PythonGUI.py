import PySimpleGUI as sg
import os
import json
from typing import Any, Dict


sg.theme('SystemDefaultForReal')

layout = [
    [sg.Menu([['&File', ['&New Project...', '&Open...', '&Save', '---', 'E&xit']],
              ['&Edit', ['&Preferences']],
              ['&View', ['&Full Screen', '&Restore']],
              ['&Help', ['&About']])],
    [sg.Text('Output:', size=(40, 1))],
    [sg.Output(size=(88, 20), key='-OUTPUT-')],
    [sg.Button('Run', bind_return_key=True), sg.Button('Exit')]
]

def create_project_directory(project_name: str) -> None:
    """
    Creates a new project directory.

    Args:
        project_name (str): The name of the new project.
    """
    base_path = sg.popup_get_folder('Choose a directory for your project:')
    if base_path:
        project_path = os.path.join(base_path, project_name)
        os.makedirs(project_path, exist_ok=True)
        sg.popup('Success', f"Project '{project_name}' has been created at {project_path}")


def load_settings() -> Dict[str, Any]:
    """
    Loads the GUI settings from a JSON file.

    Returns:
        Dict[str, Any]: A dictionary containing the settings.
    """
    try:
        with open('settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_settings(settings: Dict[str, Any]) -> None:
    """
    Saves the GUI settings to a JSON file.

    Args:
        settings (Dict[str, Any]): A dictionary containing the settings to save.
    """
    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)


def run_my_script() -> None:
    """
    Runs the main script.
    """
    # Replace placeholder function with actual script execution code
    sg.popup('Running the script...')


settings = load_settings()
window = sg.Window('Python Script to App', layout, resizable=True)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == 'Run':
        run_my_script()
    elif event == 'New Project...':
        project_name = sg.popup_get_text('Enter the name of the new project:', 'New Project')
        if project_name:
            create_project_directory(project_name)
    elif event == 'Open...':
        sg.popup_get_file('Open Project', no_window=True)
    elif event == 'Save':
        save_settings(settings)
    elif event == 'Full Screen':
        window.maximize()
    elif event == 'Restore':
        window.normal()
    elif event == 'About':
        sg.popup('Python Script to App', 'Version 1.0', 'Created by Python PepWizard')

window.close()