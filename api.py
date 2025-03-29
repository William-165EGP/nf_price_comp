import csv
import requests


country_codes=[]

country_not_exist = ['KS', 'C1', 'Y1', 'T1', 'Y2', 'T2', 'M3', 'D1', 'M1', 'E1', 'D2', 'M2', 'JG', 'D3', 'Y3']

url='https://github.com/datasets/country-list/raw/64bee8e75d21e5ed6123c28d7cdde4dbc5692908/data.csv'

response = requests.get(url)
raw_countries = response.text.split('\n')[1:]

for raw_one_country in raw_countries:
    one_country = raw_one_country.rsplit(',', 1)
    one_country[0] = one_country[0].strip('"')
#    print(one_country[0])
    if one_country[0] != '' and one_country[0] not in country_not_exist:
        one_country[0], one_country[1] = one_country[1], one_country[0]
        country_codes.append(one_country)

country_codes.sort(key=lambda x: x[0])
#print(country_codes)

with open("api.csv", "w", newline="") as f:
    for row in country_codes:
        f.write(",".join(row) + "\n")







