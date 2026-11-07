# Enhanced Python script for a personal library database

import csv
import os
from apscheduler.schedulers.background import BackgroundScheduler
import uuid
import time
from collections import Counter
import matplotlib.pyplot as plt
import datetime
import shutil
from isbnlib.registry import bibformatters
from isbnlib import meta
from tkinter import ttk
import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
from isbnlib import meta, cover
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Connect to the SQLite database
conn = sqlite3.connect('my_library.db')
cursor = conn.cursor()

# Create a table for the library items if it doesn't exist
cursor.execute(
    CREATE TABLE IF NOT EXISTS library_items(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author_artist TEXT,
        type TEXT NOT NULL,
        isbn TEXT UNIQUE,
        publisher TEXT,
        year INTEGER,
        pages INTEGER,
        genre TEXT,
        format TEXT,
        status TEXT NOT NULL,
        cover_art BLOB
    )
)

# Function to fetch metadata using isbnlib


def fetch_metadata(isbn):
    return meta(isbn, service='goob')

# Function to fetch cover image using isbnlib


def fetch_cover_image(isbn):
    url = cover(isbn)
    if url:
        response = requests.get(url)
        return BytesIO(response.content)
    return None

# Function to add or update a book in the library using ISBN


def add_or_update_book(isbn):
    try:
        book_data = fetch_metadata(isbn)
        cover_image = fetch_cover_image(isbn)
        cursor.execute(
            INSERT OR REPLACE INTO library_items(isbn, title, author_artist, year, publisher, pages, genre, format, cover_art)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?), (
                isbn,
                book_data.get('Title'),
                ', '.join(book_data.get('Authors')),
                book_data.get('Year'),
                book_data.get('Publisher'),
                book_data.get('Pages'),
                ', '.join(book_data.get('Subjects', [])),
                book_data.get('Format'),
                cover_image.read() if cover_image else None
            ))
        conn.commit()
        messagebox.showinfo("Success", "Book added/updated successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# GUI setup
root = Tk()
root.title("Library Management System")

# ISBN entry
isbn_label = Label(root, text="Enter ISBN:")
isbn_label.pack()
isbn_entry = Entry(root)
isbn_entry.pack()

# Add/update button
add_button = Button(root, text="Add/Update Book",
                    command=lambda: add_or_update_book(isbn_entry.get()))
add_button.pack()

# Function to refresh the library display


def refresh_library_display():
    for i in tree.get_children():
        tree.delete(i)
    cursor.execute(
        'SELECT id, title, author_artist, year, genre, status FROM library_items')
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)


# Treeview setup
columns = ('ID', 'Title', 'Author/Artist', 'Year', 'Genre', 'Status')
tree = ttk.Treeview(root, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)
tree.pack()

# Refresh button
refresh_button = Button(root, text="Refresh Library",
                        command=refresh_library_display)
refresh_button.pack()

# Initial refresh
refresh_library_display()

# Run the application
root.mainloop()

# Don't forget to close the connection when done
conn.close()
# Pagination for Treeview


class Pagination:
    def __init__(self, tree, rows_per_page=10):
        self.tree = tree
        self.rows_per_page = rows_per_page
        self.current_page = 1
        self.total_pages = 1
        self.update_pagination()

    def update_pagination(self):
        total_items = len(self.tree.get_children())
        self.total_pages = int((total_items - 1) / self.rows_per_page) + 1
        self.show_page(self.current_page)

    def show_page(self, page):
        if 1 <= page <= self.total_pages:
            self.current_page = page
            start_index = (page - 1) * self.rows_per_page
            end_index = start_index + self.rows_per_page
            for index, item in enumerate(self.tree.get_children()):
                self.tree.item(item, tags=('hidden',))
                if start_index <= index < end_index:
                    self.tree.item(item, tags=('visible',))
            self.tree.tag_configure(
                'hidden', foreground='white', background='white')
            self.tree.tag_configure(
                'visible', foreground='black', background='white')

    def go_to_next_page(self):
        if self.current_page < self.total_pages:
            self.show_page(self.current_page + 1)

    def go_to_previous_page(self):
        if self.current_page > 1:
            self.show_page(self.current_page - 1)


