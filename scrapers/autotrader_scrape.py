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


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0", }
usedCarsdf = pd.DataFrame(columns=['price','year','manufacturer','model','condition', 'category','mileage',
                              'fuel_type','consumption','engine_size','transmission','doors',
                              'seats','area','emissions','extras','annual_tax','url'])



page = requests.get("https://www.autotrader.co.uk/car-search?postcode=E1%206AN&year-to=2020&include-delivery-option=on&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&advertising-location=at_cars&page=1",headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')

max_pages = int(soup.find('li', class_='paginationMini__count').text.split(" ")[3])

for i in range(51):

    list_page = requests.get("https://www.autotrader.co.uk/car-search?postcode=E1%206AN&year-to=2020&include-delivery-option=on&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&advertising-location=at_cars&page="+str(i+1), headers=headers)
    soup_list_page = BeautifulSoup(list_page.content, 'html.parser')
    link_list = [a.get('href') for a in soup_list_page.find_all('a', class_="js-click-handler listing-fpa-link tracking-standard-link")]
    
    specs = {}
    for link in link_list:
        subpage = requests.get("https://www.autotrader.co.uk/json/fpa/initial/"+link[link.find('car-details')+12:link.find('include-delivery-option')-1], headers=headers)
        print(subpage.status_code)
        car_json = subpage.json()
        specs = car_json['pageData']['tracking']
        
        area=""
        if car_json.get('seller') is not None and car_json.get('seller').get('locations'): 
            area = car_json.get('seller').get('locations').get('town')

        usedCarsdf = usedCarsdf.append(
        {   'price': specs.get('vehicle_price'),
            'year': specs.get('vehicle_year'),
            'manufacturer': specs.get('make'),
            'model': specs.get('model'),
            'condition': car_json.get('vehicle').get('condition'),
            'category' : specs.get('body_type'),
            'mileage' : float(specs.get('mileage'))*1.609 if specs.get('mileage') is not None else specs.get('mileage'),
            'fuel_type' : specs.get('fuel_type'),
            'consumption' : 235.214583/float(specs.get('average_mpg')) if specs.get('average_mpg') is not None else specs.get('average_mpg'),
            'engine_size' : specs.get('engine_size'),
            # 'horse_power' : specs.get('vehicle_price'),
            'transmission' : specs.get('gearbox'),
            # 'colour' : specs.get('Color'),
            # 'drive_type' : specs.get('gearbox'),
            'doors' : specs.get('number_of_doors'),
            'seats' : specs.get('number_of_seats'),
            # 'website_views' : specs.get('Views'),
            # 'euro_standard' : specs.get('Euro standard'),
            'area' : area,
            
            'emissions' : specs.get('co2_emissions'),
            # 'airbags' : specs.get('Airbags'),
            # 'rim_size' : specs.get('Rim size'),
            'annual_tax' : specs.get('annual_tax'),
            'url' : "https://www.autotrader.co.uk"+ link,
        }
            ,ignore_index=True
        )

usedCarsdf.to_csv ("usedCars.csv", index = False, header=True)
