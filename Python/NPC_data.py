import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import time

def parse_listing_data(location,max_pages=50):
    all_listings_data = []
    page_num = 0
    while page_num<max_pages:
        url = f"https://nigeriapropertycentre.com/for-sale/{location}?page={page_num}"
        try:            
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html5lib')
            listings_divs = soup.select('div[itemprop="itemListElement"]')

            if not listings_divs:
                break 
                
            for indv_listing in listings_divs:
                image_element = indv_listing.select_one('img[itemprop="image"]')
                if image_element:
                    image_url=image_element.get('src','N/A')
                else:
                    image_url='N/A'
                address_element=indv_listing.select('strong')
                if address_element:
                    address=address_element[0].text.strip()
                else:
                    address="N/A"
                price_element=indv_listing.select('span.price')
                if price_element:
                    currency=price_element[0].text.strip()
                    numb = price_element[1].text.strip()
                    price=f"{currency} {numb}"
                else:
                    price="N/A"
                listing_data = [address, price]
                check_element=indv_listing.select('h4[class*=content-title]')
                if check_element:
                    check=check_element[0].text.strip()
                else:
                    check="N/A"
                description_element=indv_listing.select_one('div.description.hidden-xs p')
                if description_element:
                    description=description_element.text.strip()
                else:
                    description='N/A'
                bedroom_element = indv_listing.select_one('ul.aux-info li:nth-of-type(1) span')
                bath_element = indv_listing.select_one('ul.aux-info li:nth-of-type(2) span')
                toilet_element = indv_listing.select_one('ul.aux-info li:nth-of-type(3) span')
                parking_element = indv_listing.select_one('ul.aux-info li:nth-of-type(4) span')

                bedrooms = bedroom_element.text.strip() if bedroom_element else "N/A"
                bathrooms = bath_element.text.strip() if bath_element else "N/A"
                toilets = toilet_element.text.strip() if toilet_element else "N/A"
                parking_spaces = parking_element.text.strip() if parking_element else "N/A"
                
                if 'land' not in check.lower() and 'plot' not in check.lower():
                    listing_data=[image_url,address,price,bedrooms,bathrooms,toilets,parking_spaces,description]
                    all_listings_data.append(listing_data)
                else:
                    print(f"Listing with address '{address}' excluded because it is land.")
            page_num += 1    
            time.sleep(2)  # Add a delay between requests
            print(f"Processed page {page_num} for {location}.")
        except requests.ConnectionError:
            print("Connection error. Retrying after 5 sec ...")
            time.sleep(5)
        except Exception as e:
            print(f"Error:{e}")
            break
    return(all_listings_data)
    
locations=['abia','abuja','adamawa','akwa-ibom','anambra','bauchi','bayelsa','benue','borno','cross-river','delta','ebonyi','edo','ekiti','enugu','gombe','imo','jigawa','kaduna','kano','katsina','kebbi','kogi','kwara','lagos','nassarawa','niger','ogun','ondo','osun','oyo','plateau','rivers','sokoto','taraba','yobe','zamfara'] 

All_Location_data=[]
for location in locations:
    location_data=parse_listing_data(location)
    All_Location_data.extend(location_data)

if All_Location_data:
    df = pd.DataFrame(All_Location_data, columns=['image_url','address','price','bedrooms','bathrooms','toilets','parking_spaces','description'])
    df.to_excel("nigeriapropertycentre_listings.xlsx", index=False)
else:
    print('No data Found')
