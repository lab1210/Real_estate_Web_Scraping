import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import time

def parse_listing_data(location,max_pages=50):
    all_listings_data = []
    page_num = 0
    while page_num<max_pages:
        url = f"https://www.property24.com.ng/houses-for-sale-in-{location}?Page={page_num}"
        try:            
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html5lib')
            listings_divs = soup.select('div[class*="js_listingTile"]')

            if not listings_divs:
                break 
                
            for indv_listing in listings_divs:
                image_element = indv_listing.select_one('img[class*="pull-left"]')
                if image_element:
                    image_url=image_element.get('src','N/A')
                else:
                    image_url='N/A'
                address_element=indv_listing.select('span[class*="p24_address"]')
                if address_element:
                    address=address_element[0].text.strip()
                else:
                    address="N/A"
                price_element=indv_listing.select('span[class*="p24_price"]')
                if price_element:
                    price=price_element[0].text.strip()
                else:
                    price="N/A"
                listing_data = [address, price]
               
                description_element=indv_listing.select_one('span[class*="p24_excerpt"]')
                if description_element:
                    description=description_element.text.strip()
                else:
                    description='N/A'
                bedroom_element = indv_listing.select_one('span[title*="Bedrooms"] span')
                bath_element = indv_listing.select_one('span[title*="Bathrooms"] span')
                parking_element = indv_listing.select_one('span[title*="Parking Spaces"] span')

                bedrooms = bedroom_element.text.strip() if bedroom_element else "N/A"
                bathrooms = bath_element.text.strip() if bath_element else "N/A"
                parking_spaces = parking_element.text.strip() if parking_element else "N/A"
                
                listing_data=[image_url,address,price,bedrooms,bathrooms,parking_spaces,description]
                all_listings_data.append(listing_data)
               
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
    
locations=['lagos-p37','abuja-p20','imo-p55','oyo-p48','ogun-p49','delta-p28'] 

All_Location_data=[]
for location in locations:
    location_data=parse_listing_data(location)
    All_Location_data.extend(location_data)

if All_Location_data:
    df = pd.DataFrame(All_Location_data, columns=['image_url','address','price','bedrooms','bathrooms','parking_spaces','description'])
    df.to_excel("P24_listings.xlsx", index=False)
else:
    print('No data Found')
