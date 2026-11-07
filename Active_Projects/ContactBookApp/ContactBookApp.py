import tkinter as tk
from tkinter import messagebox, filedialog
import json
import re
import sqlite3

class ContactBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title('My Personal Contact Book')
        self.root.geometry('650x500')
        self.root.config(bg='#f5f6f8')

        title_lbl = tk.Label(self.root,text='My Personal Contact Book',
                             font=('Helvetica', 25, 'bold'), fg='#4a4e69', bg='#f5f6f8')
        title_lbl.pack(side=tk.TOP, fill=tk.X, pady=20)

        # Add labels and entries for contact details
        name_lbl = tk.Label(self.root, text='Contact Name:', anchor=tk.W,
                             font=('Helvetica', 14, 'bold'), fg='#1d3557', bg='#f5f6f8')
        name_lbl.place(x=40, y=120, width=150, height=30)
        self.name_entry = tk.Entry(self.root, font=('Helvetica', 14))
        self.name_entry.place(x=200, y=120, width=350, height=30)

        phone_lbl = tk.Label(self.root, text='Phone Number:', anchor=tk.W,
                              font=('Helvetica', 14, 'bold'), fg='#1d3557', bg='#f5f6f8')
        phone_lbl.place(x=40, y=170, width=150, height=30)
        self.phone_entry = tk.Entry(self.root, font=('Helvetica', 14))
        self.phone_entry.place(x=200, y=170, width=350, height=30)

        email_lbl = tk.Label(self.root, text='Email Address:', anchor=tk.W,
                              font=('Helvetica', 14, 'bold'), fg='#1d3557', bg='#f5f6f8')
        email_lbl.place(x=40, y=220, width=150, height=30)
        self.email_entry = tk.Entry(self.root, font=('Helvetica', 14))
        self.email_entry.place(x=200, y=220, width=350, height=30)

        address_lbl = tk.Label(self.root, text='Address:', anchor=tk.W,
                                font=('Helvetica', 14, 'bold'), fg='#1d3557', bg='#f5f6f8')
        address_lbl.place(x=40, y=270, width=150, height=30)
        self.address_entry = tk.Entry(self.root, font=('Helvetica', 14))
        self.address_entry.place(x=200, y=270, width=350, height=30)

        # Add a button to upload a contact file
        upload_btn = tk.Button(self.root, text='Upload Contacts', font=('Helvetica', 14, 'bold'), bg='#e9c46a',command=self.upload_contacts)
        upload_btn.place(x=40, y=330, width=150, height=40)

        add_btn = tk.Button(self.root, text='Add Contact', font=('Helvetica', 14, 'bold'), bg='#2a9d8f', command=self.add_contact)
        add_btn.place(x=240, y=330, width=150, height=40)

        delete_btn = tk.Button(self.root, text='Delete Contact', font=('Helvetica', 14, 'bold'), bg='#e76f51',command=self.delete_contact)
        delete_btn.place(x=450, y=330, width=150, height=40)


        # Add a listbox to show existing contacts with a scrollbar
        self.contacts_listbox = tk.Listbox(self.root, font=('Helvetica', 14))
        self.contacts_listbox.place(x=40, y=400, width=560, height=150)
        scrollbar = tk.Scrollbar(self.root, orient='vertical', command=self.contacts_listbox.yview)
        scrollbar.place(x=600, y=400, height=150)
        self.contacts_listbox.config(yscrollcommand=scrollbar.set)

        # Load existing contacts
        self.load_contacts()

        export_btn = tk.Button(self.root, text='Export Contacts', font=('Helvetica', 14, 'bold'), bg='#e9c46a', command=self.export_contacts)
        export_btn.place(x=40, y=570, width=150, height=40)

        generate_btn = tk.Button(self.root, text='Generate Directory', font=('Helvetica', 14, 'bold'), bg='#2a9d',
    def load_contacts(self):
        """Load the existing contacts from the database into the GUI"""
        conn = sqlite3.connect("contacts.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM Contacts ORDER BY LastName ASC;")
            records = cursor.fetchall()
            for record in records:
                firstname = record[1]
                lastname = record[2]
                phone = record[3]
                email = record[4]
                address = record[5]
                item = "{}, {} - Phone: {}, Email: {}, Address:\n{}".format(firstname, lastname, phone, email, address),
                item = "{}, {}, Phone: {:>12}, Email: {:<30}, Address: {}".format(firstname, lastname, phone, email, address)
                item = "{}, {} - Phone: {}, Email: {}, Address: {}".format(firstname, lastname, phone, email, address)
                self.add_to_listbox("%s %s\n%s\n%s\n%s" % (firstname, lastname, phone, email, address))
        finally:
            conn.close()

    def save_contact(self):
        """Save the current contact information to the database"""
        if not self.validate():
            return

        values = [self.firstname_entry.get(), self.lastname_entry.get(), self.phone_entry.get(),
                  self.email_entry.get(), self.address_entry.get()]
        conn = sqlite3.connect("contacts.db")
        cursor = conn.cursor()
        if self.editing:
            # Update an existing entry
            id = self.contacts_listbox.selection_get()
            cursor.execute("UPDATE Contacts SET FirstName=?, LastName=?, Phone=?, Email=?, Address=? WHERE ID=
            cursor.execute("UPDATE Contacts SET FirstName=?, LastName=?, Phone=?, Email=? WHERE ID=?",
                           values + [id])
        else:
            # Add a new entry
            cursor.execute("INSERT INTO Contacts VALUES (NULL, ?, ?, ?, ?, ?)", values)
        conn.commit()
        self.refresh_view()

    def validate(self):
        """Check if all required fields have been  filled out"""
        firstname = self.firstname_entry.get().strip()
        lastname = self.lastname_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip() 
        address = self.address_entry.get().strip()

        if not firstname or not lastname or not phone or not email or not address:
            showerror("Missing Information", "Please provide all of the required information.")
            return False
        elif not phonetest.match(phone):
            showerror("Invalid Phone Number", "The phone number you entered does not appear to be valid.\n\nPlease enter it in this")
    def load_contacts(self):
        """Load the list of existing contacts from disk into the GUI"""
        try:
            with open("contacts.txt", "r") as file:
                for line in file:
                    name, phone, email, address = line.strip().split(", ")
                    self.add_to_list box(name, phone, email, address)
        except FileNotFoundError:
            pass

    def save_contacts(self):
        """Save the current list of contacts to disk"""
        with open("contacts.txt", "w") as file:
            for i in range(self.contacts_listbox.size()):
                item = self.contacts_listbox.get(i)
                file.write("%s,%s,%s,%s\n" % tuple(item))

    def add_to_listbox(self, name, phone="", email="", address=""):
        """Add an entry to the listbox"""
        index = self.contacts_listbox.size()
        self.contacts_listbox.insert(index, (name, phone, email, address))

    def on_upload(self):
        """Handle upload button click event"""
        filename = filedialog.askopenfilename(filetypes=[("CSV files","*. csv")])
        if not filename:
            return
        print("Selected CSV file: ", filename)
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            for row in reader:
                self.add_to_listbox(*row)

def main():
    app = ContactApp()
    app.mainloop() 
    if __name__ == "__main__":
        app.save_contacts()
        
    def load_contacts(self):
        """Load the existing contacts from the database into the list box."""
        conn = sqlite3.connect("contacts.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM Contacts ORDER BY LastName ASC;")
            records = cursor.fetchall()
            for record in records:
                fullname = "{}, {}".format(record[2], record[1])
                self.contacts_listbox.insert(tk.END, "{} - {} - {}".format(fullname, record[ 3], record[4]))
        finally:
            conn.close()

    def on_add_clicked(self):
        """Add a new contact to the database when the 'Add' button is clicked."""
        firstname = self.firstname_entry.get().strip()
        lastname = self.lastname_ entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()

        if not firstname or not lastname or not phone or not email:
            messagebox.showwarning("Missing Information", "Please enter all required information.") 
            return

        # Check that there are no duplicate entries (based on name and/or phone number)
        duplicates = False
        conn = sqlite3.connect("contacts.db")
        cursor = conn.cursor()
        try:
            query = "SELECT COUNT(*) FROM Contacts WHERE FirstName=? AND LastName=?"
            params = (firstname, lastname)
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            if count > 0:
                duplicates = True

            query = "SELECT COUNT(*) FROM Contacts WHERE PhoneNumber=?"
            params = (phone, )
            cursor.execute(query, params)
            other_count = cursor.fetchone()[0]
            if other_count > 0:
                duplicates |= tk.messagebox.
                askyesno("Phone Number Duplicate",
                         "This phone number is already associated with another contact.\n" +
                         "Do you want to continue adding this contact anyway?")
        finally:
            conn.commit()
            conn.close()

        if duplicates:
            return

        # Add the new contact to the database
        dml = "INSERT INTO Contacts (FirstName, LastName, PhoneNumber, Email)" \
              " VALUES(?, ?, ?, ?)"
        params = (firstname, lastname, phone, email)
        conn = sqlite3.connect("contacts.db")
        cursor = conn.cursor()
        cursor.execute(dml, params)
        conn.commit()
        self.update_listbox()</s>
        #include <iostream>
        using namespace std;

        int main(){
          cout << "Hello World!" << endl;
          
          // Declare variables and assign values
          string firstName = "John";
          string lastName = "Doe";
          int age = 25;
          double heightFeet = 6.1;
          double heightInches = (heightFeet - Math.floor(heightFeet)) * 12;
          
          // Display results
          cout << "First Name: " << firstName << endl;
          cout << "Last Name: " << lastName << endl;
          cout << "Age: " << age << endl;
          cout << "Height: " << heightFeet << "\'" << heightInches << "\'\"" << "ft." << endl;
          
          return 0;
        }
from tkinter import *
from tkinter import messagebox, filedialog
import json
import re
import sqlite3

class ContactBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title('My Personal Contact Book')
        self.root.geometry('650x500')
        self.root.config(bg='#f5f6f8')

        title_lbl = Label(self.root,text='My Personal Contact Book',
                           font=('Helvetica', 25, 'bold'), fg='#4a4e69', bg='#f5f6f8')
        title_lbl.pack(side=TOP, fill=X, pady=20)

        # Add labels and entries for contact details
        name_lbl = Label(self.root, text='Contact Name:', anchor=W,
                         font=('Helvetica', 14, 'bold'), fg='#1d3557', bg='#f5f6f8')
        name_lbl.place(x=40, y=120, width=150, height=30)
        self.name_entry = Entry(self.root, font=('Helvetica', 14))
        self.name_entry.place(x=200, y=120, width=350, height=30)

        phone_lbl = Label(self.root, text='Phone Number:', anchor=W,
                          font=('Helvetica', 14, 'bold'), fg='#1d3557', bg='#f5f6f8')
        phone_lbl.place(x=40, y=170, width=150, height=30)
        self.phone_entry = Entry(self.root, font=('Helvetica', 14))
        self.phone_entry.place(x=200, y=170, width=350, height=30)

        email_lbl = Label(self.root, text='Email Address:', anchor=W,
                          font=('Helvetica', 14, 'bold'), fg='#1d3557', bg='#f5f6f8')
        email_lbl.place(x=40, y=220, width=150, height=30)
        self.email_entry = Entry(self.root, font=('Helvetica', 14))
        self.email_entry.place(x=200, y=220, width=350, height=30)

        address_lbl = Label(self.root, text='Address:', anchor=W,
                            font=('Helvetica', 14, 'bold'), fg='#1d3557', bg='#f5f6f8')
        address_lbl.place(x=40, y=270, width=150, height=30)
        self.address_entry = Entry(self.root, font=('Helvetica', 14))
        self.address_entry.place(x=200, y=270, width=350, height=30)

        # Add a button to upload a contact file
        upload_btn = Button(self.root, text='Upload Contacts', font=('Helvetica', 14, 'bold'), bg='#e9c46a',command=self.upload_contacts)
        upload_btn.place(x=40, y=330, width=150, height=40)

        add_btn = Button(self.root, text='Add Contact', font=('Helvetica', 14, 'bold'), bg='#2a9d8f', command=self.add_contact)
        add_btn.place(x=240, y=330, width=150, height=40)

        delete_btn = Button(self.root, text='Delete Contact', font=('Helvetica', 14, 'bold'), bg='#e76f51',command=self.delete_contact)
        delete_btn.place(x=450, y=330, width=150, height=40)


        # Add a listbox to show existing contacts with a scrollbar
        self.contacts_listbox = Listbox(self.root, font=('Helvetica', 14))
        self.contacts_listbox.place(x=40, y=400, width=560, height=150)
        scrollbar = Scrollbar(self.root, orient='vertical', command=self.contacts_listbox.yview)
        scrollbar.place(x=600, y=400, height=150)
        self.contacts_listbox.config(yscrollcommand=scrollbar.set)

        # Load existing contacts
        self.load_contacts()

        export_btn = Button(self.root, text='Export Contacts', font=('Helvetica', 14, 'bold'), bg='#e9c46a', command=self.export_contacts)
        export_btn.place(x=40, y=570, width=150, height=40)

        generate_btn = Button(self.root, text='Generate Directory', font=('Helvetica', 14, 'bold'), bg='#2a9d8f', command=self.generate_directory)
        generate_btn.place(x=240, y=570, width=220, height=40)

        print_btn = Button(self.root, text='Print Contacts', font=('Helvetica', 14, 'bold'), bg='#e76f51', command=self.print_contacts)
        print_btn.place(x=480, y=570, width=120, height=40)

        exit_btn = Button(self.root, text='Exit', font=('Helvetica', 14, 'bold'), bg='#1d3557', fg='white', command=self.root.destroy)
        exit_btn.place(x=600, y=20, width=30, height=30)

    def upload_contacts(self):
        # Open a file dialog to let the user select a contact file
        file_name = filedialog.askopenfilename(defaultextension='.json', filetypes=[('JSON files', '*.json')])
        if file_name:
            # Load the contacts from the selected file and fill in the contact fields as appropriate
            with open(file_name, 'r') as file:
                contacts = json.load(file)
                for name, data in contacts.items():
                    self.name_entry.insert('end', name)
                    phone = data.get('phone', '')
                    if phone:
                        self.phone_entry.insert('end', phone)
                    email = data.get('email', '')
                    if email:
                        self.email_entry.insert('end', email)
                    address = data.get('address', '')
                    if address:
                        self.address_entry.insert('end', address)

    def add_contact(self):
        # Retrieve the contact details from the entries and add them to the contacts dictionary
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()

        if name:
            # Check if phone number and email address are provided and are in correct format
            if phone and not re.match(r'^[+\d]{1,3}\s?[\d]{3,14}$', phone):
                messagebox.showwarning("Warning", "Please enter a valid phone number")
                return
            if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                messagebox.showwarning("Warning", "Please enter a valid email address")
                return

            # Add the contact to the contacts dictionary and database
            conn = sqlite3.connect('contacts.db')
            c = conn.cursor()
            c.execute("INSERT INTO contacts VALUES (?, ?, ?, ?)", (name, phone, email, address))
            conn.commit()
            conn.close()

            # Clear all the entry fields
            self.name_entry.delete(0, 'end')
            self.phone_entry.delete(0, 'end')
            self.email_entry.delete(0, 'end')
            self.address_entry.delete(0, 'end')

            # update the existing contacts in the contact list
            self.load_contacts()

            messagebox.showinfo("Success", "Contact added successfully")
        else:
            messagebox.showwarning("Warning", "Name is required. Please provide at least one phone number, email, or address.")

    def delete_contact(self):
        # Get the selected contact from the listbox and delete it from the contacts dictionary and listbox
        try:
            selected_contact = self.contacts_listbox.get(self.contacts_listbox.curselection())
            name = selected_contact.split(':')[0].strip()

            # Delete the contact from the database
            conn = sqlite3.connect('contacts.db')
            c = conn.cursor()
            c.execute("DELETE FROM contacts WHERE name=?", (name,))
            conn.commit()
            conn.close()

            self.contacts_listbox.delete(self.contacts_listbox.curselection())
            messagebox.showinfo("Success", "Contact deleted successfully")
        except:
            messagebox.showwarning("Warning", "Please select a contact before clicking delete")

    def save_contacts(self):
        # Save the contacts dictionary to a JSON file
        with open('contacts.json', 'w') as file:
            json.dump(self.contacts, file)

    def load_contacts(self):
        # Try loading the contacts from the database, or create an empty dictionary if no database is found
        try:
            conn = sqlite3.connect('contacts.db')
            c = conn.cursor()
            c.execute("SELECT * FROM contacts")
            self.contacts = {name: {'phone': phone, 'email': email, 'address': address} for name, phone, email, address in c.fetchall()}
            conn.commit()
            conn.close()
            self.contacts_listbox.delete(0, 'end')
            for name, data in sorted(self.contacts.items()):
                phone = data.get('phone', '')
                email = data.get('email', '')
                address = data.get('address', '')
                self.contacts_listbox.insert('end', f"{name}: {phone} - {email} - {address}")
        except sqlite3.OperationalError:
            self.contacts = {}

    def export_contacts(self):
        # Export the contacts to a file chosen by the user in well-formatted text format
        file_name = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files', '*.txt')])
        if file_name:
            with open(file_name, 'w') as f:
                for name, data in sorted(self.contacts.items()):
                    phone = data.get('phone', '')
                    email = data.get('email', '')
                    address = data.get('address', '')
                    f.write(f"{name}\n")
                    f.write(f"Phone: {phone}\n" if phone else "")
                    f.write(f"Email: {email}\n" if email else "")
                    f.write(f"Address: {address}\n" if address else "")
                    f.write('\n\n')
            messagebox.showinfo("Success", f"Contacts exported to {file_name} successfully")

    def generate_directory(self):
        # Save an HTML representation of the contact list that is printable
        file_name = filedialog.asksaveasfilename(defaultextension='.html', filetypes=[('HTML files', '*.html')])
        if file_name:
            directory_template = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>My Contact Directory</title>
                    <style>
                        table, th, td {{
                            border: 1px solid black;
                            border-collapse: collapse;
                            padding: 5px;
                        }}
                        h1 {{
                            font-size: 30px;
                            text-align: center;
                            color: #4a4e69;
                        }}
                    </style>
                </head>
                <body>
                    <h1>My Contact Directory</h1>
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Phone Number</th>
                                <th>Email Address</th>
                                <th>Address</th>
                            </tr>
                        </thead>
                        <tbody>
                            {}
                        </tbody>
                    </table>
                </body>
                </html>
                """

            rows = ""
            for name, data in sorted(self.contacts.items()):
                phone = data.get('phone', '')
                email = data.get('email', '')
                address = data.get('address', '')
                rows += f"<tr><td>{name}</td><td>{phone}</td><td>{email}</td><td>{address}</td></tr>"
            with open(file_name, 'w') as f:
                f.write(directory_template.format(rows))
            messagebox.showinfo("Success", f"Contact directory generated and saved to {file_name} successfully")

    def print_contacts(self):
        # Print the list of contacts to the printer
        messagebox.showwarning("Warning", "Printing is not yet supported in this version")

root = Tk()
app = ContactBookApp(root)
root.mainloop()

# Add labels and entries for contact details
    Label(root, text='Contact Name:').grid(row=0, column=0, padx=5, pady=5, sticky='w')
    self.name_entry = Entry(root)
    self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')

    Label(root, text='Phone Number:').grid(row=1, column=0, padx=5, pady=5, sticky='w')
    self.phone_entry = Entry(root)
    self.phone_entry.grid(row=1, column=1, padx=5, pady=5, sticky='we')

    Label(root, text='Email Address:').grid(row=2, column=0, padx=5, pady=5, sticky='w')
    self.email_entry = Entry(root)
    self.email_entry.grid(row=2, column=1, padx=5, pady=5, sticky='we')

    Label(root, text='Address:').grid(row=3, column=0, padx=5, pady=5, sticky='w')
    self.address_entry = Entry(root)
    self.address_entry.grid(row=3, column=1, padx=5, pady=5, sticky='we')

    # Add a button to upload a contact file
    Button(root, text='Upload Contacts', command=self.upload_contacts).grid(row=4, column=0, padx=5, pady=5, sticky='w')

    Button(root, text='Add Contact', command=self.add_contact).grid(row=4, column=1, padx=5, pady=5, sticky='we')

    # Add a listbox to show existing contacts with a scrollbar
    self.contacts_listbox = Listbox(root)
    self.contacts_listbox.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='we')
    scrollbar = (root, orient='vertical', command=self.contacts_listbox.yview)
    scrollbar.grid(row=5, column=2, sticky='nswe')
    self.contacts_listbox.config(yscrollcommand=scrollbar.set)

    # Load existing contacts
    self.load_contacts()

    Button(root, text='Export Contacts', command=self.export_contacts).grid(row=6, column=0, padx=5, pady=5, sticky='w')
    Button(root, text='Generate Directory', command=self.generate_directory).grid(row=6, column=1, padx=5, pady=5, sticky='we')
    Button(root, text='Print Contacts', command=self.print_contacts).grid(row=6, column=2, padx=5, pady=5, sticky='e')
    Button(root, text='Exit', command=root.destroy).grid(row=7, column=2, padx=5, pady=5, sticky='e')

def upload_contacts(self):
    # Open a file dialog to let the user select a contact file
    file_name = filedialog.askopenfilename(defaultextension='.json', filetypes=[('JSON files', '*.json')])
    if file_name:
        # Load the contacts from the selected file and fill in the contact fields as appropriate
        with open(file_name, 'r') as file:
            contacts = json.load(file)
            for name, data in contacts.items():
                self.name_entry.insert('end', name)
                phone = data.get('phone', '')
                if phone:
                    self.phone_entry.insert('end', phone)
                email = data.get('email', '')
                if email:
                    self.email_entry.insert('end', email)
                address = data.get('address', '')
                if address:
                    self.address_entry.insert('end', address)

def add_contact(self):
    # Retrieve the contact details from the entries and add them to the contacts dictionary
    name = self.name_entry.get()
    phone = self.phone_entry.get()
    email = self.email_entry.get()
    address = self.address_entry.get()

    if name:
        # Check if phone number and email address are provided and are in correct format
        if phone and not re.match(r'^[+\d]{1,3}\s?[\d]{3,14}$', phone):
            messagebox.showwarning("Warning", "Please enter a valid phone number")
            return
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            messagebox.showwarning("Warning", "Please enter a valid email address")
            return

        # Add the contact to the contacts dictionary and database
        conn = sqlite3.connect('contacts.db')
        c = conn.cursor()
        c.execute("INSERT INTO contacts VALUES (?, ?, ?, ?)", (name, phone, email, address))
        conn.commit()
        conn.close()

        self.contacts_listbox.insert('end', f"{name}: {phone} - {email} - {address}")
        self.clear_entries()
        messagebox.showinfo("Success", "Contact added successfully")
    else:
        messagebox.showwarning("Warning", "Name is required. Please provide at least one phone number, email, or address.")

def delete_contact(self):
    # Get the selected contact from the listbox and delete it from the contacts dictionary and listbox
    selected_contact = self.contacts_listbox.get(self.contacts_listbox.curselection())
    name = selected_contact.split(':')[0].strip()

    # Delete the contact from the database
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute("DELETE FROM contacts WHERE name=?", (name,))
    conn.commit()
    conn.close()

    self.contacts_listbox.delete(self.contacts_listbox.curselection())
    messagebox.showinfo("Success", "Contact deleted successfully")

def save_contacts(self):
    # Save the contacts dictionary to a JSON file
    with open('contacts.json', 'w') as file:
        json.dump(self.contacts, file)

def load_contacts(self):
    # Try loading the contacts from the JSON file, or create an empty dictionary if no file is found
    try:
        with open('contacts.json', 'r') as file:
            self.contacts = json.load(file)
            for name, data in self.contacts.items():
                phone = data.get('phone', '')
                email = data.get('email', '')
                address = data.get('address', '')
                self.contacts_listbox.insert('end', f"{name}: {phone} - {email} - {address}")
    except FileNotFoundError:
        self.contacts = {}

def clear_entries(self):
    # Clear all the entry fields
    self.name_entry.delete(0, 'end')
    self.phone_entry.delete(0, 'end')
    self.email_entry.delete(0, 'end')
    self.address_entry.delete(0, 'end')

def export_contacts(self):
    # Export the contacts to a file chosen by the user in well-formatted text format
    file_name = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files', '*.txt')])
    if file_name:
        with open(file_name, 'w') as f:
            for name, data in sorted(self.contacts.items()):
                phone = data.get('phone', '')
                email = data.get('email', '')
                address = data.get('address', '')
                f.write(f"{name}\n")
                f.write(f"Phone: {phone}\n" if phone else "")
                f.write(f"Email: {email}\n" if email else "")
                f.write(f"Address: {address}\n" if address else "")
                f.write('\n\n')
        messagebox.showinfo("Success", f"Contacts exported to {file_name} successfully")

def generate_directory(self):
    # Save an HTML representation of the contact list that is printable
    file_name = filedialog.asksaveasfilename(defaultextension='.html', filetypes=[('HTML files', '*.html')])
    if file_name:
        directory_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>My Contact Directory</title>
                <style>
                    table, th, td {{
                        border: 1px solid black;
                        border-collapse: collapse;
                        padding: 5px;
                    }}
                </style>
            </head>
            <body>
                <h1>My Contact Directory</h1>
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Phone Number</th>
                            <th>Email Address</th>
                            <th>Address</th>
                        </tr>
                    </thead>
                    <tbody>
                        {}
                    </tbody>
                </table>
            </body>
            </html>
            """

        rows = ""
        for name, data in sorted(self.contacts.items()):
            phone = data.get('phone', '')
            email = data.get('email', '')
            address = data.get('address', '')
            rows += f"<tr><td>{name}</td><td>{phone}</td><td>{email}</td><td>{address}</td></tr>"
        with open(file_name, 'w') as f:
            f.write(directory_template.format(rows))
        messagebox.showinfo("Success", f"Contact directory generated and saved to {file_name} successfully")

def print_contacts(self):
    # Print the list of contacts to the printer
    messagebox.showwarning("Warning", "Printing is not yet supported in this version")
root = Tk() app = ContactBookApp(root) root.mainloop()
    # Add labels and entries for contact details
    Label(root, text='Contact Name:').grid(row=0, column=0, padx=5, pady=5, sticky='w')
    self.name_entry = Entry(root)
    self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')

    Label(root, text='Phone Number:').grid(row=1, column=0, padx=5, pady=5, sticky='w')
    self.phone_entry = Entry(root)
    self.phone_entry.grid(row=1, column=1, padx=5, pady=5, sticky='we')

    Label(root, text='Email Address:').grid(row=2, column=0, padx=5, pady=5, sticky='w')
    self.email_entry = Entry(root)
    self.email_entry.grid(row=2, column=1, padx=5, pady=5, sticky='we')

    Label(root, text='Address:').grid(row=3, column=0, padx=5, pady=5, sticky='w')
    self.address_entry = Entry(root)
    self.address_entry.grid(row=3, column=1, padx=5, pady=5, sticky='we')

    # Add a button to upload a contact file
    Button(root, text='Upload Contacts', command=self.upload_contacts).grid(row=4, column=0, padx=5, pady=5, sticky='w')

    Button(root, text='Add Contact', command=self.add_contact).grid(row=4, column=1, padx=5, pady=5, sticky='we')

    # Add a listbox to show existing contacts with a scrollbar
    self.contacts_listbox = Listbox(root)
    self.contacts_listbox.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='we')
    scrollbar = (root, orient='vertical', command=self.contacts_listbox.yview)
    scrollbar.grid(row=5, column=2, sticky='nswe')
    self.contacts_listbox.config(yscrollcommand=scrollbar.set)

    # Load existing contacts
    self.load_contacts()

    Button(root, text='Export Contacts', command=self.export_contacts).grid(row=6, column=0, padx=5, pady=5, sticky='w')
    Button(root, text='Generate Directory', command=self.generate_directory).grid(row=6, column=1, padx=5, pady=5, sticky='we')
    Button(root, text='Print Contacts', command=self.print_contacts).grid(row=6, column=2, padx=5, pady=5, sticky='e')
    Button(root, text='Exit', command=root.destroy).grid(row=7, column=2, padx=5, pady=5, sticky='e')

def upload_contacts(self):
    # Open a file dialog to let the user select a contact file
    file_name = filedialog.askopenfilename(defaultextension='.json', filetypes=[('JSON files', '*.json')])
    if file_name:
        # Load the contacts from the selected file and fill in the contact fields as appropriate
        with open(file_name, 'r') as file:
            contacts = json.load(file)
            for name, data in contacts.items():
                self.name_entry.insert('end', name)
                phone = data.get('phone', '')
                if phone:
                    self.phone_entry.insert('end', phone)
                email = data.get('email', '')
                if email:
                    self.email_entry.insert('end', email)
                address = data.get('address', '')
                if address:
                    self.address_entry.insert('end', address)

def add_contact(self):
    # Retrieve the contact details from the entries and add them to the contacts dictionary
    name = self.name_entry.get()
    phone = self.phone_entry.get()
    email = self.email_entry.get()
    address = self.address_entry.get()

    if name:
        # Check if phone number and email address are provided and are in correct format
        if phone and not re.match(r'^[+\d]{1,3}\s?[\d]{3,14}$', phone):
            messagebox.showwarning("Warning", "Please enter a valid phone number")
            return
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            messagebox.showwarning("Warning", "Please enter a valid email address")
            return

        # Add the contact to the contacts dictionary and database
        conn = sqlite3.connect('contacts.db')
        c = conn.cursor()
        c.execute("INSERT INTO contacts VALUES (?, ?, ?, ?)", (name, phone, email, address))
        conn.commit()
        conn.close()

        self.contacts_listbox.insert('end', f"{name}: {phone} - {email} - {address}")
        self.clear_entries()
        messagebox.showinfo("Success", "Contact added successfully")
    else:
        messagebox.showwarning("Warning", "Name is required. Please provide at least one phone number, email, or address.")

def delete_contact(self):
    # Get the selected contact from the listbox and delete it from the contacts dictionary and listbox
    selected_contact = self.contacts_listbox.get(self.contacts_listbox.curselection())
    name = selected_contact.split(':')[0].strip()

    # Delete the contact from the database
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute("DELETE FROM contacts WHERE name=?", (name,))
    conn.commit()
    conn.close()

    self.contacts_listbox.delete(self.contacts_listbox.curselection())
    messagebox.showinfo("Success", "Contact deleted successfully")

def save_contacts(self):
    # Save the contacts dictionary to a JSON file
    with open('contacts.json', 'w') as file:
        json.dump(self.contacts, file)

def load_contacts(self):
    # Try loading the contacts from the JSON file, or create an empty dictionary if no file is found
    try:
        with open('contacts.json', 'r') as file:
            self.contacts = json.load(file)
            for name, data in self.contacts.items():
                phone = data.get('phone', '')
                email = data.get('email', '')
                address = data.get('address', '')
                self.contacts_listbox.insert('end', f"{name}: {phone} - {email} - {address}")
    except FileNotFoundError:
        self.contacts = {}

def clear_entries(self):
    # Clear all the entry fields
    self.name_entry.delete(0, 'end')
    self.phone_entry.delete(0, 'end')
    self.email_entry.delete(0, 'end')
    self.address_entry.delete(0, 'end')

def export_contacts(self):
    # Export the contacts to a file chosen by the user in well-formatted text format
    file_name = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files', '*.txt')])
    if file_name:
        with open(file_name, 'w') as f:
            for name, data in sorted(self.contacts.items()):
                phone = data.get('phone', '')
                email = data.get('email', '')
                address = data.get('address', '')
                f.write(f"{name}\n")
                f.write(f"Phone: {phone}\n" if phone else "")
                f.write(f"Email: {email}\n" if email else "")
                f.write(f"Address: {address}\n" if address else "")
                f.write('\n\n')
        messagebox.showinfo("Success", f"Contacts exported to {file_name} successfully")

def generate_directory(self):
    # Save an HTML representation of the contact list that is printable
    file_name = filedialog.asksaveasfilename(defaultextension='.html', filetypes=[('HTML files', '*.html')])
    if file_name:
        directory_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>My Contact Directory</title>
                <style>
                    table, th, td {{
                        border: 1px solid black;
                        border-collapse: collapse;
                        padding: 5px;
                    }}
                </style>
            </head>
            <body>
                <h1>My Contact Directory</h1>
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Phone Number</th>
                            <th>Email Address</th>
                            <th>Address</th>
                        </tr>
                    </thead>
                    <tbody>
                        {}
                    </tbody>
                </table>
            </body>
            </html>
            """

        rows = ""
        for name, data in sorted(self.contacts.items()):
            phone = data.get('phone', '')
            email = data.get('email', '')
            address = data.get('address', '')
            rows += f"<tr><td>{name}</td><td>{phone}</td><td>{email}</td><td>{address}</td></tr>"
        with open(file_name, 'w') as f:
            f.write(directory_template.format(rows))
        messagebox.showinfo("Success", f"Contact directory generated and saved to {file_name} successfully")

def print_contacts(self):
    # Print the list of contacts to the printer
    messagebox.showwarning("Warning", "Printing is not yet supported in this version")