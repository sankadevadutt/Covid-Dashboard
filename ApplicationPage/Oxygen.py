import dash_html_components as html
import tweepy
import pandas as pd
import re

from ApplicationPage import Application

import warnings
warnings.filterwarnings('ignore')


def convert_camel(st):
    st = st.strip()
    s = ''
    lt = st.split(" ")
    for var in lt:
        s += (var[0].upper() + '' + var[1:].lower() + ' ')
    return s.strip()


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


lis = []

tweet2 = pd.read_csv('C:/Users/Devadutt/PycharmProjects/App/assets/twitter_data1.csv', index_col=0)
tweet2 = tweet2[tweet2['State'] == Application.address['state']]
if not tweet2.empty:
    tweet2 = tweet2[tweet2['City'] == Application.address['state_district']]
tweet_content = []
if not tweet2.empty:
    tweet_content = list(tweet2['Tweet content'])
    links = list(tweet2['URL'])
    req = list(tweet2['Requirement'])

for i in range(len(tweet_content)):
    if 'oxygen' in str(req[i]).lower():
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
                ], className='card', style={'textAlign': 'center'}), href=links[i],
                style={'color': 'black'})
        )

tweet2 = pd.read_csv('C:/Users/Devadutt/PycharmProjects/App/assets/twitter_data2.csv', index_col=0)
tweet2 = tweet2[tweet2['State'] == Application.address['state']]
if not tweet2.empty:
    tweet2 = tweet2[tweet2['City'] == Application.address['state_district']]
tweet_content = []
if not tweet2.empty:
    tweet_content = list(tweet2['Tweet content'])
    links = list(tweet2['URL'])
    req = list(tweet2['Requirement'])

for i in range(len(tweet_content)):
    if 'oxygen' in str(req[i]).lower():
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
                ], className='card', style={'textAlign': 'center'}), href=links[i],
                style={'color': 'black'})
        )

all_data = []
lt = []
Requirements = ["oxygen cylinder", "oxygen concentrator"]
header_cols = ['Id', 'Username', 'Tweet_posted_date', 'Tweet_Content', 'Requirement', 'Verified',
               'Tweet_posted_location', 'Available_State', 'Available_City', 'Phone_number', 'Tweet_URL',
               'Other_links']

for i in Requirements:
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
    if (len(i) > 0):
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
            ], className='card', style={'textAlign': 'center'}), href=links[i],
            style={'color': 'black'})
    )

if len(lis) == 0:
    lis.append('No Data Available')

layout = html.Div(children=lis)
