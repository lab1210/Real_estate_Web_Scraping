import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import time

def parse_listing_data(location):
    all_listings_data = []
    page_num = 0
    while True:
        url = f"https://www.propertypro.ng/property-for-sale/in/{location}?page={page_num}"
        try:            
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html5lib')
            listings_divs=soup.select('div[class~="single-room-sale"][class~="listings-property"]')
            if not listings_divs:
                break 
                
            for indv_listing in listings_divs:
                image_element = indv_listing.select_one('img[class="listings-img"]')
                if image_element:
                    image_url=image_element.get('data-src','N/A')
                else:
                    image_url='N/A'
                address_element=indv_listing.select('h4')
                if(len(address_element)==1):
                    address=address_element[0].text.strip()
                elif(len(address_element)>1):
                    address=address_element[1].text.strip()
                else:
                    address="N/A"
                price_element=indv_listing.select('h3[class*=listings-price]')
                if price_element:
                    price = price_element[0].text.strip()
                else:
                    price="N/A"
                listing_data = [address, price]
                check_element=indv_listing.select('h3[class*=listings-property-title2]')
                if check_element:
                    check=check_element[0].text.strip()
                else:
                    check="N/A"
                utilities = indv_listing.select('div[class*=fur-areea]')[0].text.strip().split('\n')
                listing_data.extend(utilities)
                description = indv_listing.select('div[class*=result-list-details]')[0].p.text.strip().replace('Read more', '').replace('FOR RENT: ', '')
                
                utilities = indv_listing.select('div[class*=fur-areea]')
                if utilities:
                    utilities_text = utilities[0].text.strip().split('\n')
                    beds = 0
                    baths = 0
                    toilets = 0
                    for util in utilities_text:
                        if "beds" in util:
                            try:
                                beds = int(util.split()[0])
                            except ValueError:
                                beds=0
                        elif "baths" in util:
                            try:
                                baths = int(util.split()[0])
                            except ValueError:
                                baths=0
                        elif "Toilets" in util:
                            try:
                                toilets = int(util.split()[0])
                            except ValueError:
                                toilets=0
                    if beds > 0 and baths > 0 and toilets > 0:
                        description_element = indv_listing.select('div[class*=result-list-details] p')
                        if description_element:
                            description = description_element[0].text.strip().replace('Read more', '').replace('FOR RENT: ', '')
                            if 'land' not in check.lower() and 'plot' not in check.lower():
                                extra = indv_listing.select('div[class*=furnished-btn]')
                                if extra:
                                    extra_text = extra[0].text.strip().replace('\n', ' ')
                                    listing_data = [image_url,address, price, beds, baths, toilets, extra_text + description]
                                    all_listings_data.append(listing_data)
                    else:
                        print(f"Listing with address '{address}' excluded due to zero beds, baths, and toilets.")
                else:
                    print("Utilities not found for a listing.")
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
    
locations=['abia','abuja','akwa-ibom','anambra','bayelsa','cross-river','delta','ebonyi','edo','ekiti','enugu','imo','kaduna','kano','kogi','kwara','nassarawa','niger','ogun','ondo','osun','oyo','plateau','rivers'] 
# locations=['lagos'] 

All_Location_data=[]
for location in locations:
    location_data=parse_listing_data(location)
    All_Location_data.extend(location_data)

if All_Location_data:
    df = pd.DataFrame(All_Location_data, columns=['image_url','address', 'price', 'beds', 'baths', 'toilets', 'extra'])
    df.to_excel("PropertyPro_listings_all_locations.xlsx", index=False)
else:
    print('No data Found')
