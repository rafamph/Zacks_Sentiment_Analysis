from bs4 import BeautifulSoup
import requests, urllib
from datetime import date
import re

while True:

    zacks_link = "https://www.google.com.mx/search?biw=1535&bih=799&tbm=nws&q=%22New+Strong+Buy%22+site%3A+zacks.com&oq=%22New+Strong+Buy%22+site%3A+zacks.com&gs_l=serp.3...1632004.1638057.0.1638325.24.24.0.0.0.0.257.2605.0j15j2.17.0....0...1c.1.64.serp..8.0.0.Nl4BZQWwR3o"

    request = requests.get(zacks_link)

    soup = BeautifulSoup(request.text,"html.parser")

    fetch_data =requests.get(zacks_link)

    content = str((fetch_data.content))

    Months = ["January","February","March","April","May","June","July","August","September","October","November","December"]

    today_function = date.today()

    todays_date = ("%s %s" % (Months[today_function.month - 1],today_function.day))

    day =today_function.day

    zacks_date = todays_date in content

    if zacks_date == True:
        zacks_date = ("%s %s" % (Months[today_function.month - 1], day))
    else:
        while zacks_date == False:
            day = day - 1
            zacks_date = ("%s %s" % (Months[today_function.month - 1], day))

    search = zacks_date

    print("Stocks for {}\n".format(search))

    result = None
    for i in soup.findAll('h3'):
        linkText = i.getText()
        if search in linkText:
            result = i.find('a').get('href')
            result = result.split('?')[-1]
            result = urllib.parse.parse_qs(result)['q'][0]
            break


    fetch_dota =requests.get(result)
    cantent = str((fetch_dota.content))

    tickers= "tickers :"
    pd = "publish_date :"


    Z= ("%s(.*)%s" % (tickers,pd))
    resalt = re.search(Z, cantent)
    tickerst = resalt.groups()[0]
    list = re.findall(r'\[.*?\]', tickerst)[0].split("\\'")[1::2]
    for each in list:
        link = 'https://api.stocktwits.com/api/2/streams/symbol/' + each + '.json'

        a = requests.get(link)
        a = a.json()

        from collections import Counter

        sentiment_dict = Counter()
        for message in a['messages']:
            if 'entities' in message:
                if 'sentiment' in message['entities']:
                    sentiment = message['entities']['sentiment']
                    if sentiment is not None:
                        sentiment = sentiment['basic']
                        sentiment_dict[sentiment] += 1
        for key, value in sentiment_dict.items():
            #print("%s:\n%s: %s" % (each, key, value))
            min_value = min(sentiment_dict.values())
            max_value = max(sentiment_dict.values())
            max_key = {value: key for (key, value) in sentiment_dict.items()}[max_value]
            min_key = {value: key for (key, value) in sentiment_dict.items()}[min_value]

        #print("There is a %s probability that %s stock is %s" % (max_value / (min_value + max_value), each, max_key))
        if min_key == max_key :
            print("%s:\n%s: %s" % (each, min_key, min_value))
        else:
            print("%s:\n%s: %s\n%s: %s" % (each, min_key, min_value, max_key, max_value))


    y=input("\n"+"Press any key except space to restart")

    if not y:
        break


