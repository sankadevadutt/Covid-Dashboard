import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
from ApplicationPage import Ambulance, Beds, Application, Oxygen, NearestHospital, GovernmentRegulations, OtherStates
from HelperCodes import locationFinder
from app import app
import ApplicationPage.Application
import pymongo
import pandas as pd
import numpy as np
import homePage

import warnings

warnings.filterwarnings('ignore')


def convert_camel(st):
    st = st.strip()
    s = ''
    lt = st.split(" ")
    for var in lt:
        s += (var[0].upper() + '' + var[1:].lower() + ' ')
    return s.strip()


client = pymongo.MongoClient(
    "mongodb+srv://Covidadmin:coadmin@cluster0.vqxrk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
result = client['db']['dbinformation'].find(filter={'type': 'data'})
lt = []
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
df2 = pd.DataFrame(lt,
                   columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant', 'Contact Details',
                            'Last Updated On'], dtype=object)

ltmong = df2.values.tolist()
databeds = {}
for i in ltmong:
    i[0] = i[0].strip()
    databeds[i[0]] = {}
    databeds[i[0]]['beds'] = 0
for i in ltmong:
    if 'bed' in i[3].lower() and 'total' not in i[3].lower():
        try:
            databeds[i[0]]['beds'] += int(i[5])
        except:
            continue

data2 = pd.read_csv("assets/imagedata.csv", index_col=0)
if data2['Image URL'].isnull().values.any():
    d22 = data2.replace(to_replace=np.nan,
                        value='https://thumbs.dreamstime.com/b/hospital-building-modern-parking-lot-59693686.jpg')

data = locationFinder.locn2
data['Latitude'] = data.groupby(['State', 'District']).Latitude.apply(lambda x: x.fillna(x.mean()))
data['Longitude'] = data.groupby(['State', 'District']).Longitude.apply(lambda x: x.fillna(x.mean()))
if data['Latitude'].isnull().values.any():
    data["Latitude"].fillna(method='ffill', inplace=True)

if data['Longitude'].isnull().values.any():
    data["Longitude"].fillna(method='ffill', inplace=True)
data = data.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})

app.layout = html.Div([
    html.Div([
        html.Div([
            html.A(html.Img(src='assets/Applicationpic.png',
                            style={'width': '40px', 'height': '35px'}), href="/main"),
        ], className="polaroid",
            style={'width': '60px', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)',
                   'textAlign': 'center', 'border-radius': '5px', 'padding': '5px', 'Allign': 'center'}),
        html.Br(),
        html.Hr(),
        html.A([
            html.Br(),
            html.Img(src='assets/homelogo.png',
                     style={'width': '25px', 'height': '25px'}),
        ], href="/main", style={'display': 'block', 'color': 'black', 'padding': '16px', 'text-decoration': ' none',
                                'textAlign': 'center'}),

        html.A([
            html.Br(),
            html.Img(src='assets/appslogo.png',
                     style={'width': '20px', 'height': '20px'}),
        ], href="/Application",
            style={'display': 'block', 'color': 'black', 'padding': '16px', 'text-decoration': 'none',
                   'textAlign': 'center'}),

        html.A([
            html.Br(),
            html.Img(src='assets/userslogo.png',
                     style={'width': '20px', 'height': '20px'}),
        ], href="#contact",
            style={'display': 'block', 'color': 'black', 'padding': '16px', 'text-decoration': ' none',
                   'textAlign': 'center'}),

        html.A([
            html.Br(),
            html.Img(src='assets/settingslogo.png',
                     style={'width': '25px', 'height': '25px'}),
        ], href="#settings",
            style={'display': 'block', 'color': 'black', 'padding': '16px', 'text-decoration': ' none',
                   'textAlign': 'center'}),

    ], className="sidebar",
        style={'margin': '0', 'padding': '15px', 'width': '80px', 'background-color': '#ffffff', 'position': 'fixed',
               'height': ' 100%', 'overflow': 'auto', 'border-right': 'solid 0.5px lightgrey'}),

    dcc.Location(id='url', refresh=False),
    html.Div(id='content', children=[])
])


