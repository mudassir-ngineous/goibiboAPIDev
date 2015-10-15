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

def getFlightsResp(source,destination,date,return_date):
    source_iata =None
    destination_iata = None
    flag = 0
    for iata_dict in iata_dicts:
        if(iata_dicts[iata_dict]['city'].lower()==source.lower()):
            source_iata = iata_dicts[iata_dict]['code']
            flag = flag | 1

        if(iata_dicts[iata_dict]['city'].lower()==destination.lower()):
            destination_iata = iata_dicts[iata_dict]['code']
            flag = flag | 2

        if(flag == 3):
            break

    if(source_iata and destination_iata):
        url = config['goibibo']['urls']['base_url'] + config['goibibo']['urls']['flight_search']
        data = {
            "app_id" : config['goibibo']['app_id'],
            "app_key": config['goibibo']['app_key'],
            "format": "json",
            "source":source_iata,
            "destination":destination_iata,
            "dateofdeparture":date,
            "seatingclass":"E",
            "adults":1,
            "children":0,
            "infants":0
        }
        if(return_date):
            data['dateofarrival'] = return_date
        resp = requests.get(url,params=data)
        resp_data = resp.json().get('data')
        onward_flights_resp = resp_data['onwardflights']
        return_flights_resp = resp_data['returnflights']

        onward_flights = []
        return_flights = []
        if(len(onward_flights_resp) > 0):
            for flight in onward_flights_resp:
                onward_flights.append(getFlightObj(flight))

        if(len(return_flights_resp) > 0):
            for flight in return_flights_resp:
                return_flights.append(getFlightObj(flight))

        return {
            'onward':onward_flights,
            'return':return_flights
        }

def getBusesResp(source,destination,date,return_date):
    flag = 0;
    for city_key in BusCity:

        if(city_key.lower() == source.lower()):
            source = BusCity[city_key]
            flag = flag | 1

        if(city_key.lower() == destination.lower()):
            destination = BusCity[city_key]
            flag = flag | 2

        if(flag == 3):
            break

    url = config['goibibo']['urls']['base_url'] + config['goibibo']['urls']['bus_search']
    data = {
            "app_id" : config['goibibo']['app_id'],
            "app_key": config['goibibo']['app_key'],
            "format": "json",
            "source":source,
            "destination":destination,
            "dateofdeparture":date,
        }
    if(return_date):
        data['dateofarrival'] = return_date

    resp = requests.get(url,params=data)

    resp_data = resp.json().get('data')
    onward_flights_resp = resp_data['onwardflights']
    return_flights_resp = resp_data['returnflights']

    onward_flights = []
    return_flights = []
    if(len(onward_flights_resp) > 0):
        for flight in onward_flights_resp:
            onward_flights.append(getBusObj(flight))

    if(len(return_flights_resp) > 0):
        for flight in return_flights_resp:
            return_flights.append(getBusObj(flight))

    return {
            'onward':onward_flights,
            'return':return_flights
        }

def getBusObj(flight):
    flight_obj = {}
    if('TravelsName' in flight):
        flight_obj['bus_name'] = flight['TravelsName']

    if('fare' in flight and 'totalfare' in flight['fare']):
        flight_obj['fare'] = flight['fare']['totalfare']

    if('DepartureTime' in flight):
        flight_obj['departure_time'] = flight['DepartureTime']

    if('ArrivalTime' in flight):
        flight_obj['arrival_time'] = flight['ArrivalTime']

    if('duration' in flight):
        flight_obj['duration'] = flight['duration']

    if('busCondition' in flight):
        flight_obj['bus_condition'] = flight['busCondition']

    if('BusType' in flight):
        flight_obj['type'] = flight['BusType']

    if('BPPrims' in flight):
        flight_obj['boarding_points'] = flight['BPPrims']

    if('DPPrims' in flight):
        flight_obj['drop_points'] = flight['DPPrims']

    return flight_obj

def getFlightObj(flight):
    flight_obj = {}
    if('airline' in flight):
        flight_obj['airline'] = flight['airline']
    if('fare' in flight and 'totalfare' in flight['fare']):
        flight_obj['fare'] = flight['fare']['totalfare']

    if('DepartureTime' in flight):
        flight_obj['departure_time'] = flight['DepartureTime']

    if('ArrivalTime' in flight):
        flight_obj['arrival_time'] = flight['ArrivalTime']

    if('duration' in flight):
        flight_obj['duration'] = flight['duration']

    if('stops' in flight):
        flight_obj['stops'] = flight['stops']

    return flight_obj

def giveCommonResponse(source,destination,data,return_date=None):
    return {
        "flights": getFlightsResp(source,destination,data,return_date),
        "buses": getBusesResp(source,destination,data,return_date),
        "hotels": getHotelResp(destination)
    }