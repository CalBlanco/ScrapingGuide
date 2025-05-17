"""Scrape flight information from SouthWest using Selenium"""
import urllib
import time
import json
import argparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

BASE_URL = 'https://www.southwest.com/air/booking/select-depart.html'

def make_query(args):
    """Create an encoded url using urllib"""
    encoded = urllib.parse.urlencode(args)

    url = f'{BASE_URL}?{encoded}'
    return url

def run_driver(args, sleep_time):
    """Run a Selenium driver and return the page source when we have reached a state that contains our listings"""
    driver = webdriver.Chrome() #initialize the driver
    wait = WebDriverWait(driver, 10) #set up a wait element (this will timeout and raise an error if waiting more than 10 seconds)

    query_url = make_query(args)

    driver.get('https://www.southwest.com/') #go to main domain
    time.sleep(sleep_time) #wait a second
    driver.get(query_url) #fire off our url
    time.sleep(sleep_time) #wait again
    submit = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'actionable_primary'))) #wait til we can click the search button
    submit.click() #click dat shit

    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'air-booking-select-detail'))) #wait for row item to appear
    
    source = driver.page_source
    driver.close()

    return source

def get_listings_from_source(source):
    """Extract our listings from the page"""
    soup = BeautifulSoup(source)
    listings = soup.find_all('li', 'air-booking-select-detail') #get our listing elements

    assert len(listings) > 0, 'Unable to find listing elements'

    scraped_listings = [extract_listing_info(listing) for listing in listings]

    return scraped_listings


def extract_listing_info(listing):
    """Extract information from listings"""
    times = listing.find_all('span', 'time--value') #get departure and arrival times
    real_times = [elem.get_text() for elem in times]

    duration = listing.find('div', 'select-detail--flight-duration').get_text()

    fares = listing.find_all('button', 'fare-button--button')
    fares = [elem.find('span', 'swa-g-screen-reader-only').get_text() for elem in fares if elem.find('span', 'swa-g-screen-reader-only')]

    stops = listing.find_all('div', 'select-detail--change-planes')
    stops = [stop.get_text() for stop in stops]

    info = {
        'times': real_times,
        'duration': duration,
        'fares': fares,
        'stops': stops
    }

    return info

def main():
    """Main Func"""
    parser = argparse.ArgumentParser(
        prog='Southwest Ticket Scraper',
        description='Gather ticket information from Southwest using selenium and bs4',
    )

    parser.add_argument('-p', '--params', default='params.json', help='File for parameter data')
    parser.add_argument('-t', '--time', default=1, help='Time between requests')
    parser.add_argument('-o', '--output', default='output.json', help='File to place output data')
    cli_args = parser.parse_args()

    with open(cli_args.params, 'r') as f:
        arg_list = json.load(f)

    save = []
    sleep_time = int(cli_args.time)
    for args in arg_list:
        try:
            page_source = run_driver(args, sleep_time)
            listings = get_listings_from_source(page_source)

            output = {
                'params': args,
                'results': listings
            }
            save.append(output)
        except Exception as e:
            print(f'ERROR: Encountered {e}\nUsing {args}')

        time.sleep(sleep_time) #sleep some more

    with open(cli_args.output, 'w') as f:
        json.dump(save, f, indent=4)


if __name__ == '__main__':
    main()
