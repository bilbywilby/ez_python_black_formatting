import argparse
import os

def validate_input(filename: str, initial_code: str) -> bool:
    if not filename:
        print("Error: Please provide a valid input file.")
        return False

    try:
        with open(os.path.join("challenges", filename), "r") as f:
            challenge = f.read()

        # Check that the provided code is at least one line long
        if len(initial_code.split("\n")) < 1:
            print("Error: Your solution must be at least one line of code.")
            return False

        # Compare the length of
        # - The given code and the expected code (to check for extra lines)
        # - Just the first line of the expected code to the given code
        # If they don't match in either case, then there's an error
        if len(challenge.split("\n")) != len(initial_code.split("\n")) and initial_code != challenge.split("\n")[0]:
            print("""Error: There seems to be a mismatch between what I was expecting and what you submitted.
Please make sure your submission matches exactly with the example provided.\n""")
            return False
    except FileNotFoundError:
        print(f"The file '{filename}' does not exist.")
        return False
    return True

def create_file(file_path: str, initial_code: str, overwrite: bool) -> None:
    if not overwrite and os.path.exists(file_path):
        print(f"Error: File '{file_path}' already exists. Use --overwrite flag to delete it and create a new file.")
        return

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(initial_code)

if __name__ == "__main__":
    # Parse user input for filename, initial_code, and overwrite flag
    parser = argparse.ArgumentParser(description="Create a new Python file")
    parser.add_argument("filename", help="The name of the new Python file")
    parser.add_argument("--initial-code", help="Initial code to put in the new file", default="")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the file if it exists")

    args = parser.parse_args()
    try:
        if validate_input(args.filename, args.initial_code):
            file_path = os.path.abspath(args.filename)
            create_file(file_path, args.initial_code, args.overwrite)
            print(f"Successfully created {file_path} with initial code:\n{args.initial_code}")
        else:
            raise ValueError("Invalid input")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"Error: {str(e)}")
