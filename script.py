import re
from datetime import date

import requests
import urllib
from bs4 import BeautifulSoup
from collections import Counter

# DEFINE STATIC VARIABLES
zacks_link = "https://www.google.com.mx/search?biw=1535&bih=799&tbm=nws&q=%22New+Strong+Buy%22+site%3A+zacks.com" \
             "&oq=%22New+Strong+Buy%22+site%3A+zacks.com&gs_l=serp.3...1632004.1638057.0.1638325.24.24.0.0.0.0" \
             ".257.2605.0j15j2.17.0....0...1c.1.64.serp..8.0.0.Nl4BZQWwR3o "

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]

today_function = date.today()
todays_date = ("%s %s" % (months[today_function.month - 1], today_function.day))
day = today_function.day

headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}

while True:
    print(f'********** STARTING RUN! **********')
    print(f'Fetching {zacks_link}')

    google_request = requests.get(zacks_link)

    google_soup = BeautifulSoup(google_request.text, "html.parser")
    google_content = str(google_request.content)
    zacks_date = todays_date in google_content

    if zacks_date:
        zacks_date = ("%s %s" % (months[today_function.month - 1], day))
    else:
        while not zacks_date:
            day = day - 1
            zacks_date = ("%s %s" % (months[today_function.month - 1], day))

    search = zacks_date

    print(f'Stocks for {search}')
    google_result = None
    for i in google_soup.findAll('h3'):
        linkText = i.getText()
        if search in linkText:
            google_result = i.find('a').get('href')
            google_result = google_result.split('?')[-1]
            google_result = urllib.parse.parse_qs(google_result)['q'][0]
            break

    print(f'Fetching {google_result}')

    fetch_stock_twits = requests.get(google_result, headers=headers)
    stock_twits_content = str(fetch_stock_twits.content)
    Z = ('%s(.*)%s' % ('tickers :', 'publish_date :'))
    stock_twits_result = re.search(Z, stock_twits_content)
    tickerst = stock_twits_result.groups()[0]
    found_items = re.findall(r'\[.*?\]', tickerst)[0].split("\\'")[1::2]
    
    for each in found_items:
        print(f'\n********** Found instrument: {each} **********')
        link = 'https://api.stocktwits.com/api/2/streams/symbol/' + each + '.json'
        print(f'Fetching {link}')

        a = requests.get(link)
        a = a.json()

        if 'messages' not in a:
            print(f'Validation ERROR: reason unknown instrument on Stocktwits - {each} ')
            continue

        sentiment_dict = Counter()
        for message in a['messages']:
            if 'entities' in message:
                if 'sentiment' in message['entities']:
                    sentiment = message['entities']['sentiment']
                    print(f'Fetching sentiment of {each}: {sentiment}')
                    if sentiment is not None:
                        sentiment = sentiment['basic']
                        sentiment_dict[sentiment] += 1

        if len(sentiment_dict.items()) is 0:
            print(f'Validation ERROR: reason no sentiment found - {each}')
            continue

        for key, value in sentiment_dict.items():
            # print("%s:\n%s: %s" % (each, key, value))
            min_value = min(sentiment_dict.values())
            max_value = max(sentiment_dict.values())
            max_key = {value: key for (key, value) in sentiment_dict.items()}[max_value]
            min_key = {value: key for (key, value) in sentiment_dict.items()}[min_value]

        # print("There is a %s probability that %s stock is %s" % (max_value / (min_value + max_value), each, max_key))
        if min_key == max_key:
            print("%s: %s: %s" % (each, min_key, min_value))
        else:
            print("%s: %s: %s %s: %s" % (each, min_key, min_value, max_key, max_value))

    y = input("\n Press any key except space to restart: ")

    if not y:
        break
