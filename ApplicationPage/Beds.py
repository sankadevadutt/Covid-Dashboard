import dash_html_components as html
from math import radians, cos, sin, asin, sqrt
import pandas as pd
import numpy as np
from pymongo import MongoClient
import tweepy
import re
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


# Data From MongoDB
client = MongoClient(
    "mongodb+srv://Covidadmin:coadmin@cluster0.vqxrk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
result = client['db']['dbinformation'].find(filter={'type': 'data'})
lt = []
load = False
for i in result:
    state_name = i['state'][0]['name']
    district2 = i['state'][0]['district'][0]['name']
    hospital_name = i['state'][0]['district'][0]['hospital'][0]['name']
    contact = i['state'][0]['district'][0]['hospital'][0]['contact_details']
    requirement = i['state'][0]['district'][0]['hospital'][0]['Requirement'][0]['name']
    last = i['state'][0]['district'][0]['hospital'][0]['Requirement'][0]['update']
    total = i['state'][0]['district'][0]['hospital'][0]['Requirement'][0]['availability'][0]['Total']
    vacant = i['state'][0]['district'][0]['hospital'][0]['Requirement'][0]['availability'][0]['Vacant']
    if isinstance(hospital_name, str):
        lt.append([hospital_name, state_name, district2, requirement, total, vacant, contact, last])
    else:
        for j in range(0, len(hospital_name)):
            lt.append(
                [hospital_name[j], state_name, district2[j], requirement[j], total[j], vacant[j], contact[j], last[j]])
mongodata = pd.DataFrame(lt,
                         columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                  'Contact Details',
                                  'Last Updated On'], dtype=object)

mongodata['State'] = [convert_camel(str(i)) for i in list(mongodata['State'])]
mongodata['District'] = [convert_camel(str(i)) for i in list(mongodata['District'])]

ltmong = mongodata.values.tolist()
data1 = {}
for i in ltmong:
    data1[i[0]] = {}
    data1[i[0]]['beds'] = 0
for i in ltmong:
    if 'bed' in i[3].lower() and 'total' not in i[3].lower():
        try:
            data1[i[0]]['beds'] += int(i[5])
        except:
            continue

mongodata = mongodata[mongodata['State'] == convert_camel(Application.address['state'])]
mongodata = mongodata[mongodata['District'] == convert_camel(Application.address['state_district'])]

locn = locationFinder.locn2
if locn['Latitude'].isnull().values.any():
    locn["Latitude"].fillna(method='ffill', inplace=True)

if locn['Longitude'].isnull().values.any():
    locn["Longitude"].fillna(method='ffill', inplace=True)
locn = locn.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})

