"""
This is a scraping file for car.gr that takes data from every car posting into the cars website section.
The output of this script is a dataframe with each car's specs.

"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

import requests
import random

def GET_UA():
    uastrings = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",\
                "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",\
                "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36"\
                ]
 
    return random.choice(uastrings)
headers = {'User-Agent': GET_UA()}
usedCarsdf = pd.DataFrame(columns=['price','year','manufacturer','model','condition', 'category','mileage',
                              'fuel_type','consumption','engine_size','horse_power','transmission','colour','drive_type','doors',
                              'seats','website_views','euro_standard','area','airbags','emissions','extras','rim_size','circulation_tax','url'])



page = requests.get("https://www.car.gr/classifieds/cars/?lang=en&pg=1",headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')


max_pages = int(soup.find('ul', class_='pagination pull-right').find_all('a')[-2].text)



# for i in range(max_pages):
for i in range(11):
    print('Page:',i, 'status:', page.status_code)
    headers = {'User-Agent': GET_UA()}
    list_page = requests.get("https://www.car.gr/classifieds/cars/?lang=en&pg="+str(i+1), headers=headers)
    soup_list_page = BeautifulSoup(list_page.content, 'html.parser')
    link_list = [a.get('href') for a in soup_list_page.find_all('a', class_="vehicle list-group-item clsfd_list_row")]
    specs = {}
    for link in link_list:
        subpage = requests.get("https://www.car.gr"+link + "?lang=en", headers=headers)
        print(subpage.status_code)
        # if subpage.status_code==429:
        #     print(subpage.__dict__)
        soup_subpage = BeautifulSoup(subpage.content, 'html.parser')

        breadcrumbs = soup_subpage.find_all('a', class_="carzilla-breadcrumb__anchor carzilla-breadcrumb__anchor--active")
        manufacturer = ""
        model = ""
        year = ""
        if len(breadcrumbs)>5:    
            manufacturer = breadcrumbs[3].get('aria-label')
            model = breadcrumbs[4].get('aria-label')
            year = breadcrumbs[5].get('aria-label')

        
        table_spec_rows = soup_subpage.find_all('tr')
        for row in table_spec_rows:
            spec_name_value = row.find_all('td')
            specs[re.sub('\s+',' ',spec_name_value[0].text.strip())] =re.sub('\s+',' ',spec_name_value[1].text.strip())    #index 0 is the spec name and index 1 is the value 
        
        
        extras_list = soup_subpage.find('ul', class_='row px-2')
        extras=""
        if extras_list is not None:
            extras = ",".join([re.sub('\s+',' ',a.text.strip()) for a in extras_list.find_all('li')])
        
        if specs.get('Consumption') is not None:
            consumption =specs.get('Consumption')[specs.get('Consumption').find('(Motorway)') + 13:specs.get('Consumption').find('(Mixed)')-1]
            

        usedCarsdf = usedCarsdf.append(
            {'price': re.sub(r"[€.]",  '',specs.get('Price')).strip() if specs.get('Price') is not None else specs.get('Price'),
             'year': year,
             'manufacturer': manufacturer,
             'model': model,
             'condition': specs.get('Condition'),
             'category' : specs.get('Category'),
             'mileage' : re.sub(r"km|\.",  '',specs.get('Mileage')).strip() if specs.get('Mileage') is not None else specs.get('Mileage'),
             'fuel_type' : specs.get('Fuel type'),
             'consumption' : re.sub(r"\,",  '.',specs.get('Consumption')[specs.get('Consumption').find('(Motorway)') + 13:specs.get('Consumption').find('(Mixed)')-1]) if specs.get('Consumption') is not None else specs.get('Consumption'),
             'engine_size' : re.sub(r"cc|\.",  '',specs.get('Engine')).strip() if specs.get('Engine') is not None else specs.get('Engine'),
             'horse_power' : re.sub(r"bhp|\.",  '',specs.get('Power')).strip() if specs.get('Power') is not None else specs.get('Power'),
             'transmission' : specs.get('Transmission'),
             'colour' : specs.get('Color'),
             'drive_type' : specs.get('Drive type'),
             'doors' : specs.get('Doors'),
             'seats' : specs.get('Seats'),
             'website_views' : specs.get('Views'),
             'euro_standard' : specs.get('Euro standard'),
             'area' : specs.get('Address'),
             'extras' : extras,
             'emissions' : re.sub(r"g/km|\.",  '',specs.get('Emissions (co2)')).strip() if specs.get('Emissions (co2)') is not None else specs.get('Emissions (co2)'),
             'airbags' : specs.get('Airbags'),
             'rim_size' : specs.get('Rim size'),
             'circulation_tax' : specs.get('Circulation tax'),
             'url' : "https://www.car.gr"+ link + "?lang=en",


             }
            ,ignore_index=True
        )

usedCarsdf.to_csv ("usedCars.csv", index = False, header=True)
        
        
        