# Add pagination to the Treeview
pagination = Pagination(tree)

# Navigation buttons for pagination
prev_button = Button(root, text="Previous",
                     command=pagination.go_to_previous_page)
prev_button.pack(side=LEFT)
next_button = Button(root, text="Next", command=pagination.go_to_next_page)
next_button.pack(side=RIGHT)

# Advanced filtering options
filter_frame = Frame(root)
filter_frame.pack(side=TOP, fill=BOTH, expand=True)

Label(filter_frame, text="Filter by genre:").pack(side=LEFT)
genre_var = StringVar()
genre_options = ttk.Combobox(filter_frame, textvariable=genre_var)
genre_options['values'] = ['All'] + \
    list(set([item[8] for item in list_items()]))
genre_options.pack(side=LEFT)
genre_options.bind('<<ComboboxSelected>>',
                   lambda event: refresh_library_display())

# Function to refresh the library display with filters


def refresh_library_display(search_query=''):
    for i in tree.get_children():
        tree.delete(i)
    search_genre = genre_var.get()
    cursor.execute('SELECT id, title, author_artist, year, genre, status FROM library_items WHERE title LIKE ? AND (genre=? OR ?="All")',
                   ('%'+search_query+'%', search_genre, search_genre))
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)
    update_item_colors()
    pagination.update_pagination()


# Initial refresh with filters
refresh_library_display()

# Run the application
root.mainloop()

# Don't forget to close the connection when done
conn.close()
# Function to update the treeview item colors based on status


def update_item_colors():
    for item in tree.get_children():
        status = tree.set(item, 'Status')
        if status == 'available':
            tree.item(item, tags=('available',))
        elif status == 'borrowed':
            tree.item(item, tags=('borrowed',))


tree.tag_configure('available', background='green')
tree.tag_configure('borrowed', background='red')
# Function to sort by column


def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    # Rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # Reverse sort next time
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))


for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(
        tree, _col, False))
# Search bar event


def on_search(event):
    search_query = search_var.get()
    refresh_library_display(search_query)


search_var = StringVar()
search_var.trace('w', on_search)
search_entry = Entry(root, textvariable=search_var)
search_entry.pack()
# Function to view book details including cover image


def view_book_details(item_id):
    cursor.execute('SELECT * FROM library_items WHERE id=?', (item_id,))
    book = cursor.fetchone()
    if book:
        top = Toplevel()
        top.title(f"Details for {book[1]}")

        # Book details
        details_frame = Frame(top)
        details_frame.pack(side=TOP, fill=BOTH, expand=True)

        Label(details_frame, text="Title:").grid(row=0, column=0, sticky=W)
        Label(details_frame, text=book[1]).grid(row=0, column=1, sticky=W)

        Label(details_frame, text="Author/Artist:").grid(row=1, column=0, sticky=W)
        Label(details_frame, text=book[2]).grid(row=1, column=1, sticky=W)

        Label(details_frame, text="Year:").grid(row=2, column=0, sticky=W)
        Label(details_frame, text=book[5]).grid(row=2, column=1, sticky=W)

        Label(details_frame, text="Genre:").grid(row=3, column=0, sticky=W)
        Label(details_frame, text=book[8]).grid(row=3, column=1, sticky=W)

        Label(details_frame, text="Format:").grid(row=4, column=0, sticky=W)
        Label(details_frame, text=book[9]).grid(row=4, column=1, sticky=W)

        Label(details_frame, text="Status:").grid(row=5, column=0, sticky=W)
        Label(details_frame, text=book[10]).grid(row=5, column=1, sticky=W)

        # Cover image
        if book[11]:
            cover_image = Image.open(BytesIO(book[11]))
            cover_photo = ImageTk.PhotoImage(cover_image)
            cover_label = Label(top, image=cover_photo)
            cover_label.image = cover_photo  # Keep a reference!
            cover_label.pack(side=BOTTOM, fill=BOTH, expand=True)

