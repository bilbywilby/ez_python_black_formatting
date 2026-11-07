# Import the modules
import pygame
import tkinter as tk
import os

# Initialize pygame mixer
pygame.mixer.init()

# Define the directory of the music files
music_dir = "music"

# Get the list of music files
music_files = os.listdir(music_dir)

# Define the index of the current music file
current_index = 0

# Create a root window
root = tk.Tk()
# Set the title of the window
root.title("Music Player")

# Create a frame to hold the widgets
frame = tk.Frame(root)
# Pack the frame to the window
frame.pack()

# Create a label widget to display the song name
song_label = tk.Label(
    frame, text=music_files[current_index], font=("Arial", 16))
# Pack the label to the frame
song_label.pack()

# Create a button widget to play the song
play_button = tk.Button(frame, text="Play", font=("Arial", 16))
# Pack the button to the frame
play_button.pack(side=tk.LEFT)

# Create a button widget to pause the song
pause_button = tk.Button(frame, text="Pause", font=("Arial", 16))
# Pack the button to the frame
pause_button.pack(side=tk.LEFT)

# Create a button widget to stop the song
stop_button = tk.Button(frame, text="Stop", font=("Arial", 16))
# Pack the button to the frame
stop_button.pack(side=tk.LEFT)

# Create a button widget to play the next song
next_button = tk.Button(frame, text="Next", font=("Arial", 16))
# Pack the button to the frame
next_button.pack(side=tk.LEFT)

# Create a button widget to play the previous song
prev_button = tk.Button(frame, text="Prev", font=("Arial", 16))
# Pack the button to the frame
prev_button.pack(side=tk.LEFT)

# Define a function to play the song


def play_song():
    # Get the current music file
    music_file = music_files[current_index]
    # Load the music file
    pygame.mixer.music.load(os.path.join(music_dir, music_file))
    # Play the music file
    pygame.mixer.music.play()
    # Update the song label with the music file name
    song_label.config(text=music_file)

# Define a function to pause the song


def pause_song():
    # Pause the music file
    pygame.mixer.music.pause()

# Define a function to stop the song


def stop_song():
    # Stop the music file
    pygame.mixer.music.stop()

# Define a function to play the next song


def next_song():
    # Declare the current index as a global variable
    global current_index
    # Increment the current index by 1
    current_index += 1
    # Check if the current index is out of range
    if current_index >= len(music_files):
        # Reset the current index to 0
        current_index = 0
    # Play the song
    play_song()

# Define a function to play the previous song


def prev_song():
    # Declare the current index as a global variable
    global current_index
    # Decrement the current index by 1
    current_index -= 1
    # Check if the current index is out of range
    if current_index < 0:
        # Reset the current index to the last index
        current_index = len(music_files) - 1
    # Play the song
    play_song()


# Configure the buttons to call the corresponding functions when clicked
play_button.config(command=play_song)
pause_button.config(command=pause_song)
stop_button.config(command=stop_song)
next_button.config(command=next_song)
prev_button.config(command=prev_song)

# Start the main loop of the window
root.mainloop()
