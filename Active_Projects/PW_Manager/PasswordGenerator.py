# Import the modules
import string
import random
import pyperclip

# Define the password length
password_length = 16

# Define the password characters
password_characters = string.ascii_letters + string.digits + string.punctuation

# Generate the password
password = "".join(random.choice(password_characters)
                   for i in range(password_length))

# Print the password
print(f"Your password is: {password}")

# Copy the password to the clipboard
pyperclip.copy(password)
print("Your password has been copied to the clipboard.")
