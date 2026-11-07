import sqlite3

# Connect to the SQLite database or create it if it doesn't exist
try:
    conn = sqlite3.connect('my_library.db')
except sqlite3.Error as e:
    print(f"Error connecting to database: {e}")
    exit()
cursor = conn.cursor()

# Create a table for the library items if it doesn't exist
cursor.execute(
    CREATE TABLE IF NOT EXISTS library_items(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author_artist TEXT,
        type TEXT NOT NULL,  -- 'book', 'media', etc.
        isbn TEXT,
        publisher TEXT,
        year INTEGER,
        pages INTEGER,
        genre TEXT,
        format TEXT,  -- 'hardcover', 'paperback', 'digital', etc.
        status TEXT NOT NULL,  -- 'available', 'borrowed', etc.
        borrower TEXT,
        due_date TEXT,
        cover_art BLOB - - Store cover art as binary data
    )
)

# Function to add a new item to the library


def add_item():
    title = input("Enter title: ")
    author_artist = input("Enter author/artist: ")
    item_type = input("Enter type (book, media, etc.): ")
    isbn = input("Enter ISBN: ")
    publisher = input("Enter publisher: ")
    year = input("Enter year: ")
    pages = input("Enter number of pages: ")
    genre = input("Enter genre: ")
    format = input("Enter format: ")
    # Prompt user for cover art (optional)
    cover_art = None
    cover_art_input = input("Add cover art? (y/n) ")
    if cover_art_input.lower() == 'y':
        cover_art = input("Enter path to cover art file: ")
        with open(cover_art, 'rb') as f:
            cover_art = f.read()
    status = 'available'
    add_status = input("Add status? (y/n) ")
    if add_status.lower() == 'y':
        status = input("Enter status (available, borrowed, etc.): ")
    cursor.execute(
        INSERT INTO library_items(title, author_artist, type, isbn, publisher, year, pages, genre, format, cover_art, status)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?), (title, author_artist, item_type, isbn, publisher, year, pages, genre, format, cover_art, status))
    print("Item was added successfully.")
    conn.commit()

# Function to update the status and borrower of an item


def update_item_status():
    item_id = input("Enter item ID: ")
    new_status = input("Enter new status: ")
    borrower = None
    due_date = None
    update_borrower = input("Add borrower? (y/n) ")
    if update_borrower.lower() == 'y':
        borrower = input("Enter borrower name: ")
        due_date = input("Enter due date (YYYY-MM-DD): ")
    cursor.execute(
        UPDATE library_items
        SET status=?, borrower=?, due_date=?
        WHERE id=?, (new_status, borrower, due_date, item_id))
    print("Item status was updated successfully.")
    conn.commit()

# Function to search for items by various criteria


def search_items():
    title = input("Enter title: ")
    author_artist = input("Enter author/artist: ")
    genre = input("Enter genre: ")
    year = input("Enter year: ")
    cursor.execute(
        SELECT * FROM library_items
        WHERE title LIKE ?
        AND author_artist LIKE ?
        AND genre LIKE ?
        AND year LIKE ?, ('%'+title+'%', '%'+author_artist+'%', '%'+genre+'%', '%'+year+'%'))
    results = cursor.fetchall()
    print("{} results found:".format(len(results)))
    for item in results:
        print(
            "ID: {}\tTitle: {}\tAuthor/Artist: {}".format(item[0], item[1], item[2]))

# Function to suggest similar items based on genre


def suggest_similar_items():
    current_genre = input("Enter current item genre: ")
    cursor.execute(
        'SELECT * FROM library_items WHERE genre = ?', (current_genre,))
    results = cursor.fetchall()
    print("{} similar items found:".format(len(results)))
    for item in results:
        print(
            "ID: {}\tTitle: {}\tAuthor/Artist: {}".format(item[0], item[1], item[2]))

# Menu system to allow the user to select different functions


def main_menu():
    while True:
        print("Options:")
        print("1. Add item")
        print("2. Update item status")
        print("3. Search items")
        print("4. Find similar items")
        print("5. Exit")
        try:
            choice = int(input("Enter choice: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        if choice == 1:
            add_item()
        elif choice == 2:
            update_item_status()
        elif choice == 3:
            search_items()
        elif choice == 4:
            suggest_similar_items()
        elif choice == 5:
            print("Exiting...")
            break
        else:
            print("Invalid choice.")


# Run the main menu function
main_menu()

# Don't forget to close the connection when done
conn.close()


# Connect to the SQLite database or create it if it doesn't exist
conn = sqlite3.connect('my_library.db')
cursor = conn.cursor()

# Create a table for the library items if it doesn't exist
cursor.execute(
    CREATE TABLE IF NOT EXISTS library_items(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author_artist TEXT,
        type TEXT NOT NULL,  # 'book', 'media', etc.
        isbn TEXT,
        publisher TEXT,
        year INTEGER,
        pages INTEGER,
        genre TEXT,
        format TEXT,  # 'hardcover', 'paperback', 'digital', etc.
        status TEXT NOT NULL,  # 'available', 'borrowed', etc.
        borrower TEXT,
        due_date TEXT,
        cover_art BLOB  # Store cover art as binary data
    )
)

# Function to add a new item to the library


def add_item(title, author_artist, item_type, isbn, publisher, year, pages, genre, format, cover_art=None, status='available'):
    cursor.execute(
        INSERT INTO library_items(title, author_artist, type, isbn, publisher, year, pages, genre, format, cover_art, status)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?), (title, author_artist, item_type, isbn, publisher, year, pages, genre, format, cover_art, status))
    conn.commit()

# Function to update the status and borrower of an item


def update_item_status(item_id, new_status, borrower=None, due_date=None):
    cursor.execute(
        UPDATE library_items
        SET status=?, borrower=?, due_date=?
        WHERE id=?, (new_status, borrower, due_date, item_id))
    conn.commit()

# Function to search for an item by various criteria


def search_items(title='', author_artist='', genre='', year=''):
    cursor.execute(
        SELECT * FROM library_items
        WHERE title LIKE ?
        AND author_artist LIKE ?
        AND genre LIKE ?
        AND year LIKE ?, ('%'+title+'%', '%'+author_artist+'%', '%'+genre+'%', '%'+year+'%'))
    return cursor.fetchall()

# Function to suggest similar items based on genre


def suggest_similar_items(current_genre):
    cursor.execute(
        'SELECT * FROM library_items WHERE genre = ?', (current_genre,))
    return cursor.fetchall()


# Example usage
add_item('The Great Gatsby', 'F. Scott Fitzgerald', 'book',
         '1234567890', 'Scribner', 1925, 180, 'Classic', 'hardcover')
update_item_status(1, 'borrowed', 'John Doe', '2024-04-30')
print(search_items(genre='Classic'))
print(suggest_similar_items('Classic'))

# Don't forget to close the connection when done
conn.close()