# Bind double-click event to view book details


def on_item_double_click(event):
    selected_item = tree.selection()[0]
    item_id = tree.item(selected_item, 'values')[0]
    view_book_details(item_id)


tree.bind('<Double-1>', on_item_double_click)

# Run the application
root.mainloop()

# Don't forget to close the connection when done
conn.close()

# Connect to the SQLite database
conn = sqlite3.connect('my_library.db')
cursor = conn.cursor()

# Create a table for the library items if it doesn't exist
cursor.execute(
    CREATE TABLE IF NOT EXISTS library_items(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author_artist TEXT,
        type TEXT NOT NULL,
        isbn TEXT UNIQUE,
        publisher TEXT,
        year INTEGER,
        pages INTEGER,
        genre TEXT,
        format TEXT,
        status TEXT NOT NULL,
        cover_art BLOB
    )
)

# Function to fetch metadata using isbnlib


def fetch_metadata(isbn):
    return meta(isbn, service='goob')

# Function to fetch cover image using isbnlib


def fetch_cover_image(isbn):
    url = cover(isbn)
    if url:
        response = requests.get(url)
        return BytesIO(response.content)
    return None

# Function to add or update a book in the library using ISBN


def add_or_update_book(isbn):
    book_data = fetch_metadata(isbn)
    cover_image = fetch_cover_image(isbn)
    cursor.execute(
        INSERT OR REPLACE INTO library_items(isbn, title, author_artist, year, publisher, pages, genre, format, cover_art)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?), (
            isbn,
            book_data.get('Title'),
            ', '.join(book_data.get('Authors')),
            book_data.get('Year'),
            book_data.get('Publisher'),
            book_data.get('Pages'),
            ', '.join(book_data.get('Subjects', [])),
            book_data.get('Format'),
            cover_image.read() if cover_image else None
        ))
    conn.commit()


# GUI setup
root = Tk()
root.title("Library Management System")

# ISBN entry
isbn_label = Label(root, text="Enter ISBN:")
isbn_label.pack()
isbn_entry = Entry(root)
isbn_entry.pack()

# Add/update button
add_button = Button(root, text="Add/Update Book",
                    command=lambda: add_or_update_book(isbn_entry.get()))
add_button.pack()

# Function to refresh the library display


def refresh_library_display():
    for i in tree.get_children():
        tree.delete(i)
    cursor.execute(
        'SELECT id, title, author_artist, year, genre, status FROM library_items')
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)


# Treeview setup
columns = ('ID', 'Title', 'Author/Artist', 'Year', 'Genre', 'Status')
tree = ttk.Treeview(root, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)
tree.pack()

# Refresh button
refresh_button = Button(root, text="Refresh Library",
                        command=refresh_library_display)
refresh_button.pack()

# Initial refresh
refresh_library_display()

# Run the application
root.mainloop()

# Don't forget to close the connection when done
conn.close()

# Connect to the SQLite database
conn = sqlite3.connect('my_library.db')
cursor = conn.cursor()

# Function to fetch metadata using isbnlib


def fetch_metadata(isbn):
    # Use 'goob' for Google Books, or 'openl' for Open Library
    return meta(isbn, service='goob')

# Function to add or update a book in the library using ISBN


def add_or_update_book(isbn):
    book_data = fetch_metadata(isbn)
    cursor.execute(
        INSERT OR REPLACE INTO library_items(isbn, title, author_artist, year, publisher, pages, genre, format)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?), (
            isbn,
            book_data.get('Title'),
            ', '.join(book_data.get('Authors')),
            book_data.get('Year'),
            book_data.get('Publisher'),
            book_data.get('Pages'),
            ', '.join(book_data.get('Subjects', [])),
            book_data.get('Format')
        ))
    conn.commit()


