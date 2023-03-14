# -*- coding: utf-8 -*-

#import libraries
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
import requests
import plotly.express as px
from urllib.parse import quote
from pymongo import MongoClient, GEOSPHERE
from tqdm import tqdm
import pandas as pd
import random 
import re
tqdm.pandas()

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import pymongo
import plotly.express as px
from urllib.parse import quote
import os
import requests

#global variables to store hotel informations
hotel_name=[]
Rating=[]
Reviews=[]
Amenities=[]
Address=[]
PlacesNearby=[]

class getHotels:
    
    
    def get_search_results():
        #Hit the search page, load results and save the html file
        driver = webdriver.Chrome()
        driver.get("https://www.hotels.com/Hotel-Search?adults=2&children=&destination=San%20Francisco%2C%20California%2C%20United%20States%20of%20America&endDate=2023-04-04&latLong=&mapBounds=&pwaDialog&regionId=3132&rfrrid=TG.LP.Hotels.Hotel&semdtl=&sort=RECOMMENDED&startDate=2023-04-03&theme=&useRewards=false&userIntent=")
        for i in range(1,9):
            elements = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "//button[@data-stid='show-more-results']")))
            for elem in elements:
                elem.click()
            print(i)
            time.sleep(10)
        h = driver.page_source
        f = open("Hotels.html", "x")
        with open("Hotels.html", "w", encoding="utf-8") as f:
            f.write(h)
        f.close()
        time.sleep(10)
        driver.quit()
    
    
    
    #from the saved file, get the urls of the hotels and save the individual pages for each hotel on your local disk
    
    def get_hotel_pages():
        with open("Hotels.html") as fp:
            soup = bs(fp, 'html.parser')
        #print(soup)
        data = soup.findAll('div',attrs={'data-stid':'property-listing-results'})
        hotels=[]
        for div in data:
            links = div.findAll('a',attrs={'data-stid':'open-hotel-information'})
            for a in links:
                hotels.append(a['href'])
        
        more_data = soup.findAll('div',attrs={'class':'lazyload-wrapper', 'data-stid':'open-hotel-information'})
        for div in more_data:
            #links = div.findAll('a',attrs={'data-stid':'open-hotel-information'})
            for a in div:
                hotels.append(a['href'])
        hotels = list(set(hotels))
        #print(len(hotels))
        counter = len(hotels)
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        #for url in hotels:
        for i in range(counter):
            content=requests.get(("https://www.hotels.com/"+hotels[i]),headers=headers)
            soup=bs(content.content,'html.parser')
            filename = "HotelInfo\HotelNo_"+str(i)+".html"
            with open(filename, "w", encoding = 'utf-8') as file:
                file.write(str(soup.prettify()))
            time.sleep(5)
     
    
    #read the individual files stores and extract information for each hotel
   
    
    def extract_hotel_details():
        for i in range(0,500):
            filename = "HotelInfo\HotelNo_"+str(i)+".html"
            with open(filename,encoding="utf8") as fp:
                soup = bs(fp, 'html.parser')
                try:
                    data = soup.findAll('div',attrs={'data-stid':'content-hotel-title'})
                    for j in data:
                        #hotel_name.append((j.find('h1')).text)
                        x = (j.find('h1')).text
                        hotel_name.append((x.strip()))
                        #x = re.search("([a-zA-z ,])", x)
                except:
                    print('do nothing'+str(i))
                    continue
                try:
                    data = soup.findAll('div',attrs={'data-stid':'content-hotel-reviewsummary'})
                    for j in data:
                        x=j.find('h3')
                        if(x is None):
                            Rating.append('')
                        else:
                            x = (j.find('h3')).getText()
                            Rating.append((x.strip()))
                except:
                    print('do nothing'+str(i))
                try:
                    data = soup.findAll('div',attrs={'data-stid':'content-hotel-reviewsummary'})
                    for j in data:
                        x=j.find('h4')
                        if(x is None):
                            Reviews.append('')
                        else:
                            x = (j.find('h4')).get_text()
                            x = re.search('(\d+)', x)
                            review=int(x.group(1))
                            Reviews.append(review)
                except:
                    print('do nothing'+str(i))
                #data = soup.findAll('div',attrs={'data-stid':'hotel-amenities-list'})
                try:
                    data = soup.find('div',attrs={'data-stid':'hotel-amenities-list'}).findAll('li',attrs={'role':'listitem'})
                    amen = []
                    for j in data:
                        x=j.find('span')
                        #print(x.text())
                        if(x is None):
                            #Amenities.append([])
                            print('do nothing'+str(i))
                        else:
                            #x = (j.find('span')).getText()
                            x=j.find('span').get_text().strip()
                            #print(x)
                            amen.append(x)
                        #amen.append(j.find('span').text())
                    Amenities.append(amen)
                except:
                    #Amenities.append([])
                    print('in except'+str(i))
                try:
                    data = soup.findAll('div',attrs={'data-stid':'content-hotel-address'})
                    for j in data:
                        if(j is None):
                            Address.append('')
                        else:
                            x=j.get_text().strip()
                            Address.append(x)
                except:
                    #Amenities.append([])
                    print('in except'+str(i))
                try:
                    data1 = soup.findAll('span',attrs={'class':'uitk-layout-flex-item uitk-layout-flex-item-flex-grow-1'})
                    places=[]
                    for i in data1:
                        x=i.get_text().strip()
                        if(x == ''):
                           print('do nothing'+str(i))
                        else:
                            places.append(x)
                    if(places == []):
                        print('do nothing')
                    else:
                        PlacesNearby.append(places)
                except:
                    #PlacesNearby.append([])
                    print('do nothing'+str(i))
    
    def get_collection():
        mongodb_client = MongoClient('mongodb+srv://vjmandekar:WG6zfdo0f0GD8mi3@ddrcluster.vnnxiy3.mongodb.net/?retryWrites=true&w=majority')
        dbname = mongodb_client['SanFranciscoTravelogue']
        col = dbname['SFHotels']
        return col
    
    def insert_into_hotel_collection():
        hotels = getHotels.get_collection()
        for i in range(0,498):
            insert_dict={}
            insert_dict['HotelName'] = hotel_name[i]
            insert_dict['Address'] = Address[i]
            insert_dict['Ratings'] = Rating[i]
            insert_dict['NumberOfReviews'] = Reviews[i]
            insert_dict['Amenities'] = Amenities[i]        
            insert_dict['PlacesNearby'] = PlacesNearby[i]
            hotels.insert_one(insert_dict)
        #print(insert_dict)
        
    def extract_geo_location():
        hotels_col = getHotels.get_collection()
        base_url = "http://api.positionstack.com/v1/forward?access_key={}&query=".format("da1a74fdf5303a10fa697bccb1e5120a")
        hotels = hotels_col.find()
        #print(hotels)
        
        for hotel_dict in hotels:
            try:
                address = hotel_dict['Address']
                print(address)
                url_gen = base_url + quote(address)
                for i in range(10):
                    try:
                        geo_dict=requests.get(url_gen).json()['data'][0]
                        lat = geo_dict['latitude']
                        long = geo_dict['longitude']
                        hotels_col.update_one(
                            {'_id': hotel_dict['_id']},
                            {'$set': {'geo_location': {'type':'Point','coordinates': [long,lat]}}}
                        )
        
                        time.sleep(5)
                        break
                    except:
                        continue
                        time.sleep(5)
            except:
                continue
            
    def create_index():
        hotels_col = getHotels.get_collection()
        hotels_col.create_index([("geo_location", GEOSPHERE)])
    
    
    def show_viz():
        hotels_col = getHotels.get_collection()
        df = pd.DataFrame(list(hotels_col.find()))
        df[['Type','Coordinates','unwanted']] = df['geo_location'].apply(pd.Series)
        df.drop(columns='unwanted',inplace=True)
        df[['Latitude','Longitude']]=df['Coordinates'].apply(pd.Series)
        
        fig = px.scatter_mapbox(df, 
                            lat="Latitude", 
                            lon="Longitude", 
                            hover_name="HotelName", 
                            hover_data=["Ratings","Address","NumberOfReviews","Amenities","PlacesNearby"],
                            zoom=8, 
                            height=800,
                            width=800)
    
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.write_html("HotelView.html")
        
    def find_nearby():
        hotels_col = getHotels.get_collection()
        hotels =hotels_col.find({'geo_location':{'$nearSphere':{'$geometry':{'type':'point','coordinates':[-122.274993,37.788543]},'$maxDistance':5000}}})
        for i in hotels:
            print(i['HotelName'])

    

            
