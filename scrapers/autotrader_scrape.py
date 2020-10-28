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


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0", }
usedCarsdf = pd.DataFrame(columns=['car_id','price','year','manufacturer','model','condition', 'category','mileage',
                              'fuel_type','consumption','engine_size', 'engine_power','transmission','doors', 'extras',
                              'seats','area', 'latLong','emissions','annual_tax','url'])



page = requests.get("https://www.autotrader.co.uk/car-search?postcode=E1%206AN&year-to=2020&include-delivery-option=on&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&advertising-location=at_cars&page=1",headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')

max_pages = int(soup.find('li', class_='paginationMini__count').text.split(" ")[3])


price, year, manufacturer, model, condition, category, mileage, fuel_type, consumption, engine_size = ([] for i in range(10))
transmission, doors, seats, area_list, emissions, annual_tax, url, car_id, engine_power, extras, latLong_list = ([] for i in range(11))

try:

    for i in range(50):
        
        print('page:',i+1)
        list_page = requests.get("https://www.autotrader.co.uk/car-search?postcode=E1%206AN&year-to=2020&include-delivery-option=on&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&advertising-location=at_cars&page="+str(i+1), headers=headers)
        while str(list_page.status_code).startswith('4'):
            sleep(3*60)
            list_page = requests.get("https://www.autotrader.co.uk/car-search?postcode=E1%206AN&year-to=2020&include-delivery-option=on&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&advertising-location=at_cars&page="+str(i+1), headers=headers)

        soup_list_page = BeautifulSoup(list_page.content, 'html.parser')
        link_list = [a.get('href') for a in soup_list_page.find_all('a', class_="js-click-handler listing-fpa-link tracking-standard-link")]
        
        for link in link_list:
            

            basic_json = requests.get("https://www.autotrader.co.uk/json/fpa/initial/"+link[link.find('car-details')+12:link.find('include-delivery-option')-1], headers=headers)
            while str(basic_json.status_code).startswith('4'):
                print("Had a 4.. answer!")
                sleep(60*3)
                basic_json = requests.get("https://www.autotrader.co.uk/json/fpa/initial/"+link[link.find('car-details')+12:link.find('include-delivery-option')-1], headers=headers)
            car_json = basic_json.json()
            
            specs = car_json['pageData']['tracking']
            area=""
            if car_json.get('seller') is not None: 
                if car_json.get('seller').get('location') is not None:
                    area = car_json.get('seller').get('location').get('town')
                    latLong = car_json.get('seller').get('location').get('latLong')
                    



            specification_json = requests.get("https://www.autotrader.co.uk/json/fpa/lazy/"+link[link.find('car-details')+12:link.find('include-delivery-option')-1], headers=headers)
            while str(specification_json.status_code).startswith('4'):
                print("Had a 4.. answer!")
                sleep(60*3)
                specification_json = requests.get("https://www.autotrader.co.uk/json/fpa/lazy/"+link[link.find('car-details')+12:link.find('include-delivery-option')-1], headers=headers)
            car_tech_specs = specification_json.json()



            if car_tech_specs.get('advert').get('combinedFeatures') is not None:
                extras.append(','.join(car_tech_specs.get('advert').get('combinedFeatures')[:]))
            else:
                extras.append(None)

            if car_tech_specs.get('vehicle').get('enginePower') is not None:
                power = car_tech_specs.get('vehicle').get('enginePower')
                if power[-2:-1] == "PS":
                    engine_power.append(float(power[0:-2])*0.98632)         #engine power in PS
                else:
                    engine_power.append(float(power[0:-3]))                 #engine power in BHP
            else:
                engine_power.append(None)


            car_id.append(specs.get('ad_id'))
            price.append(specs.get('vehicle_price')) 
            year.append(specs.get('vehicle_year'))
            manufacturer.append(specs.get('make')) 
            model.append(specs.get('model'))
            condition.append(car_json.get('vehicle').get('condition'))
            category.append(specs.get('body_type'))
            mileage.append(float(specs.get('mileage'))*1.609 if specs.get('mileage') is not None else specs.get('mileage'))
            fuel_type.append(specs.get('fuel_type'))
            consumption.append(235.214583/float(specs.get('average_mpg')) if specs.get('average_mpg') is not None else specs.get('average_mpg'))
            engine_size.append(specs.get('engine_size'))
            transmission.append(specs.get('gearbox'))
            doors.append(specs.get('number_of_doors'))
            seats.append(specs.get('number_of_seats'))
            area_list.append(area)
            latLong_list.append(latLong)
            emissions.append(specs.get('co2_emissions'))
            annual_tax.append(specs.get('annual_tax'))
            url.append("https://www.autotrader.co.uk"+ link)   
finally:
    usedCarsdf = usedCarsdf.append(pd.DataFrame(
    {   'car_id' : car_id,
        'price': price,
        'year': year,
        'manufacturer': manufacturer,
        'model': model,
        'condition': condition,
        'category' : category,
        'mileage' : mileage,
        'fuel_type' : fuel_type,
        'consumption' : consumption,
        'engine_size' : engine_size,
        'engine_power' : engine_power,
        'extras' : extras,
        'transmission' : transmission,
        'doors' : doors,
        'seats' : seats,
        'area' : area_list,
        'latLong' : latLong_list,
        'emissions' : emissions,
        'annual_tax' : annual_tax,
        'url' : url,
    }), ignore_index=True)

    del price, year, manufacturer, model, condition, category, mileage, fuel_type, consumption, engine_size
    del transmission, doors, seats, area, emissions, annual_tax, url, engine_power, extras, latLong_list

    usedCarsdf = usedCarsdf.drop_duplicates(subset=["car_id"])
    usedCarsdf.to_csv ("usedCars.csv", index = False, header=True)
        

