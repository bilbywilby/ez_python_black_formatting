# Import the modules
import tkinter as tk
import pickle

# Define the file name to store the data
file_name = "todo_list.pkl"

# Define a function to load the data from the file


def load_data():
    # Try to open the file and read the data
    try:
        with open(file_name, "rb") as f:
            data = pickle.load(f)
    # If the file does not exist, create an empty list
    except FileNotFoundError:
        data = []
    # Return the data
    return data

# Define a function to save the data to the file


def save_data(data):
    # Open the file and write the data
    with open(file_name, "wb") as f:
        pickle.dump(data, f)

# Define a function to add a task to the list


def add_task():
    # Get the task from the entry widget
    task = entry.get()
    # Check if the task is not empty
    if task:
        # Add the task to the list widget
        listbox.insert(tk.END, task)
        # Clear the entry widget
        entry.delete(0, tk.END)
        # Save the data
        save_data(listbox.get(0, tk.END))

# Define a function to delete a task from the list


def delete_task():
    # Get the selected index from the list widget
    index = listbox.curselection()
    # Check if the index is not empty
    if index:
        # Delete the task from the list widget
        listbox.delete(index)
        # Save the data
        save_data(listbox.get(0, tk.END))


# Create a root window
root = tk.Tk()
# Set the title of the window
root.title("To-Do List App")

# Create a frame to hold the widgets
frame = tk.Frame(root)
# Pack the frame to the window
frame.pack()

# Create a listbox widget to display the tasks
listbox = tk.Listbox(frame, height=10, width=40)
# Pack the listbox to the frame
listbox.pack(side=tk.LEFT)

# Create a scrollbar widget to scroll the listbox
scrollbar = tk.Scrollbar(frame)
# Pack the scrollbar to the frame
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configure the scrollbar to the listbox
scrollbar.config(command=listbox.yview)
listbox.config(yscrollcommand=scrollbar.set)

# Create an entry widget to enter a task
entry = tk.Entry(root)
# Pack the entry to the window
entry.pack()

# Create a button widget to add a task
add_button = tk.Button(root, text="Add", command=add_task)
# Pack the button to the window
add_button.pack()

# Create a button widget to delete a task
delete_button = tk.Button(root, text="Delete", command=delete_task)
# Pack the button to the window
delete_button.pack()

# Load the data from the file
data = load_data()
# Loop through the data and add them to the listbox
for task in data:
    listbox.insert(tk.END, task)

# Start the main loop of the window
root.mainloop()
