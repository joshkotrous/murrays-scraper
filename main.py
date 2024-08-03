import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

baseUrl = "https://www.murrayscheese.com"
url = "https://www.murrayscheese.com/lp/cheese/alpine-and-gruyere?p=2"

column_names = ["name", "url", "description", "notes", "allergens", "ingredients", "additionalFacts"]
df = pd.DataFrame(columns=column_names)
file_name = "output.csv"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("Successfully fetched the webpage.")
else:
    print("Failed to fetch webpage")

soup = BeautifulSoup(response.content, "html.parser")

pattern = re.compile(r"^/dp/")
items = soup.find_all("a", {"class": "ProductCard_textContent__EzFFe", "href": pattern})

for item in items:
    url = baseUrl + item["href"]
    response = requests.get(baseUrl + item["href"])
    soup = BeautifulSoup(response.content, "html.parser")

    # Get Name
    subItems = soup.find_all("h1", {"itemprop": "name"})
    name = subItems[0].text.strip()

    # Get Flavors
    subItems = soup.find_all("li", {"class": "Tags_prop__L0hX9"})
    flavors = ", ".join([flavor.text.strip() for flavor in subItems])

    # Get description
    subItems = soup.find_all("p", {"itemprop": "description"})
    description = subItems[0].text.strip() if subItems else ""

    # Get allergens
    subItems = soup.find_all("p", {"class": "ContentBlock_allergens__e0lb7"})
    allergens = ", ".join([allergen.text.strip() for allergen in subItems])

    # Get additional facts
    subItems = soup.find_all("div", {"class": "ContentBlock_contentText__aPGp_ ContentBlock_propertiesText__7D0_H"})
    ingredients = ""
    additionalFacts = ""
    for item in subItems: 
        children = item.find_all("li")
        if  len(children) == 0:
            if ("non gmo" in item.text.strip().lower() )| ("family owned" in item.text.strip().lower())  | ("rotational grazing" in item.text.strip().lower()) | ("gluten free" in item.text.strip().lower()) | ("when you receive your cheese" in item.text.strip().lower()) | ("cooperative" in item.text.strip().lower()):
                additionalFacts = additionalFacts + item.text.strip() + ", "
            else:
                ingredients = item.text.strip()

        additionalFacts = additionalFacts +  ", ".join([fact.text.strip() for fact in children])

    # Add row to DataFrame
    df.loc[len(df)] = [name, url, description, flavors, allergens, ingredients, additionalFacts]

df.to_csv(file_name, index=False)
