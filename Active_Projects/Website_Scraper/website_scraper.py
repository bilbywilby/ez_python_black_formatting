import requests
from bs4 import BeautifulSoup

url = 'https://en.wikipedia.org/wiki/Web_scraping'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

for paragraph in soup.find_all('p'):
    print(paragraph.text)