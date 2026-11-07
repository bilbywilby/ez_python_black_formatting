# A python script that scrapes the headlines from a news website and saves them in a text file

# Import the requests, BeautifulSoup, tkinter, and tkinter.ttk modules
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

# Define a list of news websites and their headline elements
news_websites = {
    "CNN": ("https://www.cnn.com/", "h3", "cd__headline"),
    "BBC": ("https://www.bbc.com/news", "h3", "gs-c-promo-heading__title"),
    "NYT": ("https://www.nytimes.com/", "h2", "e1voiwgp0"),
    "FOX": ("https://www.foxnews.com/", "h2", "title")
}

# Define a list of file formats and their extensions
file_formats = {
    "Text": ".txt",
    "CSV": ".csv",
    "JSON": ".json"
}

# Define a list of encodings and their names
encodings = {
    "UTF-8": "utf-8",
    "ASCII": "ascii",
    "ISO-8859-1": "iso-8859-1",
    "Windows-1252": "cp1252"
}

# Define a function that scrapes the headlines from a news website and saves them in a file


def scrape():
    # Get the choice of the news website from the combobox widget
    choice = website_combobox.get()
    # Check if the choice is valid
    if choice in news_websites:
        # Get the url and the headline element from the dictionary
        url, tag, class_ = news_websites[choice]
        # Try to send a GET request to the website and get the HTML content
        try:
            response = requests.get(url)
            html = response.text
            # Try to parse the HTML content using BeautifulSoup
            try:
                soup = BeautifulSoup(html, "html.parser")
                # Find all the elements that contain headlines
                headlines = soup.find_all(tag, class_=class_)
                # Get the choice of the file format from the combobox widget
                file_format = format_combobox.get()
                # Check if the file format is valid
                if file_format in file_formats:
                    # Get the file extension from the dictionary
                    file_extension = file_formats[file_format]
                    # Ask the user to choose the file name and location using a file dialog
                    file_name = filedialog.asksaveasfilename(
                        title="Save as", defaultextension=file_extension, filetypes=[(file_format, file_extension)])
                    # Check if the file name is not empty
                    if file_name:
                        # Get the choice of the encoding from the combobox widget
                        encoding = encoding_combobox.get()
                        # Check if the encoding is valid
                        if encoding in encodings:
                            # Get the encoding name from the dictionary
                            encoding_name = encodings[encoding]
                            # Open a file to write the headlines
                            file = open(file_name, "w", encoding=encoding_name)
                            # Loop through the headlines and write them in the file
                            for i, headline in enumerate(headlines):
                                # Get the text of the headline
                                text = headline.text.strip()
                                # Write the text in the file with the appropriate format
                                if file_format == "Text":
                                    file.write(text + "\n")
                                elif file_format == "CSV":
                                    file.write(f'"{text}"\n')
                                elif file_format == "JSON":
                                    file.write(f'{{"headline": "{text}"}}\n')
                                # Update the progress bar widget with the percentage of completion
                                progress_bar["value"] = (
                                    i + 1) / len(headlines) * 100
                                # Update the window
                                root.update()
                            # Close the file
                            file.close()
                            # Display a message box to show the success of the scraping process
                            messagebox.showinfo("Success", f"Scraped {len(headlines)} headlines from {
                                                url} and saved them in {file_name}")
                        else:
                            # Display a message box to show the error of the encoding choice
                            messagebox.showerror(
                                "Error", "Invalid encoding choice. Please choose from the list.")
                    else:
                        # Display a message box to show the error of the file name
                        messagebox.showerror(
                            "Error", "No file name or location chosen. Please try again.")
                else:
                    # Display a message box to show the error of the file format choice
                    messagebox.showerror(
                        "Error", "Invalid file format choice. Please choose from the list.")
            # If there is a parsing error, display a message box to show the error
            except Exception as e:
                messagebox.showerror(
                    "Error", f"An error occurred while parsing the HTML content: {e}")
        # If there is a request error, display a message box to show the error
        except Exception as e:
            messagebox.showerror(
                "Error", f"An error occurred while requesting the website: {e}")
    else:
        # Display a message box to show the error of the website choice
        messagebox.showerror(
            "Error", "Invalid website choice. Please choose from the list.")


# Create a root window
root = tk.Tk()
# Set the title of the window
root.title("Headline Scraper")

# Create a label widget to ask the user to choose a news website
website_label = tk.Label(
    root, text="Please choose a news website from the following list:")
# Place the label widget in the window using grid layout
website_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

# Create a combobox widget to display the list of news websites
website_combobox = ttk.Combobox(root, values=list(
    news_websites.keys()), state="readonly")
# Set the default value of the combobox widget to the first item in the list
website_combobox.current(0)
# Place the combobox widget in the window using grid layout
website_combobox.grid(row=1, column=0, padx=10, pady=10, sticky="w")

# Create a label widget to ask the user to choose a file format
format_label = tk.Label(
    root, text="Please choose a file format to save the headlines:")
# Place the label widget in the window using grid layout
format_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

# Create a combobox widget to display the list of file formats
format_combobox = ttk.Combobox(root, values=list(
    file_formats.keys()), state="readonly")
# Set the default value of the combobox widget to the first item in the list
format_combobox.current(0)
# Place the combobox widget in the window using grid layout
format_combobox.grid(row=3, column=0, padx=10, pady=10, sticky="w")

# Create a label widget to ask the user to choose an encoding
encoding_label = tk.Label(
    root, text="Please choose an encoding to save the headlines:")
# Place the label widget in the window using grid layout
encoding_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

# Create a combobox widget to display the list of encodings
encoding_combobox = ttk.Combobox(
    root, values=list(encodings.keys()), state="readonly")
# Set the default value of the combobox widget to the first item in the list
encoding_combobox.current(0)
# Place the combobox widget in the window using grid layout
encoding_combobox.grid(row=5, column=0, padx=10, pady=10, sticky="w")

# Create a button widget to scrape the headlines
scrape_button = tk.Button(root, text="Scrape", command=scrape)
# Place the button widget in the window using grid layout
scrape_button.grid(row=6, column=0, padx=10, pady=10, sticky="w")

# Create a progress bar widget to show the progress of the scraping process
progress_bar = ttk.Progressbar(
    root, orient="horizontal", length=200, mode="determinate")
# Place the progress bar widget in the window using grid layout
progress_bar.grid(row=7, column=0, padx=10, pady=10, sticky="w")

# Start the main loop of the window
root.mainloop()
