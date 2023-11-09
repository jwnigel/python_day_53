import requests
from bs4 import BeautifulSoup
import re
import sys

zillow_url = 'https://appbrewery.github.io/Zillow-Clone/'

response = requests.get(zillow_url)

soup = BeautifulSoup(response.text, 'html.parser')

sidebar = soup.find("ul", class_="List-c11n-8-84-3-photo-cards")

results = sidebar.find_all("li")

prices = []
addresses = []
links = []

#regex patterns to extract address and price
# price_pattern = r'\$\d+(?:,\d+)?'

def extract_address(input_text):
    # Use regular expression to match the address and stop before the price
    address_match = re.search(r'(.+?)\s+\$\d+', input_text)
    if address_match:
        address = address_match.group(1)
        return address.strip()
    return ""


for res in results:

    # result text to parse with regex
    res_text = res.text.lstrip()

    # price (regex didn't work because of some extra prices thrown in)
    price_span = res.find('span', class_='PropertyCardWrapper__StyledPriceLine', attrs={'data-test': 'property-card-price'})

    # url link
    property_link = res.find('a', attrs={'data-test': 'property-card-link'})


# append url link, price, and address to respective lists
    if property_link:
        link = property_link['href']
        links.append(link)


    if price_span:
        price = price_span.text.strip()
        prices.append(price)

    address = extract_address(res_text)

    if address:
        addresses.append(address)

# Clean prices
def clean_price(price):
    pattern = r'\$\d{1,3}(?:,\d{3})*(?:\.\d+)?'
    match = re.search(pattern, price)
    if match:
        return match.group()
    return None

cleaned_prices = [clean_price(price) for price in prices]

# Clean addresses
def clean_address(address):
    # Split the address using the pipe symbol and take the second part (after the pipe)
    parts = address.split('|')
    if len(parts) > 1:
        cleaned_part = parts[1]
    else:
        cleaned_part = parts[0]

    # Remove leading and trailing spaces
    cleaned_address = cleaned_part.strip()
    return cleaned_address

# Clean the addresses and store in a new list
cleaned_addresses = [clean_address(address) for address in addresses]

# Function to combine into one list of dictionaries
def make_dictionary(addresses, prices, links):
    results = []
    # Check if all lists have the same length
    if len(addresses) == len(links) == len(prices):
        for i in range(len(addresses)):
            entry = {
                "address": addresses[i],
                "link": links[i],
                "price": prices[i]
            }
            results.append(entry)
        return results
    else:
        print("Lists are not of the same length.")
        print(f"Addresses: {len(addresses)}, Prices: {len(prices)}, Links: {len(links)}")

formatted_results = make_dictionary(addresses=cleaned_addresses,
                                    prices=cleaned_prices,
                                    links=links)

# Use Selenium to fill out google form

from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize the WebDriver (assuming Firefox)
driver = webdriver.Firefox()

# Navigate to the Google Form URL
form_url = "https://forms.gle/DWect1iqyPjcEPPH6"
driver.get(form_url)

for entry in formatted_results[:-1]:

    # Find and interact with form fields using aria-labelledby
    address_field = driver.find_element(By.CSS_SELECTOR, 'input[aria-labelledby="i1"]')
    price_field = driver.find_element(By.CSS_SELECTOR, 'input[aria-labelledby="i5"]')
    link_field = driver.find_element(By.CSS_SELECTOR, 'input[aria-labelledby="i9"]')

    # Fill in the form fields
    address_field.send_keys(entry["address"])
    price_field.send_keys(entry["price"])
    link_field.send_keys(entry["link"])

    # Submit the form (assuming there's a submit button)
    submit_button = driver.find_element(By.CSS_SELECTOR, 'span.NPEfkd.RveJvd.snByac')
    submit_button.click()

    submit_another_form_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Enviar otra respuesta")
    submit_another_form_link.click()

# On the forms page, click link to sheets to get sheet with all entries
# Open the Google Form edit page
forms_home_url = "https://docs.google.com/forms/d/1gscWMNzrN7t26OVjFmGnFH196FeDo7kjcJppmoAuqck/edit#responses"
driver.get(forms_home_url)

# Wait for a few seconds to ensure the page is loaded
driver.implicitly_wait(5)

# Find the "Link to Sheets" button by its class name
button = driver.find_element(By.CLASS_NAME, "NPEfkd")
# Click the button
button.click()

