# Oven Temperature Monitor

This Python script allows you to monitor the temperature of your oven in real-time using a connected temperature sensor. It displays the current temperature on a graphical user interface (GUI) and records temperature data to a log file for future analysis.

## Requirements

To run this script, you will need:

- Python 3.x installed on your machine
- A compatible temperature sensor connected via USB
- Required Python packages: `serial`, `tkinter`, `datetime`, and `matplotlib`

### Installation

1. Install Python 3.x on your machine if it is not already installed. Refer to the official Python documentation for your operating system for detailed installation instructions.

2. Connect a compatible temperature sensor to your machine via USB.

3. Clone or download the repository to a directory on your machine.

4. Open a terminal or command prompt and navigate to the directory where the repository is located.

5. Install the required Python packages by running the following command:

   pip install -r requirements.txt

### Usage

1. Connect your temperature sensor to your machine via USB.

2. Open a terminal or command prompt and navigate to the directory where the repository is located.

3. Run the following command to launch the script:

   python temperature_checker.py

4. The GUI window will open, displaying the current temperature of your oven in degrees Celsius. The log file will be updated with the current temperature every second.

5. The GUI window will also display an alert if the temperature exceeds a certain threshold (default value: 250 degrees Celsius). You can adjust the threshold for the alert by modifying the `threshold` variable in the script.

6. The graph displayed in the GUI window will update every second to show the temperature of the oven over time. The shaded red area on the graph indicates the alert threshold.

7. To stop the script, close the GUI window or press `CTRL+C` in the terminal or command prompt.

### Conclusion

With these instructions, you should now be able to launch and use this Python script to monitor the temperature of your oven with ease and efficiency. By customizing the threshold value and analyzing the data collected in the log file, you can diagnose potential issues with your oven and optimize its performance for your specific needs.
