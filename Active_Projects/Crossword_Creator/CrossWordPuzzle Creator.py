import requests
from bs4 import BeautifulSoup
from random import choice


# Function to get web content
def get_web_content(url):
    """
    Get the web content of the specified URL.

    :param url: The URL to download content from.
    :return: The web content as a text string.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.text


# Tokenize the text
def tokenize(text):
    """
    Tokenize the given text string.

    :param text: The text to tokenize.
    :return: A list of words in the text.
    """
    return text.split()


# Filter words based on length and punctuation
def filter_words(words):
    """
    Filter the given list of words based on length and punctuation.

    :param words: The list of words to filter.
    :return: A filtered list of words.
    """
    return [word.strip(',.!?;:\"\'[]{}()') for word in words if len(word) > 3]


# Download and filter the web content
url = "https://en.wikipedia.org/wiki/SpongeBob_SquarePants"
web_content = get_web_content(url)
words = tokenize(web_content)
words = filter_words(words)

# Placeholder for the crossword puzzle
crossword_puzzle = [[' ' for _ in range(10)] for _ in range(10)]


# Function to place a word in the grid
def place_word(word):
    """
    Place the given word in the crossword puzzle grid.

    :param word: The word to place in the grid.
    """
    direction = choice([1, 2])  # 1: Horizontal, 2: Vertical
    if direction == 1:
        row = choice(range(10))
        col = max(0, min(10, 10 - len(word)))
        if all(crossword_puzzle[row][col + i] == ' ' for i in range(len(word))):
            for i in range(len(word)):
                crossword_puzzle[row][col + i] = word[i]
    else:
        col = choice(range(10))
        row = max(0, min(10, 10 - len(word)))
        if all(crossword_puzzle[row + i][col] == ' ' for i in range(len(word))):
            for i in range(len(word)):
                crossword_puzzle[row + i][col] = word[i]


# Fill the grid with words
for _ in range(40):
    word = choice(words)
    place_word(word)

# Function to display the crossword puzzle


def display_crossword(crossword):
    """
    Display the given crossword puzzle.

    :param crossword: The crossword puzzle to display.
    """
    for row in crossword:
        print(" ".join(row))


# Display the crossword puzzle
display_crossword(crossword_puzzle)