@app.callback(Output('content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/main':
        return homePage.layout
    if pathname == '/Application':
        pathname = '/NearestHospital'
    if pathname == '/Beds':
        return html.Div([
            Application.layout,
            html.Div(id='Application Data', children=Beds.layout, className='Databox',
                     style={'position': 'absolute', 'left': '170px', 'top': '320px'}),
        ])
    if pathname == '/NearestHospital':
        return html.Div([
            Application.layout,
            html.Div(id='Application Data', children=NearestHospital.layout, className='Databox',
                     style={'position': 'absolute', 'left': '170px', 'top': '320px'}),
        ])

    if pathname == '/Oxygen':
        return html.Div([
            Application.layout,
            html.Div(id='Application Data', children=Oxygen.layout, className='Databox',
                     style={'position': 'absolute', 'left': '170px', 'top': '320px'}),
        ])

    if pathname == '/OS':
        return html.Div([
            Application.layout,
            OtherStates.layout,
        ])

    if pathname == '/GR':
        return html.Div([
            Application.layout,
            html.Div(id='Application Data', children=GovernmentRegulations.layout, className='Databox',
                     style={'position': 'absolute', 'left': '170px', 'top': '320px'}),
        ])

    if pathname == '/ambulance':
        return html.Div([
            Application.layout,
            html.Div(id='Application Data', children=ApplicationPage.Ambulance.layout, className='Databox',
                     style={'position': 'absolute', 'left': '170px', 'top': '320px'}),
        ])

    if '/info' in pathname:
        hname = str(pathname)
        hname = hname[len('/info'):]
        hname = hname.replace("%20", " ")
        hname = hname.strip()
        df2['Hospital Name'] = [i.strip() for i in list(df2['Hospital Name'])]
        data['Hospital Name'] = [i.strip() for i in list(data['Hospital Name'])]
        d22['Hospital Name'] = [i.strip() for i in list(d22['Hospital Name'])]
        d2 = df2[df2['Hospital Name'] == hname]
        d3 = data[data["Hospital Name"] == hname]
        l22 = list(d22[d22['Hospital Name'] == hname]['Image URL'])
        cleanedList = [x for x in (list(set(d2['Contact Details']))) if str(x) != 'nan']
        print(cleanedList)
        if len(cleanedList) == 0:
            contact = 'Not Available'
        else :
            contact = cleanedList[0]
        if len(l22) > 0:
            st_ad = l22[0]
        else:
            st_ad = 'https://thumbs.dreamstime.com/b/hospital-building-modern-parking-lot-59693686.jpg'
        return html.Div([
            Application.layout,
            html.Div([
                html.Div([
                    html.H2([
                        html.Br(),
                        'Information',
                    ], style={'margin-left': '70px'}),

                    html.Div([
                        html.Img(src='/assets/Bed.png', width='50px', height='50px'),
                        html.Div([
                            html.Font('Beds: ' + str(databeds[hname]['beds']),
                                      style={'font-size': 'large', 'white-space': 'pre'})

                        ], className='text2', style={'position': 'absolute', 'left': '60px', 'top': '15px'})
                    ], className='text2', style={'position': 'absolute', 'left': '150px', 'top': '110px'}),

                    html.Div([
                        html.Img(src='/assets/Bed.png', width='50px', height='50px'),
                        html.Div([
                            html.Font('Bed types: ', style={'font-size': 'large', 'white-space': 'pre'}),
                            html.Div(id='bed-types', children=[]),
                        ], className='text2', style={'position': 'absolute', 'left': '60px', 'top': '15px'})
                    ], className='text2', style={'position': 'absolute', 'left': '150px', 'top': '350px'}),

                    html.Div([
                        html.Img(src=st_ad, width='160px', height='160px', style={'border-radius': '6px'}),
                        html.P(convert_camel(hname))
                    ], style={'position': 'absolute', 'top': '160px', 'left': '770px'}),

                    html.Div([
                        html.Img(src='/assets/call.png', width='30px', height='30px'),
                        html.Div([
                            html.Font(str(contact),
                                      style={'font-size': 'large', 'white-space': 'pre'})

                        ], className='text2', style={'position': 'absolute', 'left': '60px', 'top': '15px'})
                    ], className='text2', style={'position': 'absolute', 'left': '150px', 'top': '180px'}),

                    html.Div([
                        html.Img(src='/assets/location.png', width='45px', height='45px'),
                        html.Div([
                            html.A('Direction',
                                   href=f'https://maps.google.com/?q={float(list(d3["lat"])[0])},{float(list(d3["lon"])[0])}',
                                   target='_blank',
                                   style={'font-size': 'large', 'white-space': 'pre'})

                        ], className='text2', style={'position': 'absolute', 'left': '60px', 'top': '15px'})
                    ], className='text2', style={'position': 'absolute', 'left': '148px', 'top': '230px'}),

                    html.Div([
                        html.Img(src='/assets/refresh.png', width='40px', height='40px'),
                        html.Div([
                            html.Font('Last updated On: ' + str(list(d2['Last Updated On'])[0]),
                                      style={'font-size': 'large', 'white-space': 'pre'})

                        ], className='text2', style={'position': 'absolute', 'left': '60px', 'top': '15px'})
                    ], className='text2', style={'position': 'absolute', 'left': '150px', 'top': '290px'}),
                ]),
            ], id='Application Data',
                className='Databox',
                style={'position': 'absolute', 'left': '170px', 'top': '320px'}),
        ])
    else:
        return homePage.layout


@app.callback(Output('bed-types', 'children'),
              [Input('url', 'pathname')])
def get_bed_types(pathname):
    hname = str(pathname)
    hname = hname[len('/info'):]
    hname = hname.replace("%20", " ")
    hname = hname.strip()
    df2['Hospital Name'] = [i.strip() for i in list(df2['Hospital Name'])]
    d2 = df2[df2['Hospital Name'] == hname]
    Req = list(d2['Requirement'])
    vac = list(d2['Vacant'])
    list_2 = []
    for i in range(len(Req)):
        list_2.append(html.Font([
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            str(Req[i]) + ' - ' + str(vac[i])], style={'font-size': 'medium', 'white-space': 'pre'}))
    return list_2


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
