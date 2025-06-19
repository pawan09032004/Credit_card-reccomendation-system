import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import uuid
from tqdm import tqdm
import base64
import json
import pickle


BASE_URL = "https://select.finology.in/credit-card/"
with open("response.txt", "r") as f:
    exec("details="+f.read().replace('null', 'None'))

def make_affiliate_link():
    """Generate a dummy affiliate/apply link."""
    return f"https://apply.example.com/{uuid.uuid4()}"

dataset = []
for dets in tqdm(details, desc="Scraping cards"):
    response = requests.get(BASE_URL+dets["urlSlug"])
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    useful_data = ["cardName", "joiningFee", "annualFee", "bestFor", "rewardRate", "minMonthlyIncome", "employmentType"]
    #                             ["cardImage", "features", "eligibility", "referralLink"]
    data_format = {
        "cardName": "cardName",
        "joiningFee": "joiningFee",
        "annualFee": "annualFee",
        "bestFor": "rewardType",
        "rewardRate": "rewardRate",
        "minMonthlyIncome": "minMonthlyIncome",
        "employmentType": "employmentType"
    }
    data = {data_format[i]: dets[i] for i in useful_data}
    pros = soup.find('h5', string='Pros').find_next('ul').get_text(strip=True)
    #cons = soup.find('h5', string='Cons').find_next('ul').get_text(strip=True)
    # if any h5 contains the text like "%eligibility%"
    eligibility = soup.find('h3', string=lambda text: text and "eligibility" in text.lower())
    if eligibility:
        eligibility = eligibility.find_next('ul')
        if eligibility:
            eligibility = eligibility.get_text(strip=True)

    card_img_src = soup.find_all('img')[2]['src']
    card_img_data = requests.get(card_img_src).content
    data["cardImage"] = base64.b64encode(card_img_data).decode('ascii')
    data["features"] = pros
    #data["cons"] = cons
    data["eligibility"] = eligibility
    data["affiliateLink"] = make_affiliate_link()
    dataset.append(data)

dataset = {"dataset": dataset}
json_string = json.dumps(dataset)
with open('dataset.json', 'w+') as outfile:
    outfile.write(json_string)
