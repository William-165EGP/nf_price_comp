import time
import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime
import csv

def get_current_price(country_codes):
    price_list = {}
    for one_country in country_codes:
        country_code = one_country[0]
        url = 'https://help.netflix.com/en/node/24926/' + country_code.lower()
#        print(url)
        response = requests.get(url)
        time.sleep(0.5)
        while response.url!=url:
            time.sleep(0.5)
            print('reget')
            print(response.url)
            response=requests.get(url)
        #print(one_country)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            price_plans = {}
            try:
                pricing_sections = soup.find_all(string=lambda text: ": " in text and "month" in text)
                test=pricing_sections[len(pricing_sections)-1]
#                print(len(pricing_sections))
#                print(pricing_sections)
                plan_names = []
                standard_plan_name = 'Standard with ads'
#                emergency_plan_name = 'Emergency Plan'
                # special case for some countries, currency found south africa
                if country_code == 'ZA':
                    try:
                        outside_raw_price = soup.select_one(
                            'body > div.global-container > div.global-content > div > div.pane-wrapper > div > div.left-pane > section.kb-article.kb-article-variant.gradient.sprinklr > div > div > div:nth-child(3) > ul > li:nth-child(1) > p').get_text()
                        outside_price = re.sub(r"[^\d.,]", "", outside_raw_price)

                        if ',' in outside_price:
                            if len(outside_price[outside_price.index(',') + 1:]) == 2:
                                outside_price = outside_price.replace(',', '.')
                            else:
                                outside_price = outside_price.replace(',', '')
                        if '.' in outside_price:
                            price_plans['Mobile'] = float(outside_price)
                        else:
                            price_plans['Mobile'] = int(outside_price)
                    except AttributeError:
                        pass

                for i in range(len(pricing_sections)):
                    raw_price = pricing_sections[i]
                    raw_plan_name = pricing_sections[i].find_parent('p').text
                    plan_name = raw_plan_name.split(":")[0].strip()
                    if len(plan_name) > 8:
                        plan_name = standard_plan_name
                    plan_names.append(plan_name)
#                    print(country_code,raw_plan_name)
                    # time.sleep(15)
                    #                print(raw_price)
                    # print(raw_text)
                    # print(one_country, plan_name, raw_price)
                    # price like 9699,99 in AR or 229.99 in TR can also be applied
                    price = re.sub(r"[^\d.,]", "", raw_price)
                    if ',' in price:
                        if len(price[price.index(',')+1:]) == 2:
                            price = price.replace(',', '.')
                        else:
                            price = price.replace(',', '')
                    if '.' in price:
                        price_plans[plan_names[i]] = float(price)
                    else:
                        price_plans[plan_names[i]] = int(price)
            except IndexError:  # For country like China, Russia aren't available.
                price = 0
#           print(one_country, price_plans)
            if price_plans:
                country_full_info = {}
                country_full_info['full_name'] = one_country[1]
                country_full_info['iso2_code'] = one_country[0]
                country_full_info['currency'] = one_country[2]
                country_full_info['og_price'] = price_plans
                price_list[country_code] = country_full_info
                # print(price_list[country_code])

        else:
            print("Request failed.")
    return price_list

def get_country_codes():
    with open('api.csv', 'r', encoding='utf-8') as f:
        country_codes = [line.strip().split(',', 1) for line in f.readlines()]
        for i in range(len(country_codes)):
            temp_one_country = country_codes[i]
            temp_one_country[1]=temp_one_country[1].rsplit(',', 1)
            #print(temp_one_country[1])
            country_codes[i] = [temp_one_country[0], temp_one_country[1][0], temp_one_country[1][1]]
        #print(country_codes)
    return country_codes

def comparison(prev_price_list, cur_price_list):
    diffcsv_define = {
        'Mobile': '_mobile',
        'Basic': '_basic',
        'Standard': '_standard',
        'Standard with ads': '_standard_ads',
        'Premium': '_premium',
        'currency': '_currency',
    }

    now = datetime.now()
    today = f"{now.year}-{now.month:02d}-{now.day:02d}"
    msg = ''

    for code in prev_price_list:
        if code not in cur_price_list:
            continue

        prev_entry = prev_price_list[code]
        cur_entry = cur_price_list[code]

        prev_prices = prev_entry.get("og_price", {})
        cur_prices = cur_entry.get("og_price", {})
        prev_currency = prev_entry.get("currency")
        cur_currency = cur_entry.get("currency")


        if prev_prices == cur_prices and prev_currency == cur_currency:
            continue

        msg += f'\n[{code}] List of different price:'


        row_data = {
            'date': today,
            'country_code': prev_entry.get("iso2_code", code),
            'country_name': prev_entry.get("full_name", ""),
            'old_mobile': '',
            'old_basic': '',
            'old_standard_ads': '',
            'old_standard': '',
            'old_premium': '',
            'new_mobile': '',
            'new_basic': '',
            'new_standard_ads': '',
            'new_standard': '',
            'new_premium': '',
            'old_currency': prev_currency,
            'new_currency': cur_currency,
        }

        for key, suffix in diffcsv_define.items():
            old_val = prev_prices.get(key) if key != 'currency' else prev_currency
            new_val = cur_prices.get(key) if key != 'currency' else cur_currency

            if old_val != new_val:
                msg += f'\nPrice of {key} is different. Fxxk you Netflix!!'

            old_col = 'old' + suffix
            new_col = 'new' + suffix
            row_data[old_col] = old_val
            row_data[new_col] = new_val


        with open("diffs.csv", mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=row_data.keys())
            writer.writerow(row_data)
    # print(msg)
    return msg


def sendMSG(token, msg):
    if not msg:
        return
    debugMode = False
    chat_id = os.getenv("MY_TG_CHAT_ID")
    if debugMode:
        print(msg)
    else:
        url = "https://api.telegram.org/bot{}/sendMessage".format(token)
        payload = {
            "chat_id": int(chat_id),
            "text": msg,
        }
        res = requests.post(url, data=payload)

if __name__ == '__main__':
    country_codes = get_country_codes()
    price_list = get_current_price(country_codes)

    with open('static.json', 'r', encoding='utf-8') as f:
        prev_price_list = json.load(f)

    msg = comparison(prev_price_list, price_list)
    token = os.getenv("MY_TGBOT_TOKEN")

    with open('static.json', 'w', encoding='utf-8') as f:
        json.dump(price_list, f, ensure_ascii=False, indent=4)
    sendMSG(token, msg)
