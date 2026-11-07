# Import the modules
import requests
import tkinter as tk

# Define the URL of the API to get the weather data
url = "https://api.openweathermap.org/data/2.5/weather"

# Define the API key
api_key = "your_api_key"

# Define the units
units = "metric"

# Define the parameters for the API request
params = {
    "appid": api_key,
    "units": units
}

# Create a root window
root = tk.Tk()
# Set the title of the window
root.title("Weather App")

# Create a frame to hold the widgets
frame = tk.Frame(root)
# Pack the frame to the window
frame.pack()

# Create a label widget to display the location
location_label = tk.Label(frame, text="Location:", font=("Arial", 16))
# Pack the label to the frame
location_label.pack()

# Create an entry widget to enter the location
location_entry = tk.Entry(frame, font=("Arial", 16))
# Pack the entry to the frame
location_entry.pack()

# Create a button widget to get the weather
get_weather_button = tk.Button(frame, text="Get Weather", font=("Arial", 16))
# Pack the button to the frame
get_weather_button.pack()

# Create a label widget to display the weather
weather_label = tk.Label(frame, font=("Arial", 16))
# Pack the label to the frame
weather_label.pack()

# Define a function to get the weather


def get_weather():
    # Get the location from the entry widget
    location = location_entry.get()
    # Check if the location is not empty
    if location:
        # Add the location to the parameters
        params["q"] = location
        # Send a GET request to the API with the parameters
        response = requests.get(url, params=params)
        # Get the JSON data from the response
        data = response.json()
        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            # Get the weather information from the data
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            # Format the weather information
            weather_info = f"Temperature: {temp} °C\nFeels like: {
                feels_like} °C\nHumidity: {humidity} %\nDescription: {description}"
            # Update the weather label with the weather information
            weather_label.config(text=weather_info, fg="black")
        else:
            # Update the weather label with an error message
            weather_label.config(
                text="Sorry, could not find the weather for this location.", fg="red")
    else:
        # Update the weather label with an error message
        weather_label.config(text="Please enter a location.", fg="red")


# Configure the button to call the get_weather function when clicked
get_weather_button.config(command=get_weather)

# Start the main loop of the window
root.mainloop()
