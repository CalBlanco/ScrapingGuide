"""Control based scraping / Endpoint scraping"""
import json
import argparse
import time

import requests as r
from glom import glom

BASE_URL = 'https://services.surfline.com/kbyg/mapview'
TIMEOUT = 5

def get_spot_data(spot_params):
    """Get spot information based on query parameters"""
    req = r.get(BASE_URL, params=spot_params, timeout=TIMEOUT)
    req.raise_for_status()
    data = req.json()
    out = {
        'params': spot_params, #sending our params to correlate info
        'data': glom(data, 'data.spots') #grabbing just the spot data
    }

    return out


def main():
    """main func"""
    parser = argparse.ArgumentParser(
        prog='Surfline Spot Scraper',
        description='Gather information on surf spots by making requests to the underlying api of surfline',
    )

    parser.add_argument('-p', '--params', default='params.json', help='File for parameter data')
    parser.add_argument('-t', '--time', default=0, help='Time between requests')
    parser.add_argument('-o', '--output', default='output.json', help='File to place output data')
    args = parser.parse_args()

    params_file = args.params
    with open(params_file, 'r', encoding='utf8') as f:
        params = json.loads(f.read())
    
    out = []
    for param in params:
        try:
            data = get_spot_data(param)
            out.append(data)
            time.sleep(int(args.time)) #sleep to not overload requests (default 0 aka no sleep)
        except Exception as e: #handle potentially getting an error from the request
            print(f'ERROR: Encountered {e} while using {params}')

    with open(args.output, 'w', encoding='utf8') as f:
        json.dump(out, f, indent=4)
    print('Done Scraping Surfline!')


if __name__ == "__main__":
    main()
