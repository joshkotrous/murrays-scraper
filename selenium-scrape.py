import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set path to chromedriver as per your configuration
webdriver_service = Service('./chromedriver-mac-arm64/chromedriver')  # Change this to your actual path

# Choose Chrome Browser
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

baseUrl = "https://www.murrayscheese.com"
url = "https://www.murrayscheese.com/lp/cheese/alpine-and-gruyere?p=2"

column_names = ["name", "url", "description", "notes", "allergens", "ingredients", "additionalFacts"]
df = pd.DataFrame(columns=column_names)
file_name = "output.csv"

driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ProductCard_textContent__EzFFe")))

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

pattern = re.compile(r"^/dp/")
items = soup.find_all("a", {"class": "ProductCard_textContent__EzFFe", "href": pattern})

for item in items:
    product_url = baseUrl + item["href"]
    driver.get(product_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

    html = driver.page_source
    product_soup = BeautifulSoup(html, "html.parser")

    # Get Name
    name = product_soup.find("h1", {"itemprop": "name"}).text.strip()

    # Get Flavors
    flavors_elements = product_soup.find_all("li", {"class": "Tags_prop__L0hX9"})
    flavors = ", ".join([flavor.text.strip() for flavor in flavors_elements])

    # Get description
    description_elements = product_soup.find_all("p", {"itemprop": "description"})
    description = description_elements[0].text.strip() if description_elements else ""

    # Get allergens
    allergens_elements = product_soup.find_all("p", {"class": "ContentBlock_allergens__e0lb7"})
    allergens = ", ".join([allergen.text.strip() for allergen in allergens_elements])

    # Get additional facts and ingredients
    additional_facts = ""
    ingredients = ""
    subItems = product_soup.find_all("div", {"class": "ContentBlock_contentText__aPGp_ ContentBlock_propertiesText__7D0_H"})
    for subItem in subItems:
        children = subItem.find_all("li")
        if len(children) == 0:
            text = subItem.text.strip().lower()
            if ("non gmo" in text or "family owned" in text or "rotational grazing" in text or "gluten free" in text or "when you receive your cheese" in text or "cooperative" in text):
                additional_facts += subItem.text.strip() + ", "
            else:
                ingredients = subItem.text.strip()
        additional_facts += ", ".join([fact.text.strip() for fact in children])

    # Add row to DataFrame
    df.loc[len(df)] = [name, product_url, description, flavors, allergens, ingredients, additional_facts]

driver.quit()
df.to_csv(file_name, index=False)