class restaurants_extraction():
    
    def __init__(self):
        self.client = MongoClient('mongodb+srv://vjmandekar:WG6zfdo0f0GD8mi3@ddrcluster.vnnxiy3.mongodb.net/?retryWrites=true&w=majority')
        pass
    
    def search_func(self,
                    search_location = "San Francisco",
                    search_type = "Restaurants"   
                    ):
        """
        Search Location - Location of the search term
        Search Type     - What type of search 
        """
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            time.sleep(5)
            driver.get("https://www.tripadvisor.com/")
            search_element=driver.find_elements(By.XPATH,"//input[@role='searchbox']")[1]
            time.sleep(5)
            search_location = search_location
            search_type = search_type
            search_text = search_location+' '+search_type
            search_element.send_keys(search_text)
            time.sleep(5)
            search_element.send_keys(Keys.RETURN)
            time.sleep(5)
            return driver
        except Exception as e:
            print("Launching failed")
            print(e)
        
    

    def restaurants_extract(self,driver):
        page_num = 1
        restaurants=[]
        proj_db = self.client["trip_adv_proj"]
        tripadv_col = proj_db["trip_adv_rest"] 
        folder_path = os.path.join(os.getcwd() + r'\trip_advisor_files\pages')

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        while True:
            print(page_num)
            try:
                time.sleep(random.randint(5,10))
                
                file_path = os.path.join(folder_path+r'\tripadv_rest_{}.html'.format(page_num))

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)

                soup = BeautifulSoup(driver.page_source, "html.parser")

                for restaurant in soup.find_all("div", {"class": "QEXGj"}):
                    try:
                        name = restaurant.find("div", {"class": "RfBGI"}).text.strip()
                    except:
                        pass
                    try:
                        url = "https://www.tripadvisor.com" + restaurant.find("div", {"class": "RfBGI"}).find('a').get("href")
                    except:
                        pass
                    try:
                        rating = restaurant.find("span", {"class": "GmcgY"}).find('svg').get("aria-label")
                    except:
                        pass
                    try:
                        reviews = int(restaurant.find("span", {"class": "IiChw"}).text.strip().replace("reviews", "").replace(",", "").strip())
                    except:
                        pass
                    restaurant_dict = {
                        "restaurant_name": name,
                        "restaurant_url": url,
                        "restaurant_rating": rating,
                        "restaurant_reviews_count": reviews,
                    }
                    restaurants.append(restaurant_dict)
                
                    tripadv_col.insert_one(restaurant_dict)

                page_num+=1
                driver.find_element(By.XPATH,"//a[@data-page-number='{}']".format(page_num)).click()
                time.sleep(random.randint(5,10))
                continue
            except Exception as e:
                driver.quit()
                print(e)
                pass

    def clean_collection(self):
        proj_db = self.client["trip_adv_proj"]
        tripadv_col = proj_db["trip_adv_rest"]

        df_rest = pd.DataFrame(list(tripadv_col.find()))
        df_rest.drop_duplicates(subset=['restaurant_url'],inplace=True)

        rest_dict = df_rest.to_dict('records')

        tripadv_col_clean= proj_db['tripadv_col_cleaned']
        tripadv_col_clean.insert_many(rest_dict)

    def rest_collection_cleaned(self):
        try:
            proj_db = self.client["trip_adv_proj"]
            tripadv_col = proj_db["tripadv_col_cleaned"]
            df_rest = pd.DataFrame(list(tripadv_col.find()))
            
            proj_db = self.client["trip_adv_proj"]
            tripadv_col = proj_db["trip_adv_more_info"]
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

            time.sleep(5)
            rest_values = []
            folder_path = os.path.join(os.getcwd() + r'\trip_advisor_files\restaurants')
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            for rest in tqdm(df_rest.to_dict('records')):
                driver.get(rest['restaurant_url'])
                time.sleep(random.randint(5,10))
                
                file_path = os.path.join(folder_path+r'\tripadv_rest_{}.html'.format(rest['restaurant_name']))
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                
                soup = BeautifulSoup(driver.page_source, "html.parser")
                
                try:
                    dol_cuisine = []
                    for ele in soup.find_all("a",{"class":"dlMOJ"}):
                        dol_cuisine.append(ele.text)
                    rest['dol_cuisine'] = dol_cuisine
                except:
                    pass
            
                try:
                    tel_web = []
                    for i in soup.find_all("span",{"class":"cNFrA"}):
                        if i.text == 'Website':
                            tel_web.append(i.find('a').get('href'))
                        else:
                            tel_web.append(i.text)
                    rest['rest_details'] = tel_web
                except:
                    pass
                
                tripadv_col.insert_one(rest)
                
                rest_values.append(rest)
            print("Completed the each rest extraction process")
        except Exception as e:
            print(e)
            print("Error in each running restaurant")


    def extract_restaurant_details(self,rest_dict):
        
        if len(rest_dict['dol_cuisine'])>0:
            if '$' in rest_dict['dol_cuisine'][0]:
                rest_dict['cost'] = rest_dict['dol_cuisine'][0]
            try:
                for ele in rest_dict['dol_cuisine']:
                    if '$' not in ele:
                        rest_dict['cuisine']=''.join(ele)
            except:
                pass
        
        rest_details = rest_dict['rest_details']
        
        if len(rest_details) > 0:
            rank_match = re.search(r'#(\d+)', rest_details[0])
            
            if rank_match:
                rest_dict['rank'] = int(rank_match.group(1))
            
            address_match = re.search(r'\d+ .+, [A-Z]{2} \d+', rest_details[1])
            
            if address_match:
                rest_dict['rest_address'] = address_match.group()
        
            if (len(rest_details) > 2) and (rest_details[2] != '+ Add phone number'):
                rest_dict['rest_phone'] = rest_details[2] 
        
            if (len(rest_details) > 3) and (rest_details[3] != '+ Add website'):
                rest_dict['rest_website'] = rest_details[3] 
        
        del rest_dict['dol_cuisine'] 
        del rest_dict['rest_details']
        
        return rest_dict

    def insert_new_extract(self):
        proj_db = self.client["trip_adv_proj"]
        tripadv_col = proj_db["trip_adv_more_info"]
        trip_adv_new = proj_db["final_trip_adv_rest"]
        rest_list = list(tripadv_col.find())
        for data_dict in rest_list:
            new_data_dict = self.extract_restaurant_details(data_dict)
            trip_adv_new.insert_one(new_data_dict)

    def extract_geo_location(self,access_key):
        proj_db = self.client["trip_adv_proj"]
        tripadv_col = proj_db["final_trip_adv_rest"]
        base_url = "http://api.positionstack.com/v1/forward?access_key={}&query=".format(access_key)
        for rest_dict in tqdm(tripadv_col.find()):
            try:
                address = rest_dict['rest_address']
                url_gen = base_url + quote(address)
                for i in range(10):
                    try:
                        geo_dict=requests.get(url_gen).json()['data'][0]
                        lat = geo_dict['latitude']
                        long = geo_dict['longitude']
                        tripadv_col.update_one(
                            {'_id': rest_dict['_id']},
                            {'$set': {'geo_location': {'latitude': lat, 'longitude': long}}}
                        )
        
                        time.sleep(10)
                        break
                    except:
                        continue
                        time.sleep(5)
            except:
                continue
    
    def update_geo_location(self):
        rest_db = self.client["trip_adv_proj"]
        rest_collection = rest_db["final_trip_adv_rest"]
        for doc in rest_collection.find({}):
            if 'geo_location' in doc:
                lat = doc['geo_location']['latitude']
                lng = doc['geo_location']['longitude']
                point = {'type': 'Point', 'coordinates': [lng, lat]}
                rest_collection.update_one({'_id': doc['_id']}, {'$set': {'geo_location': point}})

        rest_collection.create_index([('geo_location', pymongo.GEOSPHERE)])

    def show_viz(self):
        proj_db = self.client["trip_adv_proj"]
        tripadv_col = proj_db["final_trip_adv_rest"]
        df = pd.DataFrame(list(tripadv_col.find()))
        df[['latitude', 'longitude','unwanted']] = df['geo_location'].apply(pd.Series)
        df.drop(columns='unwanted',inplace=True)
        fig = px.scatter_mapbox(df, 
                            lat="latitude", 
                            lon="longitude", 
                            hover_name="restaurant_name", 
                            hover_data=["rank","restaurant_rating", "restaurant_reviews_count","cuisine"],
                            zoom=8, 
                            height=800,
                            width=800)

        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.write_html("rest_view.html")

              
    def main_func(self):
        driver =  self.search_func(search_location = "San Francisco",search_type = "Restaurants")
        self.restaurants_extract(driver)
        self.clean_collection()
        self.rest_collection_cleaned()
        self.insert_new_extract()
        self.extract_geo_location(access_key='')
        self.update_geo_location()
        
        #self.show_viz()

if __name__ == '__main__':
    ### Hotels
    getHotels.get_search_results()
    getHotels.get_hotel_pages()
    getHotels.extract_hotel_details()    
    getHotels.insert_into_hotel_collection()
    getHotels.extract_geo_location()
    getHotels.create_index()
    getHotels.show_viz()

    ### Restaurants
    restaurants_extraction.main_func()







    
