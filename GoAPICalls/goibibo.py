import sys
import requests

sys.path.append("../")
from Configs.server_conf import config
from Configs.busCityList import BusCity
from Configs.IATADatabase import iata_dicts

def getFormattedText(string):
    return string.replace("\n","").replace("\r","").replace("\"","").strip()

fp = open("/home/mudassir/goibibo/GoAPICalls/city_list.csv")
lines = fp.readlines()
hotel_cities = {}
for line in lines:
    id = getFormattedText(line.split(",")[1])
    hotel_cities[id] = {}
    hotel_cities[id]['city_name'] = getFormattedText(line.split(",")[0])
    hotel_cities[id]['domestic_flag'] = int(getFormattedText(line.split(",")[2]))

def getHotelResp(city):
    target_city_id = None
    for id in hotel_cities:
        if(hotel_cities[id]['city_name'].lower() == city.lower()):
            target_city_id = id

    url = config['goibibo']['urls']['base_url'] + config['goibibo']['urls']['hotel_search']
    data = {
        "app_id" : config['goibibo']['app_id'],
        "app_key": config['goibibo']['app_key'],
        "city_id" : target_city_id
    }
    resp = requests.get(url,params=data)
    resp_data = resp.json().get('data')
    hotels = []
    for key in resp_data:
        hotel = {}
        hotel_geo_node = resp_data[key]['hotel_geo_node']
        hotel_data_node = resp_data[key]['hotel_data_node']

        hotel['id'] = hotel_geo_node['_id']
        hotel['name'] = hotel_data_node['name']
        hotel['location'] = hotel_geo_node['location']
        if('property_budget_category' in hotel_geo_node['tags'] ):
            hotel['category'] = hotel_geo_node['tags']['property_budget_category']

        if('gir_data' in hotel_data_node['extra'] and  'hotel_rating' in hotel_data_node['extra']['gir_data']):
            hotel['rating'] = hotel_data_node['extra']['gir_data']['hotel_rating']
        hotel['facilities'] = hotel_data_node['facilities']

        if('pin' in hotel_data_node['loc']):
            hotel['pincode'] = hotel_data_node['loc']['pin']
        hotels.append(hotel)

    return hotels

def getFlightsResp(source,destination,data,return_date):
    source_iata =None
    destination_iata = None
    flag = 0
    for iata_dict in iata_dicts:
        if(iata_dict['city'].lower()==source.lower()):
            source_iata = iata_dict['code']
            flag = flag | 1

        if(iata_dict['city'].lower()==destination.lower()):
            destination_iata = iata_dict['code']
            flag = flag | 2

        if(flag == 3):
            break

    if(source_iata and destination_iata):
        url = url = config['goibibo']['urls']['base_url'] + config['goibibo']['urls']['flight_search']
    pass

def getBusesResp(source,destination,data,return_date):
    pass

def giveCommonResponse(source,destination,data,return_date=None):
    return {
        "flights": getFlightsResp(source,destination,data,return_date),
        "buses": getBusesResp(source,destination,data,return_date),
        "hotels": getHotelResp(destination)
    }