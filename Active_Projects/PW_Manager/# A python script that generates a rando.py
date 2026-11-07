# A python script that generates a random password based on user input

# Import the random and string modules
import random
import string

# Define a function that asks the user for a valid integer


def ask_integer(prompt):
    # Loop until the user enters a valid integer
    while True:
        # Try to get the user input and convert it to an integer
        try:
            value = int(input(prompt))
            # Return the value if it is valid
            return value
        # If there is a ValueError, print an error message and repeat
        except ValueError:
            print("Invalid input. Please enter an integer.")

# Define a function that asks the user for a yes or no answer


def ask_yes_no(prompt):
    # Loop until the user enters a valid answer
    while True:
        # Get the user input and convert it to lowercase
        answer = input(prompt).lower()
        # Return True if the answer is yes, False if the answer is no
        if answer == "y":
            return True
        elif answer == "n":
            return False
        # If the answer is neither yes nor no, print an error message and repeat
        else:
            print("Invalid input. Please enter y or n.")


# Ask the user how long they want their password to be
# Use the ask_integer function to validate the input
length = ask_integer("Enter the length of your password: ")

# Ask the user if they want to include digits, lowercase letters, uppercase letters, and punctuation
# Use the ask_yes_no function to validate the input
digits = ask_yes_no("Do you want to include digits? (y/n): ")
lowercase = ask_yes_no("Do you want to include lowercase letters? (y/n): ")
uppercase = ask_yes_no("Do you want to include uppercase letters? (y/n): ")
punctuation = ask_yes_no("Do you want to include punctuation? (y/n): ")

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
    # Print the character set that was used to generate the password
    print("Your password will be generated from these characters:", characters)
    # Try to generate a random password by choosing a random character from the list for each position
    try:
        password = "".join(random.choice(characters) for i in range(length))
        # Print the password
        print("Your password is:", password)
    # If there is an error, print an error message
    except Exception as e:
        print("An error occurred while generating your password:", e)
else:
    # Print an error message
    print("You did not choose any characters for your password. Please try again.")