# Example usage
isbn_input = input("Enter ISBN number: ")
add_or_update_book(isbn_input)

# Don't forget to close the connection when done
conn.close()
# User Authentication


def login(username, password):
    # This function should verify the username and password
    # For demonstration purposes, we'll assume the user is authenticated
    return True


# Login form
login_frame = Frame(root)
login_frame.pack(side=TOP, fill=BOTH, expand=True)

Label(login_frame, text="Username:").pack(side=LEFT)
username_entry = Entry(login_frame)
username_entry.pack(side=LEFT)

Label(login_frame, text="Password:").pack(side=LEFT)
password_entry = Entry(login_frame, show="*")
password_entry.pack(side=LEFT)

login_button = Button(login_frame, text="Login", command=lambda: login(
    username_entry.get(), password_entry.get()))
login_button.pack(side=LEFT)
# Real-time Search Functionality


def on_search_key_release(event):
    search_query = search_entry.get()
    refresh_library_display(search_query)


search_entry.bind('<KeyRelease>', on_search_key_release)
# Edit Book Details Functionality


def edit_book_details(book_id, new_title, new_author, new_year, new_genre):
    cursor.execute(
        UPDATE library_items
        SET title=?, author_artist=?, year=?, genre=?
        WHERE id=?, (new_title, new_author, new_year, new_genre, book_id))
    conn.commit()


# Edit book details form
edit_frame = Frame(root)
edit_frame.pack(side=TOP, fill=BOTH, expand=True)

# Add entry widgets and a button for editing book details
# Similar to the lend and return book forms


def autocomplete(entries):
    def on_keyrelease(event):
        # get text from entry
        value = event.widget.get().strip().lower()
        if value == '':
            data = entries
        else:
            data = []
            for item in entries:
                if value in item.lower():
                    data.append(item)

        # update data in listbox
        update_listbox(data)

    def update_listbox(data):
        # delete previous data
        listbox.delete(0, 'end')

        # sorting data
        data = sorted(data, key=str.lower)

        # put new data
        for item in data:
            listbox.insert('end', item)

    def on_select(event):
        # display element selected on list
        print('(event) previous:', event.widget.get('active'))
        print('(event)  current:', event.widget.get(
            event.widget.curselection()))
        print('---')

    # --- main ---

    entries = ('apple', 'orange', 'banana', 'berry', 'melon')

    root = Tk()

    entry = Entry(root)
    entry.pack()
    entry.bind('<KeyRelease>', on_keyrelease)

    listbox = Listbox(root)
    listbox.pack()
    listbox.bind('<<ListboxSelect>>', on_select)

    update_listbox(entries)

    root.mainloop()


def backup_database(source, destination):
    # Create a backup of the database
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    backup_path = os.path.join(destination, f"backup_{today}.db")
    shutil.copy2(source, backup_path)
    print(f"Database backed up to {backup_path}")


# Example usage
backup_database('my_library.db', '/path/to/backup/directory')


def plot_genre_distribution(cursor):
    # Fetch genre data from the database
    cursor.execute('SELECT genre FROM library_items')
    genres = [row[0] for row in cursor.fetchall()]

    # Count the occurrences of each genre
    genre_counts = Counter(genres)

    # Plotting
    plt.bar(genre_counts.keys(), genre_counts.values())
    plt.xlabel('Genre')
    plt.ylabel('Number of Books')
    plt.title('Genre Distribution in Library')
    plt.show()


# Example usage (assuming 'cursor' is your database cursor)
plot_genre_distribution(cursor)


def refresh_table_data(tree, cursor, search_query=''):
    # Clear the treeview
    for i in tree.get_children():
        tree.delete(i)

    # Fetch new data based on the search query
    cursor.execute(
        'SELECT id, title, author_artist, year, genre, status FROM library_items WHERE title LIKE ?', ('%'+search_query+'%',))

    # Insert new data into the treeview
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)


