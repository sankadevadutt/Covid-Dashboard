import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import numpy as np
from datetime import datetime
from app import app
import plotly.express as px

import warnings
warnings.filterwarnings('ignore')

def data_Confirmed():
    dfC = pd.read_csv(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
    dfC = dfC.replace(np.nan, '', regex=True)

    in_C = dfC.loc[(dfC['Country/Region'] == 'India')]

    Confirmed = in_C.to_numpy()

    index = dfC.columns[1:].to_numpy()
    return list(index[3:]), (list(Confirmed[0][4:]))


def data_Recovered():
    dfR = pd.read_csv(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
    dfR = dfR.replace(np.nan, '', regex=True)

    in_R = dfR.loc[(dfR['Country/Region'] == 'India')]

    Recovered = in_R.to_numpy()
    try:
        Recovered = list(Recovered[0][4:])
    except IndexError:
        Recovered = []
    return Recovered


def data_Deaths():
    dfD = pd.read_csv(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
    dfD = dfD.replace(np.nan, '', regex=True)

    in_D = dfD.loc[(dfD['Country/Region'] == 'India')]

    Deaths = in_D.to_numpy()
    return list(Deaths[0][4:])

def new_cases_c():
    index, confirmed = data_Confirmed()
    recoverd = data_Recovered()
    deaths = data_Deaths()
    new_c = []
    new_r = []
    new_d = []
    for i in range(len(confirmed) - 1):
        new_c.append(confirmed[i + 1] - confirmed[i])
        new_r.append(abs(recoverd[i + 1] - recoverd[i]))
        new_d.append(deaths[i + 1] - deaths[i])
    return index[1:], new_c, new_r, new_d


def get_change(Column,year,month):
    try:
        if(year == 2020 and month == 1):
            return 0.0
        elif(month == 1):
            ds1 = df3[df3['Year'] == year]
            ds2 = df3[df3['Year'] == year-1]
            ft = ds1[ds1['Month'] == month][Column]
            bt = ds2[ds2['Month'] == 12][Column]
            rate = round(((float(ft)-float(bt))/float(bt))*100,2)
            return rate
        else:
            ds = df3[df3['Year'] == year]
            ft = ds[ds['Month'] == month][Column]
            bt = ds[ds['Month'] == month-1][Column]
            rate = round(((float(ft)-float(bt))/float(bt))*100,2)
            return rate
    except:
        return 0


lt = []
t = new_cases_c()
for i in range(0,len(t[0])):
    lt.append([t[0][i],t[1][i],t[2][i],t[3][i]])

df = pd.DataFrame(lt,columns=['Date','Confirmed','Recovered','Death'])

Month = pd.DatetimeIndex(df['Date']).month
Year = pd.DatetimeIndex(df['Date']).year
data = []
for i in range(len(Month)):
    data.append(str(Month[i])+"/"+str(Year[i]))
df['Month'] = Month
df['Year'] = Year
df['Month/Year'] = data
lis = list(set(df['Month/Year']))
dicto = {}
for i in lis:
    dicto[i] = {}
    df2 = df[df['Month/Year'] == i]
    dicto[i]['Death Rate'] = round(((sum(list(df2['Death']))/(sum(list(df2['Confirmed']))) * 1.0)*100),3)
    dicto[i]['Average Month Rate'] = round(((sum(list(df2['Confirmed'])))/(len(df2)*1.0)),3)
    dicto[i]['Recovery Rate'] = round(((sum(list(df2['Recovered']))/(sum(list(df2['Confirmed']))) * 1.0)*100),3)
new_lt = []
for i in dicto.keys():
    new_lt.append([i,dicto[i]['Death Rate'],dicto[i]['Average Month Rate'],dicto[i]['Recovery Rate']])
df3 = pd.DataFrame(new_lt,columns=['Time Period','Death Rate','Average Monthly Reported Cases','Recovery Rate'])
df3['Month'] = pd.DatetimeIndex(df3['Time Period']).month
df3['Year'] = pd.DatetimeIndex(df3['Time Period']).year
df3['Month Full'] = [datetime.strptime(str(i), "%m").strftime("%b") for i in list(df3['Month'])]
month = list(set(df['Month']))
year = list(set(df['Year']))
ll = ['Death Rate','Average Monthly Reported Cases','Recovery Rate']
ll2 = []
for i in year:
    for j in month:
        ll2.append([j,i,get_change(ll[0],i,j),get_change(ll[1],i,j),get_change(ll[2],i,j)])
df5 = pd.DataFrame(ll2,columns=['Month','Year',"Rate Change in "+ll[0],"Rate Change in "+ll[1],"Rate Change in "+ll[2]])
df5['Month Full'] = [datetime.strptime(str(i), "%m").strftime("%b") for i in list(df5['Month'])]


layout = html.Div([
        html.Br(),
        html.H1("Welcome", style={"color": "#221869",'margin-left':'50px'}),
        html.Br(),

        html.Div([
            html.Img(src='assets/notification.png',
                     style={'width': '30px', 'height': '30px'})
        ], className='image', style={"position": "absolute", 'right': '100px', 'top': '20px'}),

        html.Div([
            html.Img(src='assets/user.png',
                     style={'width': '30px', 'height': '30px'})
        ], className='image', style={"position": "absolute", 'right': '50px', 'top': '20px'}),
        html.Div([
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Img(src='assets/corona.png',
                     style={'width': '300px', 'height': '300px'})
        ], className='image', style={'position': 'absolute', 'left': '220px'}),

        html.Div([
            html.Font('Strain', style={'font-size': 'x-small', 'color': '#939299','padding':'5px'}),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Font(html.B('SARS-CoV-2'), style={'font-size':'15px','color': "#6B6783",'padding':'5px'}),

        ], className='box',
            style={'position': 'absolute', 'left': '600px', 'top': '110px', 'width': '120px', 'height': '40px',
                   'border-radius': '5px', 'border': 'solid 1px lightgrey', 'padding': '5px', 'line-height': '0.5em'}),

        html.Div([
            html.Font('Symptoms', style={'font-size': 'x-small', 'color': '#939299','padding':'5px'}),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Font(html.B('Fever, Cough, Fatigue'), style={'font-size':'15px','color': "#6B6783",'padding':'5px'}),

        ], className='box2',
            style={'position': 'absolute', 'left': '770px', 'top': '110px', 'width': '180px', 'height': '40px',
                   'border-radius': '5px', 'border': 'solid 1px lightgrey', 'padding': '5px', 'line-height': '0.5em'}),

        html.Div([
            html.Font('Expected Vaccine Cure', style={'font-size': 'x-small', 'color': '#939299','padding':'5px'}),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Font(html.B('2021'), style={'font-size':'15px','color': "#6B6783",'padding':'5px'}),

        ], className='box2',
            style={'position': 'absolute', 'left': '1000px', 'top': '110px', 'width': '180px', 'height': '40px',
                   'border-radius': '5px', 'border': 'solid 1px lightgrey', 'padding': '5px', 'line-height': '0.5em'}),

        html.Div([
            html.Font(html.B('Death Rate'), style={'size': '-1', 'color': '#221869'}),
        ], className='text', style={'position': 'absolute', 'left': '770px', 'top': '190px'}),

        html.Div([
            html.Font([
                html.B([
                    html.Div([
                        dcc.Dropdown(id='year_drop',
                                     multi=False,
                                     searchable=False,
                                     clearable=False,
                                     disabled=False,
                                     style={'display': True,
                                            'outline': None,
                                            'border-color': 'white',
                                            'color': 'black',
                                            'width': '70px',
                                            'height': '20px'},
                                     value=list(set(Year))[0],
                                     options=[{'label': c, 'value': c}
                                              for c in list(set(Year))], className='doc_compon')
                    ], className='dropdown')
                ]),

            ], style={'font-size': 'small', 'color': '#221869'}),
        ], className='text', style={'position': 'absolute', 'left': '1150px', 'top': '178px'}),
        dcc.Graph(id='Death Rate',
                  style={'position': 'absolute', 'left': '700px', 'top': '205px','width':'600px','height':'250px'}),

        html.Div([
            html.Font('Usual onset', style={'font-size': 'x-small', 'color': '#939299','padding':'5px'}),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Font(html.B('2-14 days'), style={'font-size':'15px','color': "#6B6783",'padding':'5px'}),

        ], className='box',
            style={'position': 'absolute', 'left': '600px', 'top': '180px', 'width': '120px', 'height': '40px',
                   'border-radius': '5px', 'border': 'solid 1px lightgrey', 'padding': '5px', 'line-height': '0.5em'}),

        html.Div([
            html.Font('Origin', style={'font-size': 'x-small', 'color': '#939299','padding':'5px'}),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Font(html.B('Wuhan, China'), style={'font-size':'15px','color': "#6B6783",'padding':'5px'}),

        ], className='box',
            style={'position': 'absolute', 'left': '600px', 'top': '250px', 'width': '120px', 'height': '40px',
                   'border-radius': '5px', 'border': 'solid 1px lightgrey', 'padding': '5px', 'line-height': '0.5em'}),

        html.Div([
            html.Font(html.B('Recovery Rate'), style={'size': '-1', 'color': '#221869'}),
        ], className='text', style={'position': 'absolute', 'left': '250px', 'top': '430px'}),

        html.Div([
            html.Font([
                html.B([
                    html.Div([
                        dcc.Dropdown(id='year_drop2',
                                     multi=False,
                                     searchable=False,
                                     clearable=False,
                                     disabled=False,
                                     style={'display': True,
                                            'outline': None,
                                            'border-color': 'transparent',
                                            'color': 'black',
                                            'width': '70px',
                                            'height': '20px'},
                                     value=list(set(Year))[0],
                                     options=[{'label': c, 'value': c}
                                              for c in list(set(Year))], className='doc_compon')
                    ], className='dropdown')
                ]),

            ], style={'font-size': 'small', 'color': '#221869'}),
        ], className='text', style={'position': 'absolute', 'left': '600px', 'top': '419px'}),

        dcc.Graph(id='Recovery Rate',
                  style={'position': 'absolute', 'left': '150px', 'top': '480px','width':'600px','height':'300px'}),

        html.Div([
            html.Font(html.B('Average Monthly Reported Cases'), style={'size': '-1', 'color': '#221869'}),
        ], className='text', style={'position': 'absolute', 'left': '770px', 'top': '430px'}),

        html.Div([
            html.Font([
                html.B([
                    html.Div([
                        dcc.Dropdown(id='year_drop3',
                                     multi=False,
                                     searchable=False,
                                     clearable=False,
                                     disabled=False,
                                     style={'display': True,
                                            'outline': None,
                                            'border-color': 'white',
                                            'color': 'black',
                                            'width' : '70px',
                                            'height': '20px'},
                                     value=list(set(Year))[0],
                                     options=[{'label': c, 'value': c}
                                              for c in list(set(Year))], className='doc_compon')
                    ], className='dropdown')
                ]),

            ], style={'font-size': 'small', 'color': '#221869'}),
        ], className='text', style={'position': 'absolute', 'left': '1150px', 'top': '419px'}),
    dcc.Graph(id='Monthly Reported Cases',
              style={'position': 'absolute', 'left': '700px', 'top': '480px', 'width': '600px',
                     'height': '300px'}),
    ], className="content")










@app.callback(
    Output("Monthly Reported Cases", "figure"),
    Input("year_drop3", "value"))
def display_Monthly_Cases(year):
    df4 = df3[df3['Year'] == year]
    df4 = df4.sort_values(by='Month')
    df4 = df4.rename(columns={'Month': 'Month Number', 'Month Full': 'Month'})
    fig = px.line(df4, x='Month', y='Average Monthly Reported Cases')
    fig.data[0].line.color = '#5caded'
    fig.layout.plot_bgcolor = '#f7fbfe'
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='')
    return fig

@app.callback(
    Output("Death Rate", "figure"),
    Input("year_drop", "value"))
def display_Death_Rate(year):
    df4 = df3[df3['Year'] == year]
    df4 = df4.sort_values(by='Month')
    df4 = df4.rename(columns={'Month': 'Month Number', 'Month Full': 'Month'})
    fig = px.line(df4, x='Month', y='Death Rate',markers=True)
    fig.data[0].line.color = '#ff2e5d'
    fig.layout.plot_bgcolor = '#fff3f6'
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='')
    return fig


@app.callback(
    Output("Recovery Rate", "figure"),
    Input("year_drop2", "value"))
def display_Recovery_Rate(year):
    df4 = df3[df3['Year'] == year]
    df4 = df4.sort_values(by='Month')
    df4 = df4.rename(columns={'Month': 'Month Number', 'Month Full': 'Month'})
    fig = px.bar(df4, x='Month', y='Recovery Rate',text_auto=True,color_discrete_sequence =['#7947f8']*len(df4))
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='')
    fig.layout.plot_bgcolor = '#f4f0ff'
    fig.update_layout(showlegend=False)
    fig.update_yaxes(visible=False)
    fig.update_traces(textfont_size = 8,textangle=0, textposition="outside", cliponaxis=False)
    return fig