imagedata = pd.read_csv("C:/Users/Devadutt/PycharmProjects/App/assets/imagedata.csv", index_col=0)
if imagedata['Image URL'].isnull().values.any():
    imagedata = imagedata.replace(to_replace=np.nan,
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
    distances = locn.apply(
        lambda row: round(dist(float(lat), float(long), float(row['lat']), float(row['lon'])), 2),
        axis=1)
    locn['Distance'] = list(distances)
    return locn


dd_nearesr = find_nearest(Application.locn[0], Application.locn[1]).sort_values(by='Distance')
dd_nearesr = dd_nearesr[dd_nearesr['Distance'] <= 100.0]

hospital_names = list(set(list(mongodata['Hospital Name']) + list(dd_nearesr['Hospital Name'])))

final_data = []
for i in hospital_names:
    if i in data1.keys():
        final_data.append([i, data1[i]['beds']])

df_final = pd.DataFrame(final_data, columns=['Hospital Name', 'Beds'])
df_final = df_final.sort_values(by='Beds', ascending=False)

hospital_names_final = list(df_final['Hospital Name'])

lis = []
st = ''
for i in range(min(len(hospital_names_final), 150)):

    imagelist = list(imagedata[imagedata['Hospital Name'] == hospital_names_final[i]]['Image URL'])
    if len(imagelist) > 0:
        st = imagelist[0]
    else:
        st = 'https://thumbs.dreamstime.com/b/hospital-building-modern-parking-lot-59693686.jpg'

    lis.append(
        html.A(
            html.Div([
                html.Div([
                    html.Img(
                        src=st,
                        width='160px', height='80px', style={'border-radius': '6px'}),
                    html.H4(html.B(convert_camel(hospital_names_final[i])), style={'font-size': 'x-small'}),
                    html.P("Available Beds : " + (str(data1[hospital_names_final[i]]['beds'])),
                           style={'font-size': 'xx-small'}),
                ], className='container22'),
            ], className='card', style={'textAlign': 'center'}), href='/info ' + str(hospital_names_final[i]),
            style={'color': 'black'})
    )

# twitter data
consumer_key, consumer_secret = "DIn9Kje8ey1LJb071txkm2pLD", "hhFR43QKoyceqZHPIoHuLPtdtE6riSf4zmHK86xc5Xx5pVcGh6"
Access_token, Access_secret = "1199257788-THONLqx7SuxKuduOwb1DfWKQdbRWch0sIVeDHla", "2qIWnYAV0qQaZ6cQQl5yTxTjuPEfsk6rD7P1JiUKKmNBC"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(Access_token, Access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)


# Formating date type
def datetype(tweet_data):
    for tweet in tweet_data:
        tweet[2] = tweet[2].strftime('%d-%m-%Y  %H:%M:%S')


# Inserting Verified column
def verified_check(tweet_data):
    verified = ['verified', 'confirm']
    Invalid = ['not verified', 'notverified', 'unconfirmed', 'uncertified', 'unauthorized', 'unauthenticated',
               'unrecognised', 'unverified']
    for tweet in tweet_data:
        check = False
        text = tweet[3]
        text = text.lower()
        for i in verified:
            if i in text:
                check = True
        for i in Invalid:
            if i in text:
                check = False
        if check == True:
            tweet.insert(4, 'Yes')
        else:
            tweet.insert(4, 'No')


# Inserting requirement and state
def req_state(tweet_data, Requirement, State, City):
    for tweet in tweet_data:
        tweet.insert(4, Requirement)
        tweet.append(State)
        tweet.append(City)


# Retrieve phone number from text
def phonenumber(tweet_data):
    pattern = r"\+91\d{10}"
    pattern2 = r"\d{10}"
    for tweet in tweet_data:
        text = tweet[3]
        phonenumbers = re.findall(pattern, text)
        for strin in phonenumbers:
            text = text.replace(strin, '')
        phonenumbers2 = re.findall(pattern2, text)
        phonenumbers.extend(phonenumbers2)
        tweet.append(phonenumbers)


# getting tweet url
def tweeturl(tweet_data):
    common_tweet = 'https://twitter.com/twitter/statuses/'
    for tweet in tweet_data:
        url = common_tweet + "{}"
        url = url.format(tweet[0])
        tweet.append(url)


# Other links retriving
def other_links(tweet_data):
    pattern3 = r"([a-zA-Z]{2,20})(://)([\w_-]+(?:(?:\.[\w_-]+)?))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"
    for tweet in tweet_data:
        text = tweet[3]
        whatsapp_link = re.findall(pattern3, text)
        whatsapp = []
        for i in range(0, len(whatsapp_link)):
            x = ""
            if whatsapp_link:
                for linkin in whatsapp_link[i]:
                    x = x + linkin
                whatsapp.append(x)
        tweet.append(whatsapp)


tweet = pd.read_csv('C:/Users/Devadutt/PycharmProjects/App/assets/twitter_Telangana_Hyderabad_icu_bed.csv', index_col=0)
tweet = tweet[tweet['Available_State'] == Application.address['state']]
if not tweet.empty:
    tweet = tweet[tweet['Available_City'] == Application.address['state_district']]
tweet_content = []
if not tweet.empty:
    tweet_content = list(tweet['Tweet_Content'])
    links = list(tweet['Tweet_URL'])
for i in range(len(tweet_content)):
    lis.append(
        html.A(
            html.Div([
                html.Div([
                    html.Img(
                        src='/assets/twitter_icon.png',
                        width='20px', height='20px', style={'float': 'right'}),
                    html.Br(),
                    html.H4(tweet_content[i], style={'font-size': 'x-small'}),
                ], className='container22', style={'textAlign': 'center'}),
            ], className='card', style={'textAlign': 'center'}), href=links[i], target="_blank",
            style={'color': 'black'})
    )
tweet2 = pd.read_csv('C:/Users/Devadutt/PycharmProjects/App/assets/twitter_data1.csv')
tweet2 = tweet2[tweet2['State'] == Application.address['state']]
if not tweet2.empty:
    tweet2 = tweet2[tweet2['City'] == Application.address['state_district']]
tweet_content = []
if not tweet2.empty:
    tweet_content = list(tweet2['Tweet content'])
    links = list(tweet2['URL'])
    req = list(tweet2['Requirement'])

for i in range(len(tweet_content)):
    if 'beds' in str(req[i]).lower():
        lis.append(
            html.A(
                html.Div([
                    html.Div([
                        html.Img(
                            src='/assets/twitter_icon.png',
                            width='20px', height='20px', style={'float': 'right'}),
                        html.Br(),
                        html.H4(tweet_content[i], style={'font-size': 'x-small'}),
                    ], className='container22', style={'textAlign': 'center'}),
                ], className='card', style={'textAlign': 'center'}), href=links[i], target="_blank",
                style={'color': 'black'})
        )

tweet2 = pd.read_csv('C:/Users/Devadutt/PycharmProjects/App/assets/twitter_data2.csv')
tweet2 = tweet2[tweet2['State'] == Application.address['state']]
if not tweet2.empty:
    tweet2 = tweet2[tweet2['City'] == Application.address['state_district']]
tweet_content = []
if not tweet2.empty:
    tweet_content = list(tweet2['Tweet content'])
    links = list(tweet2['URL'])
    req = list(tweet2['Requirement'])

for i in range(len(tweet_content)):
    if 'beds' in str(req[i]).lower():
        lis.append(
            html.A(
                html.Div([
                    html.Div([
                        html.Img(
                            src='/assets/twitter_icon.png',
                            width='20px', height='20px', style={'float': 'right'}),
                        html.Br(),
                        html.H4(tweet_content[i], style={'font-size': 'x-small'}),
                    ], className='container22', style={'textAlign': 'center'}),
                ], className='card', style={'textAlign': 'center'}), href=links[i], target="_blank",
                style={'color': 'black'})
        )

all_data = []
lt = []
Requirements = ["oxygen cylinder", "oxygen concentrator", "general bed", "icu bed", "oxygen bed", "ventilator",
                "ambulance", "blood", "amphotericin", "remdesivir", "tocilizumab"]
header_cols = ['Id', 'Username', 'Tweet_posted_date', 'Tweet_Content', 'Requirement', 'Verified',
               'Tweet_posted_location', 'Available_State', 'Available_City', 'Phone_number', 'Tweet_URL',
               'Other_links']

for i in Requirements:
    if 'beds' in i.lower():
        query = f'(verified OR available) ({Application.address["state"]} OR {Application.address["state_district"]}) {i} -\"Seeking\"-\"want\"-\"Requires\"-\"wanted\"-\"Require\"-\"Required\"-\"Please\"-\"Plz\"-\"Urgent\"-\"need\"-\"Any verified lead\"-\"not available\"-\"filter:retweets\"'
        tweets = tweepy.Cursor(api.search_tweets, tweet_mode='extended', q=query, lang='en').items(10)
        tweet_data = [[tweet.id, tweet.user.screen_name, tweet.created_at, tweet.full_text, tweet.user.location] for
                      tweet in tweets]
        datetype(tweet_data)
        verified_check(tweet_data)
        req_state(tweet_data, i, Application.address['state'], Application.address['state_district'])
        phonenumber(tweet_data)
        tweeturl(tweet_data)
        other_links(tweet_data)
        all_data.append(tweet_data)

for i in all_data:
    if len(i) > 0:
        for j in i:
            lt.append(j)

tweet = pd.DataFrame(lt, columns=header_cols, dtype=object)
tweet_content = []
if not tweet.empty:
    tweet_content = list(tweet['Tweet_Content'])
    links = list(tweet['Tweet_URL'])
for i in range(len(tweet_content)):
    lis.append(
        html.A(
            html.Div([
                html.Div([
                    html.Img(
                        src='/assets/twitter_icon.png',
                        width='20px', height='20px', style={'float': 'right'}),
                    html.Br(),
                    html.H4(tweet_content[i], style={'font-size': 'x-small'}),
                ], className='container22', style={'textAlign': 'center'}),
            ], className='card', style={'textAlign': 'center'}), href=links[i], target="_blank",
            style={'color': 'black'})
    )

if len(lis) == 0:
    lis.append('No Data Available')

layout = html.Div(children=lis)