# Example usage (assuming 'tree' is your Treeview widget and 'cursor' is your database cursor)
refresh_table_data(tree, cursor, 'search term')


def migrate_schema(cursor, version):
    # Perform database schema migrations based on the version
    if version == 1:
        # Add a new column to the table
        cursor.execute('ALTER TABLE library_items ADD COLUMN location TEXT')
        print("Migrated to schema version 1: Added 'location' column.")
    elif version == 2:
        # Modify an existing column
        cursor.execute(
            'ALTER TABLE library_items RENAME COLUMN author_artist TO author')
        print("Migrated to schema version 2: Renamed 'author_artist' column to 'author'.")
    # ... add more schema changes as needed
    conn.commit()


# Example usage (assuming 'cursor' is your database cursor)
migrate_schema(cursor, 1)
# Function to update book data in the database


def update_book_data(book_id, title, author, year, genre):
    cursor.execute(
        UPDATE library_items
        SET title=?, author=?, year=?, genre=?
        WHERE id=?, (title, author, year, genre, book_id))
    conn.commit()


# Function to visualize the number of books per genre


def visualize_books_per_genre():
    cursor.execute('SELECT genre, COUNT(*) FROM library_items GROUP BY genre')
    data = cursor.fetchall()
    genres = [row[0] for row in data]
    counts = [row[1] for row in data]

    plt.bar(genres, counts)
    plt.xlabel('Genre')
    plt.ylabel('Number of Books')
    plt.title('Number of Books per Genre')
    plt.show()
# Function to remove all books that have not been checked out and are older than a certain year


def cleanup_old_books(year_threshold):
    cursor.execute(
        DELETE FROM library_items
        WHERE year < ? AND times_checked_out=0, (year_threshold,))
    conn.commit()
# Function to perform an advanced search based on multiple criteria


def advanced_search(title=None, author=None, year=None):
    query = 'SELECT * FROM library_items WHERE 1=1'
    params = []

    if title:
        query += ' AND title LIKE ?'
        params.append(f'%{title}%')
    if author:
        query += ' AND author LIKE ?'
        params.append(f'%{author}%')
    if year:
        query += ' AND year = ?'
        params.append(year)

    cursor.execute(query, params)
    return cursor.fetchall()


# Function to create a backup of the database


def backup_database(database_path, backup_folder):
    timestamp = time.strftime('%Y%m%d-%H%M%S')
    backup_path = os.path.join(
        backup_folder, f'database_backup_{timestamp}.db')
    os.system(f'cp {database_path} {backup_path}')


# Function to export library data to a CSV file


def export_to_csv(cursor, file_path):
    cursor.execute('SELECT * FROM library_items')
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(columns)
        csvwriter.writerows(rows)


# Example usage
export_to_csv(cursor, 'library_data.csv')
# Function to import data from a CSV file into the library database


