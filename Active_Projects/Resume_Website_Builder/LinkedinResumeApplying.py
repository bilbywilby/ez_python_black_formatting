# Import the module
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Define the URL of the website to visit
url = "https://www.linkedin.com/jobs/"

# Define the credentials for logging in
email = "your_email@domain.com"
password = "your_password"

# Define the keywords for searching jobs
keywords = "data analyst"

# Define the location for searching jobs
location = "New York, NY"

# Create a webdriver object
driver = webdriver.Chrome()

# Open the website
driver.get(url)

# Find the sign in button and click it
sign_in_button = driver.find_element_by_link_text("Sign in")
sign_in_button.click()

# Find the email input and enter the email
email_input = driver.find_element_by_id("username")
email_input.send_keys(email)

# Find the password input and enter the password
password_input = driver.find_element_by_id("password")
password_input.send_keys(password)

# Find the submit button and click it
submit_button = driver.find_element_by_css_selector("button[type='submit']")
submit_button.click()

# Find the keywords input and enter the keywords
keywords_input = driver.find_element_by_css_selector(
    "input[placeholder='Search by title, skill, or company']")
keywords_input.send_keys(keywords)

# Find the location input and enter the location
location_input = driver.find_element_by_css_selector(
    "input[placeholder='City, state, or zip code']")
location_input.clear()
location_input.send_keys(location)

# Press the enter key to start the search
location_input.send_keys(Keys.RETURN)

# Find the Easy Apply filter and click it
easy_apply_filter = driver.find_element_by_css_selector(
    "button[data-control-name='filter_easy_apply']")
easy_apply_filter.click()

# Find the list of job cards
job_cards = driver.find_elements_by_css_selector("li[data-card-type='job']")

# Loop through the job cards
for job_card in job_cards:
    # Click on the job card
    job_card.click()
    # Find the Easy Apply button
    easy_apply_button = driver.find_element_by_css_selector(
        "button[data-control-name='jobdetails_topcard_inapply']")
    # Check if the button is enabled
    if easy_apply_button.is_enabled():
        # Click on the button
        easy_apply_button.click()
        # Find the submit button
        submit_button = driver.find_element_by_css_selector(
            "button[data-control-name='submit_unify']")
        # Click on the button
        submit_button.click()
        # Print a confirmation message
        print(f"Applied to {job_card.text}")
    else:
        # Print a skip message
        print(f"Skipped {job_card.text}")

# Close the driver
driver.close()
