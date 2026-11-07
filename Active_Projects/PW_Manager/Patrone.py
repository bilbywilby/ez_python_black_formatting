# Import the modules
import cryptography.fernet as fernet
import sqlite3

# Define the database file name
db_file = "passwords.db"

# Define the key file name
key_file = "key.key"

# Generate a key and save it in a file
key = fernet.Fernet.generate_key()
with open(key_file, "wb") as f:
    f.write(key)

# Create a fernet object with the key
fernet_obj = fernet.Fernet(key)

# Create a connection and a cursor to the database
conn = sqlite3.connect(db_file)
cur = conn.cursor()

# Create a table to store the passwords
cur.execute(
    "CREATE TABLE IF NOT EXISTS passwords (website TEXT, username TEXT, password TEXT)")

# Define a function to add a password to the database


def add_password():
    # Get the website, username, and password from the user
    website = input("Enter the website: ")
    username = input("Enter the username: ")
    password = input("Enter the password: ")
    # Encrypt the password using the fernet object
    encrypted_password = fernet_obj.encrypt(password.encode())
    # Insert the data into the table
    cur.execute("INSERT INTO passwords VALUES (?, ?, ?)",
                (website, username, encrypted_password))
    # Commit the changes
    conn.commit()
    # Print a confirmation message
    print("Password added successfully.")

# Define a function to get a password from the database


def get_password():
    # Get the website from the user
    website = input("Enter the website: ")
    # Query the table for the username and password
    cur.execute(
        "SELECT username, password FROM passwords WHERE website = ?", (website,))
    # Fetch the result
    result = cur.fetchone()
    # Check if the result is not empty
    if result:
        # Decrypt the password using the fernet object
        decrypted_password = fernet_obj.decrypt(result[1]).decode()
        # Print the username and password
        print(f"Username: {result[0]}")
        print(f"Password: {decrypted_password}")
    else:
        # Print an error message
        print("No password found for this website.")

# Define a function to show the menu and get the user choice


def show_menu():
    # Print the menu options
    print("Password Manager")
    print("1. Add a password")
    print("2. Get a password")
    print("3. Exit")
    # Get the user choice
    choice = input("Enter your choice: ")
    # Return the choice
    return choice

# Define a main function to run the program


def main():
    # Loop until the user chooses to exit
    while True:
        # Show the menu and get the user choice
        choice = show_menu()
        # Perform the action based on the choice
        if choice == "1":
            # Add a password
            add_password()
        elif choice == "2":
            # Get a password
            get_password()
        elif choice == "3":
            # Exit the program
            print("Bye!")
            break
        else:
            # Invalid choice
            print("Invalid choice. Please try again.")


# Run the main function
if __name__ == "__main__":
    main()