def import_from_csv(cursor, file_path):
    with open(file_path, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            cursor.execute(
                INSERT INTO library_items(title, author, year, genre, status)
                VALUES(?, ?, ?, ?, ?), (row['title'], row['author'], row['year'], row['genre'], row['status']))
        conn.commit()


# Example usage
import_from_csv(cursor, 'library_data.csv')
# Function to create an interactive search entry that updates the listbox in real-time


def create_search_entry(root, listbox, search_data):
    def on_search(event):
        query = search_var.get().lower()
        filtered_data = [item for item in search_data if query in item.lower()]
        update_listbox(filtered_data)

    def update_listbox(data):
        listbox.delete(0, END)
        for item in data:
            listbox.insert(END, item)

    search_var = StringVar()
    search_entry = Entry(root, textvariable=search_var)
    search_entry.pack()
    search_entry.bind('<KeyRelease>', on_search)


# Example usage
create_search_entry(
    root, listbox, ['Book Title 1', 'Book Title 2', 'Book Title 3'])
# Function to check the integrity of the database and repair if necessary


def check_and_repair_database(cursor):
    cursor.execute('PRAGMA integrity_check')
    result = cursor.fetchone()
    if result[0] == 'ok':
        print('Database integrity check passed.')
    else:
        print('Database integrity check failed. Repairing...')
        cursor.execute('REINDEX')
        cursor.execute('VACUUM')
        conn.commit()


# Example usage
check_and_repair_database(cursor)
# Function to save user preferences to the database


def save_user_preferences(cursor, user_id, preferences):
    cursor.execute(
        INSERT OR REPLACE INTO user_preferences(user_id, preferences)
        VALUES(?, ?), (user_id, json.dumps(preferences)))
    conn.commit()

# Function to load user preferences from the database


def load_user_preferences(cursor, user_id):
    cursor.execute(
        'SELECT preferences FROM user_preferences WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    return json.loads(result[0]) if result else {}


# Example usage
save_user_preferences(cursor, 1, {'theme': 'dark', 'font_size': 12})
# Function to add a new item to the library database
preferences = load_user_preference


def add_new_item(cursor, item_type, title, author, year, genre, format):
    cursor.execute(
        INSERT INTO library_items(type, title, author, year, genre, format)
        VALUES(?, ?, ?, ?, ?, ?), (item_type, title, author, year, genre, format))
    conn.commit()
# Function to add multiple new items to the library database in bulk


def add_items_in_bulk(cursor, items):
    cursor.executemany(
        INSERT INTO library_items(type, title, author, year, genre, format)
        VALUES(?, ?, ?, ?, ?, ?), items)
    conn.commit()


# Example usage
items_to_add = [
    ('book', '1984', 'George Orwell', 1949, 'Dystopian', 'Hardcover'),
    ('dvd', 'Inception', 'Christopher Nolan', 2010, 'Science Fiction', 'Blu-ray'),
    # Add more items as needed
]
add_items_in_bulk(cursor, items_to_add)
# Function to create an interactive form for adding new items


def create_add_item_form(root, cursor):
    def on_submit():
        item_type = type_var.get()
        title = title_entry.get()
        author = author_entry.get()
        year = year_entry.get()
        genre = genre_entry.get()
        format = format_entry.get()
        add_new_item(cursor, item_type, title, author, year, genre, format)

    type_var = StringVar()
    type_options = ttk.Combobox(
        root, textvariable=type_var, values=['book', 'dvd', 'cd'])
    type_options.pack()

    title_entry = Entry(root)
    title_entry.pack()

    author_entry = Entry(root)
    author_entry.pack()

    year_entry = Entry(root)
    year_entry.pack()

    genre_entry = Entry(root)
    genre_entry.pack()

    format_entry = Entry(root)
    format_entry.pack()

    submit_button = Button(root, text="Add Item", command=on_submit)
    submit_button.pack()


# Example usage
create_add_item_form(root, cursor)

# Function to generate a unique ID for each new item


def generate_unique_id():
    return str(uuid.uuid4())


# Example usage
new_item_id = generate_unique_id()
# Function to check for duplicate items before adding to the database


def check_for_duplicates(cursor, title, author):
    cursor.execute(
        SELECT * FROM library_items WHERE title=? AND author=?, (title, author))
    return cursor.fetchone() is not None


# Example usage
if not check_for_duplicates(cursor, '1984', 'George Orwell'):
    add_new_item(cursor, 'book', '1984', 'George Orwell',
                 1949, 'Dystopian', 'Hardcover')
else:
    print("Item already exists in the database.")

# Function to perform a database backup


def scheduled_backup(database_path, backup_folder):
    timestamp = time.strftime('%Y%m%d-%H%M%S')
    backup_path = os.path.join(
        backup_folder, f'database_backup_{timestamp}.db')
    os.system(f'cp {database_path} {backup_path}')


# Setting up the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_backup, 'interval', days=1, args=[
                  'path_to_database', 'path_to_backup_folder'])
scheduler.start()

# Remember to shut down the scheduler when exiting the app
scheduler.shutdown()
