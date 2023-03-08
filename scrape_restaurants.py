from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from time import sleep
import pandas as pd
from tqdm import tqdm
import numpy as np
import random 
import os
import re
tqdm.pandas()
import pymongo
import plotly.express as px
from urllib.parse import quote
import requests
client = pymongo.MongoClient("mongodb://localhost:27017/")


def search_func(
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
    
   

def restaurants_extract(driver):
    page_num = 1
    restaurants=[]
    proj_db = client["trip_adv_proj"]
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

def clean_collection():
    proj_db = client["trip_adv_proj"]
    tripadv_col = proj_db["trip_adv_rest"]

    df_rest = pd.DataFrame(list(tripadv_col.find()))
    df_rest.drop_duplicates(subset=['restaurant_url'],inplace=True)

    rest_dict = df_rest.to_dict('records')

    tripadv_col_clean= proj_db['tripadv_col_cleaned']
    tripadv_col_clean.insert_many(rest_dict)

def rest_collection_cleaned():
    try:
        proj_db = client["trip_adv_proj"]
        tripadv_col = proj_db["tripadv_col_cleaned"]
        df_rest = pd.DataFrame(list(tripadv_col.find()))
        
        proj_db = client["trip_adv_proj"]
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


def extract_restaurant_details(rest_dict):
    
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

def insert_new_extract():
    proj_db = client["trip_adv_proj"]
    tripadv_col = proj_db["trip_adv_more_info"]
    trip_adv_new = proj_db["trip_adv_rest_final"]
    rest_list = list(tripadv_col.find())
    for data_dict in rest_list:
        new_data_dict = extract_restaurant_details(data_dict)
        trip_adv_new.insert_one(new_data_dict)

def extract_geo_location(access_key):
    proj_db = client["trip_adv_proj"]
    tripadv_col = proj_db["trip_adv_rest_final"]
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

def show_viz():
    proj_db = client["trip_adv_proj"]
    tripadv_col = proj_db["trip_adv_rest_final"]
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


if __name__ == "__main__":
    driver =  search_func(search_location = "San Francisco",search_type = "Restaurants")
    restaurants_extract(driver)
    clean_collection()
    rest_collection_cleaned()
    insert_new_extract()
    extract_geo_location(access_key='')
    show_viz()