import time
from bs4 import BeautifulSoup
import requests
import csv
import re

from io import StringIO
response = requests.get('https://raw.githubusercontent.com/datasets/currency-codes/refs/heads/main/data/codes-all.csv')

csv_data = response.text

currency_codes = {
    'Arab Emirates Dirham' : 'AED',
    'US Dollars' : 'USD',
    'Canadian Dollars' : 'CAD',
    'Czech Crowns' : 'CZK',
    'British Pound' : 'GBP',
    'Hungarian Forint' : 'HUF',
    'Indonesian Rupiah' : 'IDR',
    'Israeli Shekel' : 'ILS',
    'Japanese Yen' : 'JPY',
    'Korean Won' : 'KRW',
    'Nigerian Naira' : 'NGN',
    'Peruvian Sole' : 'PEN',
    'Pakistani Rupee' : 'PKR',
    'Polish Zloty' : 'PLN',
    'Thai Baht' : 'THB',
    'Vietnamese Dong' : 'VND',
    'South African Rand' : 'ZAR',
}

with StringIO(csv_data) as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
#        print(row)
        currency_codes[row[1]] = row[2]

#print(currency_codes)

with open('api.csv', 'r', encoding='utf-8') as f:
    country_codes = [line.strip().split(',', 1) for line in f.readlines()]
    #print(country_codes)

#print(country_codes)

new_country_codes = []

for one_country in country_codes:
    country_code = one_country[0]
    url = 'https://help.netflix.com/en/node/24926/' + country_code.lower()
    response = requests.get(url)
    while response.url != url:
        time.sleep(0.5)
        print('reget')
        print(response.url)
        response = requests.get(url)
    # print(one_country)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        locate = soup.find_all(string=lambda text: "Pricing (" in text and ")" in text)
        try:
            # Extract the part inside the parentheses
            match = re.search(r'\((.*?)\)', locate[0])  # This matches text inside parentheses
            if match:
                # print(country_code, match.group(1), currency_codes[match.group(1)])  # This will print "US Dollar"
                new_one_country = one_country
                new_one_country.append(currency_codes[match.group(1)])
                new_country_codes.append(new_one_country)
        except IndexError:
            # For country like China, Russia aren't available.
            pass

new_country_codes.sort(key=lambda x: x[0])

with open("api.csv", "w", newline="") as f:
    for row in new_country_codes:
        f.write(",".join(row) + "\n")