import requests
import json

country_codes=[]

country_not_exist = ['KS', 'C1', 'Y1', 'T1', 'Y2', 'T2', 'M3', 'D1', 'M1', 'E1', 'D2', 'M2', 'JG', 'D3', 'Y3']

for i in range(0, 300, 100):
    response = requests.get(
        f'https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/countries-codes/records?select=iso2_code&limit=100&offset={i}')
    raw_json = json.loads(response.text)
    for one_country in raw_json['results']:
        if one_country['iso2_code'] not in country_not_exist:
            country_codes.append(one_country['iso2_code'])
#    print(i)

with open('api.csv', 'w') as f:
    for code in country_codes:
        f.write(f"{code}\n")

#print(country_codes)
#print(len(country_codes))






