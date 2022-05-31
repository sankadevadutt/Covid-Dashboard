import dash_html_components as html
from geopy.geocoders import Nominatim
import geocoder

import warnings

warnings.filterwarnings('ignore')
count = 0
while 1:
    try:
        g = geocoder.ip('me')
        locn = g.latlng
        geoLoc = Nominatim(user_agent="GetLoc")
        s = str(locn[0]) + " ," + str(locn[1])
        locname = geoLoc.reverse(s)
        address = locname.raw['address']
        break
    except:
        if count > 5:
            locn[0] = 17.3850
            locn[1] = 78.4867
            address = {'amenity': 'University College for Women', 'road': 'Womens College to Esamia Bazar Road',
                       'neighbourhood': 'Esamia Bazaar', 'suburb': 'Ward 78 Gunfoundry',
                       'city_district': 'Greater Hyderabad Municipal Corporation Central Zone', 'city': 'Hyderabad',
                       'county': 'Nampally mandal', 'state_district': 'Hyderabad', 'state': 'Telangana',
                       'ISO3166-2-lvl4': 'IN-TG', 'postcode': '500095', 'country': 'India', 'country_code': 'in'}
            break
        count += 1

layout = html.Div([
    html.Br(),
    html.H1("Welcome", style={"color": "#221869", 'margin-left': '30px'}),
    html.Br(),
    html.Div([
        html.Font([
            html.Img(src='/assets/location1.png', width='30px', height='35px'),
            f'You are in {address["state_district"]},{address["state"]}'
        ], style={'font-size': 'small', 'margin-left': '50px'}),
        html.Br(),
        html.H4('Choose requirement'),
    ], className='text', style={'position': 'absolute', 'left': '250px', 'top': '65px'}),

    html.Div([
        html.Img(src='/assets/notification.png', width='30px', height='30px'),
    ], className='image', style={'position': 'absolute', 'right': '100px', 'top': '20px'}),
    html.Div([
        html.Img(src='/assets/user.png', width='30px', height='30px'),
    ], className='image', style={'position': 'absolute', 'right': '50px', 'top': '20px'}),

    html.A([
        html.Div([
            html.Img(src='/assets/NH.png', width='70px', height='70px'),
            html.Div([
                html.P(html.Font(html.B('Nearest Hospital'), style={'color': '#000000', 'font-size': 'x-small'}))
            ], className='container', style={'position': 'absolute', 'left': '5px', 'top': '50px'}),
        ], className='polaroid1', style={'position': 'absolute', 'left': '250px', 'top': '170px'}),
    ], href='/NearestHospital'),

    html.A([
        html.Div([
            html.Img(src='/assets/Beds.png', width='70%', height='75%'),
            html.Div([
                html.P(html.Font(html.B('Beds'), style={'color': '#000000', 'font-size': 'x-small'}))
            ], className='container', style={'position': 'absolute', 'left': '30px', 'top': '50px'}),
        ], className='polaroid2', style={'position': 'absolute', 'left': '400px', 'top': '170px'}),
    ], href='/Beds'),

    html.A([
        html.Div([
            html.Div(
                html.Img(src='/assets/oxygen.png', width='68%', height='68%')
                , className='image', style={'position': 'absolute', 'right': '18px', 'top': '10px'}),
            html.Div([
                html.P(html.Font(html.B('Oxygen'), style={'color': '#000000', 'font-size': 'x-small'}))
            ], className='container', style={'position': 'absolute', 'left': '27px', 'top': '50px'}),
        ], className='polaroid3', style={'position': 'absolute', 'left': '550px', 'top': '170px'}),
    ], href='/Oxygen'),

    html.A([
        html.Div([
            html.Img(src='/assets/OS.png', width='100%', height='80%'),
            html.Div([
                html.P(html.Font(html.B('Other States'), style={'color': '#000000', 'font-size': 'x-small'}))
            ], className='container', style={'position': 'absolute', 'left': '16px', 'top': '50px'}),
        ], className='polaroid4', style={'position': 'absolute', 'left': '700px', 'top': '170px'}),
    ], href='/OS'),

    html.A([
        html.Div([
            html.Img(src='/assets/GR.png', width='60%'),
            html.Div([
                html.P(html.Font(html.B('Government Regulations'), style={'color': '#000000', 'font-size': 'x-small'}))
            ], className='container', style={'position': 'absolute', 'left': '4px', 'top': '45px'}),
        ], className='polaroid5', style={'position': 'absolute', 'left': '850px', 'top': '170px'}),
    ], href='/GR'),

    html.A([
        html.Div([
            html.Img(src='/assets/ambulance.png', width='70%'),
            html.Div([
                html.P(html.Font(html.B('Ambulance'), style={'color': '#000000', 'font-size': 'x-small'}))
            ], className='container', style={'position': 'absolute', 'left': '18px', 'top': '50px'}),
        ], className='polaroid6', style={'position': 'absolute', 'left': '1000px', 'top': '170px'}),
    ], href='/ambulance'),
], className="content")
