"""
This is a scraping file for car.gr that takes data from every car posting into the cars website section.
The output of this script is a dataframe with each car's specs.

"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import requests
import json
import random
from time import sleep
from scrapers.autotrader_pages import getCarsFromAllPages

def scrape_autotrader():

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0", }
    usedCarsdf = pd.DataFrame(columns=['car_id','price','year','manufacturer','model','condition', 'category','mileage',
                                'fuel_type','consumption','engine_size', 'engine_power','transmission','doors', 'extras',
                                'seats','area', 'latLong','emissions','annual_tax','url'])


    brands = pd.read_csv('brands.csv')
    brands_list = ["".join(x) for x in brands.values]
    

    years = [str(i) for i in range(1998,2020)]
    years.append('new')

    prices = [str(p) for p in range(500,10000,500)] + [str(p) for p in range(10000,30000,2000)] + [str(p) for p in range(30000,80000,5000)]

    try:

        for brand in brands_list:
            brand_link = "https://www.autotrader.co.uk/car-search?sort=relevance&postcode=e16an&radius=1500&make=" + str(brand)
            brand_page = requests.get(brand_link,headers=headers)
            brand_soup = BeautifulSoup(brand_page.content, 'html.parser')
            brand_max_pages = int(brand_soup.find('li', class_='paginationMini__count').text.split(" ")[3])
            print("Found ", brand_max_pages," pages in brand ",brand)
            if brand_max_pages > 100:
                for year in years:
                    year_link = brand_link + '&year-from='+ year + '&year-to=' + year
                    year_page = requests.get(year_link,headers=headers)
                    year_soup = BeautifulSoup(year_page.content, 'html.parser')
                    year_max_pages = int(year_soup.find('li', class_='paginationMini__count').text.split(" ")[3])
                    print("Found ", year_max_pages," pages in year ",year)
                    if year_max_pages > 100 :
                        for p in range(len(prices)-1):
                            price_link = year_link + '&price-from='+ prices[p] + '&price-to=' + prices[p+1]
                            price_page = requests.get(price_link,headers=headers)
                            price_soup = BeautifulSoup(price_page.content, 'html.parser')
                            price_max_pages = int(price_soup.find('li', class_='paginationMini__count').text.split(" ")[3])
                            print("Found ", price_max_pages," pages in price ",prices[p],"-",prices[p+1])
                            usedCarsdf_return = getCarsFromAllPages(price_link, min(price_max_pages,100), usedCarsdf)     #to prevent looping through all pages, in case they are more than 100
                            usedCarsdf = usedCarsdf.append(usedCarsdf_return)
                    else:
                        usedCarsdf_return = getCarsFromAllPages(year_link, year_max_pages, usedCarsdf)
                        usedCarsdf = usedCarsdf.append(usedCarsdf_return)
            else:
                usedCarsdf_return = getCarsFromAllPages(brand_link, brand_max_pages, usedCarsdf)
                usedCarsdf = usedCarsdf.append(usedCarsdf_return)
    finally:
        usedCarsdf = usedCarsdf.drop_duplicates(subset=["car_id"])
        usedCarsdf.to_csv ("usedCars2.csv", index = False, header=True)
        

