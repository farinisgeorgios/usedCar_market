"""
This is a scraping file for car.gr that takes data from every car posting into the cars website section.
The output of this script is a dataframe with each car's specs.

"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

import requests

usedCarsdf = pd.DataFrame(columns=['price','year','manufacturer','model','condition', 'category','mileage',
                              'fuel_type','consumption','engine','horse_power','transmission','colour','drive_type','doors',
                              'seats','website_views','euro_standard','area','airbags','emissions','extras'])


headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
page = requests.get("https://www.car.gr/classifieds/cars/?lang=en&pg=1",headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')


max_pages = int(soup.find('ul', class_='pagination pull-right').find_all('a')[-2].text)



for i in range(max_pages):
    print('Page:',i)
    list_page = requests.get("https://www.car.gr/classifieds/cars/?lang=en&pg="+str(i+1), headers=headers)
    soup_list_page = BeautifulSoup(list_page.content, 'html.parser')
    link_list = [a.get('href') for a in soup_list_page.find_all('a', class_="vehicle list-group-item clsfd_list_row")]
    for link in link_list:
        subpage = requests.get("https://www.car.gr"+link + "?lang=en", headers=headers)
        soup_subpage = BeautifulSoup(subpage.content, 'html.parser')

        breadcrumbs = soup_subpage.find_all('a', class_="carzilla-breadcrumb__anchor carzilla-breadcrumb__anchor--active")
        manufacturer = "None"
        model = "None"
        year = "None"
        if len(breadcrumbs)>4:    
            manufacturer = breadcrumbs[3].get('aria-label')
            model = breadcrumbs[4].get('aria-label')
            year = breadcrumbs[5].get('aria-label')

        specs = {}
        table_spec_rows = soup_subpage.find_all('tr')
        for row in table_spec_rows:
            spec_name_value = row.find_all('td')
            specs[re.sub('\s+',' ',spec_name_value[0].text.strip())] =re.sub('\s+',' ',spec_name_value[1].text.strip())    #index 0 is the spec name and index 1 is the value 
        
        
        extras_list = soup_subpage.find('ul', class_='row px-2')
        extras="None"
        if extras_list is not None:
            extras = ",".join([re.sub('\s+',' ',a.text.strip()) for a in extras_list.find_all('li')])
        

        usedCarsdf = usedCarsdf.append(
            {'price': specs.get('Price'),
             'year': year,
             'manufacturer': manufacturer,
             'model': model,
             'condition': specs.get('Condition'),
             'category' : specs.get('Category'),
             'mileage' : specs.get('Mileage'),
             'fuel_type' : specs.get('Fuel type'),
             'consumption' : specs.get('Consumption'),
             'engine' : specs.get('Engine'),
             'horse_power' : specs.get('Power'),
             'transmission' : specs.get('Transmission'),
             'colour' : specs.get('Colour'),
             'drive_type' : specs.get('Drive type'),
             'doors' : specs.get('Doors'),
             'seats' : specs.get('Seats'),
             'website_views' : specs.get('Views'),
             'euro_standard' : specs.get('Euro standard'),
             'area' : specs.get('Address'),
             'extras' : extras,
             'emissions' : specs.get('Emissions (co2)'),
             'airbags' : specs.get('Airbags'),

             }
            ,ignore_index=True
        )

usedCarsdf.to_csv ("usedCars.csv", index = False, header=True)
        
        
        


