from geopy.geocoders import Nominatim
import pymongo
import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings('ignore')
app = Nominatim(user_agent="xyz")

# Hospital Data Retriving MongoDB
client = pymongo.MongoClient(
    "mongodb+srv://Covidadmin:coadmin@cluster0.vqxrk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
result = client['db']['dbinformation'].find(filter={'type': 'data'})
lt = []
load = False
for i in result:
    state_name = i['state'][0]['name']
    district = i['state'][0]['district'][0]['name']
    hospital_name = i['state'][0]['district'][0]['hospital'][0]['name']
    contact = i['state'][0]['district'][0]['hospital'][0]['contact_details']
    requirement = i['state'][0]['district'][0]['hospital'][0]['Requirement'][0]['name']
    last = i['state'][0]['district'][0]['hospital'][0]['Requirement'][0]['update']
    total = i['state'][0]['district'][0]['hospital'][0]['Requirement'][0]['availability'][0]['Total']
    vacant = i['state'][0]['district'][0]['hospital'][0]['Requirement'][0]['availability'][0]['Vacant']
    if isinstance(hospital_name, str):
        lt.append([hospital_name, state_name, district, requirement, total, vacant, contact, last])
    else:
        for j in range(0, len(hospital_name)):
            lt.append(
                [hospital_name[j], state_name, district[j], requirement[j], total[j], vacant[j], contact[j], last[j]])
df = pd.DataFrame(lt,
                  columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant', 'Contact Details',
                           'Last Updated On'], dtype=object)

# Data Extraction and beds data

lt = df.values.tolist()

data = {}
for i in lt:
    data[i[0]] = {}
    data[i[0]]['beds'] = 0
    data[i[0]]['state'] = i[1]
    data[i[0]]['district'] = i[2]
    data[i[0]]['contact'] = i[6]
for i in lt:
    if 'bed' in i[3].lower() and 'total' not in i[3].lower():
        try:
            data[i[0]]['beds'] += int(i[5])
        except:
            continue

# Retriving location data from MongoDb

result = client['db']['dbinformation'].find(filter={'type': 'location'})
lt = []
for i in result:
    hn = i['latitudelongitude'][0]['Hospital Name']
    latitude = i['latitudelongitude'][0]['lat-long'][0]['latitude']
    longitude = i['latitudelongitude'][0]['lat-long'][0]['longitude']
    state = data[hn]['state']
    district = data[hn]['district']
    if latitude == 'None':
        latitude = np.nan
    if longitude == 'None':
        longitude = np.nan
    lt.append([hn, float(latitude), float(longitude), state, district])
locn = pd.DataFrame(lt, columns=['Hospital Name', 'Latitude', 'Longitude', 'State', 'District'])

# Entry of new hospital locn data

# Initialize Nominatim API
geolocator = Nominatim(user_agent="MyApp")
information = client['db']['dbinformation']


def getlocn(i):
    district = data[i]['district']
    state = data[i]['state']
    hn = i.replace('.', ' ')
    hn = hn.strip()
    hospital_name = (hn.split(','))[0]
    if pd.isna(district):
        address = f'{hospital_name} , {state} , India'
    else:
        address = f'{hospital_name} , {state} , {district} ,India'
    try:
        location = geolocator.geocode(address)
        data[i]['latlong'] = [location.latitude, location.longitude]
    except:
        if pd.isna(district):
            address = f'{state} , India'
        else:
            address = f'{state} , {district} , India'
        try:
            location = geolocator.geocode(address)
            data[i]['latlong'] = [location.latitude, location.longitude]
        except:
            address = f'{state} , India'
            try:
                location = geolocator.geocode(address)
                data[i]['latlong'] = [location.latitude, location.longitude]
            except:
                data[i]['latlong'] = [None, None]
    record = {
        'type': 'location',
        'latitudelongitude': [
            {
                'Hospital Name': i,
                'lat-long': [
                    {
                        'latitude': str(data[i]['latlong'][0]),
                        'longitude': str(data[i]['latlong'][1]),
                    }
                ]
            }
        ]
    }
    information.insert_one(record)


hospital = list(data.keys())
indb = list(locn['Hospital Name'])
for i in indb:
    hospital.remove(i)

for i in hospital:
    getlocn(i)

# Retriving location data from MongoDb after new addition

result2 = client['db']['dbinformation'].find(filter={'type': 'location'})
lt2 = []
for i in result2:
    hn = i['latitudelongitude'][0]['Hospital Name']
    latitude = i['latitudelongitude'][0]['lat-long'][0]['latitude']
    longitude = i['latitudelongitude'][0]['lat-long'][0]['longitude']
    state = data[hn]['state']
    district = data[hn]['district']
    if latitude == 'None':
        latitude = np.nan
    if longitude == 'None':
        longitude = np.nan
    lt2.append([hn, float(latitude), float(longitude), state, district])
locn2 = pd.DataFrame(lt, columns=['Hospital Name', 'Latitude', 'Longitude', 'State', 'District'])