import requests
import tkinter as tk
from tkinter import messagebox, filedialog, Menu
import json

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("HTTP Request Sender")
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        # Create a menu bar and add items to it
        menubar = Menu(self.master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.on_exit)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.master.config(menu=menubar)

        # Create labels and entry fields
        method_label = tk.Label(self, text="Method", font=("Arial", 12))
        url_label = tk.Label(self, text="URL", font=("Arial", 12))
        data_type_label = tk.Label(self, text="Data Type", font=("Arial", 12))
        data_label = tk.Label(self, text="Data", font=("Arial", 12))

        self.method_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.data_type_var = tk.StringVar(value="None")

        method_option = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        method_select = tk.OptionMenu(self, self.method_var, *method_option)

        self.url_entry = tk.Entry(self, textvariable=self.url_var, font=("Arial", 12), width=50, bd=3)

        data_type_option = ["None", "JSON"]
        data_type_select = tk.OptionMenu(self, self.data_type_var, *data_type_option, command=self.show_data_form)

        self.json_data_text = tk.Text(self, font=("Arial", 12), height=10, bd=3)

        send_button = tk.Button(self, text="Send Request", font=("Arial", 12), command=self.send_request)

        # Set the grid layout
        method_label.grid(row=0, column=0, sticky='W')
        method_select.grid(row=0, column=1, pady=(5,10))
        url_label.grid(row=1, column=0, sticky='W')
        self.url_entry.grid(row=1, column=1, pady=(5,10))
        data_type_label.grid(row=2, column=0, sticky='W')
        data_type_select.grid(row=2, column=1, pady=(5,10))
        data_label.grid(row=3, column=0, sticky='W')
        self.json_data_text.grid(row=4, column=1, pady=(5,10))
        send_button.grid(row=5, column=1)

    # Function for showing data form
    def show_data_form(self, event):
        
        data_type = self.data_type_var.get()

        if data_type == "None":
            self.json_data_text.grid_remove()
        else:
            self.json_data_text.grid(row=4, column=1, pady=(5,10))

    # Function for sending HTTP request
    def send_request(self):

        method = self.method_var.get()
        url = self.url_var.get()
        data_type = self.data_type_var.get()

        if not url:
            messagebox.showerror("Error", "URL is missing.")
            return

        try:
            if data_type == "JSON":
                data = json.loads(self.json_data_text.get("1.0", "end-1c"))
            else:
                data = None

            response = requests.request(method=method, url=url, json=data)
            messagebox.showinfo("Response", response.text)
        except:
            messagebox.showerror("Error", "An error occurred while sending the request.")

    # Function for showing about dialogue box
    def show_about(self):

        messagebox.showinfo(
            "About HTTP Request Sender", 
            "This is an application for sending HTTP requests.\n\nAuthors:\nHuang Xiaodong (1832546)\nZhang Yue (1732911)"
        )

    # Function for opening a file
    def open_file(self):

        file_path = filedialog.askopenfilename()

        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.url_var.set(content)

    # Function for exiting the application
    def on_exit(self):
        self.master.destroy()

if __name__ == "__main__":
    # Create tkinter app and run it
    root = tk.Tk()
    app = Application(root)
    app.mainloop()