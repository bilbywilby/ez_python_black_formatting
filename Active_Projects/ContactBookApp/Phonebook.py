from tkinter import *
from tkinter import messagebox, filedialog
import json
import re
import sqlite3
import os

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

            # Add the contact to the database
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
        # Get the selected contact from the listbox and delete it from the database and listbox
        selected_contacts = self.contacts_listbox.curselection()
        if len(selected_contacts) == 0:
            messagebox.showwarning("Warning", "Please select a contact before clicking delete")
            return
        for i in selected_contacts:
            selected_contact_str = self.contacts_listbox.get(i)
            name = selected_contact_str.split(':')[0].strip()

            # Confirm the deletion with the user
            if messagebox.askokcancel("Delete Contact", f"Are you sure you want to delete {name}?"):
                # Delete the contact from the database
                conn = sqlite3.connect('contacts.db')
                c = conn.cursor()
                c.execute("DELETE FROM contacts WHERE name=?", (name,))
                conn.commit()
                conn.close()

                self.contacts_listbox.delete(i)

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
        # Print the current list of contacts to the default printer
        contact_list = ""
        for name, data in sorted(self.contacts.items()):
            phone = data.get('phone', '')
            email = data.get('email', '')
            address = data.get('address', '')
            contact_list += f"{name}: {phone} - {email} - {address}\n"
        root = Tk()
        root.withdraw()
        response = messagebox.askyesno(title="Print Contacts", message="Do you want to print all contacts?")
        if response == 'yes':
            os.system(f"echo '{contact_list}' | lpr -P <your printer name>")
        root.destroy()

    def open_phonebook(self):
        # Prompt the user to select a phonebook file and open it in the application
        file_name = filedialog.askopenfilename(defaultextension='.db', filetypes=[('Database files', '*.db')])
        if file_name:
            # Rename current database and copy user-selected database in its place
            current_db_file_name = 'contacts.db'
            try:
                os.rename(current_db_file_name, 'contacts_backup.db')
                os.rename(file_name, current_db_file_name)
            except:
                messagebox.showerror("Error", "Unable to open phonebook. Please ensure the selected file is a valid phonebook.")
                os.rename('contacts_backup.db', current_db_file_name)
                return
            # Reset UI and load contacts
            self.contacts_listbox.delete(0, 'end')
            self.load_contacts()

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    root = Tk()
    app = ContactBookApp(root)
    app.open_phonebook()
    app.run()