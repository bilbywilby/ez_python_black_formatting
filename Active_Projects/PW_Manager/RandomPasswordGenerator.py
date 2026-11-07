# A python script that generates a random password based on user input

import random
import string

# Ask the user how long they want their password to be
length = int(input("Enter the length of your password: "))

# Ask the user if they want to include digits, lowercase letters, uppercase letters, and punctuation
digits = input("Do you want to include digits? (y/n): ").lower() == "y"
lowercase = input(
    "Do you want to include lowercase letters? (y/n): ").lower() == "y"
uppercase = input(
    "Do you want to include uppercase letters? (y/n): ").lower() == "y"
punctuation = input(
    "Do you want to include punctuation? (y/n): ").lower() == "y"

# Create a list of possible characters based on user preferences
characters = ""
if digits:
    characters += string.digits
if lowercase:
    characters += string.ascii_lowercase
if uppercase:
    characters += string.ascii_uppercase
if punctuation:
    characters += string.punctuation

# Check if the list of characters is not empty
if characters:
    # Generate a random password by choosing a random character from the list for each position
    password = "".join(random.choice(characters) for i in range(length))
    # Print the password
    print("Your password is:", password)
else:
    # Print an error message
    print("You did not choose any characters for your password. Please try again.")
