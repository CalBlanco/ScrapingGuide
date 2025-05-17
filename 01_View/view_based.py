"""Simple View Based Scraping Script"""
import json

import requests as r
from bs4 import BeautifulSoup


def get_headlines(url, element)->list[tuple]:
    """Get Headlines, Link Pairs from CNN"""
    #url = 'https://www.cnn.com/politics'

    cnn_req = r.get(url, timeout=2)
    cnn_req.raise_for_status()

    html = cnn_req.text
    soup = BeautifulSoup(html)

    data = soup.find_all('div', element)
    items = [(item.span.get_text(), item.a['href']) for item in data]

    return items

def main():
    """Main"""
    headlines = get_headlines('https://apnews.com/politics', 'PagePromo')
    with open('headlines.json', 'w', encoding='utf8') as f:
        json.dump(headlines, f, indent=4)



if __name__ == "__main__":
    main()
