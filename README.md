# SF Wanderer

### Executive Summary
This project aims at creating a database of tourist activities, restaurants, and hotels in San Francisco. The websites Travel Advisor and Hotels.com have been scraped to collect the details of the top 300 destinations, 3801 restaurants and 500 hotels in San Francisco. In the end, it would be leveraged to find the nearest restaurant based on your current destination (vice-versa) and distance to your hotel.

### Programming language and libraries
- Python
- Beautiful soup
- Requests
- Selenium
- Position stack api
- Mongodb


### Introduction to Data
The data is collected through Trip Advisor which is a leading travel company as well as Hotels.com. All information about things to do, hotel and restaurants in San Francisco are scraped from these websites.
- For things to do in SF, a total of 300 tourist attractions are collected. The collected information contains name of the site, website address, star ratings, trip advisor ratings, top 3 customer reviews, image URL, description, admission cost, address and geolocation.
- For restaurants, a total of 3801 restaurants are collected. The collected information contains the restaurant name and their website url, rating and number of reviews, cuisine and costs, address and geo-locations.
- For hotels, a total of 500 hotels in and around San Francisco have been scraped from Hotels.com. The information collected include hotel name, address, star ratings, number of reviews, amenities, places nearby and the geolocation.

### Business Case
The dataset provides a holistic view of the information needed for a traveler to make easier and optimized choices. 
- The business can provide this information in the form of a map that contains all the details in a graphical format. A visual representation is easier for comprehension as well as promotes quick decision making.
- In another use-case, this data can be used by businesses to find a location that attracts most tourists. Areas that have tourist destinations and not enough restaurants or hotels would be a nice spot to start a new eatery. This visualization would help filter out a small area out of a big city to start a business. Further research can be done by businesses to identify a fitting place.
- Similar platforms present today contain such information in the form of text. User must search for a specific location to see some results. There is no platform available today which shows all information in one viewport based on location proximity. Using this dataset, an interactive dashboard can be created with images of the place so user can make a choice quickly without getting into the specific pages of the location.


### Sample Restaurant View:
<img width="803" alt="Screenshot 2023-06-25 at 8 14 02 PM" src="https://github.com/Aish26/tripadv_scraping/assets/27972590/48d0b8fc-6fbe-466c-b8dc-46ec157aa90e">

### Sample Hotel View:
<img width="807" alt="Screenshot 2023-06-25 at 8 16 39 PM" src="https://github.com/Aish26/tripadv_scraping/assets/27972590/9889eae7-f498-4ba5-ac6e-a03623740187">



