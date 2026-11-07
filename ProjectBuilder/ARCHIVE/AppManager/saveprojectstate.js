{
    "Save Project State"; {
        "prefix"; "saveprojectstate",
            "body";[
                "def save_project_state(self) -> None:",
                "\t\"\"\"Saves the current state of the project to a JSON file.\"\"\"",
                "\ttry:",
                "\t\twith open('project_state.json', 'w') as f:",
                "\t\t\tjson.dump({",
                "\t\t\t\t'apps': self.apps,",
                "\t\t\t\t'project_structure': self.PROJECT_STRUCTURE",
                "\t\t\t}, f, indent=4)",
                "\t\tmessagebox.showinfo('Success', 'Project state saved successfully.')",
                "\texcept Exception as e:",
                "\t\tmessagebox.showerror('Error', f'Failed to save project state: {e}')",
                "",
                "def load_project_state(self) -> None:",
                "\t\"\"\"Loads the project state from a JSON file if it exists.\"\"\"",
                "\ttry:",
                "\t\twith open('project_state.json', 'r') as f:",
                "\t\t\tstate = json.load(f)",
                "\t\t\tself.apps = state.get('apps', [])",
                "\t\t\tself.PROJECT_STRUCTURE = state.get('project_structure', self.PROJECT_STRUCTURE)",
                "\t\t\tself.refresh_app_list()",
                "\texcept FileNotFoundError:",
                "\t\t# If the file doesn't exist, we can start with the default state",
                "\t\tpass",
                "\texcept Exception as e:",
                "\t\tmessagebox.showerror('Error', f'Failed to load project state: {e}')"
            ],
                "description"; "Snippet to save and load the project state for the AppRunner class."
    },
    "Open File in Editor"; {
        "prefix"; "openfileineditor",
            "body";[
                "import os",
                "os.startfile(\"$1\")"  # $1 is replaced by whatever you type after the snippet
            ]
    }
}
