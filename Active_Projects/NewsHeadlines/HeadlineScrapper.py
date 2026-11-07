# A python script that scrapes the headlines from a news website and saves them in a file

# Import the required modules

from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import tkinter as tk
import requests
from bs4 import BeautifulSoup

url = 'https://www.nytimes.com'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

news_headlines = []

for headline in soup.find_all('h2'):
    news_headlines.append(headline.text)

with open('headlines.txt', 'w') as file:
    for headline in news_headlines:
        file.write(headline + '\n')

# Define the constants for the news websites, file formats, and encodings
NEWS_WEBSITES = {

    "CNN": ("https://www.cnn.com/", "h3", "cd__headline"),
    "BBC": ("https://www.bbc.com/news", "h3", "gs-c-promo-heading__title"),
    "NYT": ("https://www.nytimes.com/", "h2", "e1voiwgp0"),
    "FOX": ("https://www.foxnews.com/", "h2", "title"),
    "ABC": ("https://abcnews.go.com/", "h1", "headlines-li-hed"),
    "CBS": ("https://www.cbsnews.com/", "h3", "item__hed"),
    "NBC": ("https://www.nbcnews.com/", "h2", "tease-card__headline"),
    "WSJ": ("https://www.wsj.com/", "h3", "WSJTheme--headline--19_2KfxG"),
    "Reuters": ("https://www.reuters.com/", "h3", "story-title"),
    "NPR": ("https://www.npr.org/", "h3", "title"),
    "The Guardian": ("https://www.theguardian.com/us", "h3", "fc-item__title"),
    "Al Jazeera": ("https://www.aljazeera.com/", "h2", "post-title"),
    "The Washington Post": ("https://www.washingtonpost.com/", "h2", "headline"),
    "The Huffington Post": ("https://www.huffpost.com/", "h2", "card__headline__text"),
    "USA Today": ("https://www.usatoday.com/", "h3", "gnt_ar_b_h"),
    "The Atlantic": ("https://www.theatlantic.com/", "h2", "c-tease__hed"),
    "TIME": ("https://time.com/", "h2", "title"),
    "Bloomberg": ("https://www.bloomberg.com/", "h1", "story-package-module__story__headline-link"),
    "VICE": ("https://www.vice.com/en", "h2", "vice-card-hed__link"),
    "The Economist": ("https://www.economist.com/", "h3", "headline-link"),
    "The New Yorker": ("https://www.newyorker.com/", "h4", "Link__link___3dWao"),
    "National Geographic": ("https://www.nationalgeographic.com/", "h3", "ListTitle__title___2wZ1a"),
    "BuzzFeed News": ("https://www.buzzfeednews.com/", "h2", "newsblock-story-card__title"),
    "The Onion": ("https://www.theonion.com/", "h4", "sc-759qgu-0")
}


FILE_FORMATS = {
    "Text": ".txt",
    "CSV": ".csv",
    "JSON": ".json"
}

ENCODINGS = {
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
    if choice in NEWS_WEBSITES:
        # Get the url and the headline element from the dictionary
        url, tag, class_ = NEWS_WEBSITES[choice]
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
                if file_format in FILE_FORMATS:
                    # Get the file extension from the dictionary
                    file_extension = FILE_FORMATS[file_format]
                    # Ask the user to choose the file name and location using a file dialog
                    file_name = filedialog.asksaveasfilename(
                        title="Save as", defaultextension=file_extension, filetypes=[(file_format, file_extension)])
                    # Check if the file name is not empty
                    if file_name:
                        # Get the choice of the encoding from the combobox widget
                        encoding = encoding_combobox.get()
                        # Check if the encoding is valid
                        if encoding in ENCODINGS:
                            # Get the encoding name from the dictionary
                            encoding_name = ENCODINGS[encoding]
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
    NEWS_WEBSITES.keys()), state="readonly")
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
    FILE_FORMATS.keys()), state="readonly")
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
    root, values=list(ENCODINGS.keys()), state="readonly")
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
