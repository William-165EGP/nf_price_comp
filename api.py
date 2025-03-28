import requests
import json

country_codes=[]

for i in range(0, 300, 100):
    response = requests.get(
        f'https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/countries-codes/records?select=iso2_code&limit=100&offset={i}')
    raw_json = json.loads(response.text)
    for one_country in raw_json['results']:
        country_codes.append(one_country['iso2_code'])
#    print(i)

with open('api.csv', 'w') as f:
    for code in country_codes:
        f.write(f"{code}\n")

#print(country_codes)
#print(len(country_codes))






