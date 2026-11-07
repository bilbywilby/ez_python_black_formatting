# Import the modules
import requests
from bs4 import BeautifulSoup
import re

# Define the URL of the website to crawl
url = "https://www.python.org/"

# Define the pattern to match the URLs
pattern = re.compile("^https?://(www\.)?python.org")

# Define a set to store the visited URLs
visited = set()

# Define a function to crawl a website


def crawl(url):
    # Check if the URL is not visited
    if url not in visited:
        # Add the URL to the visited set
        visited.add(url)
        # Print the URL
        print(url)
        # Get the HTML content from the URL
        response = requests.get(url)
        html = response.text
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        # Find all the links in the HTML content
        links = soup.find_all("a")
        # Loop through the links
        for link in links:
            # Get the href attribute of the link
            href = link.get("href")
            # Check if the href is not None
            if href:
                # Check if the href matches the pattern
                if pattern.match(href):
                    # Crawl the href
                    crawl(href)


# Start crawling from the URL
crawl(url)
