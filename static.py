import time
import requests
from bs4 import BeautifulSoup
import re
import json
import os

def get_current_price(country_codes):
    price_list = {}
    for country_code in country_codes:
        url = 'https://help.netflix.com/en/node/24926/' + country_code.lower()
#        print(url)
        response = requests.get(url)
        time.sleep(0.5)
        while response.url!=url:
            time.sleep(0.5)
            print('reget')
            print(response.url)
            response=requests.get(url)
        #print(country_code)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            price_plans = {}
            try:
                pricing_sections = soup.find_all(string=lambda text: ": " in text and "month" in text)
                pricing_sections=pricing_sections[len(pricing_sections)-1]
#                print(len(pricing_sections))
#                print(pricing_sections)
                raw_price = pricing_sections
#                print(raw_price)
                # print(raw_text)
                # print(country_code, plan_name, raw_price)
                # price like 9699,99 in AR or 229.99 in TR can also be applied
                price = re.sub(r"[^\d.,]", "", raw_price)
            except IndexError:  # For country like China, Russia aren't available.
                price = 0
            if price != 0:
                price_plans['Premium'] = price


            #print(price_plans)

            price_list[country_code] = price_plans

        else:
            print("Request failed.")
    return price_list

def get_country_codes():
    with open('api.csv', 'r', encoding='utf-8') as f:
        country_codes = [line.strip() for line in f.readlines()]
    return country_codes

def comparison(prev_price_list, cur_price_list):
    msg = ''
    if prev_price_list == cur_price_list:
       msg += 'Previous price list is equal to current price list'
    else:
        msg += 'List of different price:'
        for key, value in prev_price_list.items():
            if value != cur_price_list.get(key):
                msg += '\nPrice of {} is different.'.format(key) + ' Fuck you Netflix!!'

    return msg

def sendMSG(token, msg):
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
