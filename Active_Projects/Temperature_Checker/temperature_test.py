import serial
import time
from tkinter import *
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Replace 'COM3' with your sensor's serial port
ser = serial.Serial('COM3', 9600, timeout=1)
ser.flush()

# Data storage for plotting
temperatures = []
timestamps = []


def update_temperature():
    if ser.in_waiting > 0:
        try:
            line = ser.readline().decode('utf-8').rstrip()
            temperature = float(line)
            temperatures.append(temperature)
            timestamps.append(datetime.datetime.now())
            temperature_label.config(
                text=f"Current Oven Temperature: {temperature}°C")
            log_temperature(temperature)
            check_alert(temperature)
            update_graph()
        except ValueError:
            temperature_label.config(text="Error reading temperature data.")
    root.after(1000, update_temperature)


def log_temperature(temp):
    with open("oven_temperature_log.txt", "a") as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp}: {temp}°C\n")


def check_alert(temp, threshold=250):
    if temp > threshold:
        alert_label.config(
            text="Warning: Temperature is above threshold!", fg="red")
    else:
        alert_label.config(
            text="Temperature is within normal range.", fg="green")


def update_graph():
    if len(timestamps) > 1:
        ax.clear()
        ax.plot(timestamps, temperatures, 'r-')
        ax.set_title('Oven Temperature Over Time')
        canvas.draw()


# GUI setup
root = Tk()
root.title("Oven Temperature Monitor")
root.geometry('800x600')

temperature_label = Label(root, font=("Helvetica", 24), fg="black", bg="white")
temperature_label.pack(pady=20)

alert_label = Label(root, font=("Helvetica", 18), fg="green")
alert_label.pack(pady=10)

fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

update_temperature()  # Initial call to start the loop
root.mainloop()
