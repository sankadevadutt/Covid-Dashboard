import dash_html_components as html
from math import radians, cos, sin, asin, sqrt
import pandas as pd
import numpy as np
from ApplicationPage import Application
from HelperCodes import locationFinder

import warnings
warnings.filterwarnings('ignore')


def convert_camel(st):
    st = st.strip()
    s = ''
    lt = st.split(" ")
    for var in lt:
        s += (var[0].upper() + '' + var[1:].lower() + ' ')
    return s.strip()



data = locationFinder.locn2
if data['Latitude'].isnull().values.any():
    data["Latitude"].fillna(method='ffill', inplace=True)

if data['Longitude'].isnull().values.any():
    data["Longitude"].fillna(method='ffill', inplace=True)
data = data.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})

data2 = pd.read_csv("C:/Users/Devadutt/PycharmProjects/App/assets/imagedata.csv", index_col=0)
if data2['Image URL'].isnull().values.any():
    d2 = data2.replace(to_replace=np.nan,
                      value='https://thumbs.dreamstime.com/b/hospital-building-modern-parking-lot-59693686.jpg')



def dist(lat1, long1, lat2, long2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lat1, long1, lat2, long2 = map(radians, [lat1, long1, lat2, long2])
    # haversine formula
    dlon = long2 - long1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km


def find_nearest(lat, long):
    distances = data.apply(
        lambda row: round(dist(float(lat), float(long), float(row['lat']), float(row['lon'])), 2),
        axis=1)
    data['Distance'] = list(distances)
    return data


dd = find_nearest(Application.locn[0], Application.locn[1]).sort_values(by='Distance')

hospital_names = list(dd['Hospital Name'])
distance = list(dd['Distance'])
lis = []
st = ''
for i in range(min(len(hospital_names),150)):



    l22 = list(d2[d2['Hospital Name'] == hospital_names[i]]['Image URL'])
    if(len(l22) >0):
        st = l22[0]
    else:
        st = 'https://thumbs.dreamstime.com/b/hospital-building-modern-parking-lot-59693686.jpg'

    lis.append(
        html.A(
            html.Div([
                html.Div([
                    html.Img(
                        src=st,
                        width='160px', height='80px',style={'border-radius':'6px'}),
                    html.H4(html.B(convert_camel((hospital_names[i]))), style={'font-size': 'x-small'}),
                    html.P("Within " + str(distance[i]) + " KM", style={'font-size': 'xx-small'}),
                ], className='container22'),
            ], className='card', style={'textAlign': 'center'}), href='/info ' + str(hospital_names[i]),
            style={'color': 'black'})
    )
if (len(lis) == 0):
    lis.append('No Data Available')

layout = html.Div(children=lis)
