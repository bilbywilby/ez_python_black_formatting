# Import the modules
import requests
from bs4 import BeautifulSoup

# Define the URL of the website to visit
url = "https://www.indeed.com/jobs"

# Define the parameters for the search query
params = {
    "q": "data analyst",  # keywords
    "l": "New York, NY",  # location
    "salary": "$15-$25 an hour",  # salary range
    "fromage": "last",  # date posted
    "limit": 50  # number of results per page
}

# Define the headers for the request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}

# Send a GET request to the website with the parameters and headers
response = requests.get(url, params=params, headers=headers)

# Check if the response status code is 200 (OK)
if response.status_code == 200:
    # Get the HTML content from the response
    html = response.text
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    # Find the list of job cards
    job_cards = soup.find_all("div", class_="jobsearch-SerpJobCard")
    # Loop through the job cards
    for job_card in job_cards:
        # Get the job title from the job card
        job_title = job_card.find("h2", class_="title").text.strip()
        # Get the job URL from the job card
        job_url = "https://www.indeed.com" + job_card.find("a")["href"]
        # Get the job description from the job URL
        job_response = requests.get(job_url, headers=headers)
        # Check if the job response status code is 200 (OK)
        if job_response.status_code == 200:
            # Get the job HTML content from the job response
            job_html = job_response.text
            # Parse the job HTML content using BeautifulSoup
            job_soup = BeautifulSoup(job_html, "html.parser")
            # Find the job description element
            job_description = job_soup.find("div", id="jobDescriptionText")
            # Check if the job description element is not None
            if job_description:
                # Get the job description text
                job_description_text = job_description.text.lower()
                # Define the list of skills to look for
                skills = ["python", "sql", "excel", "tableau", "power bi"]
                # Check if all the skills are in the job description text
                if all(skill in job_description_text for skill in skills):
                    # Print the job title and URL
                    print(f"{job_title} - {job_url}")
                    # Apply to the job using the Easy Apply button
                    # This part is not implemented, as it may violate the Indeed terms of service
                    # print("Applied to the job")
                else:
                    # Print a skip message
                    print(f"Skipped {job_title} - {job_url}")
            else:
                # Print an error message
                print(f"Could not find the job description for {
                      job_title} - {job_url}")
        else:
            # Print an error message
            print(f"Could not get the job page for {job_title} - {job_url}")
else:
    # Print an error message
    print(f"Could not get the search results from {url}")
