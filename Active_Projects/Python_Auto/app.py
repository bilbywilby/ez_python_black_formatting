import requests
import tkinter as tk
from tkinter import messagebox, filedialog, Menu
import os
import subprocess
import json

def main():
    # Create tkinter GUI window
    root = tk.Tk()
    app = Application(root)
    app.mainloop()
    
class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        
    def create_widgets(self):
        # Create a menu bar and add items to it
        menubar = Menu(self)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=lambda: self.open_file())
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=lambda: self.on_exit())
        menubar.add_cascade(label="File", menu=filemenu)
        
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=lambda: messagebox.showinfo("About", "This is an application for sending HTTP requests.\n\nAuthor:\nHuang Xiaodong (1832546)\nZhang Yue (1732911)"))
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.config(menu=menubar)
        
        # Create labels and entry fields
        self.method_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.data_type_var = tk.StringVar()
        self.data_var = tk.Text(self)
        method_label = tk.Label(self, text="Method")
        url_label = tk.Label(self, text="URL")
        data_type_label = tk.Label(self, text="Data Type")
        send_button = tk.Button(self, text="Send Request", command=lambda: self.send_request())
        method_entry = tk.Entry(self, textvariable=self.method_var)
        url_entry = tk.Entry(self, textvariable=self.url_var)
        data_type_option = ["None", "JSON"]
        data_type_select = tk.OptionMenu(self, self.data_type_var, *data_type_option)
        show_data_button = tk.Button(self, text="Show Data", command=lambda: self.show_data())
        
        # Set the grid layout
        method_label.grid(row=0, column=0, sticky='W')
        url_label.grid(row=1, column=0, sticky='W')
        method_entry.grid(row=0, column=1)
        url_entry.grid(row=1, column=1)
        data_type_label.grid(row=2, column=0)
        data_type_select.grid(row=2, column=1)
        show_data_button.grid(row=3, column=1)
        method_entry.bind("<Return>", lambda event: url_entry.focus())
        url_entry.bind("<Return>", lambda event: self.send_request())
        self.data_var.grid(row=4, column=1, rowspan=2)
        send_button.grid(row=6, column=1)
    
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
                data = json.loads(self.data_var.get("1.0", "end-1c"))
            else:
                data = None
            
            response = requests.request(method=method, url=url, json=data)
            messagebox.showinfo("Response", response.text)
        except:
            messagebox.showerror("Error", "An error occurred while sending the request.")
    
    # Function for showing data
    def show_data(self):
        data_type = self.data_type_var.get()
        if data_type == "JSON":
            sample_json = json.dumps({"key": "value"}, indent=4)
            self.data_var.insert(tk.END, sample_json)
        else:
            self.data_var.insert(tk.END, "Data goes here...")
    
    # Function for opening a file
    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.url_var.delete(0, tk.END)
                self.url_var.insert(0, content)
    
    # Function for exiting the application
    def on_exit(self):
        self.master.quit()

if __name__ == "__main__":
    # Create tkinter app and run it
    app = Application()
    app.mainloop